# Oasis — Product Requirements Document (PRD)

> Version 1.0 | Confidential | 2025

---

## 1. Product Overview

| Field | Value |
|---|---|
| **Product Name** | Oasis |
| **Category** | AI Creator Platform / AI Media Infrastructure |
| **Stage** | Pre-seed / MVP Development |

---

## 2. Problem Statement

Content creators face compounding pain points that reduce productivity and increase cost:

- **Editing tools are fragmented** across multiple paid subscriptions
- **AI generation tools exist on separate platforms** with no native integration
- **Team collaboration on video is clunky**, relying on email chains and Drive links
- **GPU-based AI generation is expensive** and inaccessible without technical expertise
- **Asset and version management is manual**, error-prone, and time-consuming

Creators currently jump between: **Premiere Pro, After Effects, Runway, Descript, and Google Drive** — treating each as a siloed island.

---

## 3. Product Goals

### 3.1 Primary Goal

Create the **central platform for AI-assisted content production** — the single place where a creator goes from idea to published content.

### 3.2 Secondary Goals

- Reduce total content production time by **80%** for solo creators
- Make GPU-powered AI generation accessible **without infrastructure knowledge**
- Enable **real-time and asynchronous collaboration** across content teams
- Provide **scalable GPU rendering** that grows with creator demand

---

## 4. Success Metrics (KPIs)

| Metric | Target (6-month post-launch) | Measurement Method |
|---|---|---|
| Daily Active Creators (DAC) | 10,000 | Auth + session events |
| Projects Created per Week | 50,000 | Project service events |
| AI Jobs Generated per Day | 100,000 | Job queue telemetry |
| Avg AI Render Time (video) | < 60 seconds | Job completion timestamps |
| Avg AI Render Time (audio) | < 10 seconds | Job completion timestamps |
| Subscription Conversion Rate | > 12% | Billing service events |
| GPU Utilization Rate | > 70% | Worker cluster metrics |
| Monthly Churn Rate | < 5% | Billing cancellations |

---

## 5. Target Market

### 5.1 Primary Market

| Segment | Platform | Pain Point | Est. Global Users |
|---|---|---|---|
| YouTubers | YouTube | Long-form editing time | 50M+ |
| Short-form Creators | TikTok / Reels | Speed to publish | 200M+ |
| Podcasters | Spotify / Apple | Transcription + editing | 4M+ |
| AI Content Creators | Multi-platform | GPU access + tooling | Growing rapidly |

### 5.2 Secondary Market

- Media agencies managing multiple creator accounts
- Marketing teams producing video content at scale
- Independent game studios generating cinematic content

---

## 6. User Personas

### Persona 1 — The Solo Creator ("Maya")

| Attribute | Detail |
|---|---|
| **Role** | Full-time YouTuber, 500K subscribers |
| **Goals** | Publish 3 videos/week, grow channel, monetize faster |
| **Frustrations** | Editing takes 8–12 hours per video, voiceovers are expensive, finding royalty-free music is slow |
| **Tech comfort** | Medium — comfortable with Premiere but not command-line tools |
| **Key need** | Fast AI-assisted editing with voice generation and music built in |

### Persona 2 — The Content Team Lead ("James")

| Attribute | Detail |
|---|---|
| **Role** | Creative director at a 12-person video agency |
| **Goals** | Deliver client projects on time, manage editor team, track versions |
| **Frustrations** | Conflicting edits, no version control, file handoffs via WeTransfer |
| **Tech comfort** | High — uses git for web projects, wants same for video |
| **Key need** | GitHub-style project management for video, with roles and comments |

### Persona 3 — The AI Creator ("Zara")

| Attribute | Detail |
|---|---|
| **Role** | Full-stack AI content creator, publishes AI-generated films |
| **Goals** | Generate full videos from text prompts, clone custom voices |
| **Frustrations** | Juggling 5+ AI tools, GPU costs on RunPod are unpredictable |
| **Tech comfort** | Very high — writes Python, understands diffusion models |
| **Key need** | Unified AI generation pipeline with cost-transparent GPU billing |

