# 高考阅读 B 篇语篇寻源 / Gaokao B-Passage Finder

[![validate](https://github.com/gaofred/gaokao-b-passage-finder/actions/workflows/validate.yml/badge.svg)](https://github.com/gaofred/gaokao-b-passage-finder/actions/workflows/validate.yml)
[![license: CC BY-NC-SA 4.0](https://img.shields.io/badge/license-CC%20BY--NC--SA%204.0-lightgrey.svg)](LICENSE)
[![python](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/)

为高考英语阅读理解 **B 篇**找英文原话语篇，而且只找**能改、能命题**的那一类。

不是"搜几篇英文文章"，而是**两把尺子依次筛**：先判体裁谱系（这篇是不是 B 篇要的东西），再过结构预检（这篇能不能改）。谱系合格不等于结构合格——空弧、引语悬空、升华没种子的素材，在选材端换掉只需一分钟，流到改编端就是重写。

## 两把尺子

### 第一把：选材雷达（体裁谱系）

| 判定 | 对象 | 处置 |
|---|---|---|
| **靶心** | A1/A2 第一人称叙事——教育／家庭／成长，教师或家长视角最佳 | 过第二把尺后最高优先 |
| **次选** | B 型人物特写 / C 型项目报道，须有具体人物、地点、数字 | 过第二把尺后可推，但原文**必须含 ≥2 处可保留的直接引语** |
| **淘汰** | D 谱系知识传递型：无人物主线的知识罗列、纯书评、纯实验报告、纯科普 | **一票否决**，不进第二把尺 |

依据：2024 年后 B 篇位 D 谱系零出现，该篇位已完成"知识测试 → 叙事理解与人物认知"的转型。

### 第二把：结构预检（五查）

谱系通过后、打分之前，逐条过：

| # | 查什么 | 不合格的代价 |
|---|---|---|
| 查一 | 三段完整（冲击→反应→升华） | 无升华 = 主旨题无依据 |
| 查二 | 空弧检测（转变有没有中间过程） | 空弧 = 段落衔接硬伤 |
| 查三 | 引语生态（有情境、身份可写、意图可读） | 引语悬空 = 归因题无落点 |
| 查四 | 升华支撑（末段概念前文有无种子） | 概念凭空出现 = 改不出来 |
| 查五 | 时间线闭合（跳跃有交代、时态基点可判） | 大跨度素材 = 截取窗口难选 |

五查全过 → 直推；单条轻度风险且原文有修复原料 → 可推但必须写"结构风险与改编预案"；两条以上不合格或单条重度 → **换篇，不得带伤推荐**。

## 工作流

```text
阶段一  搜索 → 初筛 → 推荐清单
        ≥4 轮并行搜索，按体裁谱系分路
        先过雷达三分，再过预检五查，按六维打分，总分 ≥3.8 入选
        🛑 交付清单后暂停，等用户选定篇目

阶段二  全文抓取 → Word 生成
        只抓用户点名的篇目，保留段落结构与全部直接引语
        scripts/create_docx.py 批量出 Word
```

阶段二不得在用户选定前启动——用户可能只要清单、不要 Word，也可能改选或排除某篇。

## 参数

| 参数 | 说明 | 默认 |
|---|---|---|
| `topic` | 题材倾向（成长／教育／家庭第一人称叙事、人物特写、项目报道，可多选） | 必填 |
| `count` | 文章数量 | 5 |
| `length_window` | 原文词数窗口 | 280–1000 |
| `exclude_topics` | 排除已搜过的主题 | 无 |
| `output_dir` | Word 输出目录 | `~/Desktop/<topic>_B篇语篇/` |
| `genre_target` | 体裁谱系目标（A1/A2/B/C） | 不限，靶心优先 |
| `structure_precheck` | 结构预检开关 | on（关闭须明示） |

## 产出

1. **推荐清单** `{topic}B篇语篇推荐_YYYYMMDD.md`——每篇六字段齐全：体裁谱系预判／直接引语数／结构预检结论／故事弧要素／可命题切入点／改编要点。
2. **Word 全文**（用户选定后）——Georgia 11pt 正文，深蓝 16pt 标题。

## 安装

```bash
git clone https://github.com/gaofred/gaokao-b-passage-finder.git \
  ~/.workbuddy/skills/gaokao-b-passage-finder
```

## 依赖

- Python 3.9+
- `python-docx`：`pip install python-docx`
- 联网搜索能力（由运行环境提供）

## 目录结构

```
SKILL.md                        主流程：两把尺子、两阶段、失败回退、反例黑名单
references/
  b-passage-guide.md            搜索关键词模板与来源池
  structure-precheck.md         结构预检五查的判据细则
scripts/
  create_docx.py                JSON → Word（单篇或批量）
test-prompts.json               测试用例
```

## 红线

- 不推荐 D 谱系（无人物主线的知识罗列），语篇质量再高也一票否决
- 不推荐广播梗概／口语转录（那是读后续写素材）
- 引语不足 2 处不硬塞，不隐瞒硬前提
- 候选不够就少推，不把低于 3.8 分的篇目包装成达标
- 全文抓取失败不凭摘要编正文
- 不把"结构完整"四个字当预检结论——三段落点要具体指认到段落

## 与下游衔接

选材（本 skill）→ 改编 `gaokao-b-passage-adapt` → 命题 `gaokao-b-reading-generator` → 评析 `gaokao-b-reading-analyzer`

## 作者

Fred 老师 · 公众号：佛瑞德英语教学

## License

[CC BY-NC-SA 4.0](LICENSE)，禁止商业使用。课堂、校内、教研、非营利分享均可，需署名。详见 [NOTICE](NOTICE)。
