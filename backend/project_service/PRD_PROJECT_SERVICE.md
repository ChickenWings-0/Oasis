# Product Requirements Document: Project Service

**Document Version:** 1.0  
**Last Updated:** March 24, 2026  
**Service Name:** Project Service  
**Service Port:** 8002  
**Technology Stack:** FastAPI, SQLAlchemy

---

## 1. Executive Summary

The Project Service is a Git-like version control backend that enables users to manage projects, branches, commits, and merge requests. It provides RESTful APIs for creating and managing version-controlled projects with support for branching strategies, commit lineage tracking, and merge conflict resolution.

**Core Purpose:** Enable collaborative version control with project ownership, branch management, commit history, and merge operations.

---

## 2. Product Overview

### 2.1 Vision

Provide a lightweight, accessible version control system that brings Git-like functionality to web applications without requiring local Git installation. Users can manage projects, create branches, track commits, and merge branches through simple HTTP APIs.

### 2.2 Target Users

- Developers building collaborative editing systems
- Applications requiring version control features
- Teams managing document or code versions
- Educational platforms teaching version control concepts

### 2.3 Key Success Metrics

- API response time < 200ms for typical operations
- Support for projects with 100+ branches and 1000+ commits
- Zero data loss during merge operations
- 99.9% uptime for core endpoints

---

## 3. Core Features

### 3.1 Project Management

**Feature:** Create, read, update, and delete projects

**Capabilities:**
- Users create projects (auto-generates 'main' branch)
- Projects are scoped to user ownership
- Each project maintains metadata (name, description, created_at)
- Automatic cleanup of related branches, commits, merges on deletion

**Acceptance Criteria:**
- ✓ Only project owner can read/update/delete their projects
- ✓ 'main' branch created automatically on project creation
- ✓ Project names must be unique per user
- ✓ Cascading delete removes all related data

### 3.2 Branch Management

**Feature:** Create and manage branches as isolated development lines

**Capabilities:**
- Create branches from any existing branch (including 'main')
- List branches in a project
- Each branch maintains a HEAD pointer (current commit)
- Branch history tracking with creation metadata
- Parent branch reference for lineage

**Acceptance Criteria:**
- ✓ Branches must have unique names within a project
- ✓ Creating a branch requires valid parent branch
- ✓ Can create from any branch, not just 'main'
- ✓ List branches returns full metadata (id, name, created_at)

### 3.3 Commit Management

**Feature:** Track code changes as commits with parent references

**Capabilities:**
- Create commits on any branch
- Commits form an immutable chain via parent references
- SHA-like hash generation for commit identification
- Commit metadata (message, timestamp, author_id)
- View commit history per branch

**Acceptance Criteria:**
- ✓ Commits cannot be modified after creation (immutable)
- ✓ Commit hash is unique per project
- ✓ Parent commit must exist or be null (initial commit)
- ✓ Branch HEAD updates to latest commit on creation

### 3.4 Merge Management

**Feature:** Merge branches and track merge history

**Capabilities:**
- Create merge requests between branches
- Track merge status (PENDING, MERGED, CONFLICT)
- Merge approval workflow
- Merge history queryable per project
- Automatic conflict detection

**Acceptance Criteria:**
- ✓ Source and target branches must differ
- ✓ Merges require explicit approval
- ✓ Merge operations are transactional
- ✓ Merge history is immutable
- ✓ Conflict status prevents auto-merge

---

## 4. API Specifications

### 4.1 Projects Endpoints

#### CREATE PROJECT
```
POST /api/v1/projects
Authorization: Bearer {jwt_token}
Content-Type: application/json

Request Body:
{
  "name": "my-project",
  "description": "Optional description"
}

Response (201):
{
  "id": 1,
  "name": "my-project",
  "description": "Optional description",
  "owner_id": 123,
  "created_at": "2026-03-24T10:00:00Z",
  "updated_at": "2026-03-24T10:00:00Z"
}
```

