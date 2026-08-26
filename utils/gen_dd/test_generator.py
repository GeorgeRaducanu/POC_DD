import tempfile
import unittest
from pathlib import Path

from main import Symbol, filter_compilation_arguments, fixture, render, render_graph


class GeneratorSmokeTest(unittest.TestCase):
    def test_fixture_writes_index_and_traceability(self):
        with tempfile.TemporaryDirectory() as directory:
            fixture(Path(directory))
            self.assertTrue((Path(directory) / "index.md").exists())
            self.assertTrue((Path(directory) / "traceability.md").exists())
            self.assertIn("dd_canvas::Canvas", (Path(directory) / "index.md").read_text(encoding="utf-8"))

    def test_filter_compilation_arguments_removes_output_and_source(self):
        source = Path("src/example.cpp")
        arguments = [
            "/usr/bin/c++",
            "-Iinclude",
            "-g",
            "-std=c++14",
            "-o",
            "build/example.cpp.o",
            "-c",
            str(source.resolve()),
        ]

        filtered = filter_compilation_arguments(arguments, source)

        self.assertEqual(filtered, [
            "-Iinclude",
            "-g",
            "-std=c++14",
        ])

    def test_graph_contains_styled_directed_relationship(self):
        parent = Symbol("sample::Canvas", "class", "src/example.cpp", 4)
        child = Symbol("sample::Canvas::draw", "method", "src/example.cpp", 8)
        parent.children.append(child)

        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            svg = render_graph([parent, child], output)
            dot = (output / "symbol-relationships.dot").read_text(encoding="utf-8")

            self.assertIn("contains", dot)
            self.assertIn("arrowsize", dot)
            self.assertIn("fillcolor", dot)
            self.assertTrue(svg or not (output / "symbol-relationships.svg").exists())

    def test_render_writes_self_contained_report_and_unique_symbol_pages(self):
        symbols = [
            Symbol("sample::main", "function", "src/one.cpp", 3),
            Symbol("sample::main", "function", "src/two.cpp", 3),
        ]

        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            render(symbols, "src/one.cpp, src/two.cpp", ["clang++", "-std=c++14"], output)
            pages = list((output / "symbols").glob("*.md"))
            report = (output / "design-report.html").read_text(encoding="utf-8")

            self.assertEqual(len(pages), 2)
            self.assertIn("Relationship diagram", report)
            self.assertIn("sample::main", report)
            self.assertIn("symbol-relationships", report)


if __name__ == "__main__":
    unittest.main()
