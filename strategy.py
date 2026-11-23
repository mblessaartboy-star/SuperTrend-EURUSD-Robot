def _ema(values, period):
    alpha = 2 / (period + 1)
    out = [float(values[0])]
    for value in values[1:]:
        out.append(alpha * float(value) + (1-alpha) * out[-1])
    return out

def _rsi(values, period=14):
    changes = [float(values[i])-float(values[i-1]) for i in range(1,len(values))]
    gains = [max(x,0) for x in changes]
    losses = [max(-x,0) for x in changes]
    avg_gain, avg_loss = sum(gains[:period])/period, sum(losses[:period])/period
    for i in range(period,len(gains)):
        avg_gain = (avg_gain*(period-1)+gains[i])/period
        avg_loss = (avg_loss*(period-1)+losses[i])/period
    if avg_loss == 0: return 100.0
    rs = avg_gain/avg_loss
    return 100-(100/(1+rs))

def analyze_candles(candles):
    if len(candles)<40: raise ValueError("At least 40 candles are required")
    closes,highs,lows=[],[],[]
    for c in candles:
        o,h,l,cl=(float(c[k]) for k in ("open","high","low","close"))
        if not (l<=min(o,cl)<=max(o,cl)<=h): raise ValueError("Invalid OHLC candle")
        closes.append(cl);highs.append(h);lows.append(l)
    e9,e21=_ema(closes,9),_ema(closes,21)
    macd=[a-b for a,b in zip(_ema(closes,12),_ema(closes,26))]
    macd_sig=_ema(macd,9);rsi=_rsi(closes)
    buy=sell=0;reasons=[]
    if e9[-1]>e21[-1]: buy+=1;reasons.append("EMA 9 above EMA 21")
    elif e9[-1]<e21[-1]: sell+=1;reasons.append("EMA 9 below EMA 21")
    if macd[-1]>macd_sig[-1] and macd[-2]<=macd_sig[-2]: buy+=2;reasons.append("MACD bullish crossover")
    elif macd[-1]<macd_sig[-1] and macd[-2]>=macd_sig[-2]: sell+=2;reasons.append("MACD bearish crossover")
    elif macd[-1]>macd_sig[-1]: buy+=1;reasons.append("MACD momentum bullish")
    elif macd[-1]<macd_sig[-1]: sell+=1;reasons.append("MACD momentum bearish")
    if 50<rsi<70: buy+=1;reasons.append("RSI supports upward momentum")
    elif 30<rsi<50: sell+=1;reasons.append("RSI supports downward momentum")
    elif rsi>=70: reasons.append("RSI overbought — caution")
    elif rsi<=30: reasons.append("RSI oversold — caution")
    high,low=max(highs[-20:]),min(lows[-20:]);close=closes[-1]
    near_res=(high-close)/max(abs(close),1e-12)<.001
    near_sup=(close-low)/max(abs(close),1e-12)<.001
    if buy>=3 and buy>sell and not near_res: signal="BUY"
    elif sell>=3 and sell>buy and not near_sup: signal="SELL"
    else:
        signal="WAIT"
        if near_res: reasons.append("Price near recent resistance")
        if near_sup: reasons.append("Price near recent support")
        if not reasons: reasons.append("Indicators are not sufficiently aligned")
    trend="BULLISH" if e9[-1]>e21[-1] else "BEARISH" if e9[-1]<e21[-1] else "NEUTRAL"
    return {"signal":signal,"score":max(buy,sell),"buy_score":buy,"sell_score":sell,
      "close":round(close,6),"ema9":round(e9[-1],6),"ema21":round(e21[-1],6),
      "rsi":round(rsi,2),"macd":round(macd[-1],6),"macd_signal":round(macd_sig[-1],6),
      "trend":trend,"support":round(low,6),"resistance":round(high,6),"reasons":reasons}
