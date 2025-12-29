# DrZaius – Plain-English Overview

This backend powers a mobile app where people can:
- Create an account as a recipient (patient) or caregiver.
- Invite others (by email) to connect as caregivers/recipients.
- Organize people into groups (with admins and members).
- Generate short-lived payment codes for groups (for future billing integration).
- Upload documents (today: stubbed redaction; future: real redaction + RAG indexing).

## Who’s who
- Recipient: The person receiving care. Can invite a caregiver.
- Caregiver: The person providing care. Can invite a recipient.
- Group: A small team. One user creates the group and is the “creator admin.”

## Core flows
1) Invitations
   - Send invite by email.
   - The receiver sees it under “received invites” and can accept or decline.
   - On accept, the link between recipient and caregiver is created.
   - Emails can include a deep link to accept (MVP-ready).

2) Groups
   - Create a group (you become the creator admin).
   - Add/remove members, change roles (admin/member).
   - Guardrails:
     - Creator cannot leave, be removed, or be demoted.
     - There must always be at least one admin (last-admin protection).
   - Members list supports pagination.

3) Payment codes (for groups)
   - Admins can create codes (optionally with an expiry time).
   - Admins can list and void codes.
   - Any authenticated user can redeem a code (if valid).

4) Documents (stubbed)
   - Upload a file for a recipient.
   - Basic validation: allowed MIME types (PDF/PNG/JPEG) and max file size.
   - Redaction endpoint is stubbed; we’ll plug in a real DLP provider later.

## What happens on errors
- You’ll get a clear error code (e.g., “forbidden”, “user_not_found”) and correct HTTP status.
- A request ID is attached to every response so we can trace problems in logs.

## Why the code is structured this way
- Routers handle HTTP only.
- Services contain business rules.
- Repositories talk to the database.
- Constants keep strings and paths consistent.
- This makes the code easier to test, change, and reason about.

## What’s next (after MVP)
- Real redaction via Google Cloud DLP.
- Vertex RAG integration for document search/chat.
- Frontend polish: pagination UI, better invite UX, and notifications.


