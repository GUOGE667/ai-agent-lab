"""Build the self-contained, offline project walkthrough from task manifests."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = Path(__file__).with_name("demo.template.html")
OUTPUT = Path(__file__).with_name("demo.html")

TITLES = {
    "tqdm-1-enumerate-start": "枚举起始索引失效",
    "tqdm-2-ansi-trim": "截断进度条后重复重置颜色",
    "tqdm-3-generator-bool": "生成器进度条无法判断真假",
    "tqdm-4-scale-no-total": "未知总量时数值缩放报错",
    "tqdm-5-disabled-bool": "禁用进度条丢失总量",
    "tqdm-6-disabled-iterator": "禁用进度条迭代异常",
    "tqdm-7-option-boundary": "命令行参数边界误判",
    "tqdm-8-custom-bar-format": "自定义进度条格式被覆盖",
    "tqdm-9-si-boundary": "SI 单位边界格式错误",
    "pysnooper-1-unicode-log": "Unicode 日志输出异常",
    "pysnooper-2-custom-repr": "自定义变量表示未生效",
    "tornado-5-backward-clock": "系统时钟回退影响超时",
    "tornado-9-none-url-args": "空 URL 参数处理异常",
    "tornado-14-force-current": "强制当前 IOLoop 失效",
    "youtube-dl-1-boolean-filter": "布尔筛选条件判断错误",
    "youtube-dl-3-html-unescape": "HTML 实体未正确还原",
    "youtube-dl-4-zero-arg-call": "零参数调用解析失败",
    "youtube-dl-5-pm-timestamp": "下午时间戳解析错误",
    "youtube-dl-6-dfxp-timing": "DFXP 字幕时间解析错误",
    "youtube-dl-7-escaped-apostrophe": "转义撇号解析错误",
}


def build() -> str:
    real_tasks = json.loads((ROOT / "real_tasks/tasks.json").read_text(encoding="utf-8"))
    examples = json.loads((ROOT / "examples/tasks.json").read_text(encoding="utf-8"))
    fixes = json.loads(
        (ROOT / "real_tasks/checks/reference_fixes.json").read_text(encoding="utf-8")
    )
    assert set(TITLES) == {task["id"] for task in real_tasks}
    assert set(fixes) == set(TITLES)
    payload = {
        "counts": {
            "real": len(real_tasks),
            "synthetic": len(examples),
            "projects": len({task["source"]["project"] for task in real_tasks}),
        },
        "tasks": [
            {
                "id": task["id"],
                "title": TITLES[task["id"]],
                "project": task["source"]["project"],
                "issue": task["issue"],
                "repo": task["repo"],
                "public_test": "test_issue.py",
                "acceptance_test": "real_tasks/checks/acceptance.py",
                "buggy_commit": task["source"]["buggy_commit"],
                "fixed_commit": task["source"]["fixed_commit"],
                "edits": fixes[task["id"]],
            }
            for task in real_tasks
        ],
    }
    data = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
    data = data.replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
    return TEMPLATE.read_text(encoding="utf-8").replace("/*__DEMO_DATA__*/", data)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="fail if demo.html needs rebuilding")
    args = parser.parse_args()
    content = build()
    if args.check:
        if not OUTPUT.exists() or OUTPUT.read_text(encoding="utf-8") != content:
            print("docs/demo.html is stale; run python docs/build_demo.py")
            return 1
        print("docs/demo.html is current")
    else:
        OUTPUT.write_text(content, encoding="utf-8")
        print(f"Built {OUTPUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
