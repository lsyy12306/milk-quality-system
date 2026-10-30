# 牛奶品质分级系统 · RAG 语料库

> 生成时间：2026-10-23　|　知识块总数：**47**　|　格式：JSONL（每行一个 JSON）

## 1. 这是什么
本语料库为「牛奶品质分级系统」项目沉淀的可检索知识，覆盖项目概述、数据、模型、后端、前端、部署、测试、安全、Agent 智能体、企业落地、FAQ 十一大类。可用于搭建项目级问答机器人、智能助手或文档检索，让使用者用自然语言问「怎么部署」「数据从哪来」「预测接口怎么调」「企业日报怎么生成」等问题并拿到准确答案。

## 2. 文件
- `rag_corpus.jsonl`：主语料，每行一个 JSON 知识块。
- `build_rag_corpus.py`（位于 `src/`）：可复现的生成脚本，修改后重跑即可重建语料。
- 本文件：使用说明。

## 3. 知识块字段
| 字段 | 含义 |
| --- | --- |
| id | 唯一编号，如 `mq-001` |
| category | 分类（项目概述/数据/模型/后端/前端/部署/测试/安全/Agent/企业落地/FAQ） |
| title | 知识块标题 |
| type | `doc`=事实性知识块；`qa`=问答对（含 question/answer，可直接作答案） |
| content | 正文（自包含、可被检索与引用） |
| keywords | 关键词数组，建议作为检索 boost 或标签 |
| source | 出处文档，便于溯源 |
| question / answer | 仅 `qa` 类型有，问答对原文 |

## 4. 分类统计
- 项目概述：6 条
- 数据：6 条
- 模型：7 条
- 后端：6 条
- 前端：2 条
- 部署：5 条
- 测试：2 条
- 安全：1 条
- Agent：3 条
- 企业落地：5 条
- FAQ：4 条

## 5. 如何接入 RAG 管线（示例）
语料为纯文本 + 元数据，embedding 在摄取（ingest）阶段生成。以下为通用接入示例（Python + sentence-transformers）：

```python
import json
from sentence_transformers import SentenceTransformer

# 1) 读取语料
chunks = [json.loads(l) for l in open("docs/rag_corpus.jsonl", encoding="utf-8")]

# 2) 构造待嵌入文本（qa 优先用 question+answer，doc 用 title+content）
model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")  # 多语言，支持中文
texts = []
for c in chunks:
    if c["type"] == "qa":
        texts.append(c["question"] + " " + c["answer"])
    else:
        texts.append(c["title"] + " " + c["content"])

embs = model.encode(texts, normalize_embeddings=True)

# 3) 写入向量库（以 sqlite + 简单余弦为例，或换 chroma/pgvector/FAISS）
#    chroma: collection.add(ids=[c['id'] for c in chunks], documents=texts, embeddings=embs, metadatas=chunks)
# 4) 检索时取 top-k，把对应 content 作为上下文喂给 LLM 生成答案
```

接入要点：
- **检索粒度**：以单个知识块为单位，块已拆分为「一事一议」，便于精准命中。
- **中文 embedding**：推荐多语言模型（如 paraphrase-multilingual-MiniLM-L12-v2、bge-m3）以保证中文召回。
- **关键词 boost**：命中 `keywords` 的查询可直接提升该块权重。
- **答案来源**：`qa` 块的 `answer` 字段可直接作为高置信答案；`doc` 块交给 LLM 基于 content 归纳。

## 6. 维护建议
- 项目文档（docs/01~06、README）更新后，重跑 `python src/build_rag_corpus.py` 重建语料。
- 新增 FAQ 直接在 `build_rag_corpus.py` 的 `CORPUS` 列表追加条目即可，脚本自动编号与分流。
