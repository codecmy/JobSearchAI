# CareerOS
## AI-Powered Career Discovery & Agent Platform

## Implementation Status

| Phase | Status |
|---|---|
| Phase 1 — Foundation | Done |
| Phase 2 — Resume Intelligence | Done |
| Phase 3 — Job Ingestion | Done |
| Phase 4 — Retrieval Engine | Done |
| Phase 5 — Recommendation Engine | Done |
| Phase 6 — Agent Engineering | Done |
| Phase 7 — Resume Tailoring and Tracking | Done |
| Phase 8 — Production Engineering | Done |

## 1. Project Overview

CareerOS is an AI-powered career discovery platform inspired by Elip.

The platform acts as a personal AI career agent that:

- Understands candidate resumes, skills, experience, and preferences.
- Continuously discovers relevant job opportunities.
- Performs semantic and keyword-based job retrieval.
- Ranks jobs based on candidate-job compatibility.
- Explains why a particular job matches a candidate.
- Remembers candidate preferences across conversations.
- Uses AI agents and tools to perform job-search operations.
- Generates role-specific resume drafts.
- Tracks job applications and candidate interactions.

### Primary Objective

Build a production-oriented AI system demonstrating:

1. Agentic AI and tool calling.
2. Retrieval-Augmented Generation.
3. Semantic search and hybrid retrieval.
4. Relational database design and SQL optimization.
5. Personalized recommendation systems.
6. Distributed asynchronous processing.
7. LLM evaluation and observability.

---

# 2. Technology Stack

## Frontend

| Technology | Purpose |
|---|---|
| React | Frontend application |
| JavaScript | Application logic |
| React Router | Client-side routing |
| Tailwind CSS | UI styling |
| TanStack Query | Server-state management |
| Axios | API communication |

## Backend

| Technology | Purpose |
|---|---|
| Python 3.12+ | Primary backend language |
| FastAPI | REST API framework |
| Pydantic | Request validation and structured outputs |
| SQLAlchemy | ORM and database interaction |
| Alembic | Database migrations |
| Pytest | Unit and integration testing |

## AI and Agent Engineering

| Technology | Purpose |
|---|---|
| LangGraph | Stateful agent orchestration |
| MCP | Standardized tool integration |
| Gemini API | LLM reasoning and structured generation |
| Sentence Transformers | Embedding generation |
| Hugging Face | Open-source models |
| Cross-Encoder | Retrieval reranking |
| Pydantic | Structured LLM outputs |

## Databases and Retrieval

| Technology | Purpose |
|---|---|
| PostgreSQL | Primary relational database |
| Qdrant | Vector database |
| Valkey | Caching and temporary state |
| PostgreSQL Full-Text Search | Lexical retrieval |
| Sentence Transformers | Vector embeddings |

## Distributed Systems

| Technology | Purpose |
|---|---|
| RabbitMQ | Asynchronous job processing |
| Celery | Background task execution |
| Docker | Containerization |
| Docker Compose | Local infrastructure orchestration |

## Observability

| Technology | Purpose |
|---|---|
| OpenTelemetry | Distributed tracing |
| Prometheus | Metrics collection |
| Grafana | Monitoring dashboards |
| Structlog | Structured application logging |
| k6 | Load testing |

---

# 3. High-Level Architecture

                  REACT FRONTEND
                         |
                         |
                    FASTAPI
                         |
          +--------------+--------------+
          |              |              |
      AUTH API       PROFILE API     JOB API
          |              |              |
          +--------------+--------------+
                         |
                   SERVICE LAYER
                         |
          +--------------+--------------+
          |              |              |
      POSTGRESQL       QDRANT         VALKEY
          |              |              |
          +--------------+--------------+
                         |
                   AI ORCHESTRATION
                         |
                      LANGGRAPH
                         |
          +--------------+--------------+
          |              |              |
      LLM REASONING   MCP TOOLS      MEMORY
          |              |              |
          +--------------+--------------+
                         |
                  RETRIEVAL ENGINE
                         |
             HYBRID SEARCH + RANKING
                         |
                 RECOMMENDATIONS

          BACKGROUND PROCESSING
                         |
                     RABBITMQ
                         |
                    CELERY WORKERS
                         |
             JOB INGESTION / EMBEDDINGS

