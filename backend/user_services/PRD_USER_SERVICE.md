# Product Requirements Document: User Service

**Document Version:** 1.0  
**Last Updated:** March 24, 2026  
**Service Name:** User Service  
**Service Port:** 8001  
**Technology Stack:** FastAPI, SQLAlchemy, SQLite, PyJWT, Bcrypt

---

## 1. Executive Summary

The User Service handles all authentication and user profile management for the Oasis platform. It supports multiple authentication methods (local registration/login and Google OAuth), secure password management, and comprehensive user profile features. The service issues JWT tokens for use across other microservices.

**Core Purpose:** Provide secure user authentication, account management, and JWT token generation for the Oasis ecosystem.

---

## 2. Product Overview

### 2.1 Vision

Enable secure, flexible authentication that supports both traditional email/password registration and modern OAuth2 integration with Google, allowing users to access the platform through their preferred authentication method.

### 2.2 Target Users

- End users seeking secure account access
- Developers integrating Oasis into their applications
- Organizations managing team access

### 2.3 Key Success Metrics

- Authentication success rate > 99.9%
- Password reset completion time < 5 minutes
- OAuth integration conversion rate > 85%
- Token validation < 50ms per request
- Account registration completion < 2 minutes

---

## 3. Core Features

### 3.1 User Registration

**Feature:** Create new user accounts with email and password

**Capabilities:**
- Email/password registration
- Email uniqueness validation
- Username uniqueness validation
- Secure password hashing (bcrypt)
- Account activation status
- Auto-population of optional fields (first_name, last_name)

**Acceptance Criteria:**
- ✓ Email must be unique across system
- ✓ Username must be unique across system
- ✓ Password strength enforced (8+ chars recommended)
- ✓ Passwords hashed with bcrypt salt
- ✓ Account active by default
- ✓ All registrations logged with timestamp

### 3.2 Local Authentication (Email/Password Login)

**Feature:** Authenticate users with email and password credentials

**Capabilities:**
- Username or email login
- Password verification against bcrypt hash
- JWT token generation on success
- Session management via tokens
- Failed login tracking
- Account lockout after N failed attempts (future)

**Acceptance Criteria:**
- ✓ Login accepts either email or username
- ✓ Password compared securely (timing-attack resistant)
- ✓ Returns JWT token on success
- ✓ Returns descriptive error on failure
- ✓ Tokens valid for 24 hours
- ✓ Failed login attempts logged

### 3.3 Google OAuth Authentication

**Feature:** Third-party authentication via Google OAuth 2.0

**Capabilities:**
- Google ID token verification
- Auto-user creation on first login
- Account linking for existing users
- Google account metadata capture (if provided)
- No password required for OAuth users
- Account provider tracking (local vs. google)

**Acceptance Criteria:**
- ✓ ID token validated against Google's public keys
- ✓ New users auto-created with Google ID
- ✓ Existing email auto-linked to Google account
- ✓ Returns JWT token on authentication
- ✓ Google sub ID stored for account linking
- ✓ OAuth users cannot login with password
- ✓ First name/last name extracted from Google profile if available

### 3.4 Profile Management

**Feature:** View and manage user profile information

**Capabilities:**
- View complete user profile
- Update first name and last name
- Update username
- Email address viewing (not editable after creation)
- Account creation timestamp visibility
- Auth provider visibility (local or google)

**Acceptance Criteria:**
- ✓ Only user can view/edit own profile
- ✓ Email immutable after account creation
- ✓ Username changes reflected immediately
- ✓ Profile updates include timestamp
- ✓ Auth provider shown but not changeable

### 3.5 Password Management

**Feature:** Secure password change functionality

**Capabilities:**
- Change password with current password verification
- Password strength requirements
- Old password must be provided
- History tracking (prevent reuse) - future
- Clear session tokens on password change - future

