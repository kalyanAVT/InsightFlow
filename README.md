# InSyfy

Autonomous Research & Competitive Intelligence Agent.

InSyfy is a multi-agent research system built with LangGraph that performs autonomous web research, retrieves relevant knowledge from persistent vector memory, synthesizes evidence with citations, evaluates report quality through self-critique, and generates structured research reports.

---

# Features

* Multi-agent workflow powered by LangGraph
* Parallel web research using Tavily Search API
* Persistent semantic memory with Qdrant Cloud
* Hybrid Retrieval (Vector Search + Re-ranking)
* Automatic citation generation and evidence validation
* Self-critique with retry loops for quality improvement
* Structured Markdown report generation
* FastAPI REST API
* Gradio Web Interface
* Redis state management and caching
* Server-Sent Events (SSE) for live progress streaming
* Designed for Competitive Intelligence and Deep Research

---

# Workflow

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
        Store Report into Vector Memory
```

---

# Architecture

```text
User
 │
 ▼
Gradio UI
 │
 ▼
FastAPI
 │
 ▼
LangGraph State Machine
 │
 ├── Planner
 ├── Parallel Search Agents
 ├── Memory Retrieval (Qdrant)
 ├── Hybrid Retrieval
 ├── Synthesizer
 ├── Critic
 └── Writer
 │
 ▼
Redis (State Cache)
 │
 ▼
Structured Markdown Report
```

---

# Agent Pipeline

## Planner

Breaks a user question into focused research tasks.

Example:

```
Latest RAG systems
```

becomes

* Recent RAG architectures
* Open-source RAG frameworks
* Enterprise RAG adoption
* Research papers
* Performance benchmarks

---

## Search Agents

Runs multiple searches in parallel using Tavily.

Responsibilities:

* Web Search
* Metadata extraction
* Result filtering
* Source ranking

---

## Memory Retrieval

Retrieves relevant historical research from Qdrant.

Uses:

* Semantic embeddings
* Similarity search
* Persistent knowledge base

---

## Hybrid Retrieval

Combines

* Vector Search
* Keyword Search
* Cross Encoder Re-ranking

to improve retrieval quality.

---

## Synthesizer

Combines information from

* Web search
* Vector memory
* Previous reports

while removing duplicate information and attaching citations.

---

## Citation Enforcement

Every factual claim must be supported by evidence.

If evidence is insufficient,

* Report generation is rejected
* Missing citation warnings are returned

---

## Critic

Evaluates report quality.

Checks

* Completeness
* Hallucinations
* Citation coverage
* Confidence
* Readability

Automatically retries low-quality generations.

---

## Writer

Produces the final Markdown report and stores it into persistent vector memory for future retrieval.

---

# Technology Stack

| Component       | Technology            |
| --------------- | --------------------- |
| Agent Framework | LangGraph             |
| LLM             | Groq                  |
| Search Engine   | Tavily Search         |
| Vector Database | Qdrant Cloud          |
| State Store     | Redis                 |
| Backend         | FastAPI               |
| Frontend        | Gradio                |
| Embeddings      | sentence-transformers |
| Re-ranking      | Cross Encoder         |
| Validation      | Pydantic              |
| Async Runtime   | asyncio               |

---

# Project Structure

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
├── ui/
│   └── app.py
│
├── prompts/
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

# Quick Start

## 1. Clone Repository

```bash
git clone https://github.com/kalyanAVT/InSyfy.git

cd InSyfy
```

---

## 2. Create Virtual Environment

### Windows

```bash
python -m venv .venv

.venv\Scripts\activate
```

### Linux / macOS

```bash
python3 -m venv .venv

source .venv/bin/activate
```

---

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

# Configuration

Create a `.env` file in the project root.

```env
QDRANT_URL=https://your-cluster.qdrant.io
QDRANT_API_KEY=your_qdrant_api_key

TAVILY_API_KEY=your_tavily_api_key

GROQ_API_KEY=your_groq_api_key

REDIS_URL=redis://localhost:6379
```

---

# Redis Setup

## Option 1 — Redis Cloud

Use the free Redis Cloud service.

```env
REDIS_URL=redis://username:password@your-host:port
```

---

## Option 2 — Docker

```bash
docker run -d -p 6379:6379 --name redis redis:7-alpine
```

---

## Option 3 — Windows

Install Redis for Windows or use Redis Cloud if preferred.

---

# Running the Application

Start the server.

```bash
uvicorn api.main:app --reload --port 8000
```

Open your browser at

```
http://localhost:8000
```

The FastAPI backend and Gradio interface will both be available.

---

# API Endpoints

| Method | Endpoint                | Description                 |
| ------ | ----------------------- | --------------------------- |
| POST   | /api/v1/research        | Start a research run        |
| GET    | /api/v1/stream/{run_id} | Stream live events (SSE)    |
| GET    | /api/v1/status/{run_id} | Check research status       |
| GET    | /api/v1/report/{run_id} | Retrieve final report       |
| GET    | /api/v1/history         | View previous research runs |
| DELETE | /api/v1/report/{run_id} | Delete a report             |

---

# Example Request

```http
POST /api/v1/research
```

```json
{
  "question": "Latest advances in Retrieval-Augmented Generation"
}
```

Using curl

```bash
curl -X POST http://localhost:8000/api/v1/research \
-H "Content-Type: application/json" \
-d "{\"question\":\"Latest advances in Retrieval-Augmented Generation\"}"
```

---

# Development

Run tests

```bash
python test_pipeline.py
```

Freeze dependencies

```bash
pip freeze > requirements.txt
```

---

# Roadmap

## Completed

* Step 1: Foundation (Linear Pipeline)
* Step 2: Full Pipeline

  * Parallel Search
  * Hybrid Retrieval
  * Critic Retry Loop
* Step 3

  * Gradio UI
  * SSE Streaming
  * Redis State Management

## Planned

* Evaluation Framework
* CI/CD Pipeline
* Weights & Biases Logging
* Multi-document Research
* Scheduled Monitoring
* Report Export
* Team Collaboration
* Enterprise Deployment

---

# Contributing

Contributions are welcome.

1. Fork the repository.
2. Create a feature branch.

```bash
git checkout -b feature/my-feature
```

3. Commit your changes.

```bash
git commit -m "Add new feature"
```

4. Push the branch.

```bash
git push origin feature/my-feature
```

5. Open a Pull Request.

---

# License

This project is licensed under the MIT License.
