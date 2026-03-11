# 🎬 Oasis — AI-Powered Collaborative Content Creation Platform

> The operating system for content creation. From prompt to published — without leaving the platform.

[![License](https://img.shields.io/badge/license-Proprietary-red.svg)]()
[![Stage](https://img.shields.io/badge/stage-Pre--seed%20%2F%20MVP-blue.svg)]()
[![Version](https://img.shields.io/badge/version-1.0-green.svg)]()

---

## Table of Contents

- [Overview](#overview)
- [The Problem](#the-problem)
- [The Solution](#the-solution)
- [Key Features](#key-features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Architecture Overview](#architecture-overview)
- [Documentation](#documentation)
- [MVP Scope](#mvp-scope)
- [Roadmap](#roadmap)
- [Monetization](#monetization)
- [Contributing](#contributing)
- [License](#license)

---

## Overview

**Oasis** is a GPU-powered, collaborative AI platform that merges GitHub-style version control, AI-driven media generation (video, voice, music), cloud GPU infrastructure, and direct social publishing into a single unified workspace.

**Mission:** Eliminate tool fragmentation for content creators by delivering every stage of the content production pipeline — generation, editing, collaboration, and publishing — on one intelligent platform.

---

## The Problem

Modern content creators operate across **5+ disconnected tools**: video editing suites, AI generation apps, cloud storage, collaboration platforms, and publishing schedulers. This fragmentation costs creators an estimated **60–70% of their production time** in context-switching, file management, and manual handoffs.

Creators currently jump between: Premiere Pro, After Effects, Runway, Descript, and Google Drive — treating each as a siloed island.

---

## The Solution

Oasis unifies the entire workflow into a single GPU-native platform with AI at its core.

| Capability | Legacy Workflow | Oasis |
|---|---|---|
| Video Generation | Runway / Gen-2 (separate app) | Built-in diffusion pipeline |
| Voice & Narration | Descript / ElevenLabs | Integrated XTTS + voice cloning |
| Music | Artlist / Epidemic Sound | MusicGen + Riffusion on-demand |
| Version Control | Google Drive folders | Git-style commit history |
| Collaboration | Frame.io / Slack | Native timeline comments + roles |
| Publishing | Native platform apps | Direct API publish + scheduling |

---

## Key Features

### 🎥 AI Video Generation
- Text-to-video and image-to-video generation
- Style transfer, duration control (4s/8s/16s), resolution options (720p–4K)

### 🎙️ AI Voice Generation
- Text-to-speech with 50+ voice styles
- Voice cloning from 30 seconds of audio
- Multilingual support (20+ languages), emotion/pace control

### 🎵 AI Music Generation
- Generate background music from style prompts
- Tempo/key control, duration matching, stems export

### 📝 AI Subtitles & Transcription
- Whisper-powered auto-transcription
- Multi-language subtitle generation and translation
- Subtitle style editor

### ✂️ Browser-Based Video Editor
- Multi-track timeline editor (video, audio, subtitle, overlay)
- Trimming, splitting, transitions, audio ducking
- Export to MP4/MOV

### 👥 Collaboration System
- Role-based access: Owner, Admin, Editor, Viewer
- Timeline commenting with timestamp-linked threads
- Real-time presence indicators

### 📤 Content Publishing
- Direct publish to YouTube, Instagram, TikTok via OAuth
- Scheduled publishing with time zone support

### 📁 Creator Workspace (Project Repository)
- Git-style version history with named commits and rollback
- Project branching for experimental edits
- Asset organization with tags and preview

---

## Tech Stack

### Frontend
| Component | Technology |
|---|---|
| Framework | Next.js 14 (App Router) |
| UI Library | React 18 |
| Styling | Tailwind CSS + shadcn/ui |
| 3D / Visual FX | Three.js |
| Video Rendering | FFmpeg WASM + WebGL Canvas |
| State Management | Zustand + React Query |
| Real-time | Socket.IO (WebSocket) |
| Auth | NextAuth.js |

### Backend (8 Microservices — Python / FastAPI)
| Service | Port | Responsibility |
|---|---|---|
| User Service | 8001 | Registration, login, profile, OAuth, JWT |
| Project Service | 8002 | CRUD projects, branching, commit history, merge |
| Asset Service | 8003 | Upload pipeline, chunked transfer, thumbnails |
| AI Job Service | 8004 | Submit jobs, poll status, credits, retry |
| Rendering Service | 8005 | Timeline export, video encoding, watermarking |
| Collaboration Service | 8006 | Invitations, roles, comments, presence |
| Billing Service | 8007 | Subscriptions, credit ledger, Stripe webhooks |
| Notification Service | 8008 | Email (SendGrid), in-app push, webhooks |

### Infrastructure
| Layer | Technology |
|---|---|
| Database | PostgreSQL |
| Cache | Redis |
| Message Queue | Celery + Redis, Kafka |
| Object Storage | AWS S3 / Cloudflare R2 |
| Container Orchestration | Kubernetes (EKS/GKE) |
| CI/CD | GitHub Actions + ArgoCD |
| CDN | Cloudflare |
| API Gateway | Kong / AWS API Gateway |
| Monitoring | Prometheus + Grafana + ELK + Jaeger |

### AI / GPU Stack
| Domain | Primary Model | Framework |
|---|---|---|
| Text-to-Video | Stable Video Diffusion (SVD-XT) | PyTorch / Diffusers |
| Image-to-Video | SVD img2vid | PyTorch / Diffusers |
| Text-to-Speech | XTTS v2 (Coqui) | PyTorch |
| Voice Cloning | XTTS v2 fine-tuned | PyTorch |
| Music Generation | MusicGen (Meta) | PyTorch / HuggingFace |
| Speech Recognition | Whisper large-v3 | OpenAI Whisper / faster-whisper |
| Auto Editing | Video segmentation CNN | PyTorch / OpenCV |

---

## Project Structure

```
oasis/
├── README.md                          # This file
├── docs/                              # All project documentation
│   ├── PRD.md                         # Product Requirements Document
│   ├── ARCHITECTURE.md                # System Architecture Document
│   ├── TRD.md                         # Technical Requirements Documents
│   ├── SETUP.md                       # Developer Setup Guide
│   ├── DATABASE.md                    # Database Schema Reference
│   ├── API.md                         # API Reference
│   ├── TASKS.md                       # Implementation Task Breakdown
│   ├── GLOSSARY.md                    # Glossary of Terms
│   └── CONTRIBUTING.md                # Contributing Guide
├── frontend/                          # Next.js 14 web application
│   ├── app/
│   │   ├── (auth)/                    # Login, Register, Reset Password
│   │   ├── dashboard/                 # Project list, activity feed
│   │   ├── project/[id]/             # Workspace, assets, versions
│   │   ├── editor/[id]/             # WebGL timeline editor
│   │   ├── generate/                  # AI prompt panel
│   │   ├── assets/                    # Asset manager and search
│   │   ├── billing/                   # Plan management, credit balance
│   │   └── settings/                  # Profile, API keys, integrations
│   ├── components/
│   ├── lib/
│   ├── hooks/
│   └── public/
├── backend/                           # FastAPI microservices
│   ├── user-service/                  # Port 8001
│   ├── project-service/               # Port 8002
│   ├── asset-service/                 # Port 8003
│   ├── ai-job-service/                # Port 8004
│   ├── rendering-service/             # Port 8005
│   ├── collaboration-service/         # Port 8006
│   ├── billing-service/               # Port 8007
│   ├── notification-service/          # Port 8008
│   └── shared/                        # Shared utilities, models, config
├── gpu-workers/                       # AI model inference workers
│   ├── video/                         # SVD, AnimateDiff workers
│   ├── voice/                         # XTTS, voice cloning workers
│   ├── music/                         # MusicGen, Riffusion workers
│   ├── transcription/                 # Whisper workers
│   └── Dockerfile.gpu                 # GPU worker container image
├── infra/                             # Infrastructure as Code
│   ├── kubernetes/                    # K8s manifests & Helm charts
│   ├── docker/                        # Docker Compose for local dev
│   ├── terraform/                     # Cloud infrastructure provisioning
│   └── ci-cd/                         # GitHub Actions workflows
├── migrations/                        # Alembic database migrations
├── docker-compose.yml                 # Local development environment
├── .env.example                       # Environment variable template
└── Makefile                           # Common development commands
```

---

## Getting Started

> See [docs/SETUP.md](docs/SETUP.md) for the full developer setup guide.

### Prerequisites
- **Python 3.11+**
- **Node.js 18+** and **pnpm**
- **Docker** and **Docker Compose**
- **PostgreSQL 15+**
- **Redis 7+**
- **NVIDIA GPU** (optional, for local AI inference)

### Quick Start
```bash
# 1. Clone the repository
git clone https://github.com/your-org/oasis.git
cd oasis

# 2. Copy environment variables
cp .env.example .env

# 3. Start all services with Docker Compose
docker-compose up -d

# 4. Run database migrations
cd backend && alembic upgrade head

# 5. Start the frontend
cd frontend && pnpm install && pnpm dev

# 6. Open http://localhost:3000
```

---

## Architecture Overview

Oasis uses a **cloud-native, microservices-based architecture** with a distributed GPU worker cluster.

```
┌─────────────────────────────────────────────────────────────────┐
│                        CLIENT TIER                              │
│                   Next.js 14 Web App                            │
│          (React 18 + Tailwind + Socket.IO)                      │
└───────────────────────┬─────────────────────────────────────────┘
                        │
┌───────────────────────▼─────────────────────────────────────────┐
│                     EDGE TIER                                    │
│              Cloudflare CDN + WAF                                │
└───────────────────────┬─────────────────────────────────────────┘
                        │
┌───────────────────────▼─────────────────────────────────────────┐
│                  API GATEWAY TIER                                 │
│           Kong / AWS API Gateway                                 │
│    (JWT validation, rate limiting, routing)                       │
└───────────────────────┬─────────────────────────────────────────┘
                        │
┌───────────────────────▼─────────────────────────────────────────┐
│                APPLICATION TIER                                   │
│         8 FastAPI Microservices                                   │
│  (User, Project, Asset, AI Job, Rendering,                       │
│   Collaboration, Billing, Notification)                          │
└──────────┬──────────────────────────┬───────────────────────────┘
           │                          │
┌──────────▼──────────┐   ┌──────────▼───────────────────────────┐
│   MESSAGING TIER    │   │         GPU WORKER TIER               │
│ Redis + Celery +    │   │  PyTorch workers on GPU VMs           │
│ Kafka               │   │  (Video, Voice, Music, Whisper)       │
└─────────────────────┘   └──────────────────────────────────────┘
           │
┌──────────▼──────────────────────────────────────────────────────┐
│                    STORAGE TIER                                   │
│     PostgreSQL  |  Redis Cache  |  S3/R2 Object Storage          │
└─────────────────────────────────────────────────────────────────┘
           │
┌──────────▼──────────────────────────────────────────────────────┐
│                 OBSERVABILITY TIER                                │
│     Prometheus  |  Grafana  |  ELK  |  Jaeger                    │
└─────────────────────────────────────────────────────────────────┘
```

> See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for the full system architecture document.

---

## Documentation

| Document | Description |
|---|---|
| [README.md](README.md) | Project overview (this file) |
| [docs/PRD.md](docs/PRD.md) | Product Requirements Document — goals, personas, features, KPIs |
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | System Architecture — frontend, backend, GPU, data, DevOps |
| [docs/TRD.md](docs/TRD.md) | Technical Requirements Documents — per-module specs |
| [docs/SETUP.md](docs/SETUP.md) | Developer Setup Guide — environment, tools, running locally |
| [docs/DATABASE.md](docs/DATABASE.md) | Database Schema Reference — tables, relationships, caching |
| [docs/API.md](docs/API.md) | API Reference — endpoints, request/response formats |
| [docs/TASKS.md](docs/TASKS.md) | Implementation Task Breakdown — all dev tasks by phase |
| [docs/GLOSSARY.md](docs/GLOSSARY.md) | Glossary of key terms and concepts |
| [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md) | Contributing guide — workflow, standards, PR process |

---

## MVP Scope (Phase 1 — Months 1–3)

| Feature | Included |
|---|---|
| User authentication (email + OAuth) | ✅ Yes |
| Project workspace + asset storage | ✅ Yes |
| AI voice generation (TTS) | ✅ Yes |
| AI subtitle generation (Whisper) | ✅ Yes |
| GPU job queue + credit system | ✅ Yes |
| Basic asset manager | ✅ Yes |
| AI video generation | ❌ Phase 2 |
| Browser timeline editor | ❌ Phase 2 |
| Collaboration + roles | ❌ Phase 2 |
| AI music generation | ❌ Phase 2 |

---

## Roadmap

| Phase | Timeline | Deliverables |
|---|---|---|
| **Phase 1 — MVP** | Months 1–3 | Auth, project workspace, AI voice (TTS), Whisper subtitles, GPU job queue, basic asset storage |
| **Phase 2 — Core Product** | Months 4–6 | AI video generation, browser timeline editor, AI music generation, collaboration + roles |
| **Phase 3 — Growth** | Months 7–9 | Voice cloning, AI marketplace, direct social publishing, automated editing AI |
| **Phase 4 — Scale** | Months 10–12 | Enterprise tier, custom model training pipeline, advanced analytics, mobile app |

---

## Monetization

| Plan | Price | GPU Credits/mo | Storage | Seats |
|---|---|---|---|---|
| **Free** | $0 | 50 credits | 5 GB | 1 |
| **Pro** | $29/mo | 500 credits | 100 GB | 1 |
| **Team** | $79/mo | 2,000 credits | 500 GB | 5 |
| **Enterprise** | Custom | Unlimited | Custom | Unlimited |

---

## Success Metrics (KPIs)

| Metric | Target (6-month post-launch) |
|---|---|
| Daily Active Creators (DAC) | 10,000 |
| Projects Created per Week | 50,000 |
| AI Jobs Generated per Day | 100,000 |
| Avg AI Render Time (video) | < 60 seconds |
| Avg AI Render Time (audio) | < 10 seconds |
| Subscription Conversion Rate | > 12% |
| GPU Utilization Rate | > 70% |
| Monthly Churn Rate | < 5% |

---

## Contributing

See [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md) for details on our development workflow, coding standards, and pull request process.

---

## License

This project is **proprietary and confidential**. All rights reserved.

---

*Oasis — Version 1.0 | Confidential | 2025*