**Acceptance Criteria:**
- ✓ Current password verified before change
- ✓ New password cannot be same as old
- ✓ Password hashed with bcrypt before storage
- ✓ Change logged with timestamp
- ✓ Only user can change their own password

### 3.6 Account Deletion

**Feature:** Allow users to permanently delete their accounts

**Capabilities:**
- Permanent account deletion
- Cascading deletion of related data (projects, etc.)
- Deletion confirmation required
- Audit logging of deletions
- Graceful handling with Project Service

**Acceptance Criteria:**
- ✓ User must provide correct password for confirmation
- ✓ All user data deleted from system
- ✓ Cannot be undone (permanent)
- ✓ Related resources cascade delete
- ✓ Deletion logged with timestamp and reason

---

## 4. API Specifications

### 4.1 Registration Endpoints

#### REGISTER NEW USER
```
POST /api/auth/register
Content-Type: application/json
Authorization: None

Request Body:
{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "SecurePassword123!",
  "first_name": "John",
  "last_name": "Doe"
}

Response (201):
{
  "id": 42,
  "username": "john_doe",
  "email": "john@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "auth_provider": "local",
  "created_at": "2026-03-24T10:00:00Z",
  "is_active": true
}

Error Response (400):
{
  "error": "ValidationError",
  "message": "Email already exists",
  "detail": "john@example.com is already registered"
}

Error Response (409):
{
  "error": "ConflictError",
  "message": "Username already taken",
  "detail": "john_doe not available"
}
```

#### VALIDATE EMAIL AVAILABILITY
```
GET /api/auth/check-email?email=john@example.com
Authorization: None

Response (200):
{
  "email": "john@example.com",
  "available": true
}

Response (200):
{
  "email": "existing@example.com",
  "available": false
}
```

#### VALIDATE USERNAME AVAILABILITY
```
GET /api/auth/check-username?username=john_doe
Authorization: None

Response (200):
{
  "username": "john_doe",
  "available": true
}
```

---

### 4.2 Local Authentication Endpoints

#### LOGIN WITH EMAIL/PASSWORD
```
POST /api/auth/login
Content-Type: application/json
Authorization: None

Request Body:
{
  "username": "john_doe",  // or email
  "password": "SecurePassword123!"
}

Response (200):
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "Bearer",
  "expires_in": 86400,
  "user": {
    "id": 42,
    "username": "john_doe",
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "auth_provider": "local"
  }
}

Error Response (401):
{
  "error": "UnauthorizedError",
  "message": "Invalid credentials",
  "detail": "Username or password incorrect"
}
```

---

### 4.3 Google OAuth Endpoints

#### GET GOOGLE OAUTH CONFIG
```
GET /api/auth/google/config
Authorization: None

Response (200):
{
  "client_id": "xxx.apps.googleusercontent.com",
  "redirect_uri": "http://localhost:8000/callback"
}
```

#### AUTHENTICATE WITH GOOGLE
```
POST /api/auth/google
Content-Type: application/json
Authorization: None

Request Body:
{
  "id_token": "eyJhbGci..."  // From Google Sign-In
}

Response (200):
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "Bearer",
  "expires_in": 86400,
  "user": {
    "id": 43,
    "username": "john.doe",
    "email": "john.doe@gmail.com",
    "first_name": "John",
    "last_name": "Doe",
    "auth_provider": "google"
  },
  "is_new_user": false  // true if account just created
}

Error Response (400):
{
  "error": "InvalidTokenError",
  "message": "Invalid Google ID token",
  "detail": "Token signature verification failed"
}
```

---

### 4.4 Profile Endpoints

#### GET USER PROFILE
```
GET /api/profile
Authorization: Bearer {jwt_token}

Response (200):
{
  "id": 42,
  "username": "john_doe",
  "email": "john@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "auth_provider": "local",
  "is_active": true,
  "created_at": "2026-03-24T10:00:00Z",
  "updated_at": "2026-03-24T10:00:00Z"
}

Error Response (401):
{
  "error": "UnauthorizedError",
  "message": "Invalid or expired token"
}
```

