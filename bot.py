
import requests
import pandas as pd
import telebot
import time
from datetime import datetime

# إعدادات البوت
SYMBOL = "EUR/JPY"
INTERVAL = "5min"
API_KEY = "0dfd851139504e25a0fb17b700185b4a"
TELEGRAM_TOKEN = "7228461122:AAHdZYPpQBCkyEACzuBJ6J_SA0bNbRVLokw"
CHAT_ID = "5600364026"

bot = telebot.TeleBot(TELEGRAM_TOKEN)

def get_data():
    url = f"https://api.twelvedata.com/time_series?symbol=EUR/JPY&interval={INTERVAL}&apikey={API_KEY}&outputsize=30"
    response = requests.get(url)
    data = response.json()
    if "values" in data:
        df = pd.DataFrame(data["values"])
        df["datetime"] = pd.to_datetime(df["datetime"])
        df = df.sort_values("datetime")
        df["close"] = df["close"].astype(float)
        df["open"] = df["open"].astype(float)
        df["rsi"] = df["close"].rolling(window=14).apply(lambda x: (100 - (100 / (1 + ((x.diff().clip(lower=0).sum()) / (-x.diff().clip(upper=0).sum() + 1))))))
        return df
    else:
        print("Error fetching data:", data)
        return pd.DataFrame()

def check_buy_signal(df):
    last = df.iloc[-1]
    prev = df.iloc[-2]
    return last["close"] > last["open"] and prev["close"] < prev["open"] and last["rsi"] < 30

def check_sell_signal(df):
    last = df.iloc[-1]
    prev = df.iloc[-2]
    return last["close"] < last["open"] and prev["close"] > prev["open"] and last["rsi"] > 70

def send_signal(signal_type):
    message = f"إشارة دخول: {signal_type}\nالرمز: {SYMBOL}"
    bot.send_message(CHAT_ID, message)

def is_trading_time():
    now = datetime.utcnow()
    weekday = now.weekday()  # Monday = 0, Sunday = 6
    hour = now.hour
    if weekday in [5, 6]:  # Saturday, Sunday
        return False
    return 10 <= hour < 18  # Between 10:00 and 18:00 UTC

print("تشغيل البوت...")

while True:
    if is_trading_time():
        df = get_data()
        if not df.empty:
            if check_buy_signal(df):
                send_signal("شراء")
            elif check_sell_signal(df):
                send_signal("بيع")
    else:
        print("خارج أوقات التداول")
    time.sleep(60)
