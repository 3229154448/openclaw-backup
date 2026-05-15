# Self-Improve Engine

> Defines trigger rules, execution flow, layer creation rules

## Trigger Mechanism

### Scheduled Trigger (Every 3 Days)

```
Cron: 0 4 */3 * * (Every 3 days at 4 AM)
Model: bailian/qwen3.5-plus
Agent: {main_agent}
Timezone: Asia/Shanghai
```

**Cron message:**

See `prompts/cron-trigger.md` (complete execution instructions).

During installation, setup.mjs writes this prompt to the Cron configuration's message field.

**Execution Flow:**

```
0. Backup              → Copy critical files to data/backup/ (pure file operation, no git dependency)
1. Scan corpus         → feedback-collector extracts signals from memory logs + previous round reflections.md
2. Evaluate            → Calculate positive/negative ratio, identify repetition patterns
2.5 Distill and classify → distill-classifier performs three-level distillation + classification settlement + value_density annotation
3. Memory elevation    → memory-layer manages hot.md (≥3 times elevation)
4. Determine output    → proposer considers holistically, produces rule solidification/blog/methodology/skill improvement
5. High-value revisit  → Deep read of original corpus, deep output (optional)
6. Wrap-up             → Reflection + profile + notification + checkpoint
```

---

## Approval Rules

**用户已授权：所有修改直接执行，无需确认。**

但每次修改必须记录到 `data/changelog.md`。

### 变更日志格式 (`data/changelog.md`)

```markdown
## [日期时间]
- **文件**: 修改的文件路径
- **操作**: 新增/修改/删除
- **内容**: 修改了什么
- **原因**: 为什么修改（来自哪个反馈/错误/纠正）
- **来源**: 会话ID或触发来源
```

### 所有文件均可直接修改

- `/path/to/self-improve/data/*` - Data for improving the system itself
- `/path/to/learned/*` - Automatically distilled knowledge (written by knowledge-archiver)

---

## Layer Creation Rules

**Agents can automatically create new directories/files without asking in advance.**

### themes/ Directory (Extensible)

Existing themes:
- `behavior/` - Behavior norms
- `communication/` - Communication preferences
- `tools/` - Tool usage
- `coding/` - Coding standards
- `search/` - Search strategies
- `writing/` - Writing style
- `collaboration/` - Team collaboration
- `preferences/` - Personal preferences
- `professional/` - Professional capabilities
- `personality/` - Personality traits

**Automatically create when discovering new themes:**
```
classifier determines → doesn't belong to existing themes → create themes/{new-theme}/
```

### projects/ Directory (Extensible)

```
Discover new project experience → create projects/{project-name}/
```

### Knowledge Base Directory (Written by knowledge-archiver)

```
Errors/pitfalls → /path/to/learned/errors/{theme}.md
Experience summaries → /path/to/learned/lessons/{theme}.md
Methodologies → /path/to/learned/methodologies/{theme}.md
```

---

## Classification Mapping

| Theme | Solidification Target File |
|-------|---------------------------|
| behavior | AGENTS.md |
| communication | AGENTS.md / SOUL.md |
| tools | TOOLS.md |
| coding | AGENTS.md / TOOLS.md |
| search | AGENTS.md / TOOLS.md |
| writing | AGENTS.md / SOUL.md |
| collaboration | AGENTS.md / MEMORY.md |
| preferences | MEMORY.md / SOUL.md |
| professional | AGENTS.md / TOOLS.md |
| personality | SOUL.md |
| errors | /path/to/learned/errors/ |
| skills | /path/to/self-improve/data/skills/ |

---

## Execution Principles

1. **Fully automatic processing** — From collection to distillation, no human intervention required
2. **直接修改系统文件** — 用户已授权，无需等待确认，但必须记录变更日志
3. **Self-determined format** — The language model decides how to organize language and which section to add to
4. **Can create new** — When discovering new themes/projects, create directories directly
5. **Index auto-updates** — Update relevant index files after writing
6. **Fault-tolerant continuation** — When a step fails, log the error and continue with subsequent steps, final status marked as "partial"
7. **变更日志必写** — 每次修改系统文件后，必须追加记录到 `data/changelog.md`
8. **🚫 重启需批准** — 任何 Gateway/服务重启操作必须通知用户并获得明确同意，不能自行执行

---

## Module Dependencies

