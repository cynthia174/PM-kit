"""Validate PM-kit's repository contracts; no network or third-party packages."""
import json
import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
RULES = {
    "competitor-research": ("C", 18),
    "user-review-analysis": ("R", 20),
    "product-definition": ("D", 18),
    "product-writing-style": ("W", 12),
}


def contained(base, target):
    return target.resolve().is_relative_to(base.resolve())


def validate(root=ROOT):
    root = Path(root)
    errors = []
    skills = root / "skills"
    actual = {p.name for p in skills.iterdir() if p.is_dir()}
    if actual != set(RULES):
        errors.append("Skill catalog differs from RULES")
    for name, (prefix, count) in RULES.items():
        folder = skills / name
        entry = folder / "SKILL.md"
        if not entry.is_file():
            errors.append(f"Missing entry: {name}")
            continue
        text = entry.read_text(encoding="utf-8")
        front = re.match(r"\A---\n(.*?)\n---\n", text, re.S)
        # Deliberately supports this repository's plain single-line YAML scalars.
        fields = dict(re.findall(r"^(name|description): (.+)$", front[1], re.M)) if front else {}
        if fields.get("name") != name or not fields.get("description", "").strip():
            errors.append(f"Invalid name/description frontmatter: {name}")
        acceptance = folder / "references/acceptance.md"
        ids = re.findall(r"^\| ([CWDR]\d{2})\b", acceptance.read_text(encoding="utf-8"), re.M) if acceptance.exists() else []
        if ids != [f"{prefix}{i:02d}" for i in range(1, count + 1)]:
            errors.append(f"Missing, duplicate or unordered rule IDs: {name}")
        ui = folder / "agents/openai.yaml"
        values = {}
        if ui.exists():
            for key, value in re.findall(r'^  (\w+): (".*")$', ui.read_text(encoding="utf-8"), re.M):
                try:
                    values[key] = json.loads(value)
                except ValueError:
                    errors.append(f"Invalid quoted UI field: {name}/{key}")
        if not 25 <= len(values.get("short_description", "")) <= 64:
            errors.append(f"UI short_description must be 25-64 characters: {name}")
        if f"${name}" not in values.get("default_prompt", ""):
            errors.append(f"UI default_prompt must invoke its own Skill: {name}")

    paths = [root / "README.md"]
    paths += list((root / "docs").rglob("*.md"))
    paths += list((root / "evals").rglob("*.md"))
    paths += list(skills.rglob("*.md"))
    for path in paths:
        if not path.exists():
            errors.append(f"Missing file: {path.relative_to(root)}")
            continue
        text = path.read_text(encoding="utf-8")
        base = skills / path.relative_to(skills).parts[0] if path.is_relative_to(skills) else root
        for dest in re.findall(r"\[[^\]]*\]\(([^)]+)\)", text):
            link = urlsplit(dest.strip("<>"))
            if link.scheme or link.netloc or not link.path:
                continue
            target = path.parent / unquote(link.path)
            if not contained(base, target) or not target.exists():
                errors.append(f"Missing or non-self-contained link: {path.relative_to(root)} -> {dest}")
        # Small accidental-source-leak check, not a comprehensive secret scanner.
        if re.search(r"https?://[^\s/]+\.feishu\.cn/|thread://|[A-Z]:[\\/]Users[\\/]|BEGIN (?:RSA |OPENSSH )?PRIVATE KEY", text):
            errors.append(f"Potential private source in {path.relative_to(root)}")
    try:
        market = json.loads((root / ".claude-plugin/marketplace.json").read_text(encoding="utf-8"))
        plugins = market["plugins"]
        if len(plugins) != len(RULES) or {p["name"] for p in plugins} != set(RULES):
            errors.append("Marketplace catalog differs from Skills")
        for plugin in plugins:
            if plugin["source"] != "./" or plugin["strict"] is not False or plugin["skills"] != [f'./skills/{plugin["name"]}']:
                errors.append(f"Invalid marketplace source: {plugin['name']}")
        cases = json.loads((root / "evals/cases.json").read_text(encoding="utf-8"))
        if {c["skill"] for c in cases} != set(RULES) or len({c["id"] for c in cases}) != len(cases):
            errors.append("Eval cases need unique IDs and coverage of every Skill")
        for case in cases:
            if not all(case.get(k) for k in ("request", "checks", "positive_triggers", "negative_triggers")):
                errors.append(f"Incomplete eval: {case['id']}")
    except (OSError, ValueError, KeyError, TypeError) as exc:
        errors.append(f"Invalid catalog/eval manifest: {exc}")
    return errors


if __name__ == "__main__":
    problems = validate()
    print("\n".join(problems) if problems else "PASS: 4 Skills, 68 rules, local links, UI metadata, marketplace and eval manifests")
    sys.exit(bool(problems))
