# AI Agent Lab · Issue Fix Agent

一个用于作品集的最小 Coding Agent：输入一个小型仓库 Issue，Agent 在**临时副本**中检索代码、做精确文本修改、运行固定测试，并保存执行轨迹与补丁。原仓库不会被自动修改。

## 当前状态

- 已实现单 Agent 工具循环、文件路径限制、测试命令超时、运行记录、批量任务评测。
- 已限制单次任务最多修改 5 个文件、执行 20 次编辑；评测会输出失败类别和工具错误数。
- 已有离线单元测试和 10 个覆盖不同错误类型的合成 Issue；每个任务另有不放入 Agent 临时仓库的独立验收检查。[任务目录](examples/README.md)列出各任务的验收重点。
- 默认只运行离线演示或检查。真实模型命令必须显式加 `--live`；当前不会调用 API。
- **尚无真实模型成功率数据。**当前只验证了离线工具链；不要在简历中填写未经实测的通过率。
- [项目架构与五部分进度](docs/architecture.md)记录已完成工作和后续验收条件。

## 运行

需要 Python 3.10+。项目只用 Python 标准库，无额外依赖。先运行以下**完全离线**的命令，不读取 API 密钥，也不产生 API 用量：

```powershell
python -m unittest discover -s tests -v
python -m issue_agent.cli demo
python -m issue_agent.cli check --tasks examples/tasks.json
python -m issue_agent.cli verify --tasks examples/tasks.json --fixes examples/checks/reference_fixes.json
python -m issue_agent.cli analyze .runs/某次运行目录 --include-demo
```

以后如果你明确决定使用付费 API，再将 `OPENAI_API_KEY` 放在环境变量或项目根目录的 `.env.local`（此文件已被 Git 忽略），并显式加上 `--live`：

```powershell
python -m issue_agent.cli run `
  --repo examples/calculator_bug `
  --issue-file examples/calculator_bug/issue.md `
  --test-command '["{python}","-m","unittest","discover","-v"]' `
  --model gpt-5.1 --live
python -m issue_agent.cli eval --tasks examples/tasks.json --model gpt-5.1 --live
```

如果当前终端没有 `python` 命令，换成已安装的 Python 可执行文件。`{python}` 在测试命令中自动替换为运行 Agent 的 Python。测试命令必须是 JSON 字符串数组，执行时**不经过 shell**。

`verify` 在任务临时副本中应用参考修复，确认修复前两组测试失败、修复后两组测试通过。参考修复只用于检查合成题是否可解，不代表 Agent 的模型能力，也不会改动原始示例文件。

`demo` 使用预先写好的工具响应模拟 Agent，不连接模型服务，也不能用作模型效果数据。`analyze` 只读取已有报告，不重新运行模型；默认排除演示报告，`--include-demo` 仅供学习报告格式。运行结果会在 `.runs/` 下生成：

- `report.json`：修复前后测试、耗时、token 用量、修改文件。
- `trace.json`：逐步工具调用和结果，便于分析失败。
- `changes.diff`：可审阅的补丁；不会自动应用到原仓库。

## Agent 工具

| 工具 | 用途 |
|---|---|
| `list_files`、`search`、`read_file` | 定位代码与读取上下文 |
| `replace_text`、`create_file` | 修改临时副本中的源文件 |
| `run_tests` | 运行预先指定的测试命令 |

文件工具拒绝越界路径、符号链接、`.env` 文件和测试文件；单文件大小上限为 100 KB。模型不能自选 shell 命令。测试进程只继承必要的环境变量，不继承 `OPENAI_API_KEY`。这是**可信本地仓库的实验工具**；测试仍会执行仓库代码，处理不可信仓库前应加入容器隔离和网络限制。OpenAI 的[工具文档](https://developers.openai.com/api/docs/guides/function-calling)描述了函数调用循环，[Shell 安全说明](https://developers.openai.com/api/docs/guides/tools-shell)建议限制执行范围并保留日志。

## 如何做可写入简历的评测

`examples/tasks.json` 演示任务格式。每条任务包含：

```json
{
  "id": "unique-task-id",
  "repo": "relative/path/to/repo",
  "issue": "Clear behavior change with acceptance criteria",
  "test_command": ["{python}", "-m", "unittest", "discover", "-v"],
  "check_command": ["{python}", "{tasks_dir}/checks/acceptance.py", "unique-task-id"]
}
```

`{tasks_dir}` 会在运行独立验收命令前替换为任务清单所在目录。`check` 会分别验证公开测试和独立验收在修复前失败；批量评测只有两组测试都通过才算成功。验收脚本不复制进 Agent 的临时仓库，但它仍存在于公开项目中，不能视为对具有仓库外访问能力的模型保密。

正式评测建议准备至少 30 个来自固定版本仓库的**不同**小 Issue，并为每个任务保留独立验收测试。程序会先运行修复前测试；只有修复前失败、修复后通过的任务才算成功。再固定模型、提示词、任务集和最大步数批量运行。报告任务通过率、各类失败数量、工具错误数、总 token、平均耗时，并逐条分析失败原因。当前合成任务只用于接通流程，不足以支持简历中的效果结论。

## 项目结构

```text
issue_agent/agent.py       Responses API 调用、工具协议、轨迹记录
issue_agent/workspace.py   临时副本、文件工具、测试运行
issue_agent/cli.py         单任务和批量评测命令
examples/                  可运行的示例 Issue
tests/                     离线单元测试
```

## 简历描述模板

> 独立实现面向小型 Python 仓库的 Issue 修复 Agent，设计代码检索、精确编辑与测试反馈工具，在临时副本中完成修复并记录执行轨迹；构建 **N** 条任务的评测集，任务通过率 **X%**，平均耗时 **Y** 秒，并通过失败归因优化 **具体策略**。

只填写实际测得的数字和确实做过的优化。
