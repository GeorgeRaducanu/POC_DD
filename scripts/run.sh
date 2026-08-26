#!/usr/bin/env sh

set -eu

ROOT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
BUILD_DIR=${BUILD_DIR:-"$ROOT_DIR/build"}
VENV_DIR=${VENV_DIR:-"$ROOT_DIR/.venv"}
OUTPUT_DIR=${OUTPUT_DIR:-"$ROOT_DIR/utils/gen_dd/output"}

command -v cmake >/dev/null 2>&1 || { echo "cmake is required" >&2; exit 1; }
command -v ninja >/dev/null 2>&1 || { echo "ninja is required; use the devcontainer or install Ninja" >&2; exit 1; }
command -v python3 >/dev/null 2>&1 || { echo "python3 is required" >&2; exit 1; }

if [ ! -x "$VENV_DIR/bin/python" ]; then
    echo "Creating Python environment in $VENV_DIR"
    python3 -m venv "$VENV_DIR"
fi

PYTHON="$VENV_DIR/bin/python"
"$PYTHON" -m pip install -r "$ROOT_DIR/utils/gen_dd/requirements.txt"

echo "Configuring C++14 build"
cmake -S "$ROOT_DIR" -B "$BUILD_DIR" -G Ninja -DCMAKE_BUILD_TYPE=Debug

echo "Building library, application, and tests"
cmake --build "$BUILD_DIR"

echo "Running tests"
ctest --test-dir "$BUILD_DIR" --output-on-failure

mkdir -p "$BUILD_DIR/output"
echo "Running example application"
(cd "$BUILD_DIR" && ./dd_demo)

echo "Generating Doxygen XML, HTML, and diagrams"
cmake --build "$BUILD_DIR" --target dd_docs

echo "Generating project-wide design material"
"$PYTHON" "$ROOT_DIR/utils/gen_dd/main.py" \
    --compilation-database "$BUILD_DIR/compile_commands.json" \
    --doxygen-xml "$BUILD_DIR/docs/xml" \
    --output "$OUTPUT_DIR"

echo "Complete"
echo "HTML documentation: $BUILD_DIR/docs/html/index.html"
echo "Generated design material: $OUTPUT_DIR/index.md"
echo "Example image: $BUILD_DIR/output/sample.ppm"