#### LIST USER PROJECTS
```
GET /api/v1/projects?skip=0&limit=100
Authorization: Bearer {jwt_token}

Response (200):
{
  "data": [
    {
      "id": 1,
      "name": "my-project",
      "description": "...",
      "owner_id": 123,
      "created_at": "...",
      "updated_at": "..."
    }
  ],
  "total": 5,
  "skip": 0,
  "limit": 100
}
```

#### GET PROJECT
```
GET /api/v1/projects/{project_id}
Authorization: Bearer {jwt_token}

Response (200):
{
  "id": 1,
  "name": "my-project",
  "description": "...",
  "owner_id": 123,
  "created_at": "...",
  "updated_at": "..."
}
```

#### UPDATE PROJECT
```
PATCH /api/v1/projects/{project_id}
Authorization: Bearer {jwt_token}
Content-Type: application/json

Request Body:
{
  "name": "new-name",
  "description": "new description"
}

Response (200):
{ Updated project object }
```

#### DELETE PROJECT
```
DELETE /api/v1/projects/{project_id}
Authorization: Bearer {jwt_token}

Response (204): No content
```

### 4.2 Branches Endpoints

#### CREATE BRANCH
```
POST /api/v1/branches
Authorization: Bearer {jwt_token}
Content-Type: application/json

Request Body:
{
  "project_id": 1,
  "name": "feature/auth",
  "created_from": 2  // parent branch_id
}

Response (201):
{
  "id": 3,
  "project_id": 1,
  "name": "feature/auth",
  "created_from": 2,
  "head_commit_id": null,
  "created_at": "..."
}
```

#### LIST PROJECT BRANCHES
```
GET /api/v1/branches/project/{project_id}?skip=0&limit=100
Authorization: Bearer {jwt_token}

Response (200):
{
  "data": [
    {
      "id": 1,
      "project_id": 1,
      "name": "main",
      "created_from": null,
      "head_commit_id": 10,
      "created_at": "..."
    }
  ],
  "total": 5,
  "skip": 0,
  "limit": 100
}
```

#### GET BRANCH
```
GET /api/v1/branches/{branch_id}
Authorization: Bearer {jwt_token}

Response (200):
{
  "id": 1,
  "project_id": 1,
  "name": "main",
  "created_from": null,
  "head_commit_id": 10,
  "created_at": "..."
}
```

### 4.3 Commits Endpoints

#### CREATE COMMIT
```
POST /api/v1/commits
Authorization: Bearer {jwt_token}
Content-Type: application/json

Request Body:
{
  "project_id": 1,
  "branch_id": 1,
  "message": "Initial commit",
  "parent_commit_id": null  // optional, null for first commit
}

Response (201):
{
  "id": 1,
  "project_id": 1,
  "branch_id": 1,
  "hash": "abc123def456...",
  "message": "Initial commit",
  "author_id": 123,
  "parent_commit_id": null,
  "created_at": "..."
}
```

#### LIST COMMITS (Branch History)
```
GET /api/v1/commits/branch/{branch_id}?skip=0&limit=100
Authorization: Bearer {jwt_token}

Response (200):
{
  "data": [
    {
      "id": 2,
      "project_id": 1,
      "branch_id": 1,
      "hash": "...",
      "message": "Second commit",
      "author_id": 123,
      "parent_commit_id": 1,
      "created_at": "..."
    }
  ],
  "total": 25,
  "skip": 0,
  "limit": 100
}
```

#### GET COMMIT
```
GET /api/v1/commits/{commit_id}
Authorization: Bearer {jwt_token}

Response (200):
{
  "id": 1,
  "project_id": 1,
  "branch_id": 1,
  "hash": "...",
  "message": "Initial commit",
  "author_id": 123,
  "parent_commit_id": null,
  "created_at": "..."
}
```

### 4.4 Merges Endpoints

