import math
import random
import time
from datetime import datetime, timedelta

import pandas as pd
import plotly.graph_objects as go
import requests
import streamlit as st

# VN-Stock Pro — Python/Streamlit port of the supplied React app.
# Market values below are the same initial sample values as in the source.
st.set_page_config(page_title="VN-Stock Pro", page_icon="📈", layout="wide")

INITIAL_VNINDEX = {
    "symbol": "VN-INDEX",
    "name": "Chỉ số VN-Index (HOSE)",
    "price": 1268.45,
    "ref": 1259.10,
    "open": 1261.20,
    "high": 1272.80,
    "low": 1258.50,
    "volume": 745820300,
    "value": 18640.5,
    "advancers": 268,
    "ceilingCount": 14,
    "unchanged": 72,
    "decliners": 145,
    "floorCount": 3,
    "status": "Đang giao dịch / Khớp lệnh liên tục",
    "history": [
        {"time": "09:00", "value": 1259.10},
        {"time": "09:15", "value": 1261.20},
        {"time": "09:30", "value": 1263.40},
        {"time": "09:45", "value": 1260.80},
        {"time": "10:00", "value": 1262.15},
        {"time": "10:15", "value": 1265.00},
        {"time": "10:30", "value": 1264.20},
        {"time": "10:45", "value": 1266.90},
        {"time": "11:00", "value": 1265.70},
        {"time": "11:30", "value": 1266.10},
        {"time": "13:00", "value": 1266.50},
        {"time": "13:15", "value": 1268.90},
        {"time": "13:30", "value": 1270.40},
        {"time": "13:45", "value": 1267.80},
        {"time": "14:00", "value": 1269.20},
        {"time": "14:15", "value": 1271.10},
        {"time": "14:30", "value": 1268.45},
    ],
}

INITIAL_TICKERS = [
    {"symbol":"HPG","name":"CTCP Tập đoàn Hòa Phát","type":"STOCK","sector":"Thép & Vật liệu","exchange":"HOSE","ref":27.15,"price":27.65,"open":27.20,"high":27.80,"low":27.10,"volume":24850600,"foreignBuy":3450200,"foreignSell":1820100,"pe":15.4,"pb":1.68,"marketCap":"176,880 tỷ","sparkline":[27.15,27.2,27.35,27.3,27.45,27.6,27.55,27.7,27.65]},
    {"symbol":"FUEVFVND","name":"Quỹ ETF DCVFMVN Diamond","type":"ETF","sector":"Chứng chỉ quỹ ETF","exchange":"HOSE","ref":33.20,"price":33.75,"open":33.25,"high":33.85,"low":33.20,"volume":1420500,"foreignBuy":680200,"foreignSell":410000,"pe":None,"pb":1.01,"nav":"33,780 đ","marketCap":"12,450 tỷ","sparkline":[33.20,33.30,33.28,33.45,33.60,33.55,33.70,33.80,33.75]},
    {"symbol":"E1VFVN30","name":"Quỹ ETF DCVFMVN30","type":"ETF","sector":"Chứng chỉ quỹ ETF","exchange":"HOSE","ref":23.15,"price":23.40,"open":23.15,"high":23.50,"low":23.10,"volume":1950800,"foreignBuy":890000,"foreignSell":720500,"pe":None,"pb":1.00,"nav":"23,420 đ","marketCap":"7,820 tỷ","sparkline":[23.15,23.18,23.22,23.20,23.30,23.35,23.32,23.42,23.40]},
    {"symbol":"ACB","name":"Ngân hàng TMCP Á Châu","type":"STOCK","sector":"Ngân hàng","exchange":"HOSE","ref":25.80,"price":26.15,"open":25.85,"high":26.30,"low":25.75,"volume":11640200,"foreignBuy":1250000,"foreignSell":1250000,"pe":6.4,"pb":1.42,"marketCap":"116,800 tỷ","sparkline":[25.80,25.85,25.90,26.05,26.00,26.10,26.20,26.10,26.15]},
    {"symbol":"MBB","name":"Ngân hàng TMCP Quân Đội","type":"STOCK","sector":"Ngân hàng","exchange":"HOSE","ref":25.10,"price":24.85,"open":25.15,"high":25.25,"low":24.75,"volume":16320900,"foreignBuy":950400,"foreignSell":1420000,"pe":6.1,"pb":1.29,"marketCap":"131,900 tỷ","sparkline":[25.10,25.15,25.05,24.95,25.00,24.90,24.80,24.90,24.85]},
    {"symbol":"VIB","name":"Ngân hàng TMCP Quốc Tế Việt Nam","type":"STOCK","sector":"Ngân hàng","exchange":"HOSE","ref":19.25,"price":19.25,"open":19.30,"high":19.45,"low":19.15,"volume":8940100,"foreignBuy":410000,"foreignSell":530000,"pe":6.8,"pb":1.35,"marketCap":"57,350 tỷ","sparkline":[19.25,19.30,19.35,19.25,19.20,19.25,19.30,19.20,19.25]},
]

INITIAL_PORTFOLIO = {
    "HPG":{"qty":2000,"avgPrice":26.50},
    "FUEVFVND":{"qty":1000,"avgPrice":31.80},
    "E1VFVN30":{"qty":1500,"avgPrice":22.50},
    "ACB":{"qty":3000,"avgPrice":25.20},
    "MBB":{"qty":2000,"avgPrice":25.00},
    "VIB":{"qty":2500,"avgPrice":19.10},
}

def calc_ceiling(ref):
    return round(math.floor(ref * 1.07 * 20) / 20, 2)

def calc_floor(ref):
    return round(math.ceil(ref * 0.93 * 20) / 20, 2)

def format_number(num, decimals=2):
    if num is None or pd.isna(num):
        return "-"
    return f"{num:,.{decimals}f}".replace(",", "X").replace(".", ",").replace("X", ".")

def format_volume(vol):
    return f"{int(vol or 0):,}".replace(",", ".")

def stock_color(price, ref, ceiling, floor):
    if price >= ceiling:
        return "Kịch trần", "#e879f9"
    if price <= floor:
        return "Lau sàn", "#22d3ee"
    if price > ref:
        return "Đang tăng", "#34d399"
    if price < ref:
        return "Đang giảm", "#fb7185"
    return "Tham chiếu", "#fbbf24"

def init_state():
    if "vn_index" not in st.session_state:
