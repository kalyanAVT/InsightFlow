# 🚀 InSyfy

> **Autonomous Research & Competitive Intelligence Agent**
>
> A multi-agent **LangGraph** pipeline that researches any topic, retrieves knowledge from persistent vector memory, synthesizes evidence with citations, self-critiques report quality, and generates structured research reports.

---

## ✨ Features

* 🧠 Multi-Agent AI workflow powered by **LangGraph**
* 🔍 Parallel web research using **Tavily Search API**
* 📚 Persistent semantic memory with **Qdrant Cloud**
* 🔄 Hybrid Retrieval (Vector Search + Re-ranking)
* 📖 Automatic citation generation & evidence validation
* 🧪 Self-critique with retry loops for quality improvement
* 📝 Structured Markdown report generation
* ⚡ FastAPI REST API
* 🎯 Designed for Competitive Intelligence & Deep Research

---

# 📌 Workflow

```text
                User Query
                     │
                     ▼
                Planner Agent
                     │
     ┌───────────────┼───────────────┐
     ▼               ▼               ▼
 Search Agent 1  Search Agent 2  Search Agent 3
     │               │               │
     └───────────────┴───────────────┘
                     │
                     ▼
             Memory Retrieval (Qdrant)
                     │
                     ▼
        Hybrid Retrieval + Re-ranking
                     │
                     ▼
              Synthesizer Agent
                     │
                     ▼
          Citation Verification Layer
                     │
                     ▼
               Critic / Evaluator
             (Retry if score is low)
                     │
                     ▼
               Writer / Reporter
                     │
                     ▼
            Store Report into Memory
```

---

# 🏗️ Architecture

```text
                ┌─────────────┐
                │ User Request│
                └──────┬──────┘
                       │
                 FastAPI Backend
                       │
                       ▼
              LangGraph State Machine
                       │
       ┌───────────────┼────────────────┐
       ▼               ▼                ▼
 Planner Agent    Search Agents     Memory RAG
       │               │                │
       └───────────────┴────────────────┘
                       │
                       ▼
             Hybrid Retrieval Engine
                       │
             Cross Encoder Re-ranking
                       │
                       ▼
             Synthesizer + Citations
                       │
                       ▼
                 Critic Evaluation
                  │             ▲
                  │ Retry Loop  │
                  ▼             │
                 Writer─────────┘
                       │
                       ▼
             Markdown Research Report
```

---

# 🤖 Agent Pipeline

## 1️⃣ Planner

Breaks the user question into multiple focused research queries.

Example:

> "Latest RAG systems"

↓

* Recent RAG architectures
* Open-source RAG frameworks
* Enterprise RAG adoption
* Research papers
* Performance benchmarks

---

## 2️⃣ Search Agents

Runs multiple searches simultaneously using **Tavily API**.

Responsibilities:

* Web search
* Result filtering
* Metadata extraction
* Source ranking

---

## 3️⃣ Memory RAG

Retrieves relevant historical research from **Qdrant Cloud**.

Uses:

* Semantic embeddings
* Similarity search
* Persistent knowledge base

---

## 4️⃣ Hybrid Retrieval

Combines

* Vector Search
* Keyword Matching
* Cross Encoder Re-ranking

for higher retrieval accuracy.

---

## 5️⃣ Synthesizer

Combines evidence from

* Web search
* Memory
* Previous reports

Removes duplicates and creates chunk-level citations.

---

## 6️⃣ Citation Enforcement

Every claim must be backed by evidence.

If insufficient evidence exists:

* Report generation is declined
* Missing citation warning is returned

---

## 7️⃣ Critic

Evaluates report quality.

Checks:

* Completeness
* Hallucinations
* Citation coverage
* Confidence
* Readability

Triggers retry loops when necessary.

---

## 8️⃣ Writer

Generates a polished Markdown report.

Stores final report into vector memory for future retrieval.

---

# 🛠 Tech Stack