#### CREATE MERGE REQUEST
```
POST /api/v1/merges
Authorization: Bearer {jwt_token}
Content-Type: application/json

Request Body:
{
  "project_id": 1,
  "source_branch_id": 2,
  "target_branch_id": 1,
  "title": "Add authentication",
  "description": "Implements JWT authentication"
}

Response (201):
{
  "id": 1,
  "project_id": 1,
  "source_branch_id": 2,
  "target_branch_id": 1,
  "title": "Add authentication",
  "description": "...",
  "status": "PENDING",
  "created_at": "...",
  "merged_at": null
}
```

#### LIST MERGE REQUESTS
```
GET /api/v1/merges/project/{project_id}/history?skip=0&limit=100
Authorization: Bearer {jwt_token}

Response (200):
{
  "data": [
    {
      "id": 1,
      "project_id": 1,
      "source_branch_id": 2,
      "target_branch_id": 1,
      "title": "Add authentication",
      "description": "...",
      "status": "MERGED",
      "created_at": "...",
      "merged_at": "..."
    }
  ],
  "total": 10,
  "skip": 0,
  "limit": 100
}
```

#### GET MERGE REQUEST
```
GET /api/v1/merges/{merge_id}
Authorization: Bearer {jwt_token}

Response (200):
{
  "id": 1,
  "project_id": 1,
  "source_branch_id": 2,
  "target_branch_id": 1,
  "title": "Add authentication",
  "description": "...",
  "status": "PENDING",
  "created_at": "...",
  "merged_at": null
}
```

#### APPROVE MERGE REQUEST
```
POST /api/v1/merges/{merge_id}/approve
Authorization: Bearer {jwt_token}
Content-Type: application/json

Response (200):
{
  "id": 1,
  "project_id": 1,
  "source_branch_id": 2,
  "target_branch_id": 1,
  "title": "Add authentication",
  "description": "...",
  "status": "MERGED",
  "created_at": "...",
  "merged_at": "2026-03-24T10:30:00Z"
}
```

### 4.5 Health Check

#### SERVICE HEALTH
```
GET /health
Authorization: None

Response (200):
{
  "status": "healthy",
  "version": "1.0.0"
}
```

---

## 5. Data Models

### 5.1 Project Model
```python
class Project:
  id: int (primary key)
  owner_id: int (foreign key to user_service)
  name: str (unique per owner)
  description: str (optional)
  created_at: datetime
  updated_at: datetime
  
  # Relationships
  branches: List[Branch]
  commits: List[Commit]
  merges: List[Merge]
```

### 5.2 Branch Model
```python
class Branch:
  id: int (primary key)
  project_id: int (foreign key)
  name: str (unique per project)
  created_from: int (foreign key to Branch, nullable)
  head_commit_id: int (foreign key to Commit, nullable)
  created_at: datetime
  
  # Relationships
  project: Project
  parent_branch: Branch (nullable)
  commits: List[Commit]
```

### 5.3 Commit Model
```python
class Commit:
  id: int (primary key)
  project_id: int (foreign key)
  branch_id: int (foreign key)
  hash: str (unique per project, SHA-256 derived)
  message: str
  author_id: int (foreign key to user_service)
  parent_commit_id: int (foreign key to Commit, nullable)
  created_at: datetime
  
  # Relationships
  project: Project
  branch: Branch
  parent_commit: Commit (nullable)
  child_commits: List[Commit]
```

### 5.4 Merge Model
```python
class Merge:
  id: int (primary key)
  project_id: int (foreign key)
  source_branch_id: int (foreign key)
  target_branch_id: int (foreign key)
  title: str
  description: str (optional)
  status: str (PENDING | MERGED | CONFLICT)
  created_at: datetime
  merged_at: datetime (nullable)
  
  # Relationships
  project: Project
  source_branch: Branch
  target_branch: Branch
```

---

## 6. Authentication & Authorization

### 6.1 Authentication Flow

All endpoints (except `/health`) require JWT authentication:

