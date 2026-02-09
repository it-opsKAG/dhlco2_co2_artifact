from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    generator = root / "generators" / "build_exports.py"
    cmd = [sys.executable, str(generator)]
    subprocess.run(cmd, cwd=str(root), check=True)

    required = [
        root / "exports" / "KPI_Catalog.md",
        root / "exports" / "KPI_Catalog.csv",
        root / "exports" / "Lifecycle_Mapping.md",
        root / "exports" / "Gap_Report.md",
    ]
    missing = [str(path) for path in required if not path.exists()]
    if missing:
        raise SystemExit("Missing expected exports:\n" + "\n".join(missing))

    print("validate_and_export: ok")


if __name__ == "__main__":
    main()
