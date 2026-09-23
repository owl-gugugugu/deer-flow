"""job-intel 评估入口（A-M4-2 薄 CLI）：岗位清单 × 报告 → 指标 CSV。

用法（仓库根目录）：
    python evals/eval.py --jobs evals/data/jobs.csv --reports evals/samples \
        --out evals/results/metrics-YYYY-MM-DD.csv [--labels evals/data/labels.csv] [--no-fetch]

人工标注流程：先跑一次（无 --labels）得到全部唯一 URL 清单 → 人工逐条
标注 relevant∈{0,1} → 带 --labels 重跑得到引用有效率。
"""

from __future__ import annotations

import argparse
import sys
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[1] / "backend"
sys.path.insert(0, str(BACKEND))

from job_intel.eval_pipeline import run_pipeline, write_results_csv  # noqa: E402


def _fetch_with(timeout: float):
    def fetch(url: str) -> int:
        # GET 而非 HEAD：部分站点对 HEAD 回 405/403，会制造假死链
        request = urllib.request.Request(url, headers={"User-Agent": "job-intel-eval/0.1"})
        with urllib.request.urlopen(request, timeout=timeout) as resp:  # noqa: S310
            return resp.status
    return fetch


def prefetch_statuses(urls: list[str], timeout: float, workers: int = 16) -> dict[str, int]:
    """并发预取全部 URL 状态；异常映射为 -1（管线归入 unreachable）。"""
    fetch = _fetch_with(timeout)

    def probe(url: str) -> int:
        try:
            return fetch(url)
        except Exception:  # noqa: BLE001 - 统一降级为不可达
            return -1

    with ThreadPoolExecutor(max_workers=workers) as pool:
        return dict(zip(urls, pool.map(probe, urls)))


def main() -> int:
    parser = argparse.ArgumentParser(description="job-intel citation effectiveness evaluation")
    parser.add_argument("--jobs", required=True, help="岗位清单 CSV（company,position,report_file）")
    parser.add_argument("--reports", required=True, help="报告目录")
    parser.add_argument("--out", required=True, help="结果 CSV 输出路径")
    parser.add_argument("--labels", help="人工标注 CSV（url,relevant）；未提供时有效率列留空")
    parser.add_argument("--no-fetch", action="store_true", help="只统计结构，不探测 URL")
    parser.add_argument("--timeout", type=float, default=12.0, help="单 URL 超时秒数")
    args = parser.parse_args()

    from job_intel.eval_pipeline import _unique_urls

    jobs_path = Path(args.jobs)
    reports_dir = Path(args.reports)

    fetch = None
    if not args.no_fetch:
        all_urls: set[str] = set()
        for job in load_jobs_safe(jobs_path):
            md = (reports_dir / job.report_file).read_text(encoding="utf-8")
            all_urls.update(_unique_urls(md))
        statuses = prefetch_statuses(sorted(all_urls), args.timeout)

        def fetch(url: str) -> int:
            status = statuses[url]
            if status == -1:
                raise TimeoutError(url)
            return status

    rows, summary = run_pipeline(
        jobs_path, reports_dir,
        labels_csv=Path(args.labels) if args.labels else None,
        fetch=fetch,
    )
    write_results_csv(rows, summary, Path(args.out))
    print(f"reports={summary.reports} urls={summary.total_unique_urls} "
          f"reachability={summary.reachability_rate} effectiveness={summary.effectiveness_rate} "
          f"structure={summary.mean_structure_completeness}")
    print(f"results -> {args.out}")
    return 0


def load_jobs_safe(jobs_path: Path):
    from job_intel.eval_pipeline import load_jobs

    return load_jobs(jobs_path)


if __name__ == "__main__":
    raise SystemExit(main())
