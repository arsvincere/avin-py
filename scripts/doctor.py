#!/usr/bin/env python3

# ────────────────────────────────────────────────────────────────────────────
#  AVIN
#  Understand the market before trading it.
#
#  https://avin.info
# ────────────────────────────────────────────────────────────────────────────

from __future__ import annotations

import subprocess
import tomllib
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VENV = ROOT / ".venv"
CACHE = ROOT / ".cache"
PYPROJECT = ROOT / "pyproject.toml"
VENV_PYTHON = VENV / "bin" / "python"

GREEN = "\033[32m"
RED = "\033[31m"
BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"


@dataclass(frozen=True)
class Check:
    name: str
    ok: bool
    detail: str = ""


def run(cmd: list[str]) -> tuple[bool, str]:
    try:
        result = subprocess.run(
            cmd,
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
    except FileNotFoundError:
        return False, "not found"

    output = result.stdout.strip() or result.stderr.strip()
    first_line = output.splitlines()[0] if output else ""

    return result.returncode == 0, first_line


def command_check(name: str, cmd: list[str]) -> Check:
    ok, detail = run(cmd)
    return Check(name=name, ok=ok, detail=detail)


def path_check(name: str, path: Path) -> Check:
    if path.exists():
        detail = str(path.relative_to(ROOT))
        return Check(name=name, ok=True, detail=detail)

    return Check(name=name, ok=False, detail="missing")


def pyproject_check() -> Check:
    if not PYPROJECT.exists():
        return Check(name="pyproject.toml", ok=False, detail="missing")

    try:
        tomllib.loads(PYPROJECT.read_text())
    except tomllib.TOMLDecodeError as e:
        return Check(name="pyproject.toml", ok=False, detail=str(e))

    return Check(name="pyproject.toml", ok=True, detail="valid TOML")


def venv_import_check(module: str) -> Check:
    if not VENV_PYTHON.exists():
        return Check(
            name=module,
            ok=False,
            detail=".venv python missing",
        )

    code = (
        "import importlib.util; "
        f"raise SystemExit(0 if importlib.util.find_spec({module!r}) else 1)"
    )

    ok, _ = run([str(VENV_PYTHON), "-c", code])

    return Check(
        name=module,
        ok=ok,
        detail="import ok" if ok else "import failed",
    )


def print_header() -> None:
    print()
    print(f"{BOLD}AVIN DEV DOCTOR{RESET}")
    print(f"{DIM}Understand the market before trading it.{RESET}")
    print()


def print_check(check: Check) -> None:
    mark = f"{GREEN}✓{RESET}" if check.ok else f"{RED}✗{RESET}"
    detail = f"{DIM}{check.detail}{RESET}" if check.detail else ""

    print(f"  {mark} {check.name:<18} {detail}")


def main() -> int:
    checks = [
        path_check(".venv", VENV),
        path_check(".cache", CACHE),
        pyproject_check(),
        command_check("python3", ["python3", "--version"]),
        command_check("uv", ["uv", "--version"]),
        command_check("just", ["just", "--version"]),
        command_check("git", ["git", "--version"]),
        command_check("venv python", [str(VENV_PYTHON), "--version"]),
        command_check("ruff", [str(VENV_PYTHON), "-m", "ruff", "--version"]),
        command_check("mypy", [str(VENV_PYTHON), "-m", "mypy", "--version"]),
        command_check(
            "pytest", [str(VENV_PYTHON), "-m", "pytest", "--version"]
        ),
        venv_import_check("avin"),
        venv_import_check("polars"),
        venv_import_check("PyQt6"),
        venv_import_check("t_tech"),
    ]

    print_header()

    for check in checks:
        print_check(check)

    print()

    failed = [check for check in checks if not check.ok]

    if failed:
        print(f"{RED}{BOLD}AVIN environment is broken.{RESET}")
        print(f"{DIM}Fix failed checks above.{RESET}")
        return 1

    print(f"{GREEN}{BOLD}AVIN environment is ready.{RESET}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
