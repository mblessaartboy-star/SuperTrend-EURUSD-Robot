# Pocket Option EUR/USD Signal Robot V2

Configured for both **regular EUR/USD** and **EUR/USD OTC**, with 1-minute and 5-minute analysis. It produces BUY / SELL / WAIT signals only and does not execute trades.

## Run
Python 3.10+:
```bash
python -m venv .venv
# Activate the environment, then:
pip install -r requirements.txt
python app.py
```
Open http://127.0.0.1:5000

## Candle input
POST `/api/analyze` with JSON:
```json
{
  "market": "regular",
  "timeframe": "1m",
  "candles": [
    {"open": 1.08, "high": 1.081, "low": 1.079, "close": 1.0805}
  ]
}
```
At least 40 completed OHLC candles, oldest first, are required. Use `"market":"otc"` for OTC candles. Never mix regular and OTC candles.

## Telegram
Set `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` as private environment variables on your host. Create a bot with Telegram's official @BotFather. Never share the token or your Pocket Option credentials.

## Data feed limitation
V2 has market selection and analysis logic, but it does not connect to Pocket Option's live/private chart feed or retrieve OTC candles. You must supply data from a legitimate compatible feed or export. OTC prices are platform-specific and may not match ordinary EUR/USD forex feeds. No Pocket Option login, password, cookies, or account session are requested.

For hosting use a Python host and start command `gunicorn app:app`.

## Risk
Binary options are highly risky. Indicator signals can be wrong; no win rate or profit is guaranteed. Backtest and use demo trading first. This is educational software, not financial advice.
