# Caelum

A small, read-only React dashboard that compares New York City weather data with Kalshi high-temperature contracts.

The dashboard uses live public data from NWS, NOAA NBM, and Kalshi. It needs an internet connection, but it does not need trading credentials. It cannot log in, place an order, or move money.

## What you are looking at

Think of the app as three simple boxes connected in a row:

```text
NWS weather + NBM probabilities + Kalshi prices -> scoring service -> React
```

- The NWS client gets observed temperatures and the forecast.
- The NBM client gets calibrated maximum-temperature percentiles.
- The Kalshi client gets open NYC temperature contracts and their prices.
- The scoring service estimates a rough probability for each temperature range.
- The React app turns that one JSON response into a readable screen.

The probability model has two stages:

1. It starts with NOAA NBM maximum-temperature percentiles. The code draws straight lines between the published 10th, 25th, 50th, 75th, and 90th percentiles. It does not assume a bell curve.
2. It records one consistent KNYC forecast and the final observed high each day. After 30 completed days, those real local forecast errors become the probability distribution.

The model also removes outcomes below a high temperature that has already been observed. This is more honest than a fixed uncertainty number, but it is still not a proven trading strategy.

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

The first load can take longer because the API must download the current NOAA NBM bulletin. If an outside provider is unavailable, the dashboard shows a retry button instead of invented data.

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
backend/data/              local calibration ledger documentation
backend/app/main.py        small HTTP boundary
frontend/src/components/  focused React screen pieces
frontend/src/lib/         fetching and formatting helpers
frontend/src/types.ts      the browser's copy of the API shape
docs/                     architecture and AI context
```
