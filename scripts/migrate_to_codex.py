#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class CommandSpec:
    name: str
    description: str
    path: Path


@dataclass(frozen=True)
class SkillSpec:
    name: str
    description: str
    path: Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Install Codex-compatible skills from claude-code-video-toolkit."
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=None,
        help="Toolkit repository root. Auto-detected by default.",
    )
    parser.add_argument(
        "--dest",
        type=Path,
        default=Path.home() / ".codex" / "skills",
        help="Codex skills destination directory.",
    )
    parser.add_argument(
        "--map-file",
        type=Path,
        default=None,
        help="Optional migration map override file.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing generated/copied skills if they already exist.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print planned actions without writing files.",
    )
    return parser.parse_args()


def find_repo_root(explicit: Path | None) -> Path:
    if explicit is not None:
        return explicit.resolve()

    current = Path(__file__).resolve().parent
    for candidate in [current, *current.parents]:
        if (candidate / "_internal" / "toolkit-registry.json").exists() and (
            candidate / ".claude"
        ).exists():
            return candidate

    raise SystemExit("Could not auto-detect repository root.")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_mapping(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise SystemExit(f"Mapping file not found: {path}")
    data = load_json(path)
    return {
        "skip_commands": set(data.get("skip_commands", [])),
        "skip_skills": set(data.get("skip_skills", [])),
        "command_name_overrides": data.get("command_name_overrides", {}),
        "skill_name_overrides": data.get("skill_name_overrides", {}),
    }


def load_registry(repo_root: Path) -> dict[str, Any]:
    return load_json(repo_root / "_internal" / "toolkit-registry.json")


def load_command_specs(
    repo_root: Path, registry: dict[str, Any], mapping: dict[str, Any]
) -> list[CommandSpec]:
    commands: list[CommandSpec] = []
    entries = registry.get("commands", {})

    for original_name, entry in sorted(entries.items()):
        if original_name in mapping["skip_commands"]:
            continue

        command_name = mapping["command_name_overrides"].get(original_name, original_name)
        relative_path = entry.get("path")
        if not relative_path:
            continue

        command_path = repo_root / relative_path
        commands.append(
            CommandSpec(
                name=command_name,
                description=entry.get("description", f"Codex wrapper for /{original_name}"),
                path=command_path,
            )
        )

    return commands


def parse_skill_frontmatter(skill_md: Path) -> tuple[str, str]:
    text = skill_md.read_text(encoding="utf-8")
    lines = text.splitlines()
    if len(lines) < 3 or lines[0].strip() != "---":
        raise SystemExit(f"Skill frontmatter missing in {skill_md}")

    name = ""
    description = ""
    for line in lines[1:]:
        stripped = line.strip()
        if stripped == "---":
            break
        if stripped.startswith("name:"):
            name = stripped.split(":", 1)[1].strip()
        if stripped.startswith("description:"):
            description = stripped.split(":", 1)[1].strip()

    if not name or not description:
        raise SystemExit(f"Skill name/description missing in {skill_md}")
    return name, description


def load_skill_specs(
    repo_root: Path, mapping: dict[str, Any]
) -> list[SkillSpec]:
    results: list[SkillSpec] = []
    for skill_md in sorted((repo_root / ".claude" / "skills").glob("*/SKILL.md")):
        source_name, description = parse_skill_frontmatter(skill_md)
        if source_name in mapping["skip_skills"]:
            continue

        skill_name = mapping["skill_name_overrides"].get(source_name, source_name)
        results.append(
            SkillSpec(
                name=skill_name,
                description=description,
                path=skill_md.parent,
            )
        )
    return results


def ensure_clean_dir(path: Path, force: bool, dry_run: bool) -> None:
    if path.exists():
        if not force:
            raise SystemExit(
                f"Destination already exists: {path}. Re-run with --force to overwrite."
            )
        if dry_run:
            return
        if path.is_dir():
            shutil.rmtree(path)
        else:
            path.unlink()


def write_text(path: Path, content: str, dry_run: bool) -> None:
    if dry_run:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def copy_tree(src: Path, dest: Path, force: bool, dry_run: bool) -> None:
    ensure_clean_dir(dest, force=force, dry_run=dry_run)
    if dry_run:
        return
    shutil.copytree(src, dest)


def command_wrapper_content(
    repo_root: Path,
    command: CommandSpec,
    installed_skill_names: list[str],
) -> str:
    related = ", ".join(f"`{name}`" for name in installed_skill_names) or "(none)"
    source_rel = command.path.relative_to(repo_root).as_posix()
    repo_name = repo_root.name

    return f"""---
name: {command.name}
description: Codex wrapper for Claude Code `/{command.name}` in `{repo_name}`. Use when the user wants: {command.description}
---

# /{command.name} for Codex

This skill is the Codex entrypoint equivalent of the Claude Code slash command `/{command.name}`.

## Source of Truth

Before acting, read the original workflow document:

`{source_rel}`

Also use these files when relevant:

1. `CLAUDE.md`
2. `_internal/toolkit-registry.json`
3. `docs/README.md`

## Operating Rules

1. Treat `{source_rel}` as the authoritative workflow.
2. Do not rewrite or replace the original Claude resources just to satisfy Codex.
3. Reuse installed toolkit skills when they help the task.
4. If the user request maps directly to this command, follow the original command flow in Codex style.

## Related Toolkit Skills

{related}
"""


def overview_skill_content(
    repo_root: Path,
    command_names: list[str],
    skill_names: list[str],
) -> str:
    repo_name = repo_root.name
    commands = ", ".join(f"`/{name}`" for name in command_names)
    skills = ", ".join(f"`{name}`" for name in skill_names)
    return f"""---
name: video-toolkit
description: Codex entry skill for `{repo_name}`. Use when working in this repository and you need the Codex equivalents of the toolkit's Claude commands and skills.
---

# Video Toolkit

This skill helps Codex operate inside `{repo_name}` without modifying the original Claude-specific resources.

## Source of Truth

1. `README.md`
2. `CLAUDE.md`
3. `_internal/toolkit-registry.json`
4. `.claude/commands/*`
5. `.claude/skills/*`

## Command Equivalents

Generated command-wrapper skills are available for:

{commands}

## Toolkit Skills

Installed toolkit skills include:

{skills}

## Usage Rule

If a user request maps closely to one of the command-equivalent skills above, prefer that skill entrypoint first.
"""


def install_overview_skill(
    repo_root: Path,
    dest_root: Path,
    command_names: list[str],
    skill_names: list[str],
    force: bool,
    dry_run: bool,
) -> Path:
    target = dest_root / "video-toolkit"
    ensure_clean_dir(target, force=force, dry_run=dry_run)
    write_text(
        target / "SKILL.md",
        overview_skill_content(repo_root, command_names, skill_names),
        dry_run=dry_run,
    )
    return target


def install_copied_skills(
    repo_root: Path,
    dest_root: Path,
    skills: list[SkillSpec],
    force: bool,
    dry_run: bool,
) -> list[Path]:
    installed: list[Path] = []
    for skill in skills:
        target = dest_root / skill.name
        copy_tree(skill.path, target, force=force, dry_run=dry_run)
        installed.append(target)
    return installed


def install_command_wrappers(
    repo_root: Path,
    dest_root: Path,
    commands: list[CommandSpec],
    installed_skill_names: list[str],
    force: bool,
    dry_run: bool,
) -> list[Path]:
    installed: list[Path] = []
    for command in commands:
        target = dest_root / command.name
        ensure_clean_dir(target, force=force, dry_run=dry_run)
        write_text(
            target / "SKILL.md",
            command_wrapper_content(repo_root, command, installed_skill_names),
            dry_run=dry_run,
        )
        installed.append(target)
    return installed


def print_plan(
    repo_root: Path,
    dest_root: Path,
    skills: list[SkillSpec],
    commands: list[CommandSpec],
) -> None:
    print(f"repo_root={repo_root}")
    print(f"dest={dest_root}")
    print(f"copy_skills={len(skills)}")
    for skill in skills:
        print(f"  skill:{skill.name} <- {skill.path.relative_to(repo_root)}")
    print(f"generate_command_wrappers={len(commands)}")
    for command in commands:
        print(f"  command:{command.name} <- {command.path.relative_to(repo_root)}")
    print("  skill:video-toolkit <- generated overview")


def main() -> int:
    args = parse_args()
    repo_root = find_repo_root(args.repo_root)
    map_file = args.map_file or (repo_root / "codex" / "migration_map.json")
    mapping = load_mapping(map_file)
    registry = load_registry(repo_root)
    commands = load_command_specs(repo_root, registry, mapping)
    skills = load_skill_specs(repo_root, mapping)
    dest_root = args.dest.expanduser().resolve()

    print_plan(repo_root, dest_root, skills, commands)
    if args.dry_run:
        return 0

    dest_root.mkdir(parents=True, exist_ok=True)
    install_copied_skills(
        repo_root=repo_root,
        dest_root=dest_root,
        skills=skills,
        force=args.force,
        dry_run=False,
    )
    install_command_wrappers(
        repo_root=repo_root,
        dest_root=dest_root,
        commands=commands,
        installed_skill_names=[skill.name for skill in skills],
        force=args.force,
        dry_run=False,
    )
    install_overview_skill(
        repo_root=repo_root,
        dest_root=dest_root,
        command_names=[command.name for command in commands],
        skill_names=[skill.name for skill in skills],
        force=args.force,
        dry_run=False,
    )
    print("done")
    return 0


if __name__ == "__main__":
    sys.exit(main())
