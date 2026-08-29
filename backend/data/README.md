# KNYC calibration data

The live dashboard creates `knyc_forecast_history.json` in this folder.

Each row pairs one fixed 01 UTC NBM median forecast with the final KNYC observed high for the same New York calendar day. The application keeps the first forecast for a date and fills in the outcome after that date ends.

The local file is ignored by git because it is runtime data. No invented rows are used for calibration.