---

# 4. Core Modules

## Module 1: Authentication and Candidate Management

### Features

- User registration and login.
- JWT-based authentication.
- Candidate profile creation.
- Resume upload.
- Candidate experience management.
- Skill extraction.
- Career preference management.

### Database Tables

- users
- candidate_profiles
- candidate_skills
- skills
- candidate_preferences
- candidate_experiences
- candidate_projects

### Implementation

1. Implement authentication endpoints.
2. Create normalized PostgreSQL schema.
3. Implement SQLAlchemy models.
4. Configure Alembic migrations.
5. Implement resume upload.
6. Extract resume text.
7. Use an LLM to extract structured candidate information.
8. Validate extracted information using Pydantic.
9. Persist the candidate profile.

---

## Module 2: Job Ingestion Pipeline

### Objective

Build an asynchronous pipeline that continuously collects and indexes job listings.

### Job Sources

- Public job APIs.
- Company career pages with permitted access.
- RSS feeds.
- Open job datasets.

### Pipeline

Job Source
    |
    v
Job Ingestion API
    |
    v
RabbitMQ
    |
    v
Celery Worker
    |
    v
Data Normalization
    |
    v
Deduplication
    |
    v
PostgreSQL
    |
    v
Embedding Generation
    |
    v
Qdrant Index

### Responsibilities

- Normalize job titles.
- Extract skills.
- Identify employment type.
- Extract location.
- Extract experience requirements.
- Detect salary information.
- Deduplicate listings.
- Detect expired listings.
- Generate embeddings.
- Synchronize Qdrant indexes.

### Database Tables

- companies
- jobs
- job_skills
- job_sources
- job_embeddings

### Important Engineering Concepts

- Idempotent ingestion.
- Message retries.
- Dead-letter queues.
- Batch processing.
- Incremental indexing.
- Duplicate detection.
- Event-driven processing.

---

## Module 3: Resume Intelligence

### Objective

Transform candidate resumes into structured searchable profiles.

### Processing Pipeline

PDF Upload
    |
    v
Text Extraction
    |
    v
Resume Parsing
    |
    v
LLM Structured Extraction
    |
    v
Pydantic Validation
    |
    v
Candidate Profile
    |
    v
Embedding Generation
    |
    v
Qdrant

### Extracted Information

- Technical skills.
- Work experience.
- Education.
- Projects.
- Certifications.
- Years of experience.
- Preferred job roles.

### Important Requirement

Never allow the LLM to invent candidate experience.

Every extracted fact should retain its source or supporting resume text.

---

## Module 4: Hybrid Retrieval Engine

### Objective

Build a search engine that retrieves jobs using semantic understanding, keyword matching, and relational filtering.

### Query Example

"Find backend engineering internships involving Java,
distributed systems, Kafka, and AI infrastructure."

### Step 1: Query Understanding

Convert natural-language queries into structured search parameters.

Example:

{
    "roles": ["Backend Engineering Intern"],
    "skills": ["Java", "Kafka", "Distributed Systems"],
    "employment_type": "Internship",
    "locations": ["Remote", "Bangalore"],
    "experience_max": 2
}

Use Gemini with structured output validation.

### Step 2: Semantic Retrieval

1. Generate query embeddings.
2. Search Qdrant.
3. Retrieve top-K matching jobs.
4. Retrieve job metadata.

### Step 3: Lexical Retrieval

Use PostgreSQL Full-Text Search.

Match explicit keywords, technical skills, and job titles.

### Step 4: Relational Filtering

Apply SQL filters:

- Location.
- Employment type.
- Experience.
- Salary.
- Active status.
- Candidate dealbreakers.

### Step 5: Result Aggregation

Merge:

- Semantic retrieval results.
- Lexical retrieval results.
- Structured SQL results.

Deduplicate results before ranking.

### Step 6: Reranking

Use a Cross-Encoder to rerank the most promising candidates.

### Initial Ranking Formula

Score =
    0.40 * Semantic Similarity
  + 0.25 * Skill Match
  + 0.15 * Experience Match
  + 0.10 * Preference Match
  + 0.10 * Freshness

These weights must be evaluated and tuned.

Hard constraints must be applied independently of the ranking score.

---

## Module 5: Personalized Recommendation Engine

### Objective

