from pathlib import Path


def relative_report_links(run_dir: Path, reports: tuple[Path, ...]) -> list[str]:
    return [str(path.relative_to(run_dir)) for path in reports]
