# Ask ALYF Settings, History, and Prompts Fix Implementation Plan

> **For agentic workers:** Execute in the current session because the user explicitly disabled subagents. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Restore settings saves, remove test-created conversation pollution, and make suggested prompts reappear and rerandomize for new chats.

**Architecture:** Remove the invalid schema artifact, make integration tests own and clean their records, and centralize prompt-cache invalidation at both bootstrap and new-conversation boundaries.

**Tech Stack:** Frappe v16, Python 3.14 tests, browser JavaScript, Node `node:test`, Docker Compose.

---

### Task 1: Remove invalid settings metadata

- [ ] Add a regression assertion that `Ask ALYF Settings` has no numeric multi-currency field.
- [ ] Remove `111` from the DocType JSON.
- [ ] Migrate and verify effective metadata is not submittable and contains no `111`.

### Task 2: Clean test-owned conversations

- [ ] Add failing cleanup assertions around tests that create conversations.
- [ ] Track created names and delete them in teardown.
- [ ] Export and delete only the confirmed historical test rows.

### Task 3: Invalidate suggested prompt cache

- [ ] Add a failing Node source/behavior test for bootstrap and same-name new conversation invalidation.
- [ ] Add a single reset method and call it at both boundaries.
- [ ] Run Node tests and verify the fix.

### Task 4: Release verification

- [ ] Run focused and full Ask ALYF tests.
- [ ] Commit with a Chinese commit message on `haina`.
- [ ] Build assets, clear cache, restart services, and verify settings save, clean history, and prompt display.
