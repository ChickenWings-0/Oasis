# Project Service - Architecture Documentation

**Service Name:** Project Service  
**Port:** 8002  
**Technology Stack:** FastAPI, SQLAlchemy 2.0, PostgreSQL/SQLite  
**Latest Updated:** March 29, 2026

---

## Table of Contents

1. [Overview](#overview)
2. [Service Architecture](#service-architecture)
3. [Component Design](#component-design)
4. [Data Models](#data-models)
5. [API Specification](#api-specification)
6. [Database Schema](#database-schema)
7. [Authentication & Authorization](#authentication--authorization)
8. [Request/Response Flow](#requestresponse-flow)
9. [Error Handling](#error-handling)
10. [Performance Considerations](#performance-considerations)
11. [Deployment & Scaling](#deployment--scaling)

---

## Overview

### Purpose
The Project Service provides a Git-like version control backend that enables users to manage projects, branches, commits, and merge requests through RESTful APIs. It acts as a microservice handling all version control operations within the collaborative system.

### Key Responsibilities
- ✓ Project lifecycle management (create, read, update, delete)
- ✓ Branch management with branching strategies
- ✓ Commit tracking with parent/child relationships
- ✓ Merge request workflow and conflict detection
- ✓ User authorization and ownership verification
- ✓ Data persistence and transaction management

### Service Boundaries
```
┌─────────────────────────────────────────────────────────┐
│                 PROJECT SERVICE (8002)                  │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  ┌────────────────────────────────────────────────────┐ │
│  │            REST API Layer (FastAPI)                 │ │
│  │  /api/v1/projects /branches /commits /merges        │ │
│  └────────────────────────────────────────────────────┘ │
│                            │                              │
│  ┌──────────────────────────┴──────────────────────────┐ │
│  │        Business Logic Layer (Services)              │ │
│  │   ProjectService / BranchService / etc.             │ │
│  └──────────────────────────┬──────────────────────────┘ │
│                            │                              │
│  ┌──────────────────────────┴──────────────────────────┐ │
│  │     Data Access Layer (Repositories)                │ │
│  │   ProjectRepo / BranchRepo / CommitRepo / etc.      │ │
│  └──────────────────────────┬──────────────────────────┘ │
│                            │                              │
│  ┌──────────────────────────┴──────────────────────────┐ │
│  │     ORM & Database Layer (SQLAlchemy)               │ │
│  │     PostgreSQL/SQLite with Connection Pooling       │ │
│  └─────────────────────────────────────────────────────┘ │
│                                                           │
└─────────────────────────────────────────────────────────┘
         ↓                                ↑
   Consumes JWT              Verifies ownership
   from User Service          via JWT claims
```

---

## Service Architecture

### Layered Architecture Pattern

The Project Service follows a **4-layer architectural pattern**:

#### 1. API Layer (Routes)
**Location:** `app/routes/`  
**Files:** `project_routes.py`, `branch_routes.py`, `commit_routes.py`, `merge_routes.py`

**Responsibilities:**
- HTTP request/response handling
- Request validation using Pydantic schemas
- JWT token verification (via dependency injection)
- Status code and error response mapping

**Key Components:**
```python
@router.post("/api/v1/projects", response_model=ProjectResponse)
async def create_project(
    project_data: ProjectCreate,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Route receives request, validates, passes to service"""
```

#### 2. Service Layer (Business Logic)
**Location:** `app/services/`  
**Files:** `project_service.py`, `branch_service.py`, `commit_service.py`, `merge_service.py`

**Responsibilities:**
- Authorization checks (ownership verification)
- Business logic orchestration
- Validation rules enforcement
- Transaction management

**Key Patterns:**
- All write operations validate ownership
- Reads are typically public (any authenticated user)
- Services raise domain exceptions (ForbiddenError, NotFoundError, etc.)

#### 3. Repository Layer (Data Access)
**Location:** `app/repositories/`  
**Files:** `project_repo.py`, `branch_repo.py`, `commit_repo.py`, `merge_repo.py`

**Responsibilities:**
- Raw CRUD operations on database
- Query building and execution
- NO business logic - pure data access

**Design Principle:**
```python
# Repository: Pure data access, no business logic
def create_branch(self, branch_data: BranchCreate) -> Branch:
    db_branch = Branch(**branch_data.dict())
    self.db.add(db_branch)
    self.db.commit()
    return db_branch
```

#### 4. Database Layer (ORM & Storage)
**Location:** `app/models/` + `app/database.py`

**Responsibilities:**
- SQLAlchemy ORM models with relationships
- Database configuration and connection pooling
- Transaction handling

---

## Component Design

### Core Components

#### Models
```
Project (root entity)
  ├── Branches (1:N)
  │   ├── Commits (1:N)
  │   └── Merges as source/target (2:N)
  ├── Commits (1:N)
  └── Merges (1:N)
```

#### Services

**ProjectService**
- `create_project(user_id, data)` → ProjectResponse
- `get_project(user_id, project_id)` → ProjectResponse
- `list_user_projects(user_id, skip, limit)` → List[ProjectResponse]
- `update_project(user_id, project_id, data)` → ProjectResponse
- `delete_project(user_id, project_id)` → bool

**BranchService**
- `create_branch(user_id, project_id, name, base_branch_id)` → BranchResponse
- `get_branch(branch_id)` → BranchResponse
- `list_branches(project_id, skip, limit)` → List[BranchResponse]

**CommitService**
- `create_commit(user_id, branch_id, message)` → CommitResponse
- `get_commit(commit_id)` → CommitResponse
- `get_branch_history(branch_id, skip, limit)` → List[CommitResponse]
- `get_commit_parent(commit_id)` → CommitResponse
- `get_commit_children(commit_id)` → List[CommitResponse]

**MergeService**
- `merge_branches(user_id, source_id, target_id)` → MergeResponse
- `get_merge(merge_id)` → MergeResponse
- `get_merge_history(project_id, skip, limit)` → List[MergeResponse]
- `approve_merge(merge_id, user_id)` → MergeResponse

#### Repositories

Each repository handles data access for its entity:
- **ProjectRepository**: project CRUD, filtering by owner
- **BranchRepository**: branch CRUD, HEAD commit updates
- **CommitRepository**: commit creation, graph traversal (parent/child)
- **MergeRepository**: merge CRUD, status tracking

#### Dependencies & Utilities

**Authentication Dependency** (`dependencies/auth_dependency.py`)
- `get_current_user()` → CurrentUser (from JWT or dev header)
- `verify_token(token)` → UserClaims
- `create_access_token(user_id, email)` → str (JWT)

**Exception Classes** (`exceptions.py`)
```python
- AuthError (base)
- UnauthorizedError (401)
- ForbiddenError (403)
- NotFoundError (404)
- ValidationError (400)
```

**Configuration** (`config.py`)
```python
class Settings:
    project_database_url: str
    environment: str
    secret_key: str
    jwt_algorithm: str = "HS256"
```

---

## Data Models

### Project Model
```python
class Project(Base):
    __tablename__ = "projects"
    
    id: int (PK)
    name: str (indexed, unique per owner)
    description: str (optional)
    owner_id: int (from User Service)
    created_at: datetime
    
    # Relationships
    branches: List[Branch] (cascade delete)
    commits: List[Commit] (cascade delete)
    merges: List[Merge] (cascade delete)
```

**Key Properties:**
- Owner-scoped: All operations verified against owner_id
- Cascading: Deleting project deletes all branches/commits/merges
- UUID: No GUID, using sequence integer IDs with owner partitioning

### Branch Model
```python
class Branch(Base):
    __tablename__ = "branches"
    
    id: int (PK)
    name: str (unique per project)
    project_id: int (FK→Project, cascade delete)
    created_from: int (FK→Branch, self-reference, nullable)
    head_commit_id: str (FK→Commit, nullable)
    created_at: datetime
    
    # Relationships
    project: Project
    commits: List[Commit]
    parent_branch: Branch (optional)
    child_branches: List[Branch]
    source_merges: List[Merge]
    target_merges: List[Merge]
```

**Key Properties:**
- **head_commit_id**: Points to the current HEAD commit (Git equivalent)
- **created_from**: Parent branch for lineage tracking
- **self-referencing**: Enables branch hierarchy visualization

### Commit Model
```python
class Commit(Base):
    __tablename__ = "commits"
    
    id: str (PK, 64-char hash from SHA-256)
    message: str (immutable commit message)
    branch_id: int (FK→Branch, cascade delete)
    parent_commit_id: str (FK→Commit, nullable)
    author_id: int (from User Service)
    timestamp: datetime
    
    # Relationships
    branch: Branch
    parent_commit: Commit (nullable)
    child_commits: List[Commit]
```

**Key Properties:**
- **Immutable**: Once created, commit cannot be changed (Git principle)
- **Hash ID**: Generated from message + metadata, ensuring uniqueness
- **Commit Graph**: parent_id enables traversal of commit history
- **Author from User Service**: Links to authenticated users

### Merge Model
```python
class Merge(Base):
    __tablename__ = "merges"
    
    id: int (PK)
    source_branch_id: int (FK→Branch)
    target_branch_id: int (FK→Branch)
    merge_commit_id: str (FK→Commit, nullable)
    status: Enum (PENDING | MERGED | CONFLICT)
    created_at: datetime
    merged_at: datetime (nullable)
    
    # Relationships
    source_branch: Branch
    target_branch: Branch
    merge_commit: Commit (optional)
```

**Key Properties:**
- **Status Tracking**: PENDING → approval → MERGED
- **Merge Commit**: Optional, records the merge operation
- **Immutable History**: Merge records never deleted (audit trail)

---

## API Specification

### Base URL
```
http://localhost:8002
```

### Authentication
All endpoints (except `/health`) require:
```
Authorization: Bearer {jwt_token}
```

Fallback for development:
```
X-User-ID: {user_id}
```

### Endpoints Overview

#### Projects
| Method | Endpoint | Auth | Purpose |
|--------|----------|------|---------|
| POST | /api/v1/projects | Required | Create project |
| GET | /api/v1/projects | Required | List user's projects |
| GET | /api/v1/projects/{id} | Required | Get project details |
| PATCH | /api/v1/projects/{id} | Required | Update project |
| DELETE | /api/v1/projects/{id} | Required | Delete project |

#### Branches
| Method | Endpoint | Auth | Purpose |
|--------|----------|------|---------|
| POST | /api/v1/branches | Required | Create branch |
| GET | /api/v1/branches/{id} | Required | Get branch |
| GET | /api/v1/branches/project/{project_id} | Required | List branches |

#### Commits
| Method | Endpoint | Auth | Purpose |
|--------|----------|------|---------|
| POST | /api/v1/commits | Required | Create commit |
| GET | /api/v1/commits/{id} | Required | Get commit |
| GET | /api/v1/commits/branch/{branch_id}/history | Required | Get branch history |

#### Merges
| Method | Endpoint | Auth | Purpose |
|--------|----------|------|---------|
| POST | /api/v1/merges | Required | Create merge request |
| GET | /api/v1/merges/{id} | Required | Get merge |
| GET | /api/v1/merges/project/{project_id}/history | Required | Get merge history |
| POST | /api/v1/merges/{id}/approve | Required | Approve merge |

#### Health
| Method | Endpoint | Auth | Purpose |
|--------|----------|------|---------|
| GET | /health | None | Service health check |

### Request/Response Examples

#### Create Project
```
POST /api/v1/projects
Authorization: Bearer {token}

{
  "name": "my-project",
  "description": "Optional project description"
}

Response (201):
{
  "id": 1,
  "name": "my-project",
  "description": "...",
  "owner_id": 123,
  "created_at": "2026-03-29T10:00:00Z"
}
```

#### Create Commit
```
POST /api/v1/commits
Authorization: Bearer {token}

{
  "message": "Initial commit",
  "branch_id": 1
}

Response (201):
{
  "id": "abc123def456...",
  "message": "Initial commit",
  "branch_id": 1,
  "parent_commit_id": null,
  "author_id": 123,
  "timestamp": "2026-03-29T10:05:00Z"
}
```

#### Approve Merge
```
POST /api/v1/merges/1/approve
Authorization: Bearer {token}

Response (200):
{
  "id": 1,
  "source_branch_id": 2,
  "target_branch_id": 1,
  "status": "merged",
  "created_at": "2026-03-29T09:00:00Z",
  "merged_at": "2026-03-29T10:30:00Z"
}
```

---

## Database Schema

### Table: projects
```sql
CREATE TABLE projects (
    id SERIAL PRIMARY KEY,
    owner_id INTEGER NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(owner_id, name)
);

CREATE INDEX idx_projects_owner_id ON projects(owner_id);
```

### Table: branches
```sql
CREATE TABLE branches (
    id SERIAL PRIMARY KEY,
    project_id INTEGER NOT NULL,
    name VARCHAR(255) NOT NULL,
    created_from INTEGER,
    head_commit_id VARCHAR(64),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    FOREIGN KEY (created_from) REFERENCES branches(id) ON DELETE SET NULL,
    UNIQUE(project_id, name)
);

CREATE INDEX idx_branches_project_id ON branches(project_id);
```

### Table: commits
```sql
CREATE TABLE commits (
    id VARCHAR(64) PRIMARY KEY,
    message TEXT NOT NULL,
    branch_id INTEGER NOT NULL,
    parent_commit_id VARCHAR(64),
    author_id INTEGER NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (branch_id) REFERENCES branches(id) ON DELETE CASCADE,
    FOREIGN KEY (parent_commit_id) REFERENCES commits(id) ON DELETE SET NULL
);

CREATE INDEX idx_commits_branch_id ON commits(branch_id);
CREATE INDEX idx_commits_author_id ON commits(author_id);
```

### Table: merges
```sql
CREATE TABLE merges (
    id SERIAL PRIMARY KEY,
    source_branch_id INTEGER NOT NULL,
    target_branch_id INTEGER NOT NULL,
    merge_commit_id VARCHAR(64),
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    merged_at TIMESTAMP,
    FOREIGN KEY (source_branch_id) REFERENCES branches(id) ON DELETE CASCADE,
    FOREIGN KEY (target_branch_id) REFERENCES branches(id) ON DELETE CASCADE,
    FOREIGN KEY (merge_commit_id) REFERENCES commits(id) ON DELETE SET NULL
);

CREATE INDEX idx_merges_source_branch_id ON merges(source_branch_id);
CREATE INDEX idx_merges_target_branch_id ON merges(target_branch_id);
CREATE INDEX idx_merges_status ON merges(status);
```

---

## Authentication & Authorization

### Authentication Flow
```
1. User obtains JWT from User Service
2. Request includes: Authorization: Bearer {jwt_token}
3. Project Service validates JWT signature
4. JWT decoded to extract user_id (subject)
5. Request processed with user context
```

### Authorization Rules
```
┌─────────────────────────────────────────────────────────┐
│             AUTHORIZATION DECISION MATRIX               │
├──────────────────────────────┬──────────┬────────────────┤
│ Operation                    │ Requires │ Additional     │
├──────────────────────────────┼──────────┼────────────────┤
│ Create Project               │ Auth     │ -              │
│ Read Project                 │ Auth     │ Owner only     │
│ Update Project               │ Auth     │ Owner only     │
│ Delete Project               │ Auth     │ Owner only     │
│ Create Branch                │ Auth     │ Own project    │
│ Read Branch                  │ Auth     │ -              │
│ Create Commit                │ Auth     │ Own project    │
│ Read Commit                  │ Auth     │ -              │
│ Create Merge                 │ Auth     │ Own project    │
│ Approve Merge                │ Auth     │ Own project    │
│ Health Check                 │ None     │ -              │
└──────────────────────────────┴──────────┴────────────────┘
```

### JWT Token Structure
```
Header:
{
  "alg": "HS256",
  "typ": "JWT"
}

Payload:
{
  "user_id": 123,
  "email": "user@example.com",
  "iat": 1711785600,
  "exp": 1711872000
}

Signature:
HMACSHA256(base64UrlEncode(header) + "." + base64UrlEncode(payload), secret_key)
```

**Verification:**
- Algorithm: HS256
- Secret Key: Shared with User Service
- Signature: Verified on every request
- Expiration: 24 hours (refreshed by User Service)

---

## Request/Response Flow

### Complete Project Creation Flow

```
┌──────────────────┐
│  Client (UI)     │
│  POST /projects  │
└────────┬─────────┘
         │
         ▼
┌──────────────────────────────────────────┐
│  API Layer (project_routes.py)           │
│  - Validate ProjectCreate schema         │
│  - Extract CurrentUser from JWT          │
│  - Call ProjectService.create_project()  │
└────────┬─────────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────────┐
│  Service Layer (project_service.py)      │
│  - Check authentication                  │
│  - Set owner_id = current_user.user_id   │
│  - Call ProjectRepository.create()       │
│  - Trigger BranchService.create_main()   │
└────────┬─────────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────────┐
│  Repository Layer (project_repo.py)      │
│  - Build Project ORM object              │
│  - db.add() and db.commit()              │
│  - Return persisted Project              │
└────────┬─────────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────────┐
│  Database Layer (PostgreSQL)             │
│  - Insert into projects table            │
│  - Return with auto-generated ID         │
└────────┬─────────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────────┐
│  Response to Client                      │
│  {id: 1, name: "...", owner_id: 123}    │
└──────────────────────────────────────────┘
```

### Commit Creation with HEAD Update

```
1. Create Commit in CommitService
   - Generate commit hash (SHA-256)
   - Set parent_commit_id = branch.head_commit_id
   - Create commit in repository

2. Update Branch HEAD ⭐
   - Call BranchRepository.update_branch_head_commit()
   - Set branch.head_commit_id = new_commit.id
   - db.commit() (persist change)

3. Return updated commit to client
```

---

## Error Handling

### HTTP Status Codes
```
200 OK            - Successful GET/PATCH
201 Created       - Successful POST
204 No Content    - Successful DELETE
400 Bad Request   - Validation error, invalid data
401 Unauthorized  - Missing/invalid JWT token
403 Forbidden     - No permission for operation
404 Not Found     - Resource doesn't exist
409 Conflict      - Merge conflict, duplicate name
500 Internal Error - Server error
```

### Error Response Format
```json
{
  "error": "validation_error",
  "message": "Branch name must be <= 255 characters",
  "detail": "Provided name: 'very_long_branch_name...'"
}
```

### Common Error Scenarios
```
ValidationError (400)
└─ Message invalid or empty
└─ Branch name already exists
└─ Source/target branches are the same

ForbiddenError (403)
└─ User doesn't own the project
└─ Project owner mismatch

NotFoundError (404)
└─ Project not found
└─ Branch doesn't exist
└─ Commit not in history

ConflictError (409)
└─ Branches diverged (merge conflict)
```

---

## Performance Considerations

### Query Optimization
```
Strategy: Heavy use of database indexing

Indices:
├── projects(owner_id)           [Filter user projects]
├── branches(project_id)         [Find branches in project]
├── commits(branch_id)           [Get commit history]
├── commits(author_id)           [Find user's commits]
├── merges(source_branch_id)     [Find source merges]
├── merges(target_branch_id)     [Find target merges]
└── merges(status)               [Find pending merges]
```

### Connection Pooling
```python
# Development
poolclass=NullPool  # Simplicity, one connection per request

# Production
poolclass=QueuePool
pool_size=10        # Min connections
max_overflow=20     # Extra connections under load
pool_recycle=3600   # Refresh connections hourly
```

### Pagination Strategy
```
Default limits:
- List operations: 100 items
- Offset/limit pattern for scrolling
- Cursor-based pagination for large datasets (future)

Example:
GET /api/v1/commits/branch/1/history?skip=0&limit=50
```

### Caching Opportunities (Future)
```
Redis Cache Layer:
├── Branch details (5 min TTL)
├── Commit history (10 min TTL)
└── Project metadata (15 min TTL)
```

### Performance Targets
```
├── Create project        50ms  (target) | 100ms (max)
├── Get project           30ms  (target) | 50ms (max)
├── List projects (100)   100ms (target) | 200ms (max)
├── Create branch         40ms  (target) | 100ms (max)
├── Create commit         50ms  (target) | 120ms (max)
└── Approve merge         80ms  (target) | 180ms (max)
```

---

## Deployment & Scaling

### Environment Configuration

#### Development
```
DATABASE_URL=sqlite:///./project.db
ENVIRONMENT=development
SECRET_KEY=dev-key-change-in-production
POOL_CLASS=NullPool
```

#### Production
```
DATABASE_URL=postgresql://user:pass@prod-db:5432/project_db
ENVIRONMENT=production
SECRET_KEY=<strong-secret-from-env>
POOL_CLASS=QueuePool
POOL_SIZE=10
MAX_OVERFLOW=20
```

### Docker Deployment
```dockerfile
FROM python:3.10
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "backend.project_service.app.main:app", "--host", "0.0.0.0", "--port", "8002"]
```

### Kubernetes Deployment
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: project-service
spec:
  replicas: 3
  template:
    spec:
      containers:
      - name: project-service
        image: project-service:latest
        ports:
        - containerPort: 8002
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: app-secrets
              key: project-db-url
        livenessProbe:
          httpGet:
            path: /health
            port: 8002
```

### Load Balancing
```
                    ┌─────────────────┐
                    │  Load Balancer  │
                    └────────┬────────┘
                             │
           ┌─────────────────┼─────────────────┐
           ▼                 ▼                 ▼
      ┌─────────┐       ┌─────────┐       ┌─────────┐
      │Instance │       │Instance │       │Instance │
      │   #1    │       │   #2    │       │   #3    │
      │ 8002    │       │ 8002    │       │ 8002    │
      └────┬────┘       └────┬────┘       └────┬────┘
           │                 │                 │
           └─────┬───────────┴───────────┬─────┘
                 │    PostgreSQL DB      │
                 │  (Shared Database)    │
                 └───────────────────────┘
```

### Monitoring & Observability
```
Metrics to track:
├── Request latency (p50, p95, p99)
├── Database query time
├── Connection pool usage
├── Error rates by endpoint
├── JWT validation failures
├── Authentication latency
└── Service health check frequency
```

---

## Integration Points

### With User Service
```
┌──────────────────────┐
│  User Service (8001) │
│  Authentication      │
└────────┬─────────────┘
         │ Issues JWT with user_id
         ▼
┌──────────────────────┐
│ Project Service      │
│ Validates JWT        │
│ Extracts user_id     │
│ Authorizes ops       │
└──────────────────────┘
```

**Flow:**
1. User authenticates with User Service (get JWT)
2. Client includes JWT when calling Project Service
3. Project Service validates JWT signature
4. Project Service extracts user_id from JWT payload
5. All operations scoped to user_id

### With Frontend
```
┌──────────────────────┐
│  Frontend (Browser)  │
│  test-frontend.html  │
└────────┬─────────────┘
         │ REST API calls with Bearer token
         ▼
┌──────────────────────┐
│ Project Service      │
│ /api/v1/...          │
└──────────────────────┘
```

---

## Directory Structure

```
backend/project_service/
├── __init__.py
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app initialization
│   ├── config.py               # Settings & configuration
│   ├── database.py             # SQLAlchemy setup, session factory
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── project_model.py    # Project entity
│   │   ├── branch_model.py     # Branch entity
│   │   ├── commit_model.py     # Commit entity
│   │   └── merge_model.py      # Merge entity
│   │
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── project_schema.py   # Pydantic schemas
│   │   ├── branch_schema.py
│   │   ├── commit_schema.py
│   │   └── merge_schema.py
│   │
│   ├── repositories/
│   │   ├── __init__.py
│   │   ├── project_repo.py     # Data access layer
│   │   ├── branch_repo.py
│   │   ├── commit_repo.py
│   │   └── merge_repo.py
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── project_service.py  # Business logic
│   │   ├── branch_service.py
│   │   ├── commit_service.py
│   │   └── merge_service.py
│   │
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── project_routes.py   # API endpoints
│   │   ├── branch_routes.py
│   │   ├── commit_routes.py
│   │   └── merge_routes.py
│   │
│   ├── dependencies/
│   │   ├── __init__.py
│   │   └── auth_dependency.py  # JWT verification
│   │
│   └── exceptions.py           # Domain exceptions
│
└── requirements.txt
```

---

## Future Enhancements

### Phase 2
- [ ] Commit diffs and change tracking
- [ ] Branch protection rules
- [ ] Code review comments on commits
- [ ] Webhook notifications on merge
- [ ] Conflict resolution workflow

### Phase 3
- [ ] GraphQL API support
- [ ] Real-time WebSocket updates
- [ ] Audit logging for all operations
- [ ] Tags/releases system
- [ ] Cherry-pick operations

---

**Last Updated:** March 29, 2026  
**Architecture Version:** 1.0  
**Review Schedule:** Quarterly
