import websocket
import json
import pandas as pd
import plotly.graph_objects as go
import pytz
from datetime import datetime

# Boş listeler oluşturarak mum verilerini depoluyoruz
timestamps = []
opens = []
closes = []
highs = []
lows = []

def on_message(ws, message):
    global timestamps, opens, closes, highs, lows

    data = json.loads(message)
    candle = data['k']
    timestamps.append(candle['t'])
    opens.append(float(candle['o']))
    closes.append(float(candle['c']))
    highs.append(float(candle['h']))
    lows.append(float(candle['l']))

    # Grafik güncelliyoruz
    update_chart()

def on_error(ws, error):
    print(error)

def on_close(ws):
    print("WebSocket bağlantısı kapatıldı")

def on_open(ws):
    print("WebSocket bağlantısı başarıyla açıldı")
    ws.send('{"method": "SUBSCRIBE","params": ["ethusdt@kline_1s"],"id": 1}')

websocket.enableTrace(True)
ws = websocket.WebSocketApp("wss://stream.binance.com:9443/ws",
                            on_message=on_message,
                            on_error=on_error,
                            on_close=on_close,
                            on_open=on_open)

# Grafik güncelliyoruz
def update_chart():
    df = pd.DataFrame({'timestamps': timestamps, 'opens': opens, 'closes': closes, 'highs': highs, 'lows': lows})
    df['timestamps'] = pd.to_datetime(df['timestamps'], unit='ms')
    
    # Zaman damgalarını Türkiye saat dilimine dönüştürüyoruz
    turkey_tz = pytz.timezone('Europe/Istanbul')
    df['timestamps'] = df['timestamps'].dt.tz_localize(pytz.UTC).dt.tz_convert(turkey_tz)

    df.set_index('timestamps', inplace=True)

    fig = go.Figure(data=[go.Candlestick(x=df.index,
                                         open=df['opens'],
                                         close=df['closes'],
                                         high=df['highs'],
                                         low=df['lows'])])

    fig.update_layout(title='ETH Mumları',
                      xaxis_title='Tarih',
                      yaxis_title='Fiyat')

    fig.write_html('eth_mumları.html', auto_open=True)  # Grafiği tek bir sekmede kaydedip ve açıyoruz

# WebSocket bağlantısını başlatıyoruz
ws.run_forever()
