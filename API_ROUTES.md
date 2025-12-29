# API Routes (MVP)

Consolidated list of main endpoints with brief summaries. All authenticated endpoints require a bearer token unless noted.

## Auth (`/auth`)
- POST `/auth/signup` — Create user (requires role, corpus_uri)
- POST `/auth/login` — Login, returns access_token
- GET `/auth/me` — Current user
- POST `/auth/logout` — Logout (if implemented)

## Users (`/users`)
- Standard CRUD (admin-only for some operations, where implemented)

## Groups (`/groups`)
- POST `/groups` — Create group (creator becomes admin)
- GET `/groups` — List my groups
- GET `/groups/{id}` — Get group
- PUT `/groups/{id}` — Update name/description (admin)
- DELETE `/groups/{id}` — Delete (admin)

### Group Members (`/groups/{id}/access`)
- GET `/groups/{id}/access?limit&offset` — List members (any member)
- POST `/groups/{id}/access` — Add member (admin)
- PUT `/groups/{id}/access/{userId}/role` — Change role (admin; creator cannot be demoted)
- DELETE `/groups/{id}/access/{userId}` — Remove member (admin; last-admin guard)
- POST `/groups/{id}/access/self` — Leave group (creator cannot leave)

## Payments (Group Codes)
- POST `/groups/{id}/payments/codes` — Create code (admin)
- GET `/groups/{id}/payments/codes` — List codes (admin)
- POST `/groups/{id}/payments/codes/{code}/void` — Void code (admin)
- POST `/payments/redeem` — Redeem code (any authenticated user)

## Invitations
Caregiver-centric:
- POST `/caregivers/{caregiverId}/invitations` — Send invite to recipient email
- GET `/caregivers/{caregiverId}/invitations` — List invites sent/received
- POST `/caregivers/{caregiverId}/invitations/{invitationId}/accept` — Accept received invite
- POST `/caregivers/{caregiverId}/invitations/{invitationId}/decline` — Decline received invite

Recipient-centric:
- POST `/recipients/{recipientId}/invitations` — Send invite to caregiver email
- GET `/recipients/{recipientId}/invitations` — List invites received
- GET `/recipients/{recipientId}/invitations/sent` — List invites sent
- POST `/recipients/{recipientId}/invitations/{invitationId}/accept` — Accept received invite
- POST `/recipients/{recipientId}/invitations/{invitationId}/decline` — Decline received invite

Public:
- POST `/invites/accept-by-token` — Accept invite via signed token (no auth)

## Recipient Files (`/recipients/{id}/files`)
- POST `/recipients/{id}/files` — Upload (size/MIME validated)
- GET `/recipients/{id}/files` — List files
- GET `/recipients/{id}/files/{fileId}` — Get file metadata
- DELETE `/recipients/{id}/files/{fileId}` — Delete file
- POST `/recipients/{id}/files/redact-upload` — Redact (stub) then upload

## Redaction (stub) (`/redaction`)
- POST `/redaction/test` — Test redaction stub with small text

## Ops / Security (selected)
- GET `/readyz`, `/healthz` — Health endpoints
- Security routes under `/security/*` (keys, policies)

Notes:
- Error payloads include standard codes from `backend/core/constants.py::Errors`.
- Pagination headers: `X-Total-Count` for member listing.

