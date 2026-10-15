from __future__ import annotations

import argparse
from pathlib import Path

from qa_framework.analytics.dashboard import generate_dashboard


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate the QA analytics dashboard")
    parser.add_argument("--db", default="artifacts/analytics/quality.db")
    parser.add_argument("--output", default="artifacts/analytics/dashboard.html")
    parser.add_argument("--requirements", default="configs/requirements.yaml")
    args = parser.parse_args()
    output = generate_dashboard(Path(args.db), Path(args.output), Path(args.requirements))
    print(output)


if __name__ == "__main__":
    main()
