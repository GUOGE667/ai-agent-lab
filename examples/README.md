# 离线任务集

`tasks.json` 收录 10 个相互独立的小型 Python Issue。每个目录都有待修复的源码和固定的 `unittest` 验收测试；测试文件在 Agent 运行时受到写入保护。

| ID | 问题类型 | 验收重点 |
|---|---|---|
| `calculator-add` | 算术错误 | 正数、负数相加 |
| `slugify-normalization` | 文本规范化 | 小写、连续空格 |
| `config-value-equals` | 分隔符解析 | 值中保留额外等号 |
| `pagination-one-based` | 边界与索引 | 首页、中间页、末页 |
| `retry-attempt-budget` | 控制流 | 成功返回、次数上限、错误传播 |
| `dedupe-stable-order` | 集合与顺序 | 按首次出现顺序去重 |
| `median-even-length` | 奇偶分支 | 偶数长度取中间两数均值 |
| `query-encoding` | 编码 | 键和值的表单 URL 编码 |
| `inventory-unknown-sku` | 输入校验 | 拒绝未知商品、负数及超量请求 |
| `filename-final-extension` | 字符串边界 | 多个点、隐藏文件、末尾点 |

运行 `python -m issue_agent.cli check --tasks examples/tasks.json` 可验证每个任务的修复前基线都会失败。当前 10 个任务全是**合成练习题**，用于开发和回归检查；它们不能代表真实仓库上的模型修复能力，也没有在线模型通过率。

正式评测需要另建固定版本的公开仓库任务集，记录仓库 commit、Issue 来源、独立验收测试和任务筛选过程。不要把此目录的合成任务计入简历中的真实效果指标。