#### UPDATE USER PROFILE
```
PUT /api/profile
Authorization: Bearer {jwt_token}
Content-Type: application/json

Request Body:
{
  "first_name": "John",
  "last_name": "Smith",
  "username": "john_smith"
}

Response (200):
{
  "id": 42,
  "username": "john_smith",
  "email": "john@example.com",
  "first_name": "John",
  "last_name": "Smith",
  "auth_provider": "local",
  "is_active": true,
  "created_at": "2026-03-24T10:00:00Z",
  "updated_at": "2026-03-24T10:30:00Z"
}

Error Response (409):
{
  "error": "ConflictError",
  "message": "Username already taken",
  "detail": "john_smith is not available"
}
```

#### CHANGE PASSWORD
```
POST /api/profile/change-password
Authorization: Bearer {jwt_token}
Content-Type: application/json

Request Body:
{
  "current_password": "OldPassword123!",
  "new_password": "NewPassword456!"
}

Response (200):
{
  "message": "Password changed successfully"
}

Error Response (400):
{
  "error": "ValidationError",
  "message": "Current password incorrect",
  "detail": "Old password does not match"
}

Error Response (422):
{
  "error": "ValidationError",
  "message": "Password too weak",
  "detail": "Password must be at least 8 characters"
}
```

#### DELETE USER ACCOUNT
```
DELETE /api/profile
Authorization: Bearer {jwt_token}
Content-Type: application/json

Request Body:
{
  "password": "SecurePassword123!"  // Confirmation
}

Response (204): No content

Error Response (400):
{
  "error": "ValidationError",
  "message": "Password required for account deletion"
}

Error Response (401):
{
  "error": "UnauthorizedError",
  "message": "Invalid password for account deletion"
}
```

---

### 4.5 Utility Endpoints

#### HEALTH CHECK
```
GET /health
Authorization: None

Response (200):
{
  "status": "healthy",
  "version": "1.0.0"
}
```

#### VERIFY TOKEN
```
POST /api/auth/verify
Authorization: Bearer {jwt_token}
Content-Type: application/json

Response (200):
{
  "valid": true,
  "user_id": 42,
  "expires_at": "2026-03-25T10:00:00Z"
}

Response (401):
{
  "valid": false,
  "error": "Token expired or invalid"
}
```

---

## 5. Data Models

### 5.1 User Model
```python
class User:
  id: int (primary key)
  username: str (unique)
  email: str (unique)
  password_hash: str (bcrypt, nullable for OAuth)
  first_name: str (optional)
  last_name: str (optional)
  auth_provider: str (local | google)
  google_sub: str (nullable, Google account ID)
  is_active: bool (default: true)
  created_at: datetime
  updated_at: datetime
  
  # Computed Properties
  full_name: str (first_name + " " + last_name)
  is_oauth_user: bool (auth_provider == "google")
  is_local_user: bool (auth_provider == "local")
```

### 5.2 Password Requirements
```
Minimum Length: 8 characters
Recommended: Mix of uppercase, lowercase, numbers, symbols
Hashing: bcrypt with salt rounds = 12
Storage: Salted hash only (plaintext never stored)
```

### 5.3 JWT Token Structure
```
Header:
{
  "alg": "HS256",
  "typ": "JWT"
}

Payload:
{
  "sub": "42",              # User ID as subject
  "email": "john@example.com",
  "username": "john_doe",
  "exp": 1711270800,        # 24 hours from issue
  "iat": 1711184400,        # Issued at
  "jti": "uuid-string"      # Unique token ID
}

Signature:
HMACSHA256(header + payload, secret_key)
```

---

## 6. Authentication & Authorization

### 6.1 Authentication Methods

| Method | Requirement | Token Issued | Account Type |
|--------|-------------|--------------|--------------|
| Email/Password | Username + Password | Yes | Local |
| Google OAuth | Valid ID Token | Yes | OAuth |
| Token Refresh | Valid JWT | New JWT (future) | Any |

