"""Modular SAT-benchmarks verification checks with automatic plugin discovery.

Any new check file named ``check_<feature>.py`` placed inside ``src/checks/`` that exposes:
  - ``CHECK_NAME: str``
  - ``run(ctx: CheckContext) -> CheckResult``
  - (optional) ``CHECK_ORDER: int = 100``
  - (optional) ``REQUIRES_HYGIENE_FLAG: bool = False``
  - (optional) ``DESCRIPTION: str = ""``
is automatically discovered and available via ``verify_expected.py --check <name>``.
"""
from __future__ import annotations

import importlib
import pkgutil
from pathlib import Path
from types import ModuleType

from checks.common import CheckContext, CheckResult

__all__ = [
    "CheckContext",
    "CheckResult",
    "discover_checks",
    "get_checks_by_name",
    "select_checks",
]


def discover_checks() -> list[ModuleType]:
    """Auto-discover all ``check_*.py`` modules in ``src/checks/``, sorted by ``(CHECK_ORDER, CHECK_NAME)``."""
    pkg_dir = Path(__file__).resolve().parent
    modules: list[ModuleType] = []
    for info in pkgutil.iter_modules([str(pkg_dir)]):
        if not info.name.startswith("check_"):
            continue
        mod = importlib.import_module(f"checks.{info.name}")
        if hasattr(mod, "CHECK_NAME") and callable(getattr(mod, "run", None)):
            modules.append(mod)
    modules.sort(key=lambda m: (getattr(m, "CHECK_ORDER", 100), getattr(m, "CHECK_NAME", m.__name__)))
    return modules


def get_checks_by_name() -> dict[str, ModuleType]:
    """Return mapping of canonical check name -> check module."""
    return {mod.CHECK_NAME: mod for mod in discover_checks()}


def select_checks(requested: list[str] | None, check_hygiene: bool = False) -> list[ModuleType]:
    """Select modular check modules to run based on ``--check`` and ``--check-hygiene``.

    - When ``requested`` is provided (e.g. ``["math_hygiene"]`` or ``["layout,formats"]`` or ``["all"]``),
      accepts comma-separated names and optional ``check_`` prefixes.
    - When ``requested`` is omitted:
        * with ``check_hygiene=True``: runs ALL discovered checks in ``src/checks/``.
        * with ``check_hygiene=False``: runs all core checks (``REQUIRES_HYGIENE_FLAG == False``).
    """
    discovered = discover_checks()
    if not requested:
        if check_hygiene:
            return discovered
        return [m for m in discovered if not getattr(m, "REQUIRES_HYGIENE_FLAG", False)]

    by_name = {m.CHECK_NAME: m for m in discovered}
    tokens: list[str] = []
    for raw in requested:
        for tok in raw.split(","):
            t = tok.strip()
            if t:
                tokens.append(t)

    if any(t.lower() == "all" for t in tokens):
        return discovered

    selected: list[ModuleType] = []
    seen: set[str] = set()
    for tok in tokens:
        norm = tok[6:] if tok.startswith("check_") and tok[6:] in by_name else tok
        if norm not in by_name:
            avail = ", ".join(by_name.keys())
            raise ValueError(f"Unknown check {tok!r} (available: {avail}, all)")
        if norm not in seen:
            seen.add(norm)
            selected.append(by_name[norm])

    selected.sort(key=lambda m: (getattr(m, "CHECK_ORDER", 100), getattr(m, "CHECK_NAME", m.__name__)))
    return selected