| Component       | Technology                             |
| --------------- | -------------------------------------- |
| Agent Framework | LangGraph                              |
| LLM             | Groq (Mixtral-8x7B)                    |
| Fallback LLM    | OpenAI                                 |
| Search Engine   | Tavily API                             |
| Vector Database | Qdrant Cloud                           |
| Embeddings      | sentence-transformers/all-MiniLM-L6-v2 |
| Re-ranking      | cross-encoder/ms-marco-MiniLM-L-6-v2   |
| Backend         | FastAPI                                |
| Frontend        | Gradio *(Planned)*                     |
| Validation      | Pydantic                               |
| Async Runtime   | asyncio                                |

---

# 📂 Project Structure

```text
InSyfy/
│
├── agents/
│   ├── planner.py
│   ├── searcher.py
│   ├── memory_rag.py
│   ├── synthesizer.py
│   ├── critic.py
│   └── writer.py
│
├── api/
│   ├── main.py
│   ├── routes.py
│   └── schemas.py
│
├── graph/
│   ├── graph.py
│   ├── state.py
│   └── nodes.py
│
├── retrieval/
│   ├── embeddings.py
│   ├── qdrant_store.py
│   ├── hybrid.py
│   ├── reranker.py
│   └── citation.py
│
├── prompts/
│   ├── planner.yaml
│   ├── synthesizer.yaml
│   ├── critic.yaml
│   └── writer.yaml
│
├── tests/
│
├── eval/
│
├── .env.example
├── requirements.txt
├── README.md
└── LICENSE
```

---

# ⚙️ Installation

## 1. Clone Repository

```bash
git clone https://github.com/kalyanAVT/InSyfy.git

cd InSyfy
```

---

## 2. Create Virtual Environment

### Windows

```bash
python -m venv venv

venv\Scripts\activate
```

### Linux / macOS

```bash
python3 -m venv venv

source venv/bin/activate
```

---

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

# 🔑 Environment Variables

Create a `.env` file in the project root.

```env
##############################
# Qdrant Cloud
##############################

QDRANT_URL=https://your-cluster-url.qdrant.io
QDRANT_API_KEY=your_qdrant_key

##############################
# Tavily Search
##############################

TAVILY_API_KEY=your_tavily_key

##############################
# LLM Providers
##############################

GROQ_API_KEY=your_groq_key

OPENAI_API_KEY=your_openai_key

##############################
# Optional Overrides
##############################

LLM_PROVIDER=groq

LLM_MODEL=openai/gpt-oss-120b
```

---

# 🧪 Running Tests

## Test Qdrant Connection

```bash
python test_qdrant.py
```

---

## Test Complete Pipeline

```bash
python test_pipeline.py
```

---

# 🚀 Running the API

Start the FastAPI server.

```bash
uvicorn api.main:app --reload --port 8000
```

Server will be available at

```
http://localhost:8000
```

---

# 📡 API Usage

## Start Research

```http
POST /api/v1/research
```

Example request:

```json
{
  "question": "What are the latest advances in RAG systems?"
}
```

Using curl:

```bash
curl -X POST http://localhost:8000/api/v1/research \
-H "Content-Type: application/json" \
-d "{\"question\":\"What are the latest advances in RAG systems?\"}"
```

---

## Fetch Report

```http
GET /api/v1/report/{run_id}
```

Example:

```bash
curl http://localhost:8000/api/v1/report/<run_id>
```

---

# 📈 Roadmap

### ✅ Step 1

* Project foundation
* LangGraph pipeline
* FastAPI backend
* Qdrant integration
* Tavily Search
* Planner
* Search Agent
* Synthesizer

### 🚧 Step 2

* Memory RAG
* Hybrid Retrieval
* Citation Enforcement
* Cross Encoder Re-ranking
* Critic Agent

### 🚧 Step 3

* Gradio UI
* Evaluation Dashboard
* User Authentication
* Report Export
* PDF Generation

### 🚧 Step 4

* Multi-document research
* Scheduled monitoring
* Competitive intelligence dashboards
* Team collaboration
* Enterprise deployment

---

# 🤝 Contributing

Contributions are welcome!

1. Fork the repository
2. Create a feature branch

```bash
git checkout -b feature/my-feature
```

3. Commit your changes

```bash
git commit -m "Add new feature"
```

4. Push

```bash
git push origin feature/my-feature
```

5. Open a Pull Request

---

# 📜 License

This project is licensed under the **MIT License**.
