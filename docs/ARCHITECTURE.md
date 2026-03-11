# Oasis — System Architecture Document

> Version 1.0 | Confidential | 2025

---

## 1. Architecture Overview

Oasis is designed as a **cloud-native, microservices-based platform** with a distributed GPU worker cluster at its core. The architecture prioritizes horizontal scalability, fault isolation, and cost-optimized GPU utilization.

### 1.1 High-Level Architecture Tiers

| Tier | Components | Responsibility |
|---|---|---|
| **Client Tier** | Next.js Web App, Mobile (future) | UI rendering, user interaction, asset preview |
| **Edge Tier** | Cloudflare CDN, WAF | Static asset delivery, DDoS protection, geo-routing |
| **API Gateway Tier** | Kong / AWS API Gateway | Auth validation, rate limiting, request routing |
| **Application Tier** | FastAPI microservices (8 services) | Business logic, data persistence, job orchestration |
| **Messaging Tier** | Redis, Celery, Kafka | Async job queuing, event streaming, inter-service comms |
| **GPU Worker Tier** | PyTorch workers on GPU VMs | AI model inference, video encoding |
| **Storage Tier** | PostgreSQL, Redis cache, S3/R2 | Relational data, hot cache, object storage |
| **Observability Tier** | Prometheus, Grafana, ELK | Metrics, dashboards, log aggregation |

### 1.2 Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                          CLIENT TIER                                │
│                     Next.js 14 Web App                              │
│        React 18 + Tailwind CSS + Socket.IO WebSocket                │
└────────────────────────────┬────────────────────────────────────────┘
                             │ HTTPS
┌────────────────────────────▼────────────────────────────────────────┐
│                          EDGE TIER                                   │
│                   Cloudflare CDN + WAF                               │
│           (Static assets, DDoS protection, geo-routing)             │
└────────────────────────────┬────────────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────────────┐
│                      API GATEWAY TIER                                │
│                  Kong / AWS API Gateway                              │
│      JWT Validation | Rate Limiting | /v1/, /v2/ Routing            │
│              100 req/min (free) | 1000 req/min (pro)                │
└────────┬───────┬───────┬───────┬───────┬───────┬───────┬───────┬───┘
         │       │       │       │       │       │       │       │
    ┌────▼──┐┌───▼──┐┌───▼──┐┌───▼──┐┌───▼──┐┌───▼──┐┌───▼──┐┌───▼──┐
    │ User  ││Proj. ││Asset ││AI Job││Render││Collab││Billing││Notif.│
    │ 8001  ││ 8002 ││ 8003 ││ 8004 ││ 8005 ││ 8006 ││ 8007 ││ 8008 │
    └───┬───┘└──┬───┘└──┬───┘└──┬───┘└──┬───┘└──┬───┘└──┬───┘└──┬───┘
        │       │       │       │       │       │       │       │
        └───────┴───────┴───┬───┴───────┴───────┴───────┴───────┘
                            │
              ┌─────────────┼─────────────┐
              │             │             │
        ┌─────▼─────┐ ┌────▼────┐ ┌──────▼──────┐
        │ PostgreSQL │ │  Redis  │ │   Kafka     │
        │  (Data)    │ │ (Cache) │ │  (Events)   │
        └────────────┘ └────┬────┘ └─────────────┘
                            │
                    ┌───────▼────────┐
                    │  Celery Queue  │
                    │  (Job Broker)  │
                    └───────┬────────┘
                            │
              ┌─────────────┼──────────────┐
              │             │              │
        ┌─────▼─────┐ ┌────▼────┐ ┌───────▼──────┐
        │ GPU Worker │ │GPU Worker│ │  GPU Worker  │
        │  (Video)   │ │ (Voice) │ │   (Music)    │
        └────────────┘ └─────────┘ └──────────────┘
                            │
                    ┌───────▼────────┐
                    │   S3 / R2      │
                    │ Object Storage │
                    └────────────────┘
