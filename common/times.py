from pathlib import Path

import datetime


def create_datetime_path(parent_path: Path) -> Path:
    now = datetime.datetime.now()
    now_str = now.strftime('%Y-%m-%d-%H:%M')
    return parent_path / now_str