---

## 7. Core Features

### 7.1 Creator Workspace (Project Repository)

Every creator owns a set of projects structured like GitHub repositories. Each project is a versioned, collaborative workspace.

- Create, rename, archive, and delete projects
- Upload, tag, and organize assets (video, audio, images, scripts)
- Git-style version history with named commits and rollback
- Project branching for experimental edits
- Asset preview without download

### 7.2 AI Video Generation

- **Text-to-video:** generate clips from natural language prompts
- **Image-to-video:** animate static images with motion prompts
- **Style transfer:** apply aesthetic styles to existing footage
- **Duration control:** 4s, 8s, 16s clip generation
- **Resolution options:** 720p, 1080p, 4K (based on plan)

### 7.3 AI Voice Generation

- Text-to-speech with 50+ built-in voice styles
- Voice cloning: upload 30 seconds of audio to clone any voice
- Multilingual support: 20+ languages
- Emotion and pace control: energy, speed, pitch sliders
- Podcast narration mode: long-form TTS with chapter markers

### 7.4 AI Music Generation

- Generate background music from style prompts ("lo-fi chill", "cinematic epic")
- Tempo and key control
- Duration matching: auto-trim to video length
- Stems export: separate melody, drums, bass for custom mixing

### 7.5 AI Subtitles & Transcription

- Auto-transcribe any spoken audio using Whisper
- Auto-timed subtitle blocks synchronized to audio waveform
- Multi-language subtitle generation and translation
- Subtitle style editor (font, color, position, animation)

### 7.6 Browser-Based Video Editor

- Timeline editor with multi-track support (video, audio, subtitle, overlay)
- Clip trimming, splitting, and reordering
- Transition library (fade, cut, wipe, zoom)
- Audio ducking and volume keyframes
- Export to MP4/MOV at configurable quality presets

### 7.7 Collaboration System

- Invite collaborators by email with role-based access
- Four roles: **Owner, Admin, Editor, Viewer**
- Timeline commenting with timestamp-linked threads
- Activity feed showing all project changes
- Real-time presence indicators (who is editing now)

### 7.8 Content Publishing

- Direct publish to YouTube, Instagram, and TikTok via OAuth
- Scheduled publishing with time zone support
- Publish history and analytics summary

---

## 8. User Flows

### Flow 1 — Generate and Publish an AI Video

1. User logs in and opens or creates a project
2. User navigates to the AI Generation panel and enters a video prompt
3. User selects style, duration, and resolution; submits job
4. Job enters GPU queue; user sees real-time progress indicator
5. Completed clip appears in project assets
6. User drags clip to timeline editor
7. User generates AI voiceover and AI background music; adds both to timeline
8. User adds auto-generated subtitles and reviews in preview
9. User exports and schedules publication to YouTube

### Flow 2 — Collaborative Team Edit

1. Owner creates project, uploads raw footage, invites three editors
2. Editors receive email invitations with role assignments
3. Editors open the timeline editor simultaneously; presence indicators show who is active
4. Editor A trims and arranges clips; Editor B adds captions
5. Editor A leaves a timestamp comment on a specific cut
6. Owner reviews comment thread, approves, and commits the version
7. Owner exports final cut and publishes

---

## 9. Functional Requirements

### 9.1 Authentication

- Email + password registration and login
- Google and GitHub OAuth
- Password reset via email
- JWT-based session tokens with refresh
- Multi-factor authentication (TOTP) for Pro and Enterprise plans

### 9.2 Project Management

- CRUD operations on projects
- Branching: create branch from any commit
- Merge: merge branch back to main with conflict detection
- Commit history: view, label, and restore any past state

### 9.3 Asset Management

