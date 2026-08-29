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

1. React asks `GET /api/dashboard`.
2. `DashboardService` calls the three public clients. There is no fallback to invented data.
3. The probability service chooses NBM percentiles or the mature KNYC history.
4. `score_markets` gives every contract a model probability and estimated edge.
5. FastAPI converts the dataclasses into JSON.
6. React renders the overview, chart, recommendation, and market table.

## Safety boundary

The backend has no authenticated Kalshi client and no order route. That is intentional.

Adding order placement would be a different product with different risks. It would need authentication, position limits, idempotency, audit logs, confirmation screens, and much stronger testing. Do not slip that work into the read-only client.

## Probability and scoring

The projected high is the larger of:

- today's observed KNYC high;
- today's NWS daytime forecast high.

The starting distribution comes from NOAA's NBM 01 UTC probabilistic bulletin for KNYC. The code connects the published 10th, 25th, 50th, 75th, and 90th maximum-temperature percentiles with straight lines. No normal-distribution shape is imposed.

Each live request stores the NBM median and later fills in the final KNYC high. After 30 completed days, the app shifts the current forecast by each real historical error and counts how many shifted outcomes fall in each market range. The forecast is fixed at 01 UTC so days are comparable.

If today's observed KNYC high already exceeds part of the distribution, impossible lower outcomes are removed and the remaining probabilities are rescaled.

For each Kalshi range:

```text
modeled edge = model probability - current YES ask
```

The result says `WAIT` when the best modeled edge is below 3 cents.

The 3-cent trade threshold remains a transparent learning default. It is not fitted or backtested.

## Data contracts

Python dataclasses in `backend/app/models.py` are the backend source of truth. TypeScript interfaces in `frontend/src/types.ts` mirror the JSON response.

When a response field changes, update both files in the same change. Then build the frontend and run the backend tests.