```

---

## 2. Frontend Architecture

### 2.1 Technology Stack

| Component | Technology | Rationale |
|---|---|---|
| Framework | Next.js 14 (App Router) | SSR/SSG, file-based routing, React Server Components |
| UI Library | React 18 | Component model, concurrent rendering |
| Styling | Tailwind CSS + shadcn/ui | Utility-first, consistent design system |
| 3D / Visual FX | Three.js | WebGL rendering for editor overlays |
| Video Rendering | FFmpeg WASM + WebGL Canvas | Client-side preview without server round-trips |
| State Management | Zustand + React Query | Lightweight global state + server state caching |
| Real-time | Socket.IO (WebSocket) | Collaborative presence, job progress updates |
| Auth | NextAuth.js | OAuth providers + JWT session handling |

### 2.2 Frontend Module Structure

```
app/
├── (auth)/
│   ├── login/              # Email/password + OAuth login
│   ├── register/           # New account registration
│   └── reset-password/     # Password reset flow
├── dashboard/              # Project list, activity feed
├── project/[id]/           # Workspace, assets, versions
├── editor/[id]/            # WebGL timeline editor
├── generate/               # AI prompt panel (video/voice/music)
├── assets/                 # Asset manager and search
├── billing/                # Plan management, credit balance
└── settings/               # Profile, API keys, integrations
```

### 2.3 Real-Time Architecture

The frontend maintains a **persistent WebSocket connection** via Socket.IO for three data streams:

1. **AI job progress events** — real-time status updates for queued/processing/completed jobs
2. **Collaborative presence/cursors** — who is editing, where they are on the timeline
3. **Timeline comment notifications** — new comments, replies, resolutions

WebSocket rooms are namespaced by **project ID**, so users only receive events for their active project.

### 2.4 Key Frontend Libraries

```
next                  # 14.x — App Router
react                 # 18.x
tailwindcss           # 3.x
@shadcn/ui            # Component library
zustand               # Global state management
@tanstack/react-query # Server state caching
socket.io-client      # WebSocket client
three                 # 3D WebGL rendering
@ffmpeg/ffmpeg        # WASM video processing
next-auth             # Authentication
```

---

## 3. Backend Microservices Architecture

### 3.1 Service Inventory

| Service | Language/Framework | Port | Primary Responsibility |
|---|---|---|---|
| **User Service** | Python / FastAPI | 8001 | Registration, login, profile, OAuth, JWT issuance |
| **Project Service** | Python / FastAPI | 8002 | CRUD projects, branching, commit history, merge |
| **Asset Service** | Python / FastAPI | 8003 | Upload pipeline, chunked transfer, format validation, thumbnails |
| **AI Job Service** | Python / FastAPI | 8004 | Submit jobs, poll status, deduct credits, retry logic |
| **Rendering Service** | Python / FastAPI | 8005 | Timeline export, final video encoding, watermarking |
| **Collaboration Service** | Python / FastAPI | 8006 | Invitations, roles, timeline comments, presence |
| **Billing Service** | Python / FastAPI | 8007 | Subscription management, credit ledger, Stripe webhooks |
| **Notification Service** | Python / FastAPI | 8008 | Email (SendGrid), in-app push, webhook delivery |

### 3.2 Inter-Service Communication

| Pattern | Technology | Use Case |
|---|---|---|
| **Synchronous** | REST over internal HTTP with mutual TLS | Direct service-to-service calls |
| **Asynchronous** | Kafka topics | Domain events (`job.completed`, `asset.uploaded`, `billing.credit_deducted`) |
| **Service Discovery** | Kubernetes DNS | e.g., `user-service.oasis.svc.cluster.local` |
| **Circuit Breaker** | Hystrix pattern | Prevents cascade failures between services |

### 3.3 API Gateway

**Kong API Gateway** sits in front of all microservices and handles:

- JWT validation
- Rate limiting (100 req/min free, 1000 req/min pro)
- Request transformation
- API versioning (`/v1/`, `/v2/`)
- Access logging

---

## 4. AI Generation Engine

### 4.1 Generation Pipeline

All AI generation follows a **five-stage pipeline**:

```
┌──────────────┐    ┌────────────────┐    ┌──────────┐    ┌────────────────┐    ┌────────────────┐
│ 1. INGESTION │───▶│2. PREPROCESSING│───▶│3. INFERENCE│──▶│4. POST-PROCESS │───▶│ 5. ENCODE &    │
│              │    │                │    │           │    │                │    │    STORAGE     │
│ Parse prompt │    │ Tokenize text  │    │ GPU model │    │ Upscale,       │    │ H.264/H.265   │
│ Validate     │    │ Resize images  │    │ forward   │    │ denoise, CLUT  │    │ or AAC        │
│ Enqueue job  │    │ Normalize audio│    │ pass      │    │ color grade    │    │ Upload to S3   │
└──────────────┘    └────────────────┘    └──────────┘    └────────────────┘    └────────────────┘
   AI Job Service      GPU Worker           GPU Worker       GPU Worker            GPU Worker