### 6.2 Authorization Rules

| Endpoint | Auth Required | Scope |
|----------|---------------|-------|
| POST /api/auth/register | No | Public |
| POST /api/auth/login | No | Public |
| POST /api/auth/google | No | Public |
| GET /api/profile | Yes | Own profile only |
| PUT /api/profile | Yes | Own profile only |
| POST /api/profile/change-password | Yes | Own account only |
| DELETE /api/profile | Yes | Own account only |

### 6.3 Token Validation

**On Every Protected Request:**
1. Extract Bearer token from Authorization header
2. Decode JWT using HS256 algorithm
3. Verify signature using shared secret
4. Check expiration timestamp
5. Validate user_id exists and is active
6. Add user context to request

**Token Expiration:**
- Standard JWT: 24 hours
- Refresh tokens: 30 days (future)
- Sliding window: 1 hour inactivity timeout (future)

---

## 7. Security

### 7.1 Password Security

- **Bcrypt Hashing:** 12 salt rounds
- **Comparison:** Constant-time comparison (timing-attack resistant)
- **Storage:** Hash only (never store plaintext)
- **Requirements:** Minimum 8 characters (enforced in frontend)

### 7.2 OAuth Security

- **Token Validation:** Verified against Google's public keys
- **Nonce Support:** (future) Prevent token reuse attacks
- **State Parameter:** (future) CSRF protection for OAuth flow
- **HTTPS Required:** All OAuth callbacks use HTTPS in production

### 7.3 Session Management

- **Token-Based:** Stateless JWT (no session storage needed)
- **Expiration:** 24 hours for security
- **Refresh:** Manual login required on expiration
- **Logout:** Token invalidation via blacklist (future)

### 7.4 Data Protection

- **HTTPS Only:** All endpoints CORS-enabled for HTTPS
- **Email Verification:** (future) Confirm email ownership
- **Rate Limiting:** (future) Prevent brute force attacks
- **Account Lockout:** (future) After N failed login attempts

---

## 8. Error Handling

### 8.1 HTTP Status Codes

| Code | Scenario |
|------|----------|
| 200 | Successful GET/PUT operation |
| 201 | Successful registration (resource created) |
| 204 | Successful DELETE |
| 400 | Invalid request body, validation error |
| 401 | Missing/invalid authentication, wrong password |
| 409 | Conflict (duplicate email/username) |
| 422 | Validation error (password too weak) |
| 500 | Server error |

### 8.2 Error Response Format

```json
{
  "error": "error_type",
  "message": "Human readable message",
  "detail": "Additional context (optional)",
  "validation_errors": [
    {
      "field": "password",
      "message": "Password must be at least 8 characters"
    }
  ]
}
```

### 8.3 Common Error Scenarios

| Scenario | Status | Error Type |
|----------|--------|-----------|
| Duplicate email | 409 | ConflictError |
| Duplicate username | 409 | ConflictError |
| Weak password | 422 | ValidationError |
| Invalid credentials | 401 | UnauthorizedError |
| Expired token | 401 | UnauthorizedError |
| Invalid Google token | 400 | InvalidTokenError |
| User not found | 404 | NotFoundError |
| Wrong password | 401 | UnauthorizedError |

---

## 9. Database Schema

### 9.1 Users Table

```sql
CREATE TABLE users (
  id INTEGER PRIMARY KEY,
  username VARCHAR(255) NOT NULL UNIQUE,
  email VARCHAR(255) NOT NULL UNIQUE,
  password_hash VARCHAR(255),  -- NULL for OAuth users
  first_name VARCHAR(255),
  last_name VARCHAR(255),
  auth_provider VARCHAR(50) NOT NULL DEFAULT 'local',
  google_sub VARCHAR(255),     -- NULL for local users
  is_active BOOLEAN NOT NULL DEFAULT true,
  created_at TIMESTAMP NOT NULL,
  updated_at TIMESTAMP NOT NULL
);
```

