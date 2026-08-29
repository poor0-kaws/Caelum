# Architecture

## The main idea

Each module should answer one easy question.

```text
clients:   "What did the outside service say?"
services:  "What does our app calculate from that data?"
API:       "How do we send the answer to the browser?"
React:     "How do we show the answer to a person?"
```

This matters because outside APIs change. When Kalshi changes a field name, the fix belongs in one client instead of leaking through the whole app.

## Request flow

1. React asks `GET /api/dashboard?mode=sample` or `mode=live`.
2. `DashboardService` picks sample data or calls the two public clients.
3. `score_markets` gives every contract a model probability and estimated edge.
4. FastAPI converts the dataclasses into JSON.
5. React renders the overview, chart, recommendation, and market table.

## Safety boundary

The backend has no authenticated Kalshi client and no order route. That is intentional.

Adding order placement would be a different product with different risks. It would need authentication, position limits, idempotency, audit logs, confirmation screens, and much stronger testing. Do not slip that work into the read-only client.

## Scoring model

The projected high is the larger of:

- today's observed KNYC high;
- today's NWS daytime forecast high.

The model treats the final high as a normal distribution centered on that number. The standard deviation is `2.25°F`. For each Kalshi range:

```text
modeled edge = model probability - current YES ask
```

The result says `WAIT` when the best modeled edge is below 3 cents.

These numbers are transparent constants in `backend/app/services/recommendation.py`. They are learning defaults, not fitted parameters.

## Data contracts

Python dataclasses in `backend/app/models.py` are the backend source of truth. TypeScript interfaces in `frontend/src/types.ts` mirror the JSON response.

When a response field changes, update both files in the same change. Then build the frontend and run the backend tests.
