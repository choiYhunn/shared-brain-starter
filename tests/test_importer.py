from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "import_notebooklm.py"
spec = importlib.util.spec_from_file_location("import_notebooklm", MODULE_PATH)
assert spec and spec.loader
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class ImporterTests(unittest.TestCase):
    def test_parses_valid_blocks(self) -> None:
        text = """<!-- FILE: brain/00_CURRENT.md -->
# Current
<!-- END FILE -->

<!-- FILE: sources/SOURCE_MAP.md -->
# Sources
<!-- END FILE -->
"""
        blocks = mod.parse_export(text)
        self.assertEqual([str(path) for path, _ in blocks], ["brain/00_CURRENT.md", "sources/SOURCE_MAP.md"])

    def test_rejects_traversal(self) -> None:
        text = """<!-- FILE: brain/../vault/secret.md -->
no
<!-- END FILE -->
"""
        with self.assertRaises(ValueError):
            mod.parse_export(text)

    def test_rejects_text_outside_blocks(self) -> None:
        with self.assertRaises(ValueError):
            mod.parse_export("model commentary\n")

    def test_rejects_duplicate_path(self) -> None:
        text = """<!-- FILE: brain/00_CURRENT.md -->
a
<!-- END FILE -->
<!-- FILE: brain/00_CURRENT.md -->
b
<!-- END FILE -->
"""
        with self.assertRaises(ValueError):
            mod.parse_export(text)

    def test_destination_remains_inside_root(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            dest = mod.destination(root, mod.safe_relative_path("brain/projects/demo.md"))
            self.assertEqual(dest, root.resolve() / "brain" / "projects" / "demo.md")


if __name__ == "__main__":
    unittest.main()
