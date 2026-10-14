"""Package self-contained Skills with reproducible member order and timestamps."""
import os
import tempfile
import zipfile
from pathlib import Path

from validate_repo import ROOT, RULES, contained, validate


def package_skill(folder, output):
    folder, output = Path(folder), Path(output)
    if folder.is_symlink() or not (folder / "SKILL.md").is_file():
        raise ValueError("Expected a real Skill directory with SKILL.md")
    members = []
    for path in sorted(folder.rglob("*")):
        if path.is_symlink() or not contained(folder, path):
            raise ValueError(f"Refusing linked or escaping resource: {path.name}")
        if path.is_file():
            members.append(path)
    output.mkdir(parents=True, exist_ok=True)
    destination = output / f"{folder.name}.zip"
    if destination.is_symlink():
        raise ValueError("Refusing linked output")
    fd, temp = tempfile.mkstemp(suffix=".zip", dir=output)
    os.close(fd)
    try:
        with zipfile.ZipFile(temp, "w", zipfile.ZIP_DEFLATED) as archive:
            for path in members:
                info = zipfile.ZipInfo(f"{folder.name}/{path.relative_to(folder).as_posix()}", (2026, 1, 1, 0, 0, 0))
                info.compress_type = zipfile.ZIP_DEFLATED
                info.external_attr = 0o100644 << 16
                archive.writestr(info, path.read_bytes())
        os.replace(temp, destination)
    finally:
        if os.path.exists(temp):
            os.unlink(temp)
    return destination


if __name__ == "__main__":
    problems = validate()
    if problems:
        raise SystemExit("\n".join(problems))
    for name in sorted(RULES):
        print(package_skill(ROOT / "skills" / name, ROOT / "dist").relative_to(ROOT))
