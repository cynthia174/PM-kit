# PM-kit

把产品工作中反复修改、验收形成的方法，整理为可以独立使用的 Agent Skills。

目前包含 **4 个独立 Skill**，分别用于竞品分析、用户评论收集、产品定义和文风调整。它们可以分别使用，也可以组合起来写一篇完整的产品文档：先做竞品分析和用户评论收集，再完成产品定义，最后用文风 Skill 统一整理表达。每个 Skill 都有独立入口、验收标准与正反例。

## Skill 目录

| Skill | 解决什么问题 | 典型请求 |
| --- | --- | --- |
| [competitor-research](skills/competitor-research/SKILL.md) | **竞品分析**：整理竞品总览、实际用法、交互比较、素材与结论 | “比较这几款产品，重点讲功能和操作差异。” |
| [user-review-analysis](skills/user-review-analysis/SKILL.md) | **用户评论收集**：筛选、拆分、概括、分类、去重评论，生成表格与洞察 | “整理这些用户评论，按产品分表，原文和出处保留。” |
| [product-definition](skills/product-definition/SKILL.md) | **产品定义**：梳理用户、场景、需求到功能的映射，以及形态和范围取舍 | “根据这些反馈做产品定义，先比较方案。” |
| [product-writing-style](skills/product-writing-style/SKILL.md) | **文风调整**：把产品工作文字改得平实、具体、简洁，适合写产品文档 | “这段太像AI写的，缩短，但不要丢掉条件和结论。” |

这四个 Skill 都可以用于写产品文档。可以只处理已有材料，也可以在用户要求下补充研究；可以单独使用，也可以按“竞品分析 → 用户评论收集 → 产品定义 → 文风调整”的顺序组合使用。业务 Skill 包含必要表达约束，文风 Skill 用于统一整篇文档的表达。验收是各业务流程的一部分，不必另开一个只会打分的“大验收 Skill”。

## 安装与使用

### Claude Code：按 Skill 安装

仓库提供与 Anthropic Skills 仓库同类的 marketplace 目录结构。在 Claude Code 中运行：

```text
/plugin marketplace add cynthia174/PM-kit
/plugin install competitor-research@pm-kit
/plugin install user-review-analysis@pm-kit
/plugin install product-definition@pm-kit
/plugin install product-writing-style@pm-kit
```

只执行需要的安装行。安装后用自然语言提出对应任务；插件命令名以客户端显示为准。定义文件见 [.claude-plugin/marketplace.json](.claude-plugin/marketplace.json)。

### Claude：上传单个 Skill

下载仓库后运行：

```text
python scripts/build_skills.py
```

`dist/` 会生成四个独立 ZIP。每个 ZIP 的根目录是对应 Skill 文件夹，包含 `SKILL.md` 和其资源；将需要的 ZIP 上传到 Claude 的 Skills 设置。不要把整个仓库当成一个 Skill 上传。

### 其他支持 Agent Skills 的客户端

将需要的 `skills/<skill-name>/` 整个文件夹复制到客户端支持的 Skill 目录，保留内部相对路径。例如，使用 `~/.codex/skills` 的 Codex 环境可以复制到该目录。不同客户端的发现目录和刷新方式以自身设置为准；仓库不自动修改本机配置。

## 文件如何分工

```text
PM-kit/
├── .claude-plugin/marketplace.json
├── skills/
│   └── <skill-name>/
│       ├── SKILL.md                 触发、流程、关键约束与按需阅读入口
│       ├── references/             详细验收标准、few-shot、专题规则
│       ├── assets/                 业务输出模板（有需要的 Skill 才提供）
│       └── agents/openai.yaml      可选的 Codex 展示元数据
├── evals/                          触发样例、合成输入及行为检查点
├── scripts/                        结构校验与独立 ZIP 打包
└── docs/                           维护说明与验证记录
```

每个 Skill 自包含，不依赖另一个 Skill 被自动安装或加载。`SKILL.md` 直接链接所需参考文件，避免多层跳转和整库预读。

## 开发与验证

需要 Python 3.10+，仓库脚本只使用标准库：

```text
python scripts/validate_repo.py
python -m unittest discover -s tests -v
python scripts/build_skills.py
```

结构校验检查发现入口、规则编号、内部链接、marketplace 路径、测试样例及发布边界。行为测试需另按 [评测方法](evals/README.md) 使用真实 Agent 执行；结构通过不等于输出质量已经得到验证。具体完成范围见 [验证记录](docs/validation.md)。

## 资料与维护边界

方法来自真实产品工作中的反复纠错。公开示例已泛化或合成，并标记为教学样例，不是当前产品事实、真实买家评价或市场结论。原始聊天、内部文档、个人档案和访问凭证不属于发布内容。

改进时先保留失败样例，再调整对应模块，并复测同类案例。不要因一次问题就把所有任务变成同一格式；用户本轮明确要求优先于默认约定。详见 [维护与设计](docs/design.md)。

结构参考 [Agent Skills 规范](https://agentskills.io/specification)、[Anthropic Skills 仓库](https://github.com/anthropics/skills)与 [Claude Skill 编写指南](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)。PM-kit 是独立维护的项目。