```
1. Client obtains JWT token from User Service
2. Client includes token: Authorization: Bearer {jwt_token}
3. Project Service validates token signature
4. User ID extracted from JWT claims (subject)
5. Operations scoped to user ownership
```

### 6.2 Authorization Rules

| Operation | Rule |
|-----------|------|
| Create Project | Any authenticated user |
| Read Project | Only project owner |
| Update Project | Only project owner |
| Delete Project | Only project owner |
| Create Branch | User must own parent project |
| Create Commit | User must own project |
| Create Merge | User must own project |
| Approve Merge | User must own project |

### 6.3 Token Validation

- **Algorithm:** HS256
- **Expiration:** 24 hours (user_service tokens accepted)
- **Claims Required:** `sub` (user_id), `exp`, `iat`
- **Signature Verification:** Using shared secret key

---

## 7. Error Handling

### 7.1 HTTP Status Codes

| Code | Scenario |
|------|----------|
| 200 | Successful GET/PATCH operation |
| 201 | Successful POST (resource created) |
| 204 | Successful DELETE |
| 400 | Invalid request body, validation error |
| 401 | Missing or invalid JWT token |
| 403 | User lacks ownership/permission |
| 404 | Resource not found |
| 409 | Conflict (e.g., duplicate branch name) |
| 500 | Server error |

### 7.2 Error Response Format

```json
{
  "error": "error_type",
  "message": "Human readable message",
  "detail": "Additional context (optional)"
}
```

### 7.3 Common Error Scenarios

- **ValidationError (400):** Invalid project/branch/commit data
- **NotFoundError (404):** Parent branch doesn't exist, commit not found
- **ForbiddenError (403):** User doesn't own the project
- **ConflictError (409):** Branch name already exists in project
- **MergeConflictError (409):** Commits diverged, manual resolution needed

---

## 8. Database Schema

### 8.1 Tables

**projects**
```sql
CREATE TABLE projects (
  id INTEGER PRIMARY KEY,
  owner_id INTEGER NOT NULL,
  name VARCHAR(255) NOT NULL,
  description TEXT,
  created_at TIMESTAMP NOT NULL,
  updated_at TIMESTAMP NOT NULL,
  UNIQUE(owner_id, name)
);
```

**branches**
```sql
CREATE TABLE branches (
  id INTEGER PRIMARY KEY,
  project_id INTEGER NOT NULL,
  name VARCHAR(255) NOT NULL,
  created_from INTEGER,
  head_commit_id INTEGER,
  created_at TIMESTAMP NOT NULL,
  FOREIGN KEY (project_id) REFERENCES projects(id),
  FOREIGN KEY (created_from) REFERENCES branches(id),
  FOREIGN KEY (head_commit_id) REFERENCES commits(id),
  UNIQUE(project_id, name)
);
```

**commits**
```sql
CREATE TABLE commits (
  id INTEGER PRIMARY KEY,
  project_id INTEGER NOT NULL,
  branch_id INTEGER NOT NULL,
  hash VARCHAR(64) NOT NULL,
  message TEXT NOT NULL,
  author_id INTEGER NOT NULL,
  parent_commit_id INTEGER,
  created_at TIMESTAMP NOT NULL,
  FOREIGN KEY (project_id) REFERENCES projects(id),
  FOREIGN KEY (branch_id) REFERENCES branches(id),
  FOREIGN KEY (parent_commit_id) REFERENCES commits(id),
  UNIQUE(project_id, hash)
);
```

**merges**
```sql
CREATE TABLE merges (
  id INTEGER PRIMARY KEY,
  project_id INTEGER NOT NULL,
  source_branch_id INTEGER NOT NULL,
  target_branch_id INTEGER NOT NULL,
  title VARCHAR(255) NOT NULL,
  description TEXT,
  status VARCHAR(50) NOT NULL,
  created_at TIMESTAMP NOT NULL,
  merged_at TIMESTAMP,
  FOREIGN KEY (project_id) REFERENCES projects(id),
  FOREIGN KEY (source_branch_id) REFERENCES branches(id),
  FOREIGN KEY (target_branch_id) REFERENCES branches(id)
);
```