```

### 4.2 AI Model Stack

| Domain | Primary Model | Fallback | Framework |
|---|---|---|---|
| Text-to-Video | Stable Video Diffusion (SVD-XT) | AnimateDiff + MotionLoRA | PyTorch / Diffusers |
| Image-to-Video | SVD img2vid | CogVideoX | PyTorch / Diffusers |
| Text-to-Speech | XTTS v2 (Coqui) | VITS / MeloTTS | PyTorch |
| Voice Cloning | XTTS v2 fine-tuned | RVC (Retrieval Voice Conv) | PyTorch |
| Music Generation | MusicGen (Meta) | Riffusion | PyTorch / HuggingFace |
| Speech Recognition | Whisper large-v3 | Whisper medium (fast path) | OpenAI Whisper / faster-whisper |
| Auto Editing | Video segmentation CNN | PySceneDetect (rules-based) | PyTorch / OpenCV |

### 4.3 GPU Worker Architecture

GPU workers are **stateless Docker containers** deployed on GPU VM instances. Each worker:

1. Polls a Redis-backed Celery queue
2. Acquires a job
3. Loads the required model (from local NVMe cache or S3 model store)
4. Runs inference
5. Uploads the output to S3/R2

**Key design decisions:**

- **Auto-scaling:** Kubernetes HPA based on queue depth metric (Prometheus)
- **Model caching:** Weights cached on persistent NVMe volumes to avoid re-download
- **Multi-tenancy:** GPU time-slicing (MIG on A100, CUDA MPS on smaller GPUs)
- **Cold-start mitigation:** At least 2 workers per model type kept warm during business hours

### 4.4 GPU Infrastructure Providers

| Tier | Provider | Use Case | GPU Type | Est. Cost |
|---|---|---|---|---|
| Development | RunPod / Vast.ai | Low-cost testing and staging | RTX 3090 / A5000 | $0.30–0.70/hr |
| Production Burst | Lambda Labs | Cost-optimized production inference | A10G / A100 | $0.60–1.10/hr |
| Enterprise Scale | AWS EC2 (p3/p4d) | High-reliability, reserved capacity | V100 / A100 | $3–12/hr (reserved) |
| Enterprise Scale | Google Cloud (A2) | Multi-region failover | A100 80GB | $2.90–4.50/hr |

---

## 5. Data Architecture

> See [DATABASE.md](DATABASE.md) for the full schema reference.

### 5.1 Core Tables

- `users` — User accounts, subscription tier, GPU credits
- `projects` — Creator workspaces with branching support
- `project_branches` — Branch records linked to projects
- `commits` — Versioned snapshots of project asset manifests
- `assets` — Uploaded files with metadata
- `ai_jobs` — AI inference jobs with status tracking
- `team_members` — Project collaborators with roles
- `comments` — Timestamp-linked threaded comments
- `credit_ledger` — Append-only GPU credit audit log
- `subscriptions` — Stripe subscription records

### 5.2 Caching Strategy

| Cache Layer | Technology | TTL | Data Cached |
|---|---|---|---|
| Session cache | Redis | 24 hours | JWT refresh tokens, user session data |
| API response cache | Redis | 60 seconds | Project list, asset metadata |
| AI result cache | Redis | 7 days | Identical prompt + params hash → output URL |
| CDN cache | Cloudflare | 30 days | Static assets, thumbnails, exported videos |

### 5.3 Object Storage Layout

```
oasis-assets/
├── users/{user_id}/avatars/
├── projects/{project_id}/raw/{asset_id}/
├── projects/{project_id}/ai_outputs/{job_id}/
└── projects/{project_id}/exports/{export_id}/

oasis-models/
├── svd-xt/weights.safetensors
├── xtts-v2/checkpoint.pth
└── musicgen-medium/model.bin
```

---

## 6. Task Queue Architecture

### 6.1 Queue Topology

| Queue Name | Workers | Priority | Job Types |
|---|---|---|---|
| `high_priority` | Dedicated pool | Highest | Voice TTS (fast), subtitle generation |
| `video_generation` | GPU workers | High | Text-to-video, image-to-video |
| `music_generation` | GPU workers | Medium | MusicGen, Riffusion |
| `rendering` | CPU+GPU | Medium | Timeline export, encoding |
| `background` | CPU workers | Low | Thumbnail generation, format conversion |

### 6.2 Job State Machine

```
                  ┌───────────┐
            ┌────▶│ CANCELLED │ (user cancels before worker acquires)
            │     └───────────┘
            │