Recommend jobs based on candidate profiles, preferences, and interaction history.

### Features

- Personalized job recommendations.
- Similar job discovery.
- Candidate-job compatibility scoring.
- Preference-based filtering.
- Recommendation explanations.
- Feedback collection.

### Feedback Types

- Interested.
- Not interested.
- Saved.
- Applied.
- Rejected.
- Viewed.

### Recommendation Pipeline

Candidate Profile
      |
      v
Preference Retrieval
      |
      v
Hybrid Job Retrieval
      |
      v
Hard Constraint Filtering
      |
      v
Reranking
      |
      v
Top-K Recommendations
      |
      v
Explanation Generation

### Evaluation Metrics

- Precision@K.
- Recall@K.
- NDCG@K.
- MRR.
- Recommendation diversity.

---

## Module 6: AI Career Agent

### Objective

Build a stateful agent that interacts with the candidate and performs operations through tools.

### Technology

- LangGraph.
- MCP.
- Gemini.
- Pydantic.

### Agent Tools

| Tool | Responsibility |
|---|---|
| search_jobs | Search relevant opportunities |
| get_job_details | Retrieve complete job details |
| get_candidate_profile | Retrieve candidate information |
| update_preferences | Update candidate preferences |
| save_job | Save an opportunity |
| reject_job | Record rejected opportunities |
| get_match_explanation | Explain job compatibility |
| tailor_resume | Generate a tailored resume |
| track_application | Update application status |

### Agent Workflow

User Message
     |
     v
Intent Detection
     |
     v
Context Retrieval
     |
     v
Agent Planner
     |
     v
Tool Selection
     |
     v
Tool Execution
     |
     v
Result Validation
     |
     v
Response Generation

### Agent Requirements

- Tool calling.
- Structured outputs.
- Persistent state.
- Conversation context.
- Error handling.
- Tool execution validation.
- Human approval for sensitive actions.

---

## Module 7: Persistent Candidate Memory

### Objective

Allow the agent to remember meaningful candidate information across conversations.

### Memory Categories

1. Profile Memory
   - Education.
   - Skills.
   - Experience.
   - Projects.

2. Preference Memory
   - Target roles.
   - Locations.
   - Salary expectations.
   - Employment preferences.
   - Dealbreakers.

3. Interaction Memory
   - Saved jobs.
   - Rejected jobs.
   - Previous recommendations.
   - Candidate feedback.

### Storage

PostgreSQL is the source of truth.

Valkey stores frequently accessed context.

### Memory Workflow

Conversation
    |
    v
Memory Extraction
    |
    v
Validation
    |
    v
PostgreSQL Persistence
    |
    v
Future Context Retrieval

The agent must distinguish between confirmed preferences and assumptions.

Candidates must be able to inspect and modify stored preferences.

---

## Module 8: Resume Tailoring

### Objective

Generate job-specific resume drafts using existing candidate information.

### Workflow

Candidate Resume
       |
       v
Job Description
       |
       v
Requirement Extraction
       |
       v
Candidate Evidence Retrieval
       |
       v
LLM Resume Tailoring
       |
       v
Resume Validation
       |
       v
Side-by-Side Comparison
       |
       v
Candidate Approval
       |
       v
PDF Export

### Requirements

- Preserve factual accuracy.
- Never invent experience.
- Highlight relevant skills.
- Reorder relevant projects.
- Generate role-specific summaries.
- Require candidate approval.

---

## Module 9: Application Tracking

### Features

- Save jobs.
- Track applications.
- Track interviews.
- Record application outcomes.
- Schedule follow-ups.
- Store feedback.

### Application States

DISCOVERED
    |
    v
SAVED
    |
    v
APPLIED
    |
    v
INTERVIEW
    |
    v
OFFER / REJECTED

### Database Tables

- applications
- application_events
- candidate_feedback

Use database transactions to maintain application state consistency.

---

# 5. Database Architecture

PostgreSQL is the primary relational database.

### Core Tables

users
candidate_profiles
candidate_preferences
candidate_experiences
candidate_projects
candidate_skills
skills

companies
jobs
job_skills
job_sources

conversations
messages
candidate_memories

job_matches
applications
application_events
candidate_feedback

### SQL Engineering Requirements

Implement and benchmark:

