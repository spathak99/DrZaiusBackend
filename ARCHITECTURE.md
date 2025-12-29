# Architecture Overview

## Layers
- Routers (`backend/routers/*`): HTTP I/O, request/response models, auth dependencies, error mapping.
- Services (`backend/services/*`): business logic; orchestrate repositories, enforce guards and invariants.
- Repositories (`backend/repositories/*`): data access via SQLAlchemy; no business rules.
- Schemas (`backend/schemas/*`): Pydantic request/response shapes (response_model on routes).
- Constants (`backend/core/constants.py`): routes, messages, errors, roles, headers, pagination, etc.
- Settings (`backend/core/settings.py`): typed env configuration with sane defaults.

## Dependency Injection
- Routers provide services via small providers (constructor DI): e.g., `get_groups_service()` builds services with concrete repos.
- Services accept repos as constructor args (default to concrete implementations). Swap with mocks in tests.

## Error Handling
- Global handlers: 400 for validation (`invalid_payload`), 500 for unhandled errors (`internal_error`) with `X-Request-Id`.
- Routers map `ValueError(Errors.*)` to HTTP codes (400/403/404/409) via `_raise`.
- Upload endpoints validate size (413) and MIME (415).

## Observability
- `RequestIdMiddleware` sets/propagates `X-Request-Id`.
- Action logs via `LogEvents` constants; include structured IDs (groupId, actorId, invitationId, etc.).

## Groups
- Models: `Group`, `GroupMembership` with `admin|member`, creator invariants (creator cannot leave/remove/demote), last-admin guard.
- Pagination on members (`limit/offset` + `X-Total-Count`), clamped via `utils/pagination.py`.
- Services: `GroupsService`, `MembershipsService`; Repos: `groups_repo.py`, `group_memberships_repo.py`.

## Payments
- `GroupPaymentCode` with statuses (`active|redeemed|expired`).
- Routes: create/list/void/redeem; admin-only for create/list/void.
- Codes are URL-safe tokens; lengths centralized in constants.

## Redaction (stub)
- `DlpService` is stubbed (no provider calls). `POST /redaction/test` for future integration testing.
- `POST /recipients/{id}/files/redact-upload` uses the stub; returns findings as empty list for now.

## Design Principles
- SOLID, DRY, KISS, YAGNI:
  - Single-responsibility per layer.
  - No business logic in routers or repositories.
  - No magic numbers/strings; use constants.
  - Keep interfaces small and focused; constructor DI for services.