┌────────┐  │  ┌────────────┐     ┌───────────┐
│ QUEUED │──┴─▶│ PROCESSING │────▶│ COMPLETED │
└────────┘     └─────┬──────┘     └───────────┘
                     │
                     │     ┌────────┐
                     └────▶│ FAILED │ (retry up to 3x on transient errors)
                           └────────┘
```

**State definitions:**

| State | Description | Credits |
|---|---|---|
| `QUEUED` | Job created and waiting in Celery/Redis queue | Reserved (not deducted) |
| `PROCESSING` | Worker has acquired the job and is running inference | Reserved |
| `COMPLETED` | Inference finished, output uploaded to S3 | Deducted atomically |
| `FAILED` | Inference error; error message stored; user can retry | Refunded |
| `CANCELLED` | User cancelled before worker acquired job | Fully refunded |

---

## 7. Security Architecture

### 7.1 Authentication & Authorization

- **JWT access tokens:** 15-minute expiry, signed with RS256
- **Refresh tokens:** Redis-backed, 30-day expiry, opaque tokens
- **OAuth 2.0 with PKCE:** Google and GitHub sign-in
- **RBAC:** Enforced at API Gateway and re-validated in each service
- **Row-level security (RLS):** PostgreSQL RLS to prevent cross-tenant data access

### 7.2 Data Security

- All S3/R2 objects encrypted at rest with **AES-256** (SSE-S3)
- All inter-service communication uses **TLS 1.3** with certificate rotation every 90 days
- User-uploaded content is **virus-scanned** on ingest (ClamAV integration)
- PII (email, billing info) stored encrypted with application-level AES-256 key

### 7.3 Rate Limiting

| Endpoint Category | Free Tier | Pro Tier | Enterprise |
|---|---|---|---|
| API (general) | 100 req/min | 1,000 req/min | Custom |
| AI job submission | 5 jobs/hour | 100 jobs/hour | Unlimited |
| Asset upload | 500 MB/day | 10 GB/day | Custom |
| Export | 2 exports/day | Unlimited | Unlimited |

---

## 8. DevOps & Infrastructure

### 8.1 Containerization & Orchestration

- All services containerized with **Docker** (multi-stage builds for minimal image size)
- **Kubernetes** (EKS or GKE) orchestrates all application-tier pods
- GPU worker nodes use dedicated node pools with **NVIDIA device plugin**
- **Helm charts** manage service deployment configuration per environment

### 8.2 CI/CD Pipeline

| Stage | Tool | Action |
|---|---|---|
| Source control | GitHub | Feature branch → PR → main |
| CI — Test | GitHub Actions | pytest, ESLint, type checking |
| CI — Build | GitHub Actions | Docker build + push to ECR/GCR |
| CD — Staging | ArgoCD | Auto-deploy main to staging on merge |
| CD — Production | ArgoCD | Manual promotion from staging to prod |
| DB Migrations | Alembic | Auto-run on deploy, rollback on failure |

### 8.3 Observability Stack

| Layer | Tool | Metrics Collected |
|---|---|---|
| Infrastructure metrics | Prometheus + Node Exporter | CPU, memory, GPU utilization, network I/O |
| Application metrics | Prometheus + FastAPI middleware | Request latency, error rates, job throughput |
| Dashboards | Grafana | Real-time and historical views per service |
| Log aggregation | ELK (Elasticsearch + Logstash + Kibana) | Structured JSON logs, error alerting |
| Distributed tracing | Jaeger (OpenTelemetry) | Request traces across microservices |
| Alerting | PagerDuty + Grafana Alerts | On-call escalation for SLA breaches |

---

## 9. GPU Cost Optimization Strategies

| Strategy | Description | Savings |
|---|---|---|
| **Batch inference** | Accumulate small TTS jobs (< 5s audio) and process in a single forward pass | Reduced per-job overhead |
| **Model quantization** | INT8 / FP16 quantized models reduce VRAM usage | 30–50% VRAM savings |
| **Result caching** | sha256(model + prompt + params) lookup before inference | ~20% compute saved |
| **Spot/preemptible instances** | Use spot GPUs for non-time-critical batch jobs | 60–80% cost savings |
| **GPU sharing** | CUDA MPS allows multiple workers to share a single GPU | Better utilization |
| **Auto-scale to zero** | Scale worker pools to zero during off-peak hours (00:00–06:00 UTC) | Zero idle cost |