1. One-to-many relationships.
2. Many-to-many relationships.
3. Foreign keys and constraints.
4. Database normalization.
5. Composite indexes.
6. Partial indexes.
7. CTEs.
8. Window functions.
9. Transaction isolation.
10. EXPLAIN ANALYZE.

### Important Indexes

- Unique index on job source and external job ID.
- Composite index on candidate_id and skill_id.
- Index on job status and posted_at.
- Index on application candidate_id and status.
- Index on company_id.

Measure query performance before and after optimization.

---

# 6. API Design

## Authentication

POST /api/v1/auth/register
POST /api/v1/auth/login
POST /api/v1/auth/refresh

## Candidate

GET    /api/v1/candidates/me
PUT    /api/v1/candidates/me
POST   /api/v1/candidates/resume
GET    /api/v1/candidates/preferences
PUT    /api/v1/candidates/preferences

## Jobs

GET  /api/v1/jobs
GET  /api/v1/jobs/{job_id}
POST /api/v1/jobs/search
POST /api/v1/jobs/{job_id}/save

## Recommendations

GET  /api/v1/recommendations
POST /api/v1/recommendations/feedback

## Agent

POST /api/v1/agent/chat
GET  /api/v1/agent/conversations
GET  /api/v1/agent/memory

## Applications

POST  /api/v1/applications
GET   /api/v1/applications
PATCH /api/v1/applications/{application_id}

## Resume Tailoring

POST /api/v1/resumes/tailor
GET  /api/v1/resumes/{resume_id}
POST /api/v1/resumes/{resume_id}/approve

---

# 7. Frontend Pages

1. Landing Page.
2. Registration and Login.
3. Candidate Onboarding.
4. Resume Upload.
5. Candidate Dashboard.
6. Job Discovery.
7. Job Details.
8. AI Career Agent Chat.
9. Personalized Recommendations.
10. Candidate Profile.
11. Preference Management.
12. Resume Tailoring.
13. Application Tracker.
14. Settings and Memory Management.

---

# 8. Development Roadmap

## Phase 1 — Foundation

- Initialize Git repository.
- Set up FastAPI.
- Set up React.
- Configure PostgreSQL.
- Configure SQLAlchemy.
- Configure Alembic.
- Implement authentication.
- Design ER diagram.
- Create initial migrations.

Deliverable: Working backend and candidate profile system.

## Phase 2 — Resume Intelligence

- Implement PDF parsing.
- Extract candidate information.
- Validate structured outputs.
- Store skills and experience.
- Generate candidate embeddings.

Deliverable: Structured candidate profiles.

## Phase 3 — Job Ingestion

- Integrate job sources.
- Configure RabbitMQ.
- Implement Celery workers.
- Normalize job data.
- Implement deduplication.
- Persist jobs.
- Generate embeddings.
- Index jobs in Qdrant.

Deliverable: Searchable job database.

## Phase 4 — Retrieval Engine

- Implement semantic retrieval.
- Implement PostgreSQL full-text search.
- Implement SQL filtering.
- Implement result aggregation.
- Implement reranking.
- Generate match explanations.
- Benchmark SQL queries.

Deliverable: Hybrid job search engine.

## Phase 5 — Recommendation Engine

- Implement candidate-job scoring.
- Add personalization.
- Add recommendation feedback.
- Implement Precision@K and NDCG@K evaluation.

Deliverable: Personalized job recommendations.

## Phase 6 — Agent Engineering

- Configure LangGraph.
- Implement MCP server.
- Build agent tools.
- Implement tool calling.
- Implement persistent memory.
- Add conversation state.
- Add error handling and validation.

Deliverable: Functional AI career agent.

## Phase 7 — Resume Tailoring and Tracking

- Implement resume tailoring.
- Implement document comparison.
- Implement approval workflow.
- Implement application tracking.

Deliverable: Complete candidate experience.

## Phase 8 — Production Engineering

- Dockerize all services.
- Add OpenTelemetry.
- Configure Prometheus.
- Configure Grafana.
- Add structured logging.
- Write integration tests.
- Load test with k6.
- Optimize database queries.
- Document architecture and deployment.

Deliverable: Production-style demonstrable application.

---

# 9. Repository Structure

