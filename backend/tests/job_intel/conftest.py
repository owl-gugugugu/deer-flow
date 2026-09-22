"""job_intel 测试包的路径引导：把 backend/ 加入 sys.path 以导入自研包。

刻意不改动上游 pyproject——保持二开 diff 最小、CI 零额外安装步骤。
"""

from __future__ import annotations

import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[2]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))