```
feedback-collector (no dependencies)
      ↓
evaluator (depends on feedback-collector)
      ↓
classifier (no dependencies)
      ↓
memory-layer (no dependencies)
      ↓
knowledge-archiver (depends on memory-layer)
methodology-extractor (depends on memory-layer)
skill-improver (depends on evaluator)
      ↓
proposer (depends on memory-layer)
profiler (depends on evaluator)
reflector (no dependencies)
```

**Execution order:** Execute in dependency order to ensure upstream modules complete first.

---

## Target Detection

**All agents share this system.**

When self-improve runs:
1. Scan `/path/to/self-improve/` (system-level, shared by all agents)
2. Read each agent's session logs (if accessible)
3. Write results to shared location, readable by all agents

---

## Intermediate File Locations

| Module | Input | Output |
|--------|-------|--------|
| feedback-collector | Conversation logs | `data/feedback/*.jsonl`<br>`data/corrections.md` |
| evaluator | `data/feedback/` | `data/feedback/*.jsonl` (append evaluation results) |
| classifier | `data/corrections.md` | `data/themes/{theme}/*.md` (with frontmatter tags) |
| memory-layer | `data/themes/` | `data/hot.md`<br>`data/themes/`<br>`data/archive/` |
| knowledge-archiver | `data/corrections.md`<br>`data/reflections.md` | `/path/to/learned/errors/*.md`<br>`/path/to/learned/lessons/*.md` |
| methodology-extractor | `data/reflections.md`<br>`data/feedback/` | `/path/to/learned/methodologies/*.md` |
| skill-improver | feedback/ | themes/skill-improvements/ (settle first, solidify later) |
| proposer | `data/hot.md`<br>`data/corrections.md` | `proposals/PENDING.md` |
| profiler | `data/feedback/` | `data/profile.md` |
| reflector | `data/feedback/` | `data/reflections.md` |

---

## Write Specification Compliance

**This system complies with the following specifications:**

| Location | Specification |
|----------|--------------|
| `/path/to/self-improve/` | Follows shared-manager skill write specification |
| `/path/to/learned/` | Follows knowledge-manager skill write specification |

**Specific requirements:**
- Update index after writing (`data_structure.md`)
- New directories must have `data_structure.md`
- Follow directory classification rules

---

## Module Switches

### Check Switch Status
```bash
node scripts/status.mjs
```

### One-click Enable/Disable Modules

**Method A: Modify config.yaml**
```yaml
modules:
  classifier:
    enabled: false  # Change to false to disable
```

**Method B: Use command (needs implementation)**
```bash
node scripts/module.mjs enable classifier
node scripts/module.mjs disable classifier
```

---

## Adding New Modules Flow

```
1. Create directory under modules/: modules/new-module/
2. Write MODULE.md (follow standard format)
3. Register in config.yaml under modules
4. If new data directory needed, create under data/
5. Update changelog.md
```

**Standard MODULE.md format:**
```markdown
# Module Name

> Version: x.y.z
> Status: active | disabled

## Responsibility
One-line description

## Input
Where to read data from

## Output
Where to write to

## Interface
How to call

## Dependencies
Which modules it depends on
```

---

## Deleting Modules Flow

```
1. Set enabled: false in config.yaml
2. Confirm module is not depended on by other modules
3. Delete modules/module-name/ directory
4. Remove registration from config.yaml
5. If data deletion needed, confirm then delete relevant directories under data/
6. Update changelog.md
```

**Note:** Data files are not automatically deleted, require manual confirmation.

---

## Prompt System

All module execution instructions are centrally managed in the `prompts/` directory:

| Prompt File | Purpose | When Used |
|------------|---------|-----------|
| `cron-trigger.md` | Execution entry when Cron triggers | Every 3 days scheduled trigger |
| `feedback-collector.md` | Scan conversations, extract signals | Step 1 |
| `distill-classifier.md` | Distill three-level rules + classify + value density | Step 2 |
| `memory-layer.md` | Layered memory management (elevation/demotion) | Step 3 |
| `proposer.md` | Determine output channel, generate solidification proposals | Step 4 |
| `reflector.md` | Self-reflection | Step 5 |
| `profiler.md` | Team capability profile (every 3 times) | Step 6 |
| `notify.md` | Notify user | Step 7 |
| `execution.md` | Execute write after approval | Independent trigger |

**Reference documentation (merged into main prompt files, not included in release package):**
- Value judgment five questions, three-level distillation → `distill-classifier.md`
- Classification tag system → `distill-classifier.md`
- Routing decision tree → `proposer.md`
- Detailed solidification execution steps → `execution.md`
- Methodology extraction → `distill-classifier.md`

**Prompt quality is the core of the system.** Please test thoroughly before modifying prompts.