careeros/
|
|-- frontend/
|   |-- src/
|   |   |-- components/
|   |   |-- pages/
|   |   |-- hooks/
|   |   |-- services/
|   |   |-- contexts/
|   |   |-- layouts/
|   |   |-- App.jsx
|   |   |-- main.jsx
|
|-- backend/
|   |-- app/
|   |   |-- api/
|   |   |-- core/
|   |   |-- models/
|   |   |-- schemas/
|   |   |-- repositories/
|   |   |-- services/
|   |   |-- agents/
|   |   |-- retrieval/
|   |   |-- memory/
|   |   |-- ranking/
|   |   |-- ingestion/
|   |   |-- workers/
|   |   |-- integrations/
|   |   |-- main.py
|
|-- mcp_server/
|   |-- tools/
|   |-- server.py
|
|-- migrations/
|
|-- evals/
|   |-- retrieval/
|   |-- ranking/
|   |-- agent/
|   |-- explanations/
|
|-- tests/
|   |-- unit/
|   |-- integration/
|   |-- performance/
|
|-- infrastructure/
|   |-- docker/
|   |-- prometheus/
|   |-- grafana/
|
|-- docs/
|   |-- architecture.md
|   |-- database-schema.md
|   |-- api-contracts.md
|
|-- docker-compose.yml
|-- .env.example
|-- README.md
|-- plan.md

---

# 10. Testing Strategy

## Unit Testing

- Resume parsing.
- Skill extraction validation.
- Ranking functions.
- Preference filtering.
- Memory extraction.
- SQL repository logic.

## Integration Testing

- PostgreSQL integration.
- Qdrant integration.
- RabbitMQ ingestion.
- Agent tool execution.
- MCP communication.
- End-to-end job discovery.

## AI Evaluation

- Retrieval relevance.
- Ranking quality.
- Hallucination rate.
- Explanation faithfulness.
- Tool selection accuracy.
- Memory correctness.

## Performance Testing

Use k6 to measure:

- Search API latency.
- Concurrent job searches.
- Candidate profile retrieval.
- Recommendation endpoint performance.
- Agent response latency.

---

# 11. Non-Functional Requirements

- API authentication and authorization.
- Rate limiting.
- Input validation.
- Secure resume storage.
- PII protection.
- Idempotent ingestion.
- Database transaction consistency.
- Retry mechanisms.
- Observability.
- Graceful service failure.
- Candidate-controlled memory.
- Human approval for external actions.

---

# 12. Project Success Criteria

The project is considered complete when:

1. A candidate can upload a resume.
2. The system extracts a structured profile.
3. Jobs are ingested asynchronously.
4. Jobs are indexed in Qdrant.
5. Users can search using natural language.
6. Hybrid retrieval returns relevant results.
7. A ranking engine personalizes recommendations.
8. The AI agent can call tools.
9. Candidate preferences persist across conversations.
10. The agent explains its recommendations.
11. Users can generate tailored resume drafts.
12. Users can track applications.
13. Retrieval and ranking are evaluated quantitatively.
14. The entire application runs through Docker Compose.
15. The system has meaningful tests and observability.

---

# 13. Engineering Principles

1. Build a modular monolith first. Split services only when justified.
2. PostgreSQL is the source of truth for candidate and job metadata.
3. Qdrant stores embeddings, not authoritative business records.
4. LLMs should interpret and generate, not make unvalidated database decisions.
5. Apply hard constraints outside the LLM.
6. Every agent tool must have a clear contract and permission boundary.
7. Persistent memory must be structured and editable.
8. Every recommendation should be traceable to evidence.
9. Measure retrieval and ranking quality rather than assuming they work.
10. Never fabricate candidate experience or job information.

---

# 14. Final Project Goal

CareerOS should demonstrate the ability to engineer an end-to-end AI product combining:

- Backend engineering.
- Relational database design.
- SQL optimization.
- Distributed asynchronous processing.
- Semantic retrieval.
- Hybrid search.
- Recommendation systems.
- Agent orchestration.
- MCP tool integration.
- Persistent memory.
- LLM evaluation.
- Production observability.

The final result should not merely be an AI chatbot that searches jobs.

It should be a complete AI career discovery system capable of understanding candidates, discovering opportunities, ranking jobs, remembering preferences, and assisting candidates throughout their job search.