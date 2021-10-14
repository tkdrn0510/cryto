import json
import time
import requests
import datetime
import telegram
import traceback
import pyupbit
from pytz import timezone
from decimal import *

# 거래 대금 상위 n개
def get_top_k(n):
    coin_list = []
    tickers = pyupbit.get_tickers(fiat="KRW")
    market_code = ','.join(tickers)

    url = "https://api.upbit.com/v1/ticker"
    params = {
        "markets": market_code
    }
    response = requests.get(url, params=params).json()

    for info in response:
        coin_list.append([info['market'], info['acc_trade_price_24h']])

    coin_list.sort(key=lambda x: x[1], reverse=True)

    top_k_list = []
    for i in coin_list:
        top_k_list.append(i[0])
    return top_k_list[:n]


# 당일 최고가 계산 (프로그램 시작시 이미 목표가 돌파한 코인 구매 방지)
def get_highest_price(tickers):
    highest_price = dict()
    market_code = ','.join(tickers)
    url = "https://api.upbit.com/v1/ticker"
    params = {
        "markets": market_code
    }
    response = requests.get(url, params=params).json()

    for info in response:
        highest_price[info['market']] = info['high_price']

    return highest_price


# 목표가 계산
def get_target_price_list(tickers, k):
    target_price_list = dict()
    for ticker in tickers:
        target_price_list[ticker] = get_target_price(ticker, k)
        time.sleep(0.1)  # 요청 수 제한 (초당 10회)

    return target_price_list


def get_target_price(ticker, k):
    yesterday = datetime.date.today() - datetime.timedelta(1)
    df = pyupbit.get_ohlcv(ticker, interval="day", count=2)
    chart_yesterday = df.index[0].date()
    if chart_yesterday != yesterday:
        target_price = None
    else:
        target_price = df.iloc[0]['close'] + (df.iloc[0]['high'] - df.iloc[0]['low']) * k

    return target_price


# 이동평균선 계산
def get_ma(ticker, days):
    df = pyupbit.get_ohlcv(ticker, interval="day", count=days+1)
    ma = df['close'].rolling(window=days).mean()
    return ma[-2]


def get_ma_list(tickers, days):
    ma_list = dict()
    for ticker in tickers:
        ma_list[ticker] = get_ma(ticker, days)
        time.sleep(0.1)

    return ma_list

# Load API keys
with open("setting.json") as f:
    setting_loaded = json.loads(f.read())

# Upbit
access = setting_loaded["access_key"]
secret = setting_loaded["secret_key"]

# Telegram
telegram_token = setting_loaded["telegram_token"]
telegram_chat_id = setting_loaded["telegram_chat_id"]
telegram_bot = telegram.Bot(token=telegram_token)

# Initialize
upbit = pyupbit.Upbit(access, secret)
start_time = datetime.time(9)
sell_time = datetime.time(8, 59, 30)
tickrate = 0.5
fee = 0.0005
top_k = 20
portfolio_limit = 4
k_value = 0.15
stop_loss = 0.05
buymode = True  # ToDo: 매수 on off 추가
buy_time_data = {}
if __name__ == "__main__":
    fmt = "%Y-%m-%d %H:%M:%S"

#코인티커 순서 확인 문자
a = 0

#구매여부 확인 문자
b = 0

#매수구매 확인 문자
c = 0

#구매가격 확인 문자
d = 0

#현제시세 확인 문자
e = 0

#수익률 확인 문자
h = 0