### 9.2 Indices

```sql
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_google_sub ON users(google_sub);
CREATE INDEX idx_users_auth_provider ON users(auth_provider);
```

### 9.3 Data Constraints

```sql
-- Email and username must be unique
ALTER TABLE users ADD CONSTRAINT unique_email UNIQUE(email);
ALTER TABLE users ADD CONSTRAINT unique_username UNIQUE(username);

-- Auth provider must be 'local' or 'google'
ALTER TABLE users ADD CHECK (auth_provider IN ('local', 'google'));

-- Local users must have password hash
ALTER TABLE users ADD CONSTRAINT local_user_password_check 
  CHECK (auth_provider = 'google' OR password_hash IS NOT NULL);

-- OAuth users must have google_sub
ALTER TABLE users ADD CONSTRAINT oauth_user_google_check 
  CHECK (auth_provider = 'local' OR google_sub IS NOT NULL);
```

---

## 10. Performance Requirements

| Operation | Target | Max |
|-----------|--------|-----|
| Register User | 150ms | 300ms |
| Login | 100ms | 250ms |
| Google OAuth | 200ms | 500ms |
| Get Profile | 30ms | 50ms |
| Update Profile | 50ms | 100ms |
| Change Password | 150ms | 300ms |
| Delete Account | 100ms | 200ms |
| Token Validation | 30ms | 50ms |

**Password Hash Time:** Bcrypt with 12 rounds ≈ 100-150ms (intentionally slow for security)

---

## 11. Integration Points

### 11.1 With Project Service

```
User Service                 Project Service
   ↓                              ↓
Issues JWT token ────────→ Validates JWT
                          Extracts user_id
                          Enforces ownership rules
```

- JWT tokens issued by User Service accepted by Project Service
- User IDs from JWT used for resource ownership
- **No direct API calls** between services (decoupled)

### 11.2 Frontend Integration

```
Frontend
   ├─→ POST /api/auth/register → Create account
   ├─→ POST /api/auth/login → Get JWT token
   ├─→ POST /api/auth/google → OAuth login
   ├─→ GET /api/profile → View profile
   ├─→ PUT /api/profile → Update profile
   └─→ Store JWT → Use in Project Service requests
```

---

## 12. Compliance & Standards

### 12.1 OAuth 2.0 Compliance

- ✓ Follows RFC 6749 Authorization Framework
- ✓ Uses Google OAuth 2.0 authorization code flow
- ✓ ID token validation per JWT RFC 7519
- ✓ PKCE support (future)

### 12.2 JWT Standards

- ✓ RFC 7519 JSON Web Token (JWT)
- ✓ HS256 signature algorithm (HMAC with SHA-256)
- ✓ Standard claims: `sub`, `exp`, `iat`
- ✓ Custom claims: `email`, `username`

### 12.3 Security Standards

- ✓ OWASP Top 10: Injection protection via parameterized queries
- ✓ Password hashing: Bcrypt NIST-approved
- ✓ HTTPS-only: In production
- ✓ CORS: Configured for frontend origin

---

## 13. Future Enhancements

### Phase 2 Features
- [ ] Email verification on registration
- [ ] Password reset via email
- [ ] Two-factor authentication (2FA) via TOTP
- [ ] Account lockout after failed attempts
- [ ] Token refresh mechanism

### Phase 3 Features
- [ ] SAML support for enterprise SSO
- [ ] GitHub OAuth integration
- [ ] Biometric authentication support
- [ ] Session management dashboard
- [ ] Login history and geolocation tracking
- [ ] API key generation for service-to-service auth

---

## 14. Development Roadmap

| Phase | Timeline | Deliverables |
|-------|----------|--------------|
| Phase 1 (Current) | Completed | Local auth, Google OAuth, profiles |
| Phase 2 | Q2 2026 | Email verification, password reset, 2FA |
| Phase 3 | Q3 2026 | Enterprise SSO, advanced auth methods |

