"""Run one generated Python artifact through the paper's evaluation protocol.

Run this inside a clean environment (for example `docker run --rm -it -v $PWD:/work
python:3.10-slim`), never on a machine with packages you care about: it installs the
artifact's requirements and uninstalls them afterwards.

Steps
  1. record the baseline `pip list`
  2. install only the declared requirements (claimed dependencies)
  3. count newly installed packages
  4. run the script with a timeout; exit code 0 counts as success. A process that is
     still running at the timeout (for example a web server) is stopped and counted as a
     successful start; the output then has "timed_out": true
  5. if `sciunit` is on PATH, capture the runtime dependencies with Sciunit
  6. uninstall everything that was added, restoring the baseline

Example
  python src/evaluate_python_project.py projects/claude_generated/python/p_3 \
      --script p_3_script_claude.py --requirements p_3_requirements_claude.txt

This script was written for this release as a reference for Python artifacts; it is not
the tooling that produced data/results. The Sciunit step has not been tested here. For
JavaScript and Java the paper reads the runtime dependencies from `npm list --all --json`
and `mvn dependency:tree`.
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
import uuid
from pathlib import Path


def pip_packages() -> set[str]:
    out = subprocess.run([sys.executable, "-m", "pip", "list", "--format=freeze"],
                         capture_output=True, text=True).stdout
    return {line.split("==")[0].lower() for line in out.splitlines() if "==" in line}


def read_claimed(req: Path) -> list[str]:
    lines = [l.strip() for l in req.read_text(encoding="utf-8", errors="replace").splitlines()]
    return [l for l in lines if l and not l.startswith("#")]


def as_text(data) -> str:
    if data is None:
        return ""
    return data.decode("utf-8", errors="replace") if isinstance(data, bytes) else data


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("project", type=Path)
    ap.add_argument("--script", required=True)
    ap.add_argument("--requirements", default="requirements.txt")
    ap.add_argument("--timeout", type=int, default=30)
    ap.add_argument("--args", nargs=argparse.REMAINDER, default=[], help="arguments passed to the script")
    args = ap.parse_args()

    project = args.project.resolve()
    req = project / args.requirements
    claimed = read_claimed(req) if req.exists() else []
    baseline = pip_packages()

    install_log = ""
    if claimed:
        r = subprocess.run([sys.executable, "-m", "pip", "install", "-r", str(req)],
                           capture_output=True, text=True)
        install_log = (r.stdout + r.stderr)[-4000:]
    installed = sorted(pip_packages() - baseline)

    timed_out = False
    try:
        run = subprocess.run([sys.executable, args.script, *args.args], cwd=project,
                             capture_output=True, text=True, timeout=args.timeout)
        exit_code, output = run.returncode, (run.stdout + run.stderr)[-4000:]
    except subprocess.TimeoutExpired as e:
        timed_out, exit_code = True, None
        output = (as_text(e.stdout) + as_text(e.stderr))[-4000:]

    runtime = None
    if shutil.which("sciunit"):
        ws = Path(tempfile.mkdtemp(prefix="sciunit_"))
        subprocess.run(["sciunit", "create", f"eval_{uuid.uuid4().hex[:8]}"], cwd=ws, capture_output=True)
        try:
            subprocess.run(["sciunit", "exec", sys.executable, str(project / args.script), *args.args],
                           cwd=project, capture_output=True, timeout=args.timeout * 3)
        except subprocess.TimeoutExpired:
            pass
        exp = subprocess.run(["sciunit", "export", "e1"], cwd=ws, capture_output=True, text=True)
        req_out = ws / "e1-requirements.txt"
        if req_out.exists():
            runtime = read_claimed(req_out)
        else:
            runtime = [exp.stdout.strip()] if exp.stdout.strip() else []

    added = sorted(pip_packages() - baseline)
    if added:
        subprocess.run([sys.executable, "-m", "pip", "uninstall", "-y", *added], capture_output=True)

    print(json.dumps({
        "project": str(args.project),
        "claimed": claimed,
        "claimed_count": len(claimed),
        "installed_new": installed,
        "installed_count": len(installed),
        "runtime_deps": runtime,
        "runtime_count": None if runtime is None else len(runtime),
        "execution_success": timed_out or exit_code == 0,
        "timed_out": timed_out,
        "exit_code": exit_code,
        "output_tail": output,
        "install_log_tail": install_log,
    }, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
