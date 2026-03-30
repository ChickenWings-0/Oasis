# User Service - Architecture Documentation

**Service Name:** User Service  
**Port:** 8001  
**Technology Stack:** FastAPI, SQLAlchemy 2.0, PostgreSQL/SQLite, PyJWT, Bcrypt, Google OAuth 2.0  
**Latest Updated:** March 29, 2026

---

## Table of Contents

1. [Overview](#overview)
2. [Service Architecture](#service-architecture)
3. [Component Design](#component-design)
4. [Data Models](#data-models)
5. [Authentication Flows](#authentication-flows)
6. [API Specification](#api-specification)
7. [Database Schema](#database-schema)
8. [Security Architecture](#security-architecture)
9. [Request/Response Flow](#requestresponse-flow)
10. [Error Handling](#error-handling)
11. [Performance Considerations](#performance-considerations)
12. [Deployment & Scaling](#deployment--scaling)

---

## Overview

### Purpose
The User Service provides comprehensive authentication and profile management for the collaborative system. It handles user registration, local authentication, Google OAuth integration, profile management, and JWT token generation.

### Key Responsibilities
- ✓ User registration with validation
- ✓ Local authentication (email/password)
- ✓ Google OAuth 2.0 integration
- ✓ JWT token generation and validation
- ✓ Profile management (CRUD)
- ✓ Password management and security
- ✓ Account deletion with cleanup
- ✓ Multi-provider account linking

### Service Boundaries
```
┌─────────────────────────────────────────────────────────┐
│                 USER SERVICE (8001)                     │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  ┌────────────────────────────────────────────────────┐ │
│  │            REST API Layer (FastAPI)                 │ │
│  │  /api/auth/register /login /google /profile         │ │
│  └────────────────────────────────────────────────────┘ │
│                            │                              │
│  ┌──────────────────────────┴──────────────────────────┐ │
│  │        Business Logic Layer (Services)              │ │
│  │  RegistrationService / LoginService / etc.          │ │
│  └──────────────────────────┬──────────────────────────┘ │
│                            │                              │
│  ┌──────────────────────────┴──────────────────────────┐ │
│  │    Security Layer (JWT & OAuth Handlers)            │ │
│  │  JWTHandler / PasswordHandler / GoogleAuthService   │ │
│  └──────────────────────────┬──────────────────────────┘ │
│                            │                              │
│  ┌──────────────────────────┴──────────────────────────┐ │
│  │     Data Access Layer (Repositories)                │ │
│  │   UserRepository                                    │ │
│  └──────────────────────────┬──────────────────────────┘ │
│                            │                              │
│  ┌──────────────────────────┴──────────────────────────┐ │
│  │     ORM & Database Layer (SQLAlchemy)               │ │
│  │     PostgreSQL/SQLite with Connection Pooling       │ │
│  └─────────────────────────────────────────────────────┘ │
│                                                           │
└─────────────────────────────────────────────────────────┘
         ↓                                ↑
   Sends JWT tokens         Uses tokens from
   to Project Service       Project Service for auth
```

---

## Service Architecture

### Layered Architecture Pattern

The User Service follows a **4-layer architectural pattern with security focus**:

#### 1. API Layer (Routes)
**Location:** `registration/`, `login/`, `profiles/`  
**Files:** `reg_routes.py`, `log_routes.py`, `google_routes.py`, `prof_routes.py`

**Responsibilities:**
- HTTP request/response handling
- Request validation (email format, password strength)
- Response formatting with JWT tokens
- Status code mapping

**Route Organization:**
```
Registration Module (reg_routes.py)
├── POST /api/auth/register
└── Validation: email, username, password strength

Login Module (log_routes.py)
├── POST /api/auth/login
└── Response: JWT token + user info

Google Module (google_routes.py)
├── POST /api/auth/google
└── Payload: Google ID token

Profiles Module (prof_routes.py)
├── GET /api/profile/{user_id}
├── PATCH /api/profile/{user_id}
├── POST /api/profile/change-password
└── DELETE /api/profile/{user_id}
```

#### 2. Service Layer (Business Logic)
**Location:** `registration/`, `login/`, `profiles/`  
**Files:** `reg_services.py`, `log_services.py`, `prof_services.py`, `google_services.py`

**Responsibilities:**
- User creation and validation
- Password hashing coordination
- OAuth token verification
- Profile operations
- Account cleanup on deletion

**Key Services:**
```python
class RegistrationService:
    - validate_email(email)
    - validate_username(username)
    - create_user(email, username, password)

class LoginService:
    - authenticate(email, password)
    - generate_token(user_id, email)

class GoogleAuthService:
    - verify_google_token(token)
    - upsert_user(google_sub, email)
    - link_account(user_id, google_sub)

class ProfileService:
    - get_profile(user_id)
    - update_profile(user_id, data)
    - change_password(user_id, old_pwd, new_pwd)
    - delete_account(user_id)
```

#### 3. Security Layer (JWT & Cryptography)
**Location:** `jwt/`  
**Files:** `jwt_handler.py`, `pass_handler.py`

**Responsibilities:**
- JWT token creation and validation
- Password hashing and verification
- Google OAuth token verification

**Key Components:**
```python
class JWTHandler:
    - create_token(user_id, email)
    - decode_token(token)
    - validate_expiration(token)

class PasswordHandler:
    - hash_password(password)
    - verify_password(password, hash)
    - validate_strength(password)
```

#### 4. Data Layer (ORM & Storage)
**Location:** `models.py`, `database.py`

**Responsibilities:**
- User ORM model definition
- Database configuration
- Connection pooling and transaction management

---

## Component Design

### Core Components

#### Models
```
User (root entity)
  ├── Credentials (embedded)
  │   ├── password_hash (for local auth)
  │   └── auth_provider (local | google)
  └── OAuth Properties
      ├── google_sub (for Google OAuth)
      └── email (unique, used for linking)
```

#### Route Modules

**RegistrationModule**
- Validates email format and uniqueness
- Validates username uniqueness
- Validates password strength
- Creates user with hashed password
- Returns JWT token on success

**LoginModule**
- Accepts email + password
- Verifies password against hash
- Generates JWT token
- Returns user info with token

**GoogleModule**
- Accepts Google ID token
- Verifies token signature with Google
- Checks if user exists (by google_sub or email)
- Creates user if new (auto signup)
- Links account if existing user
- Returns JWT token

**ProfileModule**
- GET: Retrieve user profile data
- PATCH: Update profile (bio, avatar, etc.)
- POST (change-password): Verify old password, hash new, update
- DELETE: Remove user account with cascade cleanup

#### Security Handlers

**JWTHandler** (`jwt/jwt_handler.py`)
```python
# Token generation
def create_access_token(user_id: int, email: str) -> str:
    payload = {
        "user_id": user_id,
        "email": email,
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(hours=24)
    }
    return jwt.encode(payload, JWT_SECRET_KEY, HS256)

# Token validation
def decode_token(token: str) -> dict:
    return jwt.decode(token, JWT_SECRET_KEY, algorithms=["HS256"])
```

**PasswordHandler** (`jwt/pass_handler.py`)
```python
# Password hashing (Bcrypt)
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt(12))

# Password verification
def verify_password(password: str, hash: str) -> bool:
    return bcrypt.checkpw(password.encode(), hash)

# Password strength validation
def validate_strength(password: str) -> bool:
    # Min 8 chars, uppercase, lowercase, digit, special char
    return (len(password) >= 8 and 
            any(c.isupper() for c in password) and
            any(c.islower() for c in password) and
            any(c.isdigit() for c in password))
```

**GoogleAuthService** (`login/google_services.py`)
```python
class GoogleAuthService:
    def verify_google_token(self, id_token: str):
        # 1. Fetch Google public keys
        # 2. Decode token header
        # 3. Find matching key by kid
        # 4. Verify signature
        # 5. Check iss, aud, exp claims
        # 6. Return decoded payload
        
    def upsert_user(self, google_sub: str, email: str):
        # Try to find by google_sub
        # If exists: return user
        # If not exists: check by email
        #   If email exists: link account (set google_sub)
        #   If email doesn't exist: create new user
```

---

## Data Models

### User Model
```python
class User(Base):
    __tablename__ = "users"
    
    # Primary Key
    id: int (PK, auto-incremented)
    
    # Unique Identifiers
    email: str (unique, normalized to lowercase)
    username: str (unique, alphanumeric with underscores)
    
    # Authentication
    password_hash: str (nullable, for local auth only)
    auth_provider: str (local | google)
    google_sub: str (nullable, unique, Google's user identifier)
    
    # Profile Data
    first_name: str (optional)
    last_name: str (optional)
    avatar_url: str (optional, for custom/uploaded avatars)
    bio: str (optional, user biography)
    bio_location: str (optional)
    
    # Account Status
    is_active: bool (default True)
    is_verified: bool (default False, future: email verification)
    
    # Metadata
    created_at: datetime (ISO 8601)
    updated_at: datetime (auto-updated on changes)
    last_login: datetime (nullable, tracks last access)
    
    # Indexes
    UNIQUE(email)
    UNIQUE(username)
    UNIQUE(google_sub)
    INDEX(auth_provider)
```

**Key Design Decisions:**
- **Multiple Auth Providers:** `auth_provider` field enables local + Google
- **google_sub Unique:** Prevents duplicate Google accounts
- **Nullable Fields:** Flexible for different auth methods
- **Normalized Email:** Lowercase for case-insensitive queries
- **Account Linking:** Email used as link between local and Google

### Example User Records

#### Local Authentication User
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "john_doe",
  "password_hash": "$2b$12$...",
  "auth_provider": "local",
  "google_sub": null,
  "is_verified": true,
  "created_at": "2026-03-01T10:00:00Z"
}
```

#### Google OAuth User
```json
{
  "id": 2,
  "email": "user@gmail.com",
  "username": "jane_smith",
  "password_hash": null,
  "auth_provider": "google",
  "google_sub": "110123456789...",
  "is_verified": true,
  "created_at": "2026-03-15T14:30:00Z"
}
```

#### Linked Account (Local + Google)
```json
{
  "id": 3,
  "email": "user@corporate.com",
  "username": "bob_johnson",
  "password_hash": "$2b$12$...",
  "auth_provider": "local",
  "google_sub": "113987654321...",
  "is_verified": true,
  "created_at": "2026-02-20T08:15:00Z",
  "updated_at": "2026-03-25T16:45:00Z"
}
```

---

## Authentication Flows

### Local Registration Flow
```
┌─────────────────┐
│ User inputs:    │
│ - email         │
│ - username      │
│ - password      │
└────────┬────────┘
         │
         ▼
┌──────────────────────────────────────┐
│ Validation                           │
├──────────────────────────────────────┤
│ 1. Email format valid (RFC 5322)     │
│ 2. Email unique (not in DB)          │
│ 3. Username alphanumeric             │
│ 4. Username unique (not in DB)       │
│ 5. Password strength (8+ chars,      │
│    upper, lower, digit, special)     │
└────────┬─────────────────────────────┘
         │
         ▼ All valid
┌──────────────────────────────────────┐
│ Hash Password                        │
│ password_hash = bcrypt.hash(pwd, 12) │
└────────┬─────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────┐
│ Create User Record                   │
│ INSERT INTO users (...)              │
└────────┬─────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────┐
│ Generate JWT Token                   │
│ Payload: {user_id, email, exp: 24h}  │
└────────┬─────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│ Response (201 Created)                  │
│ {                                       │
│   "user_id": 1,                         │
│   "email": "user@example.com",          │
│   "username": "john_doe",               │
│   "token": "eyJhbGc...",                │
│   "created_at": "2026-03-29T10:00:00Z"  │
│ }                                       │
└─────────────────────────────────────────┘
```

### Local Login Flow
```
┌──────────────────────┐
│ User inputs:         │
│ - email              │
│ - password           │
└─────────┬────────────┘
          │
          ▼
┌────────────────────────────────────────┐
│ Query Database                         │
│ SELECT * FROM users WHERE email = ?   │
└─────────┬───────────────────────────────┘
          │
          ├─ User not found
          │  └─ Response (401): Invalid credentials
          │
          └─ User found
             │
             ▼
┌────────────────────────────────────────┐
│ Verify Password                        │
│ bcrypt.checkpw(pwd, hash)             │
└─────────┬───────────────────────────────┘
          │
          ├─ Password incorrect
          │  └─ Response (401): Invalid credentials
          │
          └─ Password correct
             │
             ▼
┌────────────────────────────────────────┐
│ Update last_login                      │
│ UPDATE users SET last_login = NOW()   │
└─────────┬───────────────────────────────┘
          │
          ▼
┌────────────────────────────────────────┐
│ Generate JWT Token                     │
│ Payload: {user_id, email, exp: 24h}   │
└─────────┬───────────────────────────────┘
          │
          ▼
┌────────────────────────────────────────┐
│ Response (200 OK)                      │
│ {                                      │
│   "user_id": 1,                        │
│   "email": "user@example.com",         │
│   "token": "eyJhbGc...",               │
│   "last_login": "2026-03-29T10:30:00Z" │
│ }                                      │
└────────────────────────────────────────┘
```

### Google OAuth Flow
```
┌───────────────────────────────┐
│ Frontend                      │
│ 1. Loads Google Sign-In SDK   │
│ 2. User clicks "Sign with...  │
│ 3. Google auth popup opens    │
│ 4. User authenticates         │
│ 5. Frontend receives ID token │
└────────────┬──────────────────┘
             │
             ▼
┌──────────────────────────────────────┐
│ POST /api/auth/google                │
│ Body: {id_token: "eyJhbGc..."}       │
└────────────┬───────────────────────────┘
             │
             ▼
┌──────────────────────────────────────┐
│ Verify Google Token                  │
│ ✓ Fetch Google public keys           │
│ ✓ Verify signature                   │
│ ✓ Check issuer (accounts.google.com) │
│ ✓ Check aud (client_id)              │
│ ✓ Check expiration                   │
└────────────┬───────────────────────────┘
             │
             ▼ Token valid
┌──────────────────────────────────────┐
│ Extract Claims                       │
│ - google_sub (e.g., "110123...")     │
│ - email (e.g., "user@gmail.com")     │
│ - name, picture (optional)           │
└────────────┬───────────────────────────┘
             │
             ▼
┌──────────────────────────────────────────┐
│ Check if User Exists                     │
│                                          │
│ SELECT * FROM users                      │
│ WHERE google_sub = ? OR email = ?        │
└────────────┬─────────────────────────────┘
             │
    ┌────────┴────────┐
    │                 │
    ├─ User exists    │  ├─ New user
    │                 │  │
    ▼                 │  ▼
POP (update last_     │ CREATE user
│   login)            │ gen JWT
│                     │
└────────┬────────────┘
         │
         ▼
┌────────────────────────────────────────┐
│ Generate JWT Token                     │
└────────┬────────────────────────────────┘
         │
         ▼
┌────────────────────────────────────────┐
│ Response (200 OK)                      │
│ {                                      │
│   "user_id": 2,                        │
│   "email": "user@gmail.com",           │
│   "token": "eyJhbGc...",               │
│   "is_new": false                      │
│ }                                      │
└────────────────────────────────────────┘
```

### Account Linking Flow (Local → Google)
```
Step 1: User has existing local account
        id=5, email="user@example.com", password_hash set

Step 2: User clicks "Add Google Account"
        Sends Google ID token

Step 3: Service verifies Google token
        Extracts google_sub & email (same as Step 1)

Step 4: Check if google_sub exists
        SELECT * FROM users WHERE google_sub = ?
        → Not found (first time linking)

Step 5: Check if email matches
        SELECT * FROM users WHERE email = ?
        → Found! (user_id=5)

Step 6: Update existing user record
        UPDATE users
        SET google_sub = ?,
            auth_provider = 'local'  // Keep as primary
        WHERE id = 5

Step 7: Account now linked!
        User can login with:
        - Email + password (local)
        - Google OAuth (ID token)
```

---

## API Specification

### Base URL
```
http://localhost:8001
```

### Endpoints Overview

#### Registration
| Method | Endpoint | Auth | Purpose |
|--------|----------|------|---------|
| POST | /api/auth/register | None | Create user account |

#### Login
| Method | Endpoint | Auth | Purpose |
|--------|----------|------|---------|
| POST | /api/auth/login | None | Authenticate with email/password |
| POST | /api/auth/google | None | Authenticate with Google token |

#### Profile
| Method | Endpoint | Auth | Purpose |
|--------|----------|------|---------|
| GET | /api/profile/{user_id} | JWT | Get user profile |
| PATCH | /api/profile/{user_id} | JWT | Update profile |
| POST | /api/profile/change-password | JWT | Change password |
| DELETE | /api/profile/{user_id} | JWT | Delete account |

#### Health
| Method | Endpoint | Auth | Purpose |
|--------|----------|------|---------|
| GET | /health | None | Service health |

### Request/Response Examples

#### Register
```
POST /api/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "username": "john_doe",
  "password": "SecurePass123!"
}

Response (201 Created):
{
  "user_id": 1,
  "email": "user@example.com",
  "username": "john_doe",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "created_at": "2026-03-29T10:00:00Z"
}
```

#### Login
```
POST /api/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePass123!"
}

Response (200 OK):
{
  "user_id": 1,
  "email": "user@example.com",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "last_login": "2026-03-29T10:30:00Z"
}
```

#### Google OAuth
```
POST /api/auth/google
Content-Type: application/json

{
  "id_token": "eyJhbGciOiJSUzI1NiIsImtpZCI6IjExNzU4Yj..."
}

Response (200 OK):
{
  "user_id": 2,
  "email": "user@gmail.com",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "is_new": true
}
```

#### Get Profile
```
GET /api/profile/1
Authorization: Bearer {token}

Response (200 OK):
{
  "user_id": 1,
  "email": "user@example.com",
  "username": "john_doe",
  "first_name": "John",
  "last_name": "Doe",
  "bio": "Software developer",
  "avatar_url": "https://example.com/avatars/1.jpg",
  "created_at": "2026-03-29T10:00:00Z",
  "updated_at": "2026-03-29T15:30:00Z"
}
```

#### Update Profile
```
PATCH /api/profile/1
Authorization: Bearer {token}
Content-Type: application/json

{
  "first_name": "Jonathan",
  "bio": "Senior software developer"
}

Response (200 OK):
{
  "user_id": 1,
  "email": "user@example.com",
  "username": "john_doe",
  "first_name": "Jonathan",
  "last_name": "Doe",
  "bio": "Senior software developer",
  "updated_at": "2026-03-29T16:00:00Z"
}
```

#### Change Password
```
POST /api/profile/change-password
Authorization: Bearer {token}
Content-Type: application/json

{
  "user_id": 1,
  "old_password": "OldPass123!",
  "new_password": "NewPass456!"
}

Response (200 OK):
{
  "message": "Password changed successfully",
  "updated_at": "2026-03-29T16:10:00Z"
}
```

#### Delete Account
```
DELETE /api/profile/1
Authorization: Bearer {token}

Response (204 No Content):
```

---

## Database Schema

### Table: users
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255),
    auth_provider VARCHAR(50) NOT NULL DEFAULT 'local',
    google_sub VARCHAR(255) UNIQUE,
    
    -- Profile fields
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    avatar_url TEXT,
    bio TEXT,
    bio_location VARCHAR(255),
    
    -- Account status
    is_active BOOLEAN DEFAULT true,
    is_verified BOOLEAN DEFAULT false,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    
    -- Constraints
    CHECK (auth_provider IN ('local', 'google')),
    CHECK (password_hash IS NOT NULL OR google_sub IS NOT NULL)
);

-- Indices for common queries
CREATE INDEX idx_users_email ON users(LOWER(email));
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_google_sub ON users(google_sub);
CREATE INDEX idx_users_auth_provider ON users(auth_provider);
CREATE INDEX idx_users_created_at ON users(created_at DESC);
```

**Key Constraints:**
- `email` UNIQUE: Prevents duplicate registrations
- `username` UNIQUE: Ensures unique handles
- `google_sub` UNIQUE: Prevents duplicate Google accounts
- `auth_provider` CHECK: Only 'local' or 'google'
- Composite CHECK: Either password_hash (local) or google_sub (OAuth) required

---

## Security Architecture

### Password Security

#### Hashing Algorithm: Bcrypt
```
┌────────────────────────────────┐
│  Password Input                │
│  "MySecurePass123!"            │
└──────────┬─────────────────────┘
           │
           ▼
┌────────────────────────────────┐
│  Bcrypt Hash (12 rounds)       │
│  Cost: ~100ms per hash         │
│  Salt: 16-byte random          │
└──────────┬─────────────────────┘
           │
           ▼
Output: $2b$12$R9h7cIPz0gi.URNtgxCa...
        (60 characters)

Stored in database
```

**Why Bcrypt:**
- Adaptive: configurable rounds (currently 12)
- Salted: built-in salt generation
- Time-resistant: ~100ms per check (slows brute force)
- Standard: widely supported and audited

#### Password Strength Requirements
```
Minimum 8 characters
├─ At least 1 uppercase letter (A-Z)
├─ At least 1 lowercase letter (a-z)
├─ At least 1 digit (0-9)
└─ At least 1 special character (!@#$%^&*)
```

### JWT Security

#### Token Structure
```
Header:
{
  "alg": "HS256",
  "typ": "JWT"
}

Payload:
{
  "user_id": 1,
  "email": "user@example.com",
  "iat": 1711785600,
  "exp": 1711872000
}

Signature:
HMACSHA256(
  base64UrlEncode(header) + "." + base64UrlEncode(payload),
  secret_key
)
```

#### Token Lifecycle
```
1. Generation (at login/registration)
   └─ Expires in 24 hours
   
2. Transmission
   └─ In Authorization: Bearer header
   └─ HTTPS only in production
   
3. Validation (on each request to Project Service)
   └─ Signature verified with shared secret
   └─ Expiration checked
   └─ Claims extracted (user_id)
   
4. Expiration
   └─ Client must re-authenticate
   └─ New token issued
```

### Google OAuth Security

#### Token Verification Process
```
┌─────────────────────────────┐
│  ID Token from Frontend     │
│  (JWT from Google)          │
└──────────┬──────────────────┘
           │
           ▼
┌──────────────────────────────────┐
│  1. Fetch Google Public Keys    │
│  GET /.well-known/keys...       │
│  Caches for 24 hours            │
└──────────┬───────────────────────┘
           │
           ▼
┌──────────────────────────────────┐
│  2. Decode Token Header          │
│  Extract kid (key ID)            │
│  Match against public keys       │
└──────────┬───────────────────────┘
           │
           ▼
┌──────────────────────────────────┐
│  3. Verify Signature             │
│  RS256 (RSA) with public key    │
└──────────┬───────────────────────┘
           │
           ▼
┌──────────────────────────────────┐
│  4. Validate Standard Claims     │
│  ✓ iss == "accounts.google.com"  │
│  ✓ aud == GOOGLE_CLIENT_ID       │
│  ✓ exp > current_time            │
└──────────┬───────────────────────┘
           │
           ▼
┌──────────────────────────────────┐
│  5. Extract User Information     │
│  - google_sub (user ID)         │
│  - email                        │
│  - name, picture (optional)     │
└─────────────────────────────────┘
```

### API Secrets Management

#### Environment Variables
```
JWT_SECRET_KEY          - HS256 signing key (32+ bytes)
GOOGLE_CLIENT_ID        - Google OAuth client ID
DATABASE_URL            - Database connection string
ENVIRONMENT             - production | development
```

#### Secret Rotation Strategy
```
Current                 Active
└─ JWT_SECRET_KEY      ├─ Used for new tokens & validation
                       
Stored securely:
├─ HashiCorp Vault (production)
├─ AWS Secrets Manager (AWS deployment)
├─ Environment variables (.env, not committed)
└─ Kubernetes Secrets (K8s deployment)
```

---

## Request/Response Flow

### Complete Registration Flow
```
┌─────────────────────────┐
│  Client (Frontend)      │
│  POST /api/auth/register│
│  {email, user, pass}    │
└────────┬────────────────┘
         │
         ▼
┌──────────────────────────────────┐
│  API Layer (reg_routes.py)       │
│  ✓ Receive request               │
│  ✓ Parse JSON body               │
│  ✓ Validate schema (Pydantic)    │
│  → Call RegistrationService      │
└────────┬─────────────────────────┘
         │
         ▼
┌──────────────────────────────────┐
│  Service Layer (reg_services.py) │
│  ✓ Validate email format         │
│  ✓ Check email uniqueness        │
│  ✓ Validate username             │
│  ✓ Check username uniqueness     │
│  ✓ Validate password strength    │
│  → Call PasswordHandler.hash()   │
│  → Call UserRepository.create()  │
└────────┬─────────────────────────┘
         │
         ▼
┌──────────────────────────────────┐
│  Security Layer (pass_handler.py)│
│  ✓ Bcrypt hash password (12 rnds)│
│  → Return hashed password        │
└────────┬─────────────────────────┘
         │
         ▼
┌──────────────────────────────────┐
│  Repository Layer                │
│  ✓ Create User object            │
│  ✓ Set password_hash             │
│  ✓ Insert to database            │
│  → Return persisted user         │
└────────┬─────────────────────────┘
         │
         ▼
┌──────────────────────────────────┐
│  Service (continued)             │
│  → Call JWTHandler.create_token()│
└────────┬─────────────────────────┘
         │
         ▼
┌──────────────────────────────────┐
│  Security Layer (jwt_handler.py) │
│  ✓ Create payload {sub, email}   │
│  ✓ Sign with HS256               │
│  ✓ Return JWT token              │
└────────┬─────────────────────────┘
         │
         ▼
┌──────────────────────────────────┐
│  API Layer (format response)     │
│  ✓ Status 201 Created            │
│  ✓ Include token                 │
│  ✓ Include user ID & email       │
│  → Send to client                │
└────────┬─────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│  Client receives response           │
│  {user_id, email, token, created}  │
│  Stores token in localStorage       │
└─────────────────────────────────────┘
```

---

## Error Handling

### HTTP Status Codes
```
200 OK               - Successful operation
201 Created          - User created successfully
204 No Content       - Account deleted
400 Bad Request      - Validation error
401 Unauthorized     - Invalid credentials or token
403 Forbidden        - Permission denied
404 Not Found        - User/resource not found
409 Conflict         - Email/username already exists
500 Internal Error   - Server error
```

### Error Response Format
```json
{
  "error": "validation_error",
  "message": "Password must contain at least one uppercase letter",
  "status_code": 400
}
```

### Common Error Scenarios

#### Registration Errors
```
400:
├─ "Invalid email format"
├─ "Email already registered"
├─ "Username already taken"
├─ "Username must be alphanumeric"
└─ "Password too weak"

409:
└─ "Email already exists"
```

#### Login Errors
```
401:
├─ "Invalid email or password"
├─ "Account not activated"
└─ "Too many login attempts"

404:
└─ "User not found"
```

#### Google OAuth Errors
```
400:
├─ "Invalid Google token"
├─ "Token signature verification failed"
├─ "Token expired"
└─ "Invalid audience (aud)"

401:
└─ "Unable to verify Google token"
```

#### Profile Errors
```
401:
└─ "Invalid or expired token"

403:
└─ "Cannot access other user's profile"

404:
└─ "User not found"

400:
├─ "Current password incorrect"
└─ "New password same as current"
```

---

## Performance Considerations

### Query Optimization

#### Frequently Used Queries
```sql
-- Login screen lookup
SELECT * FROM users WHERE LOWER(email) = LOWER(?)
→ Index: idx_users_email

-- Username availability check
SELECT id FROM users WHERE username = ?
→ Index: idx_users_username

-- Google OAuth linking
SELECT * FROM users WHERE google_sub = ? OR LOWER(email) = LOWER(?)
→ Indices: idx_users_google_sub, idx_users_email

-- Profile management
SELECT * FROM users WHERE id = ?
→ Primary key lookup (auto-indexed)
```

### Password Hashing Performance
```
Bcrypt with 12 rounds:
├─ Hash generation: ~100ms per password
├─ Verification: ~100ms per check
└─ Intentional delay: protects against brute force

Trade-off:
├─ Pro: Security against offline attacks
└─ Con: 100ms latency per auth request (acceptable)
```

### Connection Pooling
```python
# Development
poolclass=NullPool      # One connection per request (simple)

# Production
poolclass=QueuePool
pool_size=10            # Min connections
max_overflow=20         # Extra under load
pool_recycle=3600       # Refresh connections hourly
```

### Caching Strategy (Future)
```
Redis Cache:
├─ User profiles (5 min TTL)
├─ Google public keys (24 hour TTL)
└─ Session tokens (until expiration)
```

---

## Deployment & Scaling

### Environment Configuration

#### Development
```
DATABASE_URL=sqlite:///./auth.db
JWT_SECRET_KEY=dev-secret-change-in-prod
GOOGLE_CLIENT_ID=xxx.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=xxx  # For server-side verification (optional)
ENVIRONMENT=development
CORS_ORIGINS=*
```

#### Production
```
DATABASE_URL=postgresql://user:pass@prod-db:5432/auth_db
JWT_SECRET_KEY=<strong-secret-from-vault>
GOOGLE_CLIENT_ID=<production-client-id>
ENVIRONMENT=production
CORS_ORIGINS=https://app.example.com
JWT_EXPIRATION_HOURS=24
BCRYPT_ROUNDS=12
```

### Docker Deployment
```dockerfile
FROM python:3.10
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "backend.user_services.main:app", "--host", "0.0.0.0", "--port", "8001"]
```

### Kubernetes Deployment
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: user-service
spec:
  replicas: 3
  template:
    spec:
      containers:
      - name: user-service
        image: user-service:latest
        ports:
        - containerPort: 8001
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: app-secrets
              key: auth-db-url
        - name: JWT_SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: app-secrets
              key: jwt-secret
        livenessProbe:
          httpGet:
            path: /health
            port: 8001
          initialDelaySeconds: 30
          periodSeconds: 10
```

### Load Balancing
```
                    ┌──────────────┐
                    │Load Balancer ├──HTTPS
                    └───────┬──────┘
              ┌─────────────┼─────────────┐
              ▼             ▼             ▼
         ┌────────┐    ┌────────┐    ┌────────┐
         │ User   │    │ User   │    │ User   │
         │Service │    │Service │    │Service │
         │ 8001#1 │    │ 8001#2 │    │ 8001#3 │
         └───┬────┘    └───┬────┘    └───┬────┘
             │             │             │
             └─────────────┼─────────────┘
                           │
                    ┌──────▼──────┐
                    │PostgreSQL DB│
                    │(Read Replicas)
                    └─────────────┘
```

### Monitoring
```
Metrics:
├─ Auth success/failure rates
├─ Password verification latency
├─ JWT validation failures
├─ Google OAuth failures
├─ Database connection pool usage
└─ Registration rate (new users/hour)

Alerts:
├─ Failed login attempts > threshold
├─ Google OAuth token verification failures
├─ Database pool exhaustion
└─ Service latency > 500ms
```

---

## Directory Structure

```
backend/user_services/
├── __init__.py
├── main.py                     # FastAPI app entry point
├── database.py                 # SQLAlchemy config
├── models.py                   # User ORM model
├── schemas.py                  # Pydantic schemas
├── dependencies.py             # Dependency injection
│
├── jwt/
│   ├── __init__.py
│   ├── jwt_handler.py          # JWT creation & verification
│   └── pass_handler.py         # Bcrypt password hashing
│
├── login/
│   ├── __init__.py
│   ├── log_routes.py           # Email/password endpoints
│   ├── log_services.py         # Login business logic
│   ├── google_routes.py        # Google OAuth endpoints
│   └── google_services.py      # Google OAuth logic
│
├── registration/
│   ├── __init__.py
│   ├── reg_routes.py           # Registration endpoints
│   └── reg_services.py         # Registration logic
│
└── profiles/
    ├── __init__.py
    ├── prof_routes.py          # Profile endpoints
    └── prof_services.py        # Profile business logic
```

---

## Integration with Project Service

```
Sequential Authentication Flow:

1. User logs in to User Service
   POST /api/auth/login
   ↓ returns JWT token
   
2. User wants to access Project Service
   Sends: Authorization: Bearer {jwt_token}
   
3. Project Service validates JWT
   - Verifies signature (shared secret key)
   - Extracts user_id from payload
   - All operations scoped to user_id
   
4. Project Service enforces ownership
   - Only user who owns project can modify
   - Uses user_id from JWT claims
```

---

## Future Enhancements

### Phase 2
- [ ] Email verification for new accounts
- [ ] Two-factor authentication (2FA)
- [ ] Account recovery via email
- [ ] Rate limiting on authentication
- [ ] Login history/audit trail

### Phase 3
- [ ] Enterprise SSO (SAML 2.0)
- [ ] Role-based access control (RBAC)
- [ ] Advanced security policies
- [ ] Compliance features (GDPR, HIPAA)
- [ ] Social login (GitHub, Microsoft, etc.)

---

**Last Updated:** March 29, 2026  
**Architecture Version:** 1.0  
**Review Schedule:** Quarterly