---

## 15. Testing Strategy

### Unit Tests
- Password hashing and comparison
- Token generation and validation
- Email/username uniqueness checks
- Bcrypt salt round verification

### Integration Tests
- Complete registration workflow
- Login with email and username
- Google OAuth ID token validation
- Profile update with conflict detection
- Password change with validation
- Account deletion cascading

### Security Tests
- Password timing attacks
- Token expiration enforcement
- CORS header validation
- SQL injection prevention
- Rate limiting (future)

### Load Tests
- 1000+ concurrent registrations
- 5000+ simultaneous logins
- Token validation under load

---

## 16. Deployment & Operations

### 16.1 Environment Variables
```
DATABASE_URL=sqlite:///./users.db
JWT_SECRET_KEY=change-me-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24
BCRYPT_ROUNDS=12
GOOGLE_CLIENT_ID=xxx.apps.googleusercontent.com
ENVIRONMENT=production
ALLOWED_ORIGINS=https://app.example.com
```

### 16.2 Logging Strategy

```
[2026-03-24 10:30:45] INFO: User 42 logged in from 192.168.1.1
[2026-03-24 10:31:10] INFO: User 42 profile updated
[2026-03-24 10:32:00] WARN: Failed login attempt for john_doe (3 failures)
[2026-03-24 10:33:45] ERROR: Invalid Google token: signature invalid
```

### 16.3 Monitoring

- User registration rate per hour
- Login success/failure ratio
- OAuth conversion rate
- Average response times per endpoint
- JWT validation failures
- Database connection pool utilization

---

## 17. Appendix: Example Workflows

### Registration Workflow
```
1. POST /api/auth/register
   {
     "username": "jane_doe",
     "email": "jane@example.com",
     "password": "SecurePass123!",
     "first_name": "Jane",
     "last_name": "Doe"
   }

2. Server validates:
   - Email unique
   - Username unique
   - Password strong enough
   - Bcrypt hash password

3. Returns 201:
   {
     "id": 99,
     "username": "jane_doe",
     "email": "jane@example.com",
     "first_name": "Jane",
     "last_name": "Doe",
     "auth_provider": "local",
     "created_at": "..."
   }
```

### Login Workflow
```
1. POST /api/auth/login
   {
     "username": "jane_doe",
     "password": "SecurePass123!"
   }

2. Server:
   - Finds user by username or email
   - Verifies password against hash
   - Creates JWT token
   - Returns token with user info

3. Response 200:
   {
     "access_token": "eyJhbGci...",
     "token_type": "Bearer",
     "expires_in": 86400,
     "user": { ... }
   }

4. Frontend:
   - Stores token in localStorage
   - Includes in Authorization header
   - Uses with Project Service
```

### Google OAuth Workflow
```
1. Frontend: GET /api/auth/google/config
   → Returns client_id, redirect_uri

2. Frontend: User clicks "Sign in with Google"
   → Google Sign-In dialog opens

3. User authenticates with Google
   → Returns id_token to frontend

4. Frontend: POST /api/auth/google
   {
     "id_token": "eyJhbGci..."
   }

5. Server:
   - Decodes id_token
   - Verifies signature
   - Extracts email, name
   - Finds user by email or creates new
   - Returns JWT token

6. Response:
   {
     "access_token": "eyJhbGci...",
     "user": { ... },
     "is_new_user": false
   }
```

### Profile Update Workflow
```
1. GET /api/profile
   Authorization: Bearer {token}

2. Returns current profile

3. User modifies (e.g., name change)
   PUT /api/profile
   Authorization: Bearer {token}
   {
     "first_name": "Janet",
     "last_name": "Smith",
     "username": "janet_smith"
   }

4. Server validates:
   - Username not taken
   - Token valid and not expired

5. Returns 200 with updated profile
```

---

**Last Review:** March 24, 2026 