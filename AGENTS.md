# AGENTS.md

This is a read-only NYC weather-market dashboard built with FastAPI, React, and TypeScript.

## Project map

- `backend/app/clients/`: external NWS and Kalshi parsing
- `backend/app/services/`: dashboard assembly and recommendation math
- `backend/data/`: documentation for the ignored local calibration ledger
- `backend/app/models.py`: backend data contracts
- `frontend/src/components/`: focused UI components
- `frontend/src/types.ts`: browser copy of the API contract
- `docs/ARCHITECTURE.md`: boundaries and request flow
- `docs/AI_CONTEXT.md`: required context for recommendation or LLM work

## Commands

```bash
# Backend tests
cd backend && PYTHONPATH=. python -m unittest discover -s tests -v

# Backend development server
cd backend && uvicorn app.main:app --reload

# Frontend checks
cd frontend && npm run lint && npm run build

# Frontend development server
cd frontend && npm run dev
```

## Rules for every task

- Write small, readable functions with names that explain their job.
- Prefer early returns and plain control flow over clever abstractions.
- Explain new ideas from first principles in comments and documentation.
- Keep the application read-only. It must not authenticate to Kalshi or place orders.
- Keep secrets, private keys, `.env`, build output, and dependencies out of git.
- Keep the app live-data only. Do not add invented fallback data when a provider fails.

## When changing external data clients

- Set a timeout for every request and surface a useful error.
- Parse provider-specific fields inside the matching client.
- Prefer Kalshi `*_dollars` and `*_fp` fields over removed cent fields.
- Add a parser test for every new contract shape.

## When changing recommendation logic

- Read `docs/AI_CONTEXT.md` first.
- Keep assumptions visible as named constants.
- Preserve the fixed 01 UTC forecast issue time so historical errors remain comparable.
- Keep NBM percentiles as the fallback until enough real KNYC outcomes exist.
- Never seed the calibration ledger with invented rows.
- Return `WAIT` when the data is empty or the signal is weaker than the threshold.
- Describe the result as educational and uncalibrated until backtests prove otherwise.

## When changing the API contract

- Update `backend/app/models.py` and `frontend/src/types.ts` together.
- Keep `GET /api/dashboard` backward compatible unless the user asks for a breaking change.

## When changing the interface

- Preserve loading, empty, error, and live-data states.
- Keep keyboard focus visible and text contrast readable.
- Make every multi-column layout collapse cleanly below 768px.
- Use one accent color and the existing radius scale.

## When writing tests

- Test pure services without network access.
- Cover success, empty input, and failure boundaries.
- Run backend tests, frontend lint, and frontend build before finishing.
