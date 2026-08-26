"""Generate Markdown design material from a CMake compilation database."""

from __future__ import print_function

import argparse
import hashlib
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

try:
    from jinja2 import Environment, FileSystemLoader, StrictUndefined
except ImportError:
    Environment = None

try:
    from clang import cindex
except ImportError:
    cindex = None

try:
    import doxmlparser  # Optional parser adapter; XML fallback keeps fixture mode usable.
except ImportError:
    doxmlparser = None

try:
    import graphviz
except ImportError:
    graphviz = None


@dataclass
class Symbol:
    qualified_name: str
    kind: str
    file: str
    line: int
    access: str = "public"
    comment: str = ""
    children: list = field(default_factory=list)

    @property
    def slug(self):
        readable = re.sub(r"[^a-z0-9]+", "-", self.qualified_name.lower()).strip("-")
        identity = "{}:{}:{}".format(self.qualified_name, self.file, self.line).encode("utf-8")
        return "{}-{}".format(readable, hashlib.sha1(identity).hexdigest()[:8])


def load_commands(database, source=None):
    entries = json.loads(Path(database).read_text(encoding="utf-8"))
    requested = str(Path(source).resolve()).lower() if source else None
    commands = []
    seen = set()
    for entry in entries:
        file_name = str(Path(entry["file"]).resolve())
        if requested and file_name.lower() != requested and Path(file_name).name.lower() != Path(requested).name.lower():
            continue
        key = file_name.lower()
        if key in seen:
            continue
        command = entry.get("arguments")
        if command is None:
            command = entry.get("command", "").split()
        commands.append((Path(file_name), list(command)))
        seen.add(key)
    if not commands:
        scope = source if source else "the compilation database"
        raise RuntimeError("No compilation commands found for {}".format(scope))
    return commands


def _cursor_kind(cursor):
    spelling = str(cursor.kind).split(".")[-1].lower()
    return spelling.replace("_decl", "")


def filter_compilation_arguments(arguments, source):
    source_path = str(Path(source).resolve())
    filtered = []
    skip_next = False
    for index, argument in enumerate(arguments[1:]):
        if skip_next:
            skip_next = False
            continue
        if argument in ("/c", "-c", "-o"):
            skip_next = argument == "-o"
            continue
        if argument == source_path or argument == str(Path(source).resolve().as_posix()):
            continue
        if argument.startswith("-MF") or argument.startswith("-MT") or argument.startswith("-m"):
            if argument.startswith("-MF") or argument.startswith("-MT"):
                if argument in ("-MF", "-MT"):
                    skip_next = True
                continue
        filtered.append(argument)
    return filtered


def extract_symbols(source, arguments):
    if cindex is None:
        raise RuntimeError("libclang Python bindings are unavailable; install requirements.txt")
    filtered = filter_compilation_arguments(arguments, source)
    index = cindex.Index.create()
    translation_unit = index.parse(str(Path(source).resolve()), args=filtered)
    source_path = str(Path(source).resolve()).lower()
    symbols = []

    def visit(cursor, parent=None):
        location = cursor.location
        if not location.file or str(location.file.name).lower() != source_path:
            for child in cursor.get_children():
                visit(child, parent)
            return
        if cursor.kind.is_declaration() and cursor.spelling:
            qualified = cursor.displayname
            if parent:
                qualified = parent.qualified_name + "::" + cursor.displayname
            symbol = Symbol(qualified, _cursor_kind(cursor), str(location.file.name), location.line,
                            str(cursor.access_specifier).split(".")[-1].lower(), cursor.raw_comment or "")
            symbols.append(symbol)
            if parent:
                parent.children.append(symbol)
            for child in cursor.get_children():
                visit(child, symbol)
        else:
            for child in cursor.get_children():
                visit(child, parent)

    visit(translation_unit.cursor)
    return symbols


def parse_doxygen(xml_root):
    """Return qualified-name to description mappings from Doxygen XML.

    The XML shape is intentionally normalized here so the rendering layer does
    not depend on a particular Doxygen parser package API.
    """
    import xml.etree.ElementTree as element_tree

    descriptions = {}
    root = Path(xml_root)
    for file_name in root.glob("*.xml"):
        try:
            tree = element_tree.parse(str(file_name))
        except element_tree.ParseError:
            continue
        for compound in tree.findall(".//compounddef"):
            name = compound.findtext("compoundname")
            description = " ".join(compound.findtext("briefdescription", "").split())
            if name:
                descriptions[name] = description
            for member in compound.findall(".//memberdef"):
                member_name = member.findtext("name")
                if name and member_name:
                    descriptions[name + "::" + member_name] = " ".join(
                        member.findtext("briefdescription", "").split()
                    )
    return descriptions


