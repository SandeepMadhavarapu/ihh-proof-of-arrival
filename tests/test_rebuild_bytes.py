import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class RebuildBytesTests(unittest.TestCase):
    def test_legacy_generators_preserve_shipped_bytes_in_fresh_directory(self):
        repo = Path(__file__).resolve().parents[1]
        outputs = (
            "albright-wp/copy.html", "albright-wp/copy-full.md",
            "albright-wp/preview.html", "site/verify.html",
        )
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name in ("albright-wp", "site"):
                shutil.copytree(repo / name, root / name)
            before = {name: (root / name).read_bytes() for name in outputs}
            for script in ("albright-wp/build.py", "site/gen.py"):
                subprocess.run(
                    [sys.executable, str(root / script)], cwd=root,
                    check=True, capture_output=True,
                )
            for name in outputs:
                with self.subTest(output=name):
                    self.assertEqual(before[name], (root / name).read_bytes())


if __name__ == "__main__":
    unittest.main()
