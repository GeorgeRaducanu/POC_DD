import tempfile
import unittest
from pathlib import Path

from main import fixture, filter_compilation_arguments


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


if __name__ == "__main__":
    unittest.main()
