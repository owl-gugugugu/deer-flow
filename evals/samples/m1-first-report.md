# 字节跳动 2027 届校招 Flow 团队「创意 Agent 技术研发」岗位分析报告

> 业务方向 · 岗位画像 · 技术栈 · 面试考察点 · 准备建议
> 调研日期：2026 年 9 月（基于公开网络信息整理）

---

## 0. 执行摘要

1. **Flow 是字节跳动的 AI 创新业务部门**，旗下汇聚豆包（国内第一 AI 原生应用，DAU 已破亿）、扣子/Coze（智能体开发平台，已开源）、猫箱（AI 陪伴）、星绘（AI 图像）、TRAE（AI 编程 IDE）、即梦（AIGC 创作社区）等产品线 [citation:36氪-豆包成字节最凶猛的进化](https://www.36kr.com/p/3452409797934466)。
2. **2026 年 8 月 6 日年中全员会**上，CEO 梁汝波介绍了豆包、飞书、火山引擎的整合背景：TRAE 与扣子并入豆包，整合后豆包成为字节 AI 办公/生产力业务的主干，并推出统一办公品牌「豆包工作」[citation:华尔街见闻-TRAE扣子并入豆包](https://awtmt.com/articles/3780150) [citation:腾讯新闻-整合TRAE与扣子](https://news.qq.com/rain/a/20260824A0BYTE00)。
3. **「创意 Agent 技术研发」的官方 JD 原文在公开网络上无法直接获取**（官网职位页存在抓取限制）。本报告基于 Flow 同类岗位（AI Agent 研发工程师、大模型应用开发、AIGC 创意方向）的 JD 与面经进行画像推断，并明确标注推断成分。
4. 该岗位技术栈主线：**LLM 原理 → Prompt → RAG → Function Calling → MCP → Agent（ReAct / Plan-and-Execute / 多智能体）→ 评测与可观测性**；字节系自研体系包括 **豆包 Doubao-Seed 1.6 系列模型、Eino（Go 版大模型应用框架）、DeerFlow、Coze Studio / Coze Loop、AgentKit、UI-Tars** [citation:InfoQ-Eino](https://www.infoq.cn/article/eino-golang-llm-application-framework) [citation:火山引擎-Doubao-Seed-1.6](https://www.volcengine.com/docs/82379/1666946)。
5. 面试流程：**提前批可免笔试；正式批为 1 轮笔试 + 3 轮技术面 + 1 轮 HR 面**。考察重心 = 计算机基础深挖 + 手撕算法（LeetCode medium-hard）+ 项目深挖 + LLM/Agent 专项八股 [citation:字节跳动校园招聘官网](https://jobs.bytedance.com/campus)。
6. 2027 届秋招提前批大幅提前、AI 岗位供给向头部集中：百度 27 届校招 AI 岗占比超 90%，字节技术+产品岗占比超 70%，Agent 方向是各家必争之地 [citation:劳动报-2027届秋招提前批](https://www.51ldb.com/shsldb/zc/content/019fcba0c1ffc001000066d533acd97d.html)。

---

## 1. Flow 团队业务方向与产品线

### 1.1 组织定位

- Flow 是字节跳动的 **AI 创新业务部门**，承载公司「AI 应用层」的To C 与部分 To B 产品，由产品与战略副总裁 **朱骏** 分管产品线 [citation:36氪-豆包成字节最凶猛的进化](https://www.36kr.com/p/3452409797934466)。
- 2026 年年中全员会（8 月 6 日）上，CEO 梁汝波表示 **「AI 在生产力上的发展快于预期，To B 变得更重要」**，随后启动豆包、飞书、火山引擎的整合：TRAE、扣子团队并入豆包，豆包成为字节 AI 办公业务主干 [citation:新浪-字节推统一办公品牌豆包工作](https://k.sina.com.cn/article_6105713761_16bedcc61019028zjm.html?from=news&subch=onews) [citation:凤凰网-豆包工作发布](https://finance.ifeng.com/c/8vsWeZ3k0iB)。
- 对校招生的含义：Flow 是字节内部 **资源倾斜最重、迭代速度最快** 的业务线之一；同时组织调整频繁（产品线合并、方向收缩），入职后跟随业务大方向调整的概率高，需有心理预期。

### 1.2 核心产品矩阵

| 产品 | 定位 | 关键事实 |
|---|---|---|
| **豆包 / Cici** | AI 助手（国内/海外） | DAU 已破 1 亿，被称为「字节史上推广费最少的破亿产品」；火山引擎是 2026 央视春晚独家 AI 云合作伙伴 [citation:36氪-豆包成字节最凶猛的进化](https://www.36kr.com/p/3452409797934466) |
| **扣子 Coze** | AI Bot / 智能体开发平台 | 已开源：**Coze Studio**（拖拽式工作流、知识库、插件、多模型适配）+ **Coze Loop**（日志追踪、Prompt 评测、质量监控）[citation:Coze开源官网](https://www.coze.cn/open) |
| **TRAE** | AI 原生编程 IDE | 「The Real AI Engineer」，IDE + SOLO 双模式，兼容 VS Code 插件生态；已并入豆包品牌下作为编程产品线发展 [citation:CodePick-Trae vs Cursor](https://codepick.dev/zh/compare/trae-vs-cursor/) |
| **猫箱** | AI 虚拟角色聊天/陪伴 | MAU 峰值 600 万+ 后回落至约 391 万（2026 年 6 月），AI 陪伴赛道整体收缩 [citation:QuestMobile 2026 AI应用报告](https://www.woshipm.com/it/1888530.html) |
| **星绘** | AI 图像生成 | 与猫箱同属创意方向，百万 DAU 量级 [citation:36氪-豆包成字节最凶猛的进化](https://www.36kr.com/p/3452409797934466) |
| **即梦 / Seedream / Seedance** | AIGC 创作与多模态生成 | Seedance 视频模型已迭代至 2.x，落地「豆包课堂」等教育场景 [citation:新浪-豆包课堂](https://k.sina.com.cn/article_3203211782_beed22060200217l0.html) |
| **豆包工作** | AI 办公品牌 | 整合 TRAE Work、扣子的办公场景能力，对标飞书+AI [citation:华尔街见闻-TRAE扣子并入豆包](https://awtmt.com/articles/3780150) |

### 1.3 战略动向与「创意 Agent」的位置

- **从「AI 聊天陪伴」转向「AI 生产力」**：行业集体收缩 AI 恋爱/聊天搭子类产品（米哈游《BSide: Olivia Lin》上线未足月即停服等），字节把重心压向 AI 办公与创作生产力 [citation:南都-AI陪伴产品停服潮](https://m.mp.oeeee.com/a/BAAFRD0000202608111641999.html)。
- **创意 = AIGC 生成能力（文/图/视频/音乐）+ Agent 编排能力** 的结合部：豆包对话中的创作助手、即梦的创作工作流、Coze 上的创意类智能体模板，都属于「创意 Agent」的业务射程。可以判断：该岗位大概率服务于 **豆包/即梦/Coze 中「生成式创作链路的 Agent 化」**——用 LLM 编排多模态生成模型（Seedream/Seedance），把模糊的用户意图变成可控的多步创作流程。
- **智能体中台化**：扣子开源 + Eino/DeerFlow 开源，说明字节在把 Agent 基建沉淀为可复用平台，校招生进入后有较大概率参与 **平台型/中台型** 的 Agent 研发而非纯前端套壳。

---

## 2. 岗位画像：「创意 Agent 技术研发」

> ⚠️ 说明：该岗位官方 JD 原文未能从公开渠道获取（jobs.bytedance.com 职位页存在访问限制）。以下画像基于字节/头部大厂 2026-2027 届 **AI Agent 研发、大模型应用开发、AIGC 创意方向** 同类岗位 JD 与面经综合推断，投递前请以官网 JD 原文为准。

### 2.1 职责（推断）

1. 负责创意场景下 Agent 的设计、研发与迭代：创意理解 → 方案规划 → 多步生成（文案/图像/视频）→ 自我评估与重试闭环；
2. 研发基于 LLM 的编排框架：工作流引擎、工具调用、多智能体协作、长上下文与记忆管理；
3. Prompt 工程与评测：构建创意质量评测集（人类偏好对齐）、A/B 实验、badcase 归因；
4. RAG 与知识接入：创意素材库、风格库、模板库的检索增强；
5. 多模态模型应用：与 Seedream（图像）、Seedance（视频）、语音/音乐模型的对接与调度；
6. 工程落地：高并发服务、延迟优化、成本控制、安全合规（创意内容审核链路）。

### 2.2 任职要求（推断，综合公开 JD）

- **基础**：本科及以上学历，计算机/软件/AI 相关专业；2027 届可实习 3 个月以上、能转正者优（字节 2027 届 Bytelntern 转正实习超 7000 个 Offer，史上最大规模）[citation:ViewImp-字节2027届转正实习启动](https://www.viewimp.com/a/3520.html)；
- **编程**：Python 为主力（Go 加分——Eino 生态为 Go 系），数据结构与算法扎实，熟悉至少一个 Web/服务框架与 MySQL/Redis；
- **LLM**：理解 Transformer 原理、预训练/SFT/RLHF 基本流程；有 Prompt 工程、RAG、Function Calling 实战项目；
- **Agent**：了解主流 Agent 范式（ReAct、Plan-and-Execute、Reflection），用过 LangChain / LlamaIndex / Eino / Coze 任一框架，理解 MCP 协议者加分明显；
- **加分**：AIGC 相关项目或竞赛（图像/视频生成、虚拟角色）、LLM 开源社区贡献（尤其 Eino/Coze/DeerFlow）、学术论文（NLP/CV/多模态顶会）、ACM/天池等算法竞赛成绩、重度使用 Claude Code / Cursor / TRAE 等 AI 编程工具（DeepSeek Agent 岗 JD 已明确此类偏好，字节同理）[citation:凤凰网-DeepSeek急招Agent岗](https://finance.ifeng.com/c/8vYHVl62V12)。

---

## 3. 核心技术栈全景

### 3.1 通用 LLM 应用主线（必须掌握）

```
LLM 基本原理 → Prompt 工程 → RAG → Function Calling → MCP → Agent → 多智能体 → 评测/可观测性
```

这条主线是当前 AI 应用岗公认的「八股骨架」，多个面经与求职指南均建议按此顺序补齐 [citation:阿里云开发者-校招AI岗技能清单](https://developer.aliyun.com/article/1764265)。

| 模块 | 必会知识点 | 高频面试追问 |
|---|---|---|
| LLM 原理 | Transformer、注意力机制、位置编码、KV Cache、解码策略（temperature/top_p） | 为什么需要 KV Cache；长上下文如何优化 |
| Prompt | Zero/Few-shot、CoT、角色设定、结构化输出、Prompt 注入防护 | 如何系统性迭代 Prompt 而非凭感觉 |
| RAG | 切块策略、embedding 选型、向量库（Milvus/Chroma）、混合检索、重排、引用溯源 | RAG 效果差如何排查；多路召回与重排 |
| Function Calling | schema 定义、并行调用、错误重试 | Function Calling 与 MCP、Skills 的区别（字节/淘天/B站真题）[citation:InfoQ-大厂Agent面试真题](https://www.infoq.cn/article/great-agent-interview-2025) |
| MCP | 工具发现机制、资源/提示/工具三类原语、生命周期 | MCP 工具发现 + A2A 任务管理、Agent 死循环检测（真题）|
| Agent | ReAct、Plan-and-Execute、Reflection、记忆（短期/长期）、多智能体（agent/task/flow/state）| ReAct vs Plan-and-Execute 适用场景（真题）；幻觉抑制 |
| 评测 | 评测集构建、LLM-as-a-Judge、在线指标（留存/完成率）、Coze Loop 类可观测 | 创意质量这种主观目标怎么评测 |

### 3.2 字节系自研技术栈（强烈建议了解，面试是天然加分项）

- **豆包大模型 Doubao-Seed 1.6 系列**：含 thinking（on/off/auto 三种思考模式、原生多模态）与 flash（极速）版本，均支持 256K 上下文，价格下调 63% [citation:火山引擎-Doubao-Seed-1.6发布](https://www.volcengine.com/docs/82379/1666946) [citation:36氪-豆包大模型降价](https://www.36kr.com/p/2833276823349376)。
- **Eino**：字节开源的 **Golang** 大模型应用开发框架（CloudWeGo 旗下），「组件化 + 编排 + Agent」三件套，11K+ Stars，被称为 Go 版 LangChain；其 ChatModelAgent 已进化到 DeepAgent 形态 [citation:InfoQ-Eino框架解读](https://www.infoq.cn/article/eino-golang-llm-application-framework) [citation:CloudWeGo-Eino](https://www.cloudwego.io/zh/docs/eino/)。
- **DeerFlow**：字节开源的 long-horizon AI Agent 编排框架，支持子智能体、长期记忆、沙箱执行 [citation:DeerFlow官网](https://deer-flow.dev) [citation:GitHub-bytedance/deer-flow](https://github.com/bytedance/deer-flow)。
- **Coze Studio / Coze Loop**：智能体搭建平台（拖拽工作流、知识库、插件）与运维平台（日志追踪、Prompt 评测）[citation:Coze开源官网](https://www.coze.cn/open)。
- **AgentKit + UI-Tars**：火山引擎 Agent 开发套件，集成豆包模型与开源 UI-Tars 视觉操作模型，支持 Agent 逻辑生成与工具调用 [citation:火山引擎-AgentKit发布](https://www.volcengine.com/docs/82379/1666950)。
- **多模态生成**：Seedream（图像）、Seedance 2.x（视频，已落地「豆包课堂」）[citation:新浪-豆包课堂](https://k.sina.com.cn/article_3203211782_beed22060200217l0.html)。

### 3.3 计算机基础（技术面地基，不可跳过）

语言（Python/Go/Java）与并发模型、MySQL（索引/事务/锁）、Redis（缓存/持久化/分布式锁）、计算机网络（HTTP/TCP）、操作系统（进程线程/内存管理）、消息队列与分布式基础。字节面试以「基础深挖」著称，Agent 岗也不例外。

---

## 4. 面试流程、考察点与面经

### 4.1 流程与节奏

- **提前批**：可免笔试，简历优秀者可加急；**正式批**：1 轮笔试 + 3 轮技术面 + 1 轮 HR 面 [citation:字节跳动校园招聘官网](https://jobs.bytedance.com/campus)。
- 2027 届秋招提前批密集提前启动，各家大厂集中争夺 AI 人才；字节同期也在加速发放 Offer，**投递宜早不宜迟** [citation:劳动报-2027届秋招提前批密集启动](https://www.51ldb.com/shsldb/zc/content/019fcba0c1ffc001000066d533acd97d.html)。
- 字节另有 AI 产品经理早鸟通道（北上深闭门面试，最快两天直通 Offer、不占正式校招名额），说明字节 27 届整体节奏明显前移 [citation:WonderCV-字节AI产品经理早鸟通道](https://www.wondercv.com/blog/q434RmDq.html)。

### 4.2 三轮技术面的典型结构

1. **一面（基础 + 算法）**：语言特性、并发、MySQL/Redis/网络八股深挖 + 1~2 道手撕算法。校招手撕常见：BFS 单源最短路、LRU 缓存、合并 K 个升序链表（LeetCode 23 变种）、TopK [citation:InfoQ-大厂Agent面试真题](https://www.infoq.cn/article/great-agent-interview-2025)。
2. **二面（项目 + 领域深度）**：项目深挖（每个技术选型都要能答出「为什么不是 B 方案」）；Agent 专项：Function Calling / MCP / Skills 区别、ReAct vs Plan-and-Execute、多智能体架构（agent/task/flow/state）、死循环检测、幻觉缓解、RAG 优化 [citation:InfoQ-大厂Agent面试真题](https://www.infoq.cn/article/great-agent-interview-2025)。
3. **三面（系统设计 + 潜力）**：场景设计题常见形态——「设计一个创作类 Agent」「设计高并发 AI 服务并控制成本」「设计 Agent 评测体系」；以及技术视野、学习能力、协作与抗压。
4. **HR 面**：实习时长与转正意向、对 Flow 业务的了解与兴趣、职业规划、稳定性。

### 4.3 面经摘编（Agent 方向真题）

- Function Calling、MCP、Skills 三者的区别与联系？（字节/淘天/B站均问）[citation:InfoQ-大厂Agent面试真题](https://www.infoq.cn/article/great-agent-interview-2025)
- ReAct 与 Plan-and-Execute 两种范式分别适用什么场景？
- 多智能体系统里 agent、task、flow、state 各是什么？如何做任务生命周期管理与死循环检测？
- 介绍 DeepSeek Harness 等新 Agent 技术（考察对前沿的敏感度）[citation:InfoQ-大厂Agent面试真题](https://www.infoq.cn/article/great-agent-interview-2025)
- 手撕：合并 K 个升序链表（LC23 变种）[citation:牛客网-Agent岗面经](https://www.nowcoder.com/discuss/900446383834943488)
- 计算机基础：MySQL 索引与事务、Redis 缓存三兄弟、进程/线程/协程逐层深挖 [citation:InfoQ-大厂Agent面试真题](https://www.infoq.cn/article/great-agent-interview-2025)
- Flow 测试开发 JD 显示豆包团队在做「智能化测试与 LLM/Agent 技术融合」，侧面印证 Flow 内 Agent 技术已渗透到研发效能链路 [citation:新浪-字节27届春招Flow测试开发JD](https://k.sina.com.cn/article_1753689431_1f95b165802000m9e7.html)

---

## 5. 分阶段准备建议

### 阶段一：巩固地基（持续进行，约 2-4 周启动）

1. **算法**：LeetCode hot 100 + 字节高频清单（链表/二叉树/DP/BFS/双指针/TopK）；目标 medium 稳定 20 分钟内 bug-free，hard 会讲思路。
2. **八股**：一门主力语言 + MySQL + Redis + 网络与 OS；按「是什么→为什么→怎么优化→怎么排查」四层准备。
3. **LLM 理论**：Transformer 手推注意力、KV Cache、常见解码策略、SFT/RLHF 概念级理解。

### 阶段二：Agent 专项（核心竞争力，2-4 周）

1. **动手做一个「创意 Agent」项目**（简历上最重要的一块）：例如「文案+配图+短视频脚本的端到端创作助手」——工作流编排 + RAG（风格素材库）+ Function Calling（调图像生成 API）+ 自评重试 + 评测集；能讲清架构、数据流、badcase 归因与量化收益。
2. **跑通字节系开源栈**：用 Coze Studio 搭一个智能体、读 Eino 的 Chain/Graph 编排源码、跑一遍 DeerFlow Demo；面试中「我看过你们的 Eino 源码」是极强信号 [citation:CloudWeGo-Eino](https://www.cloudwego.io/zh/docs/eino/)。
3. **理解 MCP**：本地起一个 MCP server，接 Claude/Cursor/TRAE 实测工具发现与调用，能画出协议交互图。
4. **背熟对比题**：FC vs MCP vs Skills、ReAct vs Plan-and-Execute、RAG vs 长上下文、微调 vs Prompt。

### 阶段三：冲刺与模拟（投递前 2 周）

1. 简历定稿：项目按「背景→难点→方案→量化结果」重写，突出 Agent/LLM 关键词与可验证结果。
2. **尽早投递提前批/实习**：2027 届节奏全面前移，Bytelntern 实习转正是字节校招最大入口（超 7000 个 Offer）[citation:ViewImp-字节2027届转正实习](https://www.viewimp.com/a/3520.html)。
3. 模拟面试：三轮各模拟一次；准备 2-3 个向面试官的反问（如「创意 Agent 的质量如何评测」「团队与豆包/即梦/Coze 哪条产品线协作最紧密」）。
4. HR 面：想清楚「为什么是字节 Flow」「为什么是 Agent」的个性化答案，并准备好实习时长承诺。

### 一句话战略

> 计算机基础决定你能不能过一面，Agent 实战项目决定你值不值这个 Offer，字节系开源栈（Eino/Coze/DeerFlow）决定面试官好感度的上限。

---

## 6. Sources

### 官方与一手来源
- [字节跳动校园招聘官网](https://jobs.bytedance.com/campus) - 校招流程与岗位投递官方入口
- [Coze 开源官网](https://www.coze.cn/open) - Coze Studio / Coze Loop 开源项目
- [CloudWeGo Eino 文档](https://www.cloudwego.io/zh/docs/eino/) - 字节开源 Go 大模型应用框架
- [DeerFlow 官网](https://deer-flow.dev) 与 [GitHub-bytedance/deer-flow](https://github.com/bytedance/deer-flow) - long-horizon Agent 编排框架
- [火山引擎 Doubao-Seed-1.6 文档](https://www.volcengine.com/docs/82379/1666946) - 豆包 1.6 thinking/flash 模型
- [火山引擎 AgentKit 文档](https://www.volcengine.com/docs/82379/1666950) - Agent 开发套件与 UI-Tars 集成

### 业务与组织动向
- [36氪-豆包成字节最凶猛的进化](https://www.36kr.com/p/3452409797934466) - Flow 产品线、DAU 破亿、春晚合作
- [腾讯新闻-整合TRAE与扣子，豆包成字节AI办公业务主干](https://news.qq.com/rain/a/20260824A0BYTE00) - 2026.8 组织整合
- [新浪-字节推统一办公品牌「豆包工作」](https://k.sina.com.cn/article_6105713761_16bedcc61019028zjm.html) - 梁汝波全员会表态
- [华尔街见闻-TRAE、扣子并入豆包](https://awtmt.com/articles/3780150) - 整合细节
- [凤凰网-豆包工作发布](https://finance.ifeng.com/c/8vsWeZ3k0iB) - AI 办公竞争格局
- [QuestMobile 2026 AI应用报告（人人都是产品经理转载）](https://www.woshipm.com/it/1888530.html) - 猫箱 MAU 数据
- [南都-AI陪伴产品停服潮](https://m.mp.oeeee.com/a/BAAFRD0000202608111641999.html) - AI 陪伴赛道收缩
- [新浪-字节推出豆包课堂（Seedance 落地）](https://k.sina.com.cn/article_3203211782_beed22060200217l0.html) - 多模态落地案例

### 招聘与技术栈
- [劳动报-2027届秋招提前批密集启动](https://www.51ldb.com/shsldb/zc/content/019fcba0c1ffc001000066d533acd97d.html) - 大厂 AI 人才争夺
- [ViewImp-字节2027届转正实习启动（7000+ Offer）](https://www.viewimp.com/a/3520.html) - Bytelntern 计划
- [WonderCV-字节AI产品经理早鸟通道](https://www.wondercv.com/blog/q434RmDq.html) - 27届提前批节奏
- [InfoQ-Eino 框架解读](https://www.infoq.cn/article/eino-golang-llm-application-framework) - Go 版大模型框架
- [36氪-豆包大模型 1.6 发布与降价](https://www.36kr.com/p/2833276823349376) - 模型与定价
- [CodePick-Trae vs Cursor](https://codepick.dev/zh/compare/trae-vs-cursor/) - TRAE 产品能力对比
- [凤凰网-DeepSeek 急招 Agent 岗](https://finance.ifeng.com/c/8vYHVl62V12) - AI 编程工具偏好信号

### 面试考察点与面经
- [InfoQ-2025 大厂 Agent 面试真题](https://www.infoq.cn/article/great-agent-interview-2025) - FC/MCP/Skills、ReAct、死循环检测等真题
- [牛客网-Agent 岗手撕面经](https://www.nowcoder.com/discuss/900446383834943488) - 合并 K 升序链表等
- [阿里云开发者-校招 AI 岗技能清单](https://developer.aliyun.com/article/1764265) - LLM→Prompt→RAG→FC→MCP→Agent 学习路径
- [新浪-字节27届春招 Flow 测试开发 JD](https://k.sina.com.cn/article_1753689431_1f95b165802000m9e7.html) - Flow 岗位 JD 样例

---

> **局限性说明**：①「创意 Agent 技术研发」官方 JD 原文未公开获取，第 2 章为同类岗位画像推断，投递前请以 jobs.bytedance.com 官网 JD 为准；②部分详情页（官网职位页、论坛原帖）存在抓取限制，相关结论基于搜索摘要与多方二手转述交叉验证；③产品数据（DAU/MAU）为 2026 年公开报道口径，可能随时间变化。
