import shutil
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from build_skills import package_skill
from validate_repo import RULES, validate


class DistributionTests(unittest.TestCase):
    def test_repo_contract(self):
        self.assertEqual(validate(ROOT), [])

    def test_each_zip_is_complete_isolated_and_reproducible(self):
        with tempfile.TemporaryDirectory() as temp:
            for name in RULES:
                folder = ROOT / "skills" / name
                archive = package_skill(folder, temp)
                first = archive.read_bytes()
                with zipfile.ZipFile(archive) as zip_file:
                    expected = {f"{name}/{p.relative_to(folder).as_posix()}" for p in folder.rglob("*") if p.is_file()}
                    self.assertEqual(set(zip_file.namelist()), expected)
                    for member in zip_file.namelist():
                        self.assertNotIn("..", Path(member).parts)
                        self.assertEqual(zip_file.read(member), (folder.parent / member).read_bytes())
                self.assertEqual(first, package_skill(folder, temp).read_bytes())

    def test_broken_and_cross_skill_references_are_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            copy = Path(temp) / "repo"
            shutil.copytree(ROOT, copy, ignore=shutil.ignore_patterns(".git", "dist", "__pycache__"))
            entry = copy / "skills/competitor-research/SKILL.md"
            with entry.open("a", encoding="utf-8") as stream:
                stream.write("\n[missing](references/missing.md)\n[other](../product-definition/SKILL.md)\n")
            errors = validate(copy)
            self.assertTrue(any("references/missing.md" in error for error in errors))
            self.assertTrue(any("../product-definition/SKILL.md" in error for error in errors))

    def test_missing_entry_cannot_be_packaged(self):
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaises(ValueError):
                package_skill(Path(temp), Path(temp) / "out")

    def test_symlink_resource_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            skill = base / "sample"
            skill.mkdir()
            (skill / "SKILL.md").write_text("sample", encoding="utf-8")
            (base / "private.txt").write_text("outside", encoding="utf-8")
            try:
                (skill / "linked.txt").symlink_to(base / "private.txt")
            except OSError:
                self.skipTest("Creating symlinks is unavailable on this host")
            with self.assertRaises(ValueError):
                package_skill(skill, base / "out")


if __name__ == "__main__":
    unittest.main()