while True:
    try:
        # 코인 목록 수
        coin_num = len(pyupbit.get_tickers(fiat="KRW"))
        print(a)

        # 코인이름 가져오기
        if a < coin_num:
            tickers = pyupbit.get_tickers(fiat="KRW")[a]
        else:
            tickers = pyupbit.get_tickers(fiat="KRW")[0]

        # 구매여부 확인 코드
        if b <= coin_num - 1:
            buy_time_data.update({tickers: True})
            b = b + 1

        elif b > coin_num - 1:
            b = b + 1

        else:
            b = b + 1

        # 매수 구매 가격 저장코드
        if c <= coin_num - 1:
            buy_price.update({tickers: 0})
            c = c + 1

        elif c > coin_num - 1:
            c = c + 1

        else:
            c = c + 1
        now = datetime.datetime.now(timezone('Asia/Seoul'))
        current_price_list = pyupbit.get_current_price(top_k_list)

        # 코인 현재시세+현재가격
        tickers_now_time_price = pyupbit.get_current_price(tickers), now.strftime(fmt)

        # 코인 현재시세
        tickers_now_price2 = int(pyupbit.get_current_price(tickers))

        # 코인 신호선(9분 이동평균)
        tickers_df1 = pyupbit.get_ohlcv(tickers, interval="minute1", count=9)
        tickers_signal = tickers_df1['close'].rolling(9).mean().iloc[-1]

        # 코인 12분 이동평균
        tickers_df2 = pyupbit.get_ohlcv(tickers, interval="minute1", count=12)
        tickers_ma12 = tickers_df2['close'].rolling(12).mean().iloc[-1]

        # 1분 전 코인 12분 이동평균
        tickers_df3 = pyupbit.get_ohlcv(tickers, interval="minute1", count=12)
        tickers_ma12_1mb = tickers_df3['close'].rolling(12).mean().iloc[-2]

        # 코인 21분 이동평균
        tickers_df4 = pyupbit.get_ohlcv(tickers, interval="minute1", count=21)
        tickers_ma21 = tickers_df4['close'].rolling(21).mean().iloc[-1]

        # 1분 전 코인 21분 이동평균
        tickers_df5 = pyupbit.get_ohlcv(tickers, interval="minute1", count=21)
        tickers_ma21_1mb = tickers_df5['close'].rolling(21).mean().iloc[-2]

        if a < coin_num - 1:
            # 매수조건 = 기본 매수조건
            if sell_time.hour == now.hour and sell_time.minute == now.minute and sell_time.second <= now.second < sell_time.second + 30:
                while hold:
                    ticker = hold.pop()
                    amount = upbit.get_balance(ticker)
                    response = upbit.sell_market_order(ticker, amount)
                    income = (current_price_list[ticker] - buy_price[ticker]) * amount
                    telegram_send(
                        f'⌛ 종가 매도\n📊 종목: {ticker}\n매도가: {current_price_list[ticker]}\n매수가: {buy_price[ticker]}\n수익: {income}\n{response}\n')
                time.sleep(30)
                continue

            # 9시 이전 판매, 9시 이후 새 타겟 프라이스 갱신 구현
            if start_time.hour == now.hour and start_time.minute + 1 == now.minute and start_time.second <= now.second < start_time.second + 10:
                updated_at = now
                top_k_list = get_top_k(top_k)
                target_price_list = get_target_price_list(top_k_list, k_value)
                ma_list = get_ma_list(top_k_list, 5)
                prev_balance = balance
                balance = upbit.get_balance(ticker="KRW")
                buy_list = []
                buy_price = dict()
                first_day = False
                telegram_send(f'⏳ 9시 재설정\n전일 잔고: {prev_balance}\n금일 잔고: {balance}\n수익: {balance - prev_balance}')
                time.sleep(10)
                continue

            for ticker in top_k_list:
                # 목표가 없을시 갱신하고 갱신해도 없을시 continue
                if target_price_list[ticker] is None:
                    target_price_list[ticker] = get_target_price(ticker, k_value)
                    if target_price_list[ticker] is None:
                        continue

                # 프로그램 가동 첫 날이면 고가와 목표가 비교 (이미 갱신했을 경우 구매 방지)
                if first_day and highest_price[ticker] > target_price_list[ticker]:
                    continue

                # 목표가 돌파 및 5일 이평선 기준 상승장일시 매수
                if a < coin_num - 1:
                    # 매수조건 = 기본 매수조건
                    if buy_time_data[tickers] == True and buy_price[tickers] == 0:
                        # 매수조건 = 9분 평균선이 MACD선(12분-21분) 을 상향돌파 즉,골든크로스 발생
                        if tickers_signal < (tickers_ma12 - tickers_ma21):
                            if current_price_list[ticker] > target_price_list[ticker] and current_price_list[ticker] > \
                                    ma_list[ticker] and len(buy_list) < portfolio_limit and buymode:
                                response = upbit.buy_market_order(ticker, balance / portfolio_limit * (1 - fee))
                                high_price_track[ticker] = current_price_list[ticker]
                                hold.append(ticker)
                                buy_price[ticker] = current_price_list[ticker]
                                buy_list.append(ticker)
                                telegram_send(
                                    f'🛒 목표가 매수\n종목: {ticker}\n매수가: {current_price_list[ticker]}\n목표가: {target_price_list[ticker]}\n{response}')
                                buy_time_data.update({tickers: False})
                                buy_price.update({tickers: tickers_now_price2})
                                d = int(buy_price[tickers])
                                a = a + 1
                        else:
                            print(tickers + " : 구매전 매수 준비중")
                            print(tickers_now_time_price)
                            a = a + 1

                    elif buy_time_data[tickers] == False and buy_price[tickers] > 0:
                        if ticker in buy_list:
                            if ticker in hold:
                                high_price_track[ticker] = max(high_price_track[ticker], current_price_list[ticker])
                                if (((tickers_now_price2 / d) - 1) * 100) < -1:
                                    if current_price_list[ticker] < high_price_track[ticker] * (1 - stop_loss):
                                        amount = upbit.get_balance(ticker)
                                        response = upbit.sell_market_order(ticker, amount)
                                        hold.remove(ticker)
                                        income = (current_price_list[ticker] - buy_price[ticker]) * amount
                                        telegram_send(
                                            f'📉 매도\n종목: {ticker} / 매도가: {current_price_list[ticker]}\n매수가: {buy_price[ticker]}\n수익: {income}\n{response}')
                                        d = int(buy_price[tickers])
                                        e = int(tickers_now_price2)
                                        f = (((e / d) - 1) * 100)
                                        print("수익률 :", "%.2f" % (f), "%")
                                        h = f + h
                                        print("수익률 합 : ", "%.2f" % (h), "%")
                                        telegram_send(f"📉수익률 : " + "%.2f" % (f) + "%")
                                        telegram_send(f"📉총 수익률 : " + "%.2f" % (h) + "%")
                                        buy_time_data.update({tickers: True})
                                        buy_price.update({tickers: 0})
                                        a = a + 1

                                if (tickers_ma12 - tickers_ma21) < (
                                        tickers_ma12_1mb - tickers_ma21_1mb) or tickers_signal > (
                                        tickers_ma12 - tickers_ma21):
                                    amount = upbit.get_balance(ticker)
                                    response = upbit.sell_market_order(ticker, amount)
                                    hold.remove(ticker)
                                    income = (current_price_list[ticker] - buy_price[ticker]) * amount
                                    telegram_send(
                                        f'📉 매도\n종목: {ticker} / 매도가: {current_price_list[ticker]}\n매수가: {buy_price[ticker]}\n수익: {income}\n{response}')
                                    d = int(buy_price[tickers])
                                    e = int(tickers_now_price2)
                                    f = (((e / d) - 1) * 100)
                                    print("수익률 :", "%.2f" % (f), "%")
                                    h = f + h
                                    print("수익률 합 : ", "%.2f" % (h), "%")
                                    telegram_send(f"📉수익률 : " + "%.2f" % (f) + "%")
                                    telegram_send(f"📉총 수익률 : " + "%.2f" % (h) + "%")
                                    buy_time_data.update({tickers: True})
                                    buy_price.update({tickers: 0})
                                    a = a + 1

                                else:
                                    print(tickers + " : 구매후 매도 준비중")
                                    print(tickers_now_time_price)
                                    a = a + 1



        elif a >= coin_num - 1:
            a = 0


        else:
            a = 0
        time.sleep(0.5)


    except Exception as e:
        print("ERROR")
        post_message(myToken, "#bitcoin-stock", "에러발생")
        time.sleep(0.5)