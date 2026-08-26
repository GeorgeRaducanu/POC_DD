# DD Canvas

A small C++14 raster library and example application. The public API is documented with Doxygen comments, and a Python utility turns compiler and documentation metadata into Markdown design material.

## Build

Requirements:

- CMake 3.16 or newer
- A C++ compiler with C++14 support
- Python 3.9 or newer for the generator
- LLVM/libclang, Doxygen, and Graphviz for the complete documentation workflow

Configure and build from PowerShell. Use Ninja when you need `compile_commands.json`; the Visual Studio generator does not consistently emit that file:

```powershell
cmake -S . -B build -G Ninja -DCMAKE_BUILD_TYPE=Debug
cmake --build build --config Debug
ctest --test-dir build -C Debug --output-on-failure
```

The compilation database is written to `build/compile_commands.json`. Run the sample from the build directory so its relative output path is available:

```powershell
New-Item -ItemType Directory -Force build/output | Out-Null
Push-Location build
.\dd_demo.exe
Pop-Location
```

The image is written to `build/output/sample.ppm`. Most image viewers do not open PPM files directly; ImageMagick or a small PPM viewer can inspect it.

## One-command workflow

Inside the devcontainer, run the complete build, test, documentation, diagram, and project-wide generation workflow with:

```sh
sh scripts/run.sh
```

The script creates `.venv`, installs `utils/gen_dd/requirements.txt`, configures Ninja, builds the C++14 targets, runs CTest, runs the example, generates Doxygen XML/HTML and Graphviz diagrams, then writes Markdown, styled DOT/SVG diagrams, and a standalone `design-report.html` to `utils/gen_dd/output/`.

## API documentation

If Doxygen is installed, generate XML and HTML documentation with:

```powershell
cmake --build build --target dd_docs
```

Browse `build/docs/html/index.html`, or inspect the XML consumed by the generator under `build/docs/xml/`.
Doxygen uses Graphviz's `dot` executable for its class, collaboration, and call graphs when Graphviz is installed.

## Design document generator

Create an isolated Python environment and install the utility dependencies:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r utils/gen_dd/requirements.txt
```

Then run the generator after building and generating documentation:

```powershell
.\.venv\Scripts\python.exe utils/gen_dd/main.py `
  --compilation-database build/compile_commands.json `
  --doxygen-xml build/docs/xml `
  --output utils/gen_dd/output
```

By default, the utility analyzes every unique translation unit in the compilation database. Use `--source` only when debugging one file. It uses each source file's actual compiler arguments from the compilation database, libclang to inspect declarations, a Python Doxygen XML parser to recover comments, Jinja templates to render Markdown, and the Python Graphviz binding to render relationship diagrams. The generator writes a styled `symbol-relationships.dot` source file, an SVG diagram when the native `dot` executable is available, and a self-contained `design-report.html` that can be opened directly from the filesystem and shared as the primary design artifact. Use `--help` for the complete interface. `--fixture` runs a dependency-light template smoke test.

On Windows, if libclang is not found automatically, set `LIBCLANG_PATH` to the directory containing `libclang.dll` before running the utility.

## Dev container

The project includes a Linux development container with the C++ toolchain, CMake, Ninja, Python, Doxygen, Graphviz, LLVM/libclang, and the Python packages from `utils/gen_dd/requirements.txt`:

```powershell
code --folder-uri .
```

Use **Dev Containers: Reopen in Container** in VS Code. Inside the container, configure with `cmake -S . -B build -G Ninja`, build, run `cmake --build build --target dd_docs`, and invoke the generator command above.
