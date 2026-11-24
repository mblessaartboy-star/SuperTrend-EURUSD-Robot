import os, threading
from datetime import datetime, timezone
from flask import Flask, render_template, request, jsonify
from strategy import analyze_candles

app = Flask(__name__)
LATEST = {}
LOCK = threading.Lock()

def telegram_send(message):
    token, chat_id = os.getenv("TELEGRAM_BOT_TOKEN"), os.getenv("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        return False, "Telegram is not configured"
    try:
        import requests
        r = requests.post(f"https://api.telegram.org/bot{token}/sendMessage",
                          json={"chat_id": chat_id, "text": message}, timeout=10)
        r.raise_for_status()
        return True, "sent"
    except Exception as exc:
        return False, str(exc)


@app.get("/")   
def index():
    with LOCK:   
        return jsonify({"status": "Bot is running", "signals": dict(LATEST)})

@app.get("/health")
def health():
    return jsonify({"status": "ok", "version": "2.0", "asset": "EUR/USD"})

@app.post("/api/analyze")
def analyze():
    data = request.get_json(silent=True) or {}
    market = str(data.get("market", "regular")).lower()
    timeframe = str(data.get("timeframe", "1m")).lower()
    if market not in ("regular", "otc"):
        return jsonify({"error": "market must be regular or otc"}), 400
    if timeframe not in ("1m", "5m"):
        return jsonify({"error": "timeframe must be 1m or 5m"}), 400
    candles = data.get("candles")
    if not isinstance(candles, list) or len(candles) < 40:
        return jsonify({"error": "Provide at least 40 completed OHLC candles"}), 400
    try:
        result = analyze_candles(candles)
    except (ValueError, TypeError, KeyError) as exc:
        return jsonify({"error": str(exc)}), 400

    result.update({
        "symbol": "EUR/USD",
        "market": market.upper(),
        "timeframe": timeframe,
        "updated_at": datetime.now(timezone.utc).isoformat()
    })
    key = f"EURUSD_{market}_{timeframe}"
    with LOCK:
        previous = LATEST.get(key)
        LATEST[key] = result

    if result["signal"] in ("BUY", "SELL") and (
        not previous or previous.get("signal") != result["signal"]
    ):
        message = (
            f"Pocket Option EUR/USD {market.upper()} signal\\n"
            f"{timeframe} | {result['signal']} | Score {result['score']}/5\\n"
            f"Close: {result['close']} | RSI: {result['rsi']}\\n"
            f"Trend: {result['trend']}\\n"
            f"Reasons: {', '.join(result['reasons'])}\\n"
            "Educational signal only. Verify before trading."
        )
        telegram_send(message)
    return jsonify(result)

@app.get("/api/signals")
def signals():
    with LOCK:
        return jsonify(LATEST)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")), debug=False)
