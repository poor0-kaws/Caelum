# NYC Weather Market Dashboard

A small, read-only React dashboard that compares New York City weather data with Kalshi high-temperature contracts.

It starts in sample mode, so you can see the complete interface without keys or network access. Live mode reads public NWS and Kalshi endpoints. It cannot log in, place an order, or move money.

## What you are looking at

Think of the app as three simple boxes connected in a row:

```text
NWS weather + Kalshi prices -> Python scoring service -> React dashboard
```

- The NWS client gets observed temperatures and the forecast.
- The Kalshi client gets open NYC temperature contracts and their prices.
- The scoring service estimates a rough probability for each temperature range.
- The React app turns that one JSON response into a readable screen.

The score is intentionally simple. It assumes the final temperature is shaped like a bell curve around the projected high, with 2.25°F of uncertainty. 

## Run the dashboard

Open two terminal windows.

### Terminal 1: start the Python API

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
uvicorn app.main:app --reload
```

The API will be available at `http://127.0.0.1:8000`.

### Terminal 2: start React

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`.

## Useful commands

Run the backend tests:

```bash
cd backend
PYTHONPATH=. python -m unittest discover -s tests -v
```

Check and build the frontend:

```bash
cd frontend
npm run lint
npm run build
```

## Folder map

```text
backend/app/clients/       fetch and parse outside data
backend/app/services/      combine data and calculate the signal
backend/app/models.py      shared Python data shapes
backend/app/main.py        small HTTP boundary
frontend/src/components/  focused React screen pieces
frontend/src/lib/         fetching and formatting helpers
frontend/src/types.ts      the browser's copy of the API shape
docs/                     architecture and AI context
```

## What changed from the original script

- Removed the private-key requirement from the read-only path.
- Replaced one long command-line flow with small modules that each have one job.
- Removed the duplicate `Market` class.
- Added request timeouts and proper HTTP error handling.
- Switched to Kalshi's current `external-api.kalshi.com` endpoint and dollar price fields.
- Added a deterministic scoring step that can be tested without an AI model.
- Added loading, empty, error, live, and sample states to the React screen.
- Added clear safety boundaries: this repository never places trades.

## Important limits

- A positive edge is only a rough estimate, not proof that a trade is good.
- Fees, slippage, order-book depth, forecast revisions, and market settlement details are not modeled.
- The contract parser prefers structured strike fields and falls back to reading the market title. New contract formats need tests.
- Live mode depends on two outside services, so it can fail even when this code is working.

For the reasoning behind the boundaries, read [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md). For future AI work, read [docs/AI_CONTEXT.md](docs/AI_CONTEXT.md).
