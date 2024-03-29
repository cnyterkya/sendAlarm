from binance.client import Client
import requests
import time
import config
import talib
import numpy as np
import logging
from datetime import datetime

logging.basicConfig(filename="log_file15.log", level=logging.DEBUG, format='%(asctime)s %(message)s', filemode='w')
logger = logging.getLogger()
# Binance API anahtarlarınızı buraya ekleyin
api_key = config.API_KEY
api_secret = config.API_SECRET
client = Client(api_key, api_secret)


def trading_strategy(symbol):
  # Binance API'den günlük kapanış fiyatlarını al
  klines = client.get_klines(symbol=symbol, interval=Client.KLINE_INTERVAL_15MINUTE)
  high_prices = [float(kline[2]) for kline in klines]
  low_prices = [float(kline[4]) for kline in klines]
  close_prices = [float(kline[4]) for kline in klines]

  # CCI hesapla
  cci_length = 8
  cci_values = talib.CCI(np.array(high_prices),np.array(low_prices),np.array(close_prices), cci_length)

  # Alım-satım sinyali üret
  buy_signal = cci_values[-1] < -90 and cci_values[-2] >= -90
  sell_signal = cci_values[-1] > 90 and cci_values[-2] <= 90

  return buy_signal, sell_signal

# Telegram'a mesaj gönderen fonksiyon
def send_telegram_message(message):
  # Buraya kendi Telegram botunuzun ve chat ID'nizin bilgilerini ekleyin
  bot_token = config.BOT_TOKEN
  chat_id = config.RECEIVER_ID
  url = f'https://api.telegram.org/bot{bot_token}/sendMessage'
  params = {'chat_id': chat_id, 'text': message}
  requests.post(url, params=params)

  # Sembol listesini dosyadan oku
with open('symbol_list.txt', 'r') as file:
  symbols = file.read().splitlines()
  now = datetime.now()

# Ana döngü
while True:
  # Stratejiyi uygula
  for symbol in symbols:
    buy_signal, sell_signal = trading_strategy(symbol)
    logger.info(f"evaluating for {symbol}. Time: {now}")
    if buy_signal:
      message = f"BUY signal for {symbol}. Price: {client.get_symbol_ticker(symbol=symbol)['price']}"
      logger.info(message)
      send_telegram_message(message)
    elif sell_signal:
      message = f"SELL signal for {symbol}. Price: {client.get_symbol_ticker(symbol=symbol)['price']}"
      logger.info(message)
      send_telegram_message(message)

  # Bir dakika bekleyin
  time.sleep(300)
