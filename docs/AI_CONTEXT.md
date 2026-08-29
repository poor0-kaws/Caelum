# Context for AI changes

Read this file when changing the recommendation logic, adding an LLM, or asking an AI to explain a market signal.

## Facts the AI must not invent

- Observed temperatures come from NWS station `KNYC` in Central Park.
- Forecast temperatures come from the NWS point endpoint for the configured NYC coordinates.
- Prices come from Kalshi's public market endpoint.
- The initial distribution comes from NOAA NBM maximum-temperature percentiles.
- After 30 completed days, the app uses real KNYC forecast errors without assuming a distribution shape.
- The local model is not backtested merely because it has collected 30 days.
- The application is read-only and cannot place trades.

## If an LLM is added later

Use it to explain already-calculated facts, not to silently replace the math.

Give the model one structured input containing:

- the exact observation timestamp and values;
- the exact forecast timestamp and values;
- each market ticker, range, bid, ask, and model probability;
- the fixed scoring assumptions;
- the active probability source and completed calibration-day count;
- the limitations listed below.

Require structured output with these fields:

```json
{
  "summary": "plain-language explanation",
  "supporting_facts": ["fact copied from input"],
  "risks": ["specific missing factor"],
  "data_quality_warning": null
}
```

Reject the answer if it names a ticker, price, temperature, or probability that was not in the input. Show the deterministic recommendation even when the LLM fails.

## Limits that must stay visible

- The model does not include fees or slippage.
- It does not use the full order book.
- It does not account for settlement-rule details.
- Thirty days is too small to separate forecast bias by season or weather regime.
- It has not been backtested.

The UI must call the output an educational signal, not a guaranteed opportunity.
