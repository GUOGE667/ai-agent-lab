# 真实历史缺陷任务（首批 9 条）

这 9 条任务来自 [BugsInPy 的 tqdm 项目](https://github.com/soarsmu/BugsInPy/tree/master/projects/tqdm)所记录的历史缺陷，源码来自 [tqdm 上游仓库](https://github.com/tqdm/tqdm)。任务描述和验收测试由本项目编写，**不是**原始 GitHub Issue 文本。每题固定在一个上游 buggy commit，保留运行所需的 Python 包源码和该版本的许可证文件；上游原测试及其他非运行文件没有复制进任务仓库。

筛选时使用的 BugsInPy 元数据提交：[`11c5f1e`](https://github.com/soarsmu/BugsInPy/commit/11c5f1eea954a42132cfd06bf257766a7963e0fd)。每条任务的完整提交 SHA 也写在 [`tasks.json`](tasks.json) 中。

| 任务 | BugsInPy | 上游 buggy commit | 上游 fixed commit | 可复现行为 |
|---|---|---|---|---|
| `tqdm-1-enumerate-start` | bug 1 | [`8cc777f`](https://github.com/tqdm/tqdm/commit/8cc777fe8401a05d07f2c97e65d15e4460feab88) | [`c0dcf39`](https://github.com/tqdm/tqdm/commit/c0dcf39b046d1b4ff6de14ac99ad9a1b10487512) | `tenumerate(..., start=5)` 仍从 0 开始 |
| `tqdm-2-ansi-trim` | bug 2 | [`bef86db`](https://github.com/tqdm/tqdm/commit/bef86db56654d271838b145ad77f7040a73a7b4d) | [`127af5c`](https://github.com/tqdm/tqdm/commit/127af5caf19e7d29c346f5ca8a9c7ef3004b664b) | ANSI 文本截断后重复追加重置序列 |
| `tqdm-3-generator-bool` | bug 3 | [`c2599e3`](https://github.com/tqdm/tqdm/commit/c2599e3cd6087429f48bae34347ec5d2473c8392) | [`73962a4`](https://github.com/tqdm/tqdm/commit/73962a47026dd980ac0758820efc9c41cbf938e0) | 未知长度迭代器的 `bool(tqdm(...))` 抛出 `TypeError` |
| `tqdm-4-scale-no-total` | bug 4 | [`03b3476`](https://github.com/tqdm/tqdm/commit/03b347646492131d889871939b40457d29147216) | [`964dee6`](https://github.com/tqdm/tqdm/commit/964dee631d0ed30e2f799b42fc58ba5e73795a08) | 总量为 `None` 且使用数值 `unit_scale` 时抛出 `TypeError` |
| `tqdm-5-disabled-bool` | bug 5 | [`19b08ab`](https://github.com/tqdm/tqdm/commit/19b08ab34fdbfa0275bc5cb2430436c724c7e759) | [`4f34069`](https://github.com/tqdm/tqdm/commit/4f340697af69b71850aad496387c9c5aa1904136) | 禁用实例缺少总量属性，真值判断报错 |
| `tqdm-6-disabled-iterator` | bug 6 | [`a4b9c86`](https://github.com/tqdm/tqdm/commit/a4b9c86db548b2d0dbb5af7a6bbdc26ab47e1eec) | [`6dad2e8`](https://github.com/tqdm/tqdm/commit/6dad2e89019317e875c46d5a3a82a811ad6de2f9) | 禁用实例包装无长度迭代器时，`list()` 报错 |
| `tqdm-7-option-boundary` | bug 7 | [`caefe02`](https://github.com/tqdm/tqdm/commit/caefe02fd6f3165e5634460ab20caf4c60400120) | [`4efd352`](https://github.com/tqdm/tqdm/commit/4efd35246c924236f34d8130b1055a3c3ba78605) | 文本内部的 `--` 被误识别为命令行选项 |
| `tqdm-8-custom-bar-format` | bug 8 | [`08b8ad1`](https://github.com/tqdm/tqdm/commit/08b8ad1ff3bd003ef8309faaa0cc108ffa40317d) | [`cae9d13`](https://github.com/tqdm/tqdm/commit/cae9d139c6df5614be3bf6e25ccbd600ee3286dc) | 带 `{bar}` 的自定义格式被忽略 |
| `tqdm-9-si-boundary` | bug 9 | [`9da1d5d`](https://github.com/tqdm/tqdm/commit/9da1d5d116aec7a23d8f6dc22d5e23ecb1c40a7c) | [`d877c1d`](https://github.com/tqdm/tqdm/commit/d877c1dfb4739852105f7b967a8fceb869ac5042) | 接近 SI 单位边界时取整显示错误 |

本批对 BugsInPy 的 tqdm bug 1–9 全部筛选并纳入；没有以环境问题替代行为断言的任务。

## 离线复现

在项目根目录运行：

```powershell
python -m issue_agent.cli check --tasks real_tasks/tasks.json
python -m issue_agent.cli verify --tasks real_tasks/tasks.json --fixes real_tasks/checks/reference_fixes.json
```

`check` 确认每题的公开测试和独立验收在旧版源码上失败。`verify` 在临时副本中应用参考修复，再确认两组测试通过，不会改动题目源码。独立验收和参考修复都在任务仓库之外，Agent 的文件工具读不到它们。我们还在对应上游 fixed commit 上运行了相同的测试，9 题均通过。

上述复现使用 Python 3.12.14；更换解释器版本时请重新运行两条离线验证命令。

这些是**真实历史缺陷的本地可复现子集**，不是完整 BugsInPy 环境或原项目测试套件。它们不包含模型运行结果，不能据此声称 Agent 的通过率。公开项目中的参考修复也不应作为正式盲测材料；以后做模型效果评测时，应在运行前冻结题目，并避免向模型暴露参考修复和验收答案。