- Upload: drag-and-drop, chunked upload for files > 100 MB
- Supported formats: MP4, MOV, MKV, MP3, WAV, PNG, JPG, PDF
- Auto-thumbnail generation on upload
- Search and filter by type, tag, date, size

### 9.4 AI Generation

- All AI jobs are asynchronous and queued via a task broker
- Jobs have status: `queued`, `processing`, `completed`, `failed`
- Failed jobs surface error messages and provide retry option
- Each job deducts GPU credits from user's account balance

---

## 10. Non-Functional Requirements

| Category | Requirement | Target |
|---|---|---|
| Performance | AI video generation latency | < 60 seconds (1080p, 8s clip) |
| Performance | AI audio generation latency | < 10 seconds |
| Performance | Asset upload throughput | > 100 MB/s per user |
| Scalability | Concurrent users | 100,000 |
| Scalability | AI jobs per minute | 10,000 |
| Reliability | Platform uptime SLA | 99.9% (< 8.7 hrs downtime/year) |
| Reliability | Data durability (object storage) | 99.999999999% (11 nines) |
| Security | Data encryption at rest | AES-256 |
| Security | Data encryption in transit | TLS 1.3 |
| Security | GDPR / CCPA compliance | Required at launch |

---

## 11. MVP Feature Set

| Feature | Included in MVP | Phase |
|---|---|---|
| User authentication (email + OAuth) | ✅ Yes | MVP |
| Project workspace + asset storage | ✅ Yes | MVP |
| AI voice generation (TTS) | ✅ Yes | MVP |
| AI subtitle generation (Whisper) | ✅ Yes | MVP |
| GPU job queue + credit system | ✅ Yes | MVP |
| Basic asset manager | ✅ Yes | MVP |
| AI video generation | ❌ No | Phase 2 |
| Browser timeline editor | ❌ No | Phase 2 |
| Collaboration + roles | ❌ No | Phase 2 |
| AI music generation | ❌ No | Phase 2 |
| Voice cloning | ❌ No | Phase 3 |
| AI marketplace | ❌ No | Phase 3 |
| Direct social publishing | ❌ No | Phase 3 |

---

## 12. Monetization Model

| Plan | Price | GPU Credits/mo | Storage | Seats | Features |
|---|---|---|---|---|---|
| **Free** | $0 | 50 credits | 5 GB | 1 | Basic TTS, subtitles, 3 projects |
| **Pro** | $29/mo | 500 credits | 100 GB | 1 | All AI models, video generation, exports |
| **Team** | $79/mo | 2,000 credits | 500 GB | 5 | Collaboration, roles, version history |
| **Enterprise** | Custom | Unlimited | Custom | Unlimited | Custom models, SLA, dedicated GPU |

---

## 13. Product Roadmap

| Phase | Timeline | Deliverables |
|---|---|---|
| **Phase 1 — MVP** | Months 1–3 | Auth, project workspace, AI voice (TTS), Whisper subtitles, GPU job queue, basic asset storage |
| **Phase 2 — Core Product** | Months 4–6 | AI video generation, browser timeline editor, AI music generation, collaboration + roles |
| **Phase 3 — Growth** | Months 7–9 | Voice cloning, AI marketplace, direct social publishing, automated editing AI |
| **Phase 4 — Scale** | Months 10–12 | Enterprise tier, custom model training pipeline, advanced analytics, mobile app |

---

## 14. Launch Strategy

### Stage 1 — Closed Beta (Month 3)

- Invite 500 creators from YouTube and TikTok creator communities
- Gather qualitative feedback via in-app surveys and Discord
- Iterate on AI generation quality and editor UX

### Stage 2 — Public Beta (Month 6)

- Open waitlist with referral incentive (extra GPU credits)
- Launch in Product Hunt and creator subreddits
- Press outreach to TechCrunch, The Verge, and creator economy newsletters

### Stage 3 — Global Launch (Month 9)

- Remove waitlist, open free sign-up
- Paid creator sponsorships and affiliate program
- Agency partnership program with white-label options