def render_graph(symbols, output):
    output = Path(output)
    dot_path = output / "symbol-relationships.dot"
    visible_kinds = {"namespace", "class", "struct", "function", "method", "constructor", "destructor"}
    visible = [symbol for symbol in symbols if symbol.kind in visible_kinds]
    node_ids = {id(symbol): "node{}".format(index) for index, symbol in enumerate(visible)}
    styles = {
        "namespace": ('shape=box, style="rounded,filled", fillcolor="#e8eef7", color="#54708f"'),
        "class": ('shape=box, style="rounded,filled", fillcolor="#d9f0ee", color="#287d78"'),
        "struct": ('shape=box, style="rounded,filled", fillcolor="#e6f2df", color="#5c8a3d"'),
        "function": ('shape=ellipse, style="filled", fillcolor="#fff1d6", color="#b77818"'),
        "method": ('shape=ellipse, style="filled", fillcolor="#fff1d6", color="#b77818"'),
        "constructor": ('shape=ellipse, style="filled", fillcolor="#fff1d6", color="#b77818"'),
        "destructor": ('shape=ellipse, style="filled", fillcolor="#fff1d6", color="#b77818"'),
    }
    lines = [
        "digraph design {",
        "  graph [bgcolor=\"#fbfaf7\", fontname=\"DejaVu Sans\", fontsize=12, rankdir=LR, ranksep=1.0, nodesep=0.45, splines=ortho, pad=0.3];",
        "  node [fontname=\"DejaVu Sans\", fontsize=10, margin=\"0.16,0.10\"];",
        "  edge [color=\"#718096\", fontname=\"DejaVu Sans\", fontsize=9, arrowsize=0.7, penwidth=1.2];",
    ]
    lines.append('  legend [label="Legend\\l  namespace  |  type  |  callable\\l", shape=note, style="filled", fillcolor="#f2eee6", color="#9b8f7a"];')
    for symbol in visible:
        node_id = node_ids[id(symbol)]
        label = "{}\\n{}".format(symbol.qualified_name, symbol.kind).replace('"', "\\\"")
        lines.append('  {} [label="{}", {}, URL="symbols/{}.md", tooltip="{}"];'.format(
            node_id, label, styles[symbol.kind], symbol.slug, symbol.qualified_name.replace('"', "\\\"")
        ))
        for child in symbol.children:
            if id(child) in node_ids:
                lines.append('  {} -> {} [xlabel="contains"];'.format(node_id, node_ids[id(child)]))
    lines.append("}")
    dot_source = "\n".join(lines) + "\n"
    dot_path.write_text(dot_source, encoding="utf-8")
    if graphviz is None:
        return ""
    try:
        graph = graphviz.Source(dot_source, filename=str(output / "symbol-relationships"), format="svg")
        graph.render(cleanup=True)
        return (output / "symbol-relationships.svg").read_text(encoding="utf-8")
    except graphviz.backend.ExecutableNotFound:
        return ""


def render(symbols, source, arguments, output, xml_root=None):
    if Environment is None:
        raise RuntimeError("Jinja2 is unavailable; install requirements.txt")
    documentation = parse_doxygen(xml_root) if xml_root else {}
    for symbol in symbols:
        symbol.comment = documentation.get(symbol.qualified_name, symbol.comment)
    output = Path(output)
    (output / "symbols").mkdir(parents=True, exist_ok=True)
    environment = Environment(loader=FileSystemLoader(str(Path(__file__).parent / "templates")),
                              undefined=StrictUndefined, autoescape=False)
    graph_svg = render_graph(symbols, output)
    values = {
        "project_name": "DD Canvas",
        "source": source,
        "compile_arguments": arguments,
        "symbols": symbols,
        "documented_count": sum(bool(symbol.comment) for symbol in symbols),
        "graph_svg": graph_svg,
        "graph_dot": (output / "symbol-relationships.dot").read_text(encoding="utf-8"),
    }
    (output / "index.md").write_text(environment.get_template("overview.md.j2").render(**values), encoding="utf-8")
    (output / "traceability.md").write_text(environment.get_template("traceability.md.j2").render(**values), encoding="utf-8")
    template = environment.get_template("symbol.md.j2")
    for symbol in symbols:
        (output / "symbols" / (symbol.slug + ".md")).write_text(template.render(symbol=symbol), encoding="utf-8")
    (output / "design-report.html").write_text(
        environment.get_template("report.html.j2").render(**values), encoding="utf-8"
    )


def generate_project(database, output, xml_root=None, source=None):
    all_symbols = []
    all_arguments = []
    source_names = []
    for source_path, arguments in load_commands(database, source):
        all_symbols.extend(extract_symbols(source_path, arguments))
        all_arguments.extend(arguments)
        source_names.append(str(source_path))
    unique_symbols = {}
    for symbol in all_symbols:
        unique_symbols[(symbol.qualified_name, symbol.file, symbol.line)] = symbol
    render(list(unique_symbols.values()), ", ".join(source_names), all_arguments, output, xml_root)


def fixture(output):
    symbol = Symbol("dd_canvas::Canvas", "class", "include/dd_canvas/canvas.hpp", 35,
                    comment="A compact row-major RGB raster.")
    render([symbol], "include/dd_canvas/canvas.hpp", ["clang++", "-std=c++14"], output)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--compilation-database", type=Path)
    parser.add_argument("--source", type=Path, help="optionally limit analysis to one translation unit")
    parser.add_argument("--doxygen-xml", type=Path)
    parser.add_argument("--output", type=Path, default=Path("utils/gen_dd/output"))
    parser.add_argument("--fixture", action="store_true", help="render a dependency-light smoke fixture")
    args = parser.parse_args(argv)
    try:
        if args.fixture:
            fixture(args.output)
        else:
            if not args.compilation_database:
                parser.error("--compilation-database is required unless --fixture is used")
            generate_project(args.compilation_database, args.output, args.doxygen_xml, args.source)
        print("Generated design material in {}".format(args.output))
        return 0
    except (OSError, RuntimeError, ValueError, KeyError) as error:
        print("gen_dd: {}".format(error), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