### 8.2 Indices

```sql
CREATE INDEX idx_projects_owner_id ON projects(owner_id);
CREATE INDEX idx_branches_project_id ON branches(project_id);
CREATE INDEX idx_commits_project_id ON commits(project_id);
CREATE INDEX idx_commits_branch_id ON commits(branch_id);
CREATE INDEX idx_merges_project_id ON merges(project_id);
```

---

## 9. Performance Requirements

| Operation | Target | Max |
|-----------|--------|-----|
| Create Project | 50ms | 100ms |
| Get Project | 30ms | 50ms |
| List Projects (100) | 100ms | 200ms |
| Create Branch | 40ms | 100ms |
| List Branches (100) | 80ms | 150ms |
| Create Commit | 50ms | 120ms |
| List Commits (100) | 100ms | 200ms |
| Create Merge | 60ms | 150ms |
| List Merges (100) | 100ms | 200ms |
| Approve Merge | 80ms | 180ms |

**Database Connection:** Pool size 10, max overflow 20

---

## 10. Future Enhancements

### Phase 2 Features
- [ ] Webhook support for merge events
- [ ] Commit diff generation
- [ ] Advanced conflict resolution UI
- [ ] Branch protection rules
- [ ] Code review comments

### Phase 3 Features
- [ ] GraphQL API support
- [ ] Real-time WebSocket updates
- [ ] Audit logging for all operations
- [ ] Tags for releases
- [ ] Cherry-pick operations

---

## 11. Development Roadmap

| Phase | Timeline | Deliverables |
|-------|----------|--------------|
| Phase 1 (Current) | Completed | Core CRUD, merges, auth |
| Phase 2 | Q2 2026 | Webhooks, diffs, reviews |
| Phase 3 | Q3 2026 | GraphQL, WebSockets, audit logs |

---

## 12. Testing Strategy

### Unit Tests
- Individual endpoint validation
- Authorization logic
- Error handling

### Integration Tests
- Full project creation to merge workflow
- Branch lineage tracking
- Commit history integrity

### Performance Tests
- Load testing with 1000+ concurrent users
- Large repository (100+ branches) handling
- Pagination limits

---

## 13. Deployment & Operations

### 13.1 Environment Variables
```
DATABASE_URL=sqlite:///./project.db
JWT_SECRET_KEY=change-me-in-production
JWT_ALGORITHM=HS256
ENVIRONMENT=production
```

### 13.2 Scaling Considerations
- Stateless service design allows horizontal scaling
- Database connection pooling for efficiency
- Consider PostgreSQL for production (SQLite for development)

### 13.3 Monitoring
- Request latency tracking
- Error rate alerts
- Database connection pool monitoring
- JWT validation failure tracking

---

## 14. Appendix: Example Workflows

### Complete Project Lifecycle

```
1. Create Project
   POST /api/v1/projects {"name": "my-app"}
   → Returns project_id: 1 (main branch auto-created)

2. Create Feature Branch
   POST /api/v1/branches {"project_id": 1, "name": "feature/login", "created_from": main_branch_id}
   → Returns branch_id: 2

3. Make Commits
   POST /api/v1/commits {"project_id": 1, "branch_id": 2, "message": "Add login form"}
   → Commit updates branch HEAD

4. Create Merge Request
   POST /api/v1/merges {
     "project_id": 1,
     "source_branch_id": 2,
     "target_branch_id": 1,
     "title": "Add login feature"
   }
   → Returns merge_id: 1, status: PENDING

5. Approve Merge
   POST /api/v1/merges/1/approve
   → Status changes to MERGED, target branch HEAD updates
```

---

**Document Owner:** Backend Team  
**Last Review:** March 24, 2026  
**Next Review:** June 24, 2026
