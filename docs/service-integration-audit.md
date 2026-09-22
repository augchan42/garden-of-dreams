# Existing service audit — 2026-09-23

Read-only inspection of `../8bitoracle-next/src` found existing group-divination endpoints. No remote API requests or mutations were made.

- `GET /api/group-divination/topics?locale=en`: returns `{ timeless: Topic[], temporal: Topic[] }` through `getActiveTopics(locale)`. Each row contains `id`, `title`, `slug`, `description`, `topic_type`, `created_at`, `expires_at`, `metadata`, `is_active`, and `locale`; the action filters active topics to the requested locale. This can supply the current-events pavilion after confirming the deployed origin and testing public access. The handler uses a cookie-aware server Supabase client; database row policies have not yet been checked.
- `POST /api/group-divination/read`: accepts topicId, username, hexagrams, participant_count and locale, and generates/stores a group reading through the server AI provider and Supabase. This is a write and potentially a paid model operation; the local exploration scene does not call it.
- `GET /api/shared-divination/[shareId]` exists, but its response and access rules still need inspection.
- No `src` filename containing `garden` was found beyond hexagram content. The original garden design includes illustrative endpoints, not evidence of implemented garden state or AI direction services.

Next: inspect actual topic/read/share schemas and existing authentication. Keep external data access behind a dedicated adapter. Do not invent a live feed, treat private readings as public, or embed server credentials in Godot. Local rooms and traversal are independent of these services.

## Public topic browser

The source application's canonical configuration identifies `https://app.8bitoracle.ai`. An anonymous GET to `/api/group-divination/topics?locale=en` returned HTTP 200 with five timeless topics and one temporal topic during this implementation. The installed Godot client independently loaded the same six topics.

`godot/services/topics.gd` makes only this read-only request, with a 12-second timeout and a 2 MB response cap. It validates both arrays and each topic's identity/title/description/status/locale, filters inactive or non-English rows, and passes plain text to the browser. It does not create readings, send credentials, or interpret topic content as commands.

Qinfang's `Current topics` action opens `runtime/topic_browser.gd`. It labels the response as live public content, supports refresh and scrolling, preserves already-loaded content after a refresh failure, and restores underlying controls when closed. Reading creation, private history and AI movement remain unconnected. Desktop and phone-sized native rendering were checked; web-export CORS and authentication flows are still unverified.

Evidence: `tests/test_topics.gd` passed response-schema cases; `tests/render_topics.gd` loaded six actual public topics, exercised the retained-data error state and closure, and checked the panel remains inside the viewport. The initial phone render exposed a title-width overflow; clipping/ellipsis fixed it. The test captures are `docs/reference/topics-desktop.png` and `topics-mobile.png`.
