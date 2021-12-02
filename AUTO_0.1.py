import time
import pyupbit
import datetime
import requests
from decimal import *
from pytz import timezone
from datetime import datetime
import telegram
import traceback


# 현재 시간 조회
if __name__ == "__main__":
    fmt = "%Y-%m-%d %H:%M:%S"
    KST = datetime.now(timezone('Asia/Seoul'))

# 현재 시간 조회
if __name__ == "__main__":
    fmt = "%Y-%m-%d %H:%M:%S"


# 텔레그램 메시지 전송
def telegram_send(message):
    telegram_bot.sendMessage(chat_id=telegram_chat_id, text='[UPbit 자동매매]\n' + message)


# 개인 정보 입력
access = "2y4VdxxyBF2S7BAG7wEaYQFuMBnUcmuvsNIwofuv"
secret = "eiLjsfUHwH0JSVhcg0zMbejHnJkj0Oz7LGs0kxer"
telegram_token = "2141506416:AAF9NS-ruBdR5hcQnb_pkZsTFuYUjGlcClE"
telegram_chat_id = "2087146847"
telegram_bot = telegram.Bot(token=telegram_token)
# 구매여부 확인
buy_time_data = {}

# 매수 구매 가격
buy_price = {}
telegram_send('📢 프로그램 시작')

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

        # 현재 시간 조회
        KST = datetime.now(timezone('Asia/Seoul'))

        # 코인 현재시세+현재가격
        tickers_now_time_price = pyupbit.get_current_price(tickers), KST.strftime(fmt)

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
            if buy_time_data[tickers] == True and buy_price[tickers] == 0:
                # 매수조건 = 9분 평균선이 MACD선(12분-21분) 을 상향돌파 즉,골든크로스 발생
                if tickers_signal < (tickers_ma12 - tickers_ma21):
                    print(tickers + " : 매수완료")
                    print(tickers_now_time_price)
                    telegram_send(f'🛒 목표가 매수\n종목: {ticker}\n매수가: {tickers_now_time_price[ticker]}')
                    buy_time_data.update({tickers: False})
                    buy_price.update({tickers: tickers_now_price2})
                    d = int(buy_price[tickers])
                    a = a + 1

                else:
                    print(tickers + " : 구매전 매수 준비중")
                    print(tickers_now_time_price)
                    a = a + 1

            # 매도조건 = 기본 매수조건
            elif buy_time_data[tickers] == False and buy_price[tickers] > 0:

                # 매도조건 = 1%이상 하락시 손절
                if (((tickers_now_price2 / d) - 1) * 100) < -1:
                    print(tickers + " : 매도완료")
                    print(tickers_now_time_price)
                    telegram_send(f'📉 매도\n종목: {ticker} / 매도가: {tickers_now_time_price[ticker]}')
                    print(buy_price[tickers])
                    print(tickers_now_price2)
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

                # 매도조건 = MACD선(12분-21분)이 하양추세 이거나 데드크로스발생
                if (tickers_ma12 - tickers_ma21) < (
                        tickers_ma12_1mb - tickers_ma21_1mb) or tickers_signaltickers_signal > (
                        tickers_ma12 - tickers_ma21):
                    print(tickers + " : 매도완료")
                    print(tickers_now_time_price)
                    telegram_send(f'📉 매도\n종목: {ticker} / 매도가: {tickers_now_time_price[ticker]}')
                    print(buy_price[tickers])
                    print(tickers_now_price2)
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
        time.sleep(0.5)