"""smoke_transfer.sh refuses bad input; the full run needs a built package (RBOT_SMOKE_ZIP)."""

from __future__ import annotations

import os
import subprocess
import sys
import zipfile
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "smoke_transfer.sh"


def _smoke(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["bash", str(SCRIPT), *args], capture_output=True, text=True)


def test_usage_error_without_arguments() -> None:
    done = _smoke()
    assert done.returncode == 2
    assert "usage" in done.stderr


def test_package_without_manifest_fails_at_the_manifest_step(tmp_path: Path) -> None:
    archive = tmp_path / "bad.zip"
    with zipfile.ZipFile(archive, "w") as zf:
        zf.writestr("install.sh", "echo hi\n")
    done = _smoke(str(archive), sys.executable)
    assert done.returncode != 0
    assert "FAIL: manifest matches the extracted files" in done.stderr
    assert "SMOKE PASS" not in done.stdout


@pytest.mark.skipif("RBOT_SMOKE_ZIP" not in os.environ, reason="needs a built transfer package")
def test_built_package_passes() -> None:
    done = _smoke(os.environ["RBOT_SMOKE_ZIP"], os.environ.get("RBOT_SMOKE_PYTHON", sys.executable))
    assert done.returncode == 0, done.stdout + done.stderr
    assert "SMOKE PASS" in done.stdout
