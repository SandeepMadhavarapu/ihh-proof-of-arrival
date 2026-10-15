from __future__ import annotations

import os
import re
import subprocess
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, List, Sequence

from .security import ensure_profile_output, redact_text


@dataclass
class CommandResult:
    command: str
    returncode: int
    stdout: str
    stderr: str

    @property
    def passed(self) -> bool:
        return self.returncode == 0


@dataclass
class BuildQAResult:
    passed: bool
    commands: List[CommandResult] = field(default_factory=list)
    static_errors: List[str] = field(default_factory=list)


class BuildQAAgent:
    BROWSER_HARNESSES = [
        "dark.mjs", "pixels.mjs", "states.mjs", "reflow.mjs", "wp.mjs",
        "nojs.mjs", "targets.mjs", "leak.mjs", "interact.mjs", "incomplete.mjs",
        "repro.mjs",
    ]

    def __init__(self, repo_root: Path, runner: Callable[..., subprocess.CompletedProcess] = subprocess.run) -> None:
        self.repo_root = Path(repo_root).resolve()
        self.runner = runner

    def _run(self, args: Sequence[str], env: dict[str, str] | None = None) -> CommandResult:
        p = self.runner(
            list(args), cwd=self.repo_root, env=env or os.environ.copy(),
            capture_output=True, text=True, timeout=180
        )
        print(f"QA {'PASS' if p.returncode == 0 else 'FAIL'}: {redact_text(' '.join(args))}", flush=True)
        return CommandResult(
            redact_text(" ".join(args)), p.returncode,
            redact_text(p.stdout), redact_text(p.stderr),
        )

    def _static_profile_checks(self, out_dir: Path) -> list[str]:
        errors: list[str] = []
        html = "\n".join((out_dir / name).read_text(encoding="utf-8") for name in ("copy.html", "preview.html"))
        if re.search(r"\bon[a-z]+\s*=|@import\b|url\s*\(", html, re.I):
            errors.append("generated profile contains event handlers or CSS resource loads")
        if "api.openai.com" in html.lower() or "OPENAI_API_KEY" in html or re.search(r"sk-[A-Za-z0-9_-]{20,}", html):
            errors.append("generated profile contains an API endpoint or secret marker")
        key = os.environ.get("OPENAI_API_KEY", "")
        if key and key in html:
            errors.append("generated profile contains the configured API secret")
        if re.search(r"<script\b", html, re.I):
            errors.append("generated profile contains a script element")
        if re.search(r"<(?:link|iframe|object|embed)\b", html, re.I):
            errors.append("generated profile contains a visitor-side external resource element")
        if re.search(r"\bsrc=[\"'](?:https?:)?//", html, re.I):
            errors.append("generated profile loads an external src resource")
        if re.search(r"\bhref=[\"']\s*(?:javascript|data|file|vbscript):", html, re.I):
            errors.append("generated profile contains an unsafe href scheme")
        if "REQUIRES HUMAN SIGN-OFF" not in html:
            errors.append("generated profile is not visibly marked REQUIRES HUMAN SIGN-OFF")
        if "<main" not in html or "<h1" not in html:
            errors.append("generated profile is missing expected semantic main/H1 structure")
        return errors

    def run(self, out_dir: Path) -> BuildQAResult:
        out_dir = ensure_profile_output(self.repo_root, Path(out_dir).resolve())
        results: list[CommandResult] = []
        rel_out = out_dir.relative_to(self.repo_root)
        build = self._run([sys.executable, "albright-wp/build.py", "--profile-dir", str(rel_out)])
        results.append(build)
        if not build.passed:
            return BuildQAResult(False, results, ["generic profile build failed"])
        static_errors = self._static_profile_checks(out_dir)

        integrity = self._run(["node", "qa/integrity.mjs", "."])
        results.append(integrity)
        if not integrity.passed:
            return BuildQAResult(False, results, static_errors)

        dep = self._run(["node", "-e", "require.resolve('playwright'); require.resolve('axe-core'); console.log('browser QA dependencies present')"])
        results.append(dep)
        if not dep.passed:
            static_errors.append("browser QA dependencies unavailable; profile cannot be marked done")
            return BuildQAResult(False, results, static_errors)

        site_server = subprocess.Popen(
            [sys.executable, "-m", "http.server", "8731", "--bind", "127.0.0.1", "--directory", str(self.repo_root / "site")],
            cwd=self.repo_root, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
        root_server = subprocess.Popen(
            [sys.executable, "-m", "http.server", "8741", "--bind", "127.0.0.1", "--directory", str(self.repo_root)],
            cwd=self.repo_root, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
        try:
            time.sleep(0.8)
            if any(proc.poll() is not None for proc in (site_server, root_server)):
                return BuildQAResult(False, results, static_errors + ["QA server failed to bind; refusing to test another process's content"])
            env = os.environ.copy()
            env.setdefault("CHROMIUM", "/usr/bin/chromium")
            rel = out_dir.relative_to(self.repo_root).as_posix()
            env["PROFILE_URL"] = f"http://127.0.0.1:8741/{rel}/preview.html"
            for name in self.BROWSER_HARNESSES:
                results.append(self._run(["node", f"qa/{name}"], env=env))
            results.append(self._run(["node", "qa/profile-factory.mjs"], env=env))
        finally:
            for proc in (site_server, root_server):
                proc.terminate()
                try:
                    proc.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    proc.kill()
        passed = not static_errors and all(r.passed for r in results)
        return BuildQAResult(passed, results, static_errors)
