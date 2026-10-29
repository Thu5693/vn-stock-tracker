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
        st.session_state.vn_index = INITIAL_VNINDEX.copy()
        st.session_state.vn_index["history"] = [x.copy() for x in INITIAL_VNINDEX["history"]]
        st.session_state.tickers = []
        for item in INITIAL_TICKERS:
            row = item.copy()
            row["sparkline"] = item["sparkline"][:]
            row["ceiling"] = calc_ceiling(row["ref"])
            row["floor"] = calc_floor(row["ref"])
            row["flash"] = None
            st.session_state.tickers.append(row)
        st.session_state.portfolio = {k:v.copy() for k,v in INITIAL_PORTFOLIO.items()}
        st.session_state.last_updated = datetime.now()
        st.session_state.api_status = "Đang chạy dữ liệu khớp lệnh thời gian thực"
        st.session_state.live = True
        st.session_state.mood = "BULL"

def simulated_tick(force_all=False):
    idx = st.session_state.vn_index
    mood_bias = {"BULL":0.58, "BEAR":0.38, "RANDOM":0.5}[st.session_state.mood]
    is_up = random.random() < mood_bias
    step = round((random.random() * 0.85 + 0.05) * (1 if is_up else -1), 2)
    next_price = round(max(1150, idx["price"] + step), 2)
    now = datetime.now().strftime("%H:%M:%S")
    idx["price"] = next_price
    idx["high"] = max(idx["high"], next_price)
    idx["low"] = min(idx["low"], next_price)
    idx["volume"] += math.floor(random.random() * 450000 + 80000)
    idx["value"] = round(idx["value"] + random.random() * 14.5 + 2.1, 1)
    if next_price > idx["ref"]:
        idx["advancers"] = min(380, max(180, idx["advancers"] + (1 if is_up else -1)))
    elif next_price < idx["ref"]:
        idx["decliners"] = min(350, max(110, idx["decliners"] + (0 if is_up else 1)))
    idx["history"] = idx["history"][-24:] + [{"time":now,"value":next_price}]
    idx["flash"] = "up" if step > 0 else "down"

    for t in st.session_state.tickers:
        if not force_all and random.random() > 0.55:
            t["flash"] = None
            continue
        was = t["price"]
        up = random.random() < mood_bias
        delta = (math.floor(random.random() * 2) + 1) * 0.05 * (1 if up else -1)
        next_p = round(was + delta, 2)
        next_p = min(t["ceiling"], max(t["floor"], next_p))
        t["price"] = next_p
        t["high"] = max(t["high"], next_p)
        t["low"] = min(t["low"], next_p)
        t["volume"] += math.floor(random.random() * 18500 + 1200) * 10
        t["sparkline"] = t["sparkline"][-11:] + [next_p]
        t["flash"] = ("up" if next_p > was else "down") if next_p != was else None
    st.session_state.last_updated = datetime.now()

def sync_market_data():
    st.session_state.api_status = "Đang kết nối dữ liệu thị trường..."
    try:
        symbols = ",".join(t["symbol"] for t in st.session_state.tickers)
        url = "https://finfo-api.vndirect.com.vn/v4/stock_prices"
        response = requests.get(url, params={"sort":"date","q":f"code:{symbols}","size":20}, timeout=3.5)
        response.raise_for_status()
        data = response.json().get("data", [])
        latest = {}
        for row in data:
            if row.get("code") and row["code"] not in latest:
                latest[row["code"]] = row
        updated = False
        for t in st.session_state.tickers:
            found = latest.get(t["symbol"])
            if found and found.get("close"):
                ref = float(found.get("basicPrice") or t["ref"])
                t.update({
                    "ref":ref, "price":float(found.get("close") or t["price"]),
                    "open":float(found.get("open") or t["open"]),
                    "high":float(found.get("high") or t["high"]),
                    "low":float(found.get("low") or t["low"]),
                    "volume":float(found.get("nmVolume") or t["volume"]),
                    "ceiling":float(found.get("ceilingPrice") or calc_ceiling(ref)),
                    "floor":float(found.get("floorPrice") or calc_floor(ref)),
                })
                updated = True
        if updated:
            st.session_state.api_status = "Đã đồng bộ dữ liệu từ VNDirect API"
            st.session_state.last_updated = datetime.now()
            return
        raise ValueError("No usable market data")
    except Exception:
        simulated_tick(True)
        st.session_state.api_status = "Đã cập nhật bảng giá khớp lệnh (Realtime Engine)"
        st.session_state.last_updated = datetime.now()

init_state()

st.markdown("""
<style>
.stApp { background: #070b14; color: #e2e8f0; }
[data-testid="stHeader"] { background: rgba(10,16,29,.95); }
.block-container { max-width: 1500px; padding-top: 1.2rem; }
div[data-testid="stMetric"] { background:#0f172a; border:1px solid #273449; border-radius:12px; padding:12px; }
section[data-testid="stSidebar"] { background:#0a101d; }
h1,h2,h3 { color:#f8fafc; }
</style>
""", unsafe_allow_html=True)

header_left, header_right = st.columns([1.1, 2.4])
with header_left:
    st.title("📈 VN-Stock Pro")
    st.caption("HOSE • VN30 • ETF")
    st.caption(st.session_state.api_status)
with header_right:
    c1,c2,c3,c4,c5 = st.columns([1,1,1,1.2,1.3])
    with c1:
        mood_label = st.selectbox("Tâm lý", ["Hưng phấn","Giằng co","Điều chỉnh"], index={"BULL":0,"RANDOM":1,"BEAR":2}[st.session_state.mood], label_visibility="collapsed")
        st.session_state.mood = {"Hưng phấn":"BULL","Giằng co":"RANDOM","Điều chỉnh":"BEAR"}[mood_label]
    with c2:
        st.session_state.live = st.toggle("Realtime", value=st.session_state.live)
    with c3:
        if st.button("↻ Đồng bộ giá", use_container_width=True):
            sync_market_data()
            st.rerun()
    with c4:
        st.caption("Cập nhật lần cuối")
        st.write(st.session_state.last_updated.strftime("%H:%M:%S"))
    with c5:
        st.caption("Trạng thái")
        st.write("🟢 Đang chạy" if st.session_state.live else "🟠 Tạm dừng")

idx = st.session_state.vn_index
change = round(idx["price"] - idx["ref"], 2)
percent = round(change / idx["ref"] * 100, 2)
trend_color = "#34d399" if change > 0 else "#fb7185" if change < 0 else "#fbbf24"
st.markdown("---")
st.subheader("Tổng quan thị trường — VN-INDEX")
m1,m2,m3,m4,m5,m6 = st.columns(6)
m1.metric("VN-INDEX", format_number(idx["price"]), f"{change:+.2f} ({percent:+.2f}%)")
m2.metric("Mở cửa / Tham chiếu", f'{format_number(idx["open"])} / {format_number(idx["ref"])}')
m3.metric("Cao nhất", format_number(idx["high"]))
m4.metric("Thấp nhất", format_number(idx["low"]))
m5.metric("Khối lượng GD", f'{format_number(idx["volume"]/1_000_000,1)} tr CP')
m6.metric("Giá trị GD", f'{format_number(idx["value"],1)} tỷ đ')

breadth_total = idx["advancers"] + idx["unchanged"] + idx["decliners"]
st.markdown(
    f"**<span style='color:#34d399'>▲ {idx['advancers']} mã tăng ({idx['ceilingCount']} trần)</span>**　"
    f"**<span style='color:#fbbf24'>▬ {idx['unchanged']} đứng giá</span>**　"
    f"**<span style='color:#fb7185'>▼ {idx['decliners']} mã giảm ({idx['floorCount']} sàn)</span>**",
    unsafe_allow_html=True
)
st.progress(min(1.0, idx["advancers"]/max(1,breadth_total)), text="Tỷ trọng mã tăng")

tf = st.radio("Khung thời gian biểu đồ", ["1D","1W","1M","3M","1Y"], horizontal=True, index=0)
if tf == "1D":
    chart_data = idx["history"]
else:
    count = {"1W":7,"1M":22,"3M":60,"1Y":120}[tf]
    start_base = idx["ref"] - {"1W":14,"1M":32,"3M":55,"1Y":125}[tf]
    current = start_base
    chart_data = []
    for i in range(count,0,-1):
        d = datetime.now() - timedelta(days=i)
        label = d.strftime("%d/%m")
        current = round(current + (math.sin(i*0.6)*4.5 + (idx["price"]-start_base)/count),2)
        chart_data.append({"time":label,"value":current})
    chart_data.append({"time":"Hôm nay","value":idx["price"]})
fig = go.Figure()
fig.add_trace(go.Scatter(
    x=[p["time"] for p in chart_data], y=[p["value"] for p in chart_data],
    mode="lines", name="VN-Index", line=dict(color=trend_color,width=2.5),
    fill="tozeroy", fillcolor="rgba(16,185,129,0.12)"
))
if tf == "1D":
    fig.add_hline(y=idx["ref"], line_dash="dash", line_color="#fbbf24",
                  annotation_text=f"TC: {idx['ref']}")
fig.update_layout(
    height=320, margin=dict(l=10,r=10,t=20,b=10),
    paper_bgcolor="#0b1220", plot_bgcolor="#0b1220",
    font=dict(color="#cbd5e1"), xaxis=dict(showgrid=False),
    yaxis=dict(gridcolor="#1e293b"), showlegend=False
)
st.plotly_chart(fig, use_container_width=True)

st.markdown("---")
st.subheader("Danh sách mã cổ phiếu & chứng chỉ quỹ")
left, right = st.columns([2,1])
with left:
    category = st.radio("Phân loại", ["Tất cả","Cổ phiếu","ETF"], horizontal=True)
with right:
    search_query = st.text_input("Tìm mã", placeholder="Tìm mã HPG, ACB, ETF...")
tickers = st.session_state.tickers
filtered = [t for t in tickers
            if (category == "Tất cả" or t["type"] == ("STOCK" if category == "Cổ phiếu" else "ETF"))
            and (search_query.lower() in t["symbol"].lower() or search_query.lower() in t["name"].lower())]
st.caption("Quy chuẩn màu sắc HOSE: 🟣 Giá Trần (+7%) · 🟢 Giá Tăng · 🟡 Tham chiếu · 🔴 Giá Giảm · 🔵 Giá Sàn (-7%). Đơn vị giá: 1.000 VNĐ (VD: 27.65 = 27.650 đ/CP)")

view_mode = st.radio("Kiểu hiển thị", ["Cả thẻ và bảng","Chỉ bảng","Chỉ thẻ"], horizontal=True)
if view_mode != "Chỉ bảng":
    cols = st.columns(3)
    for i, t in enumerate(filtered):
        label, color = stock_color(t["price"], t["ref"], t["ceiling"], t["floor"])
        diff = t["price"] - t["ref"]
        pct = diff/t["ref"]*100 if t["ref"] else 0
        with cols[i % 3]:
            st.markdown(f"""
            <div style="background:#0b1220;border:1px solid #273449;border-radius:14px;padding:16px;margin-bottom:12px">
              <div style="display:flex;justify-content:space-between;gap:8px">
                <div><span style="font-size:20px;font-weight:800;color:#f8fafc">{t['symbol']}</span><br>
                <span style="font-size:12px;color:#94a3b8">{t['name']}</span></div>
                <span style="height:max-content;border:1px solid {color};color:{color};border-radius:20px;padding:4px 8px;font-size:11px">{label}</span>
              </div>
              <div style="font-size:26px;font-weight:800;color:{color};margin-top:12px">{format_number(t['price'])}</div>
              <div style="color:{color};font-weight:600">{diff:+.2f} ({pct:+.2f}%)</div>
              <hr style="border-color:#273449">
              <div style="font-size:12px;color:#94a3b8">Tham chiếu: {format_number(t['ref'])}　|　Khối lượng: {format_volume(t['volume'])}</div>
              <div style="font-size:12px;color:#94a3b8">Cao / Thấp: {format_number(t['high'])} / {format_number(t['low'])}</div>
            </div>""", unsafe_allow_html=True)

if view_mode != "Chỉ thẻ":
    rows = []
    for t in filtered:
        label, _ = stock_color(t["price"], t["ref"], t["ceiling"], t["floor"])
        diff = t["price"] - t["ref"]
        rows.append({
            "Mã CK":t["symbol"],"Tên doanh nghiệp / Quỹ":t["name"],"Loại":t["type"],
            "Giá":format_number(t["price"]),"Thay đổi":f"{diff:+.2f}",
            "%":f"{(diff/t['ref']*100 if t['ref'] else 0):+.2f}%",
            "Tham chiếu":format_number(t["ref"]),"Cao nhất":format_number(t["high"]),
            "Thấp nhất":format_number(t["low"]),"Khối lượng":format_volume(t["volume"]),
            "Trạng thái":label,"P/E":format_number(t.get("pe")),"P/B":format_number(t.get("pb"))
        })
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

st.markdown("---")
st.subheader("Chi tiết mã chứng khoán")
symbols = [t["symbol"] for t in tickers]
selected_symbol = st.selectbox("Chọn mã để xem chi tiết", symbols)
selected = next(t for t in tickers if t["symbol"] == selected_symbol)
label, color = stock_color(selected["price"], selected["ref"], selected["ceiling"], selected["floor"])
d1,d2,d3,d4,d5 = st.columns(5)
d1.metric("Giá hiện tại", format_number(selected["price"]))
d2.metric("Giá tham chiếu", format_number(selected["ref"]))
d3.metric("Giá trần", format_number(selected["ceiling"]))
d4.metric("Giá sàn", format_number(selected["floor"]))
d5.metric("Trạng thái", label)
st.write(f"**{selected['name']}** · {selected['sector']} · {selected['exchange']}")
sfig = go.Figure(go.Scatter(y=selected["sparkline"], mode="lines+markers", line=dict(color=color,width=2)))
sfig.update_layout(height=180, margin=dict(l=10,r=10,t=10,b=10), paper_bgcolor="#0b1220",
                   plot_bgcolor="#0b1220", font=dict(color="#cbd5e1"), xaxis=dict(visible=False),
                   yaxis=dict(gridcolor="#1e293b"))
st.plotly_chart(sfig, use_container_width=True)

st.markdown("---")
st.subheader("Tính lãi/lỗ danh mục cá nhân")
portfolio = st.session_state.portfolio
portfolio_rows = []
total_cost = total_market = 0
for t in tickers:
    hold = portfolio.get(t["symbol"], {"qty":0,"avgPrice":t["ref"]})
    qty, avg = hold["qty"], hold["avgPrice"]
    cost = qty * avg * 1000
    market = qty * t["price"] * 1000
    profit = market - cost
    pct = ((t["price"]-avg)/avg*100) if avg > 0 else 0
    total_cost += cost
    total_market += market
    portfolio_rows.append({"Mã CK":t["symbol"],"Số lượng":qty,"Giá vốn (nghìn đ)":avg,
                           "Giá hiện tại":t["price"],"Giá trị thị trường (VNĐ)":round(market),
                           "Lãi / Lỗ (VNĐ)":round(profit),"Lãi / Lỗ (%)":round(pct,2)})
profit = total_market - total_cost
profit_pct = profit/total_cost*100 if total_cost else 0
p1,p2,p3,p4 = st.columns(4)
p1.metric("Tổng vốn", f"{format_volume(round(total_cost))} đ")
p2.metric("Giá trị thị trường", f"{format_volume(round(total_market))} đ")
p3.metric("Tổng lãi / lỗ", f"{'+' if profit>=0 else ''}{format_volume(round(profit))} đ")
p4.metric("Hiệu suất", f"{profit_pct:+.2f}%")
st.dataframe(pd.DataFrame(portfolio_rows), use_container_width=True, hide_index=True)
with st.expander("Chỉnh sửa số lượng nắm giữ và giá vốn"):
    for t in tickers:
        current = portfolio.get(t["symbol"], {"qty":0,"avgPrice":t["ref"]})
        a,b,c = st.columns([1.3,1,1])
        a.write(f"**{t['symbol']}**")
        qty = b.number_input(f"Số lượng {t['symbol']}", min_value=0, step=100, value=int(current["qty"]), key=f"qty_{t['symbol']}")
        avg = c.number_input(f"Giá vốn {t['symbol']}", min_value=0.0, step=0.05, value=float(current["avgPrice"]), key=f"avg_{t['symbol']}")
        portfolio[t["symbol"]] = {"qty":qty,"avgPrice":avg}

st.markdown("---")
st.subheader("Thêm mã mới hoặc cập nhật giá mã")
with st.form("add_ticker_form", clear_on_submit=True):
    a,b = st.columns(2)
    symbol = a.text_input("Mã chứng khoán (VD: FPT, VCB, HPG, FUEVFVND...)").strip().upper()
    name = b.text_input("Tên doanh nghiệp / Quỹ")
    c,d,e = st.columns(3)
    ref_value = c.number_input("Giá tham chiếu (nghìn đ)", min_value=0.0, value=25.0, step=0.05)
    price_value = d.number_input("Giá khớp hiện tại", min_value=0.0, value=25.0, step=0.05)
    ticker_type = e.selectbox("Loại chứng khoán", ["STOCK","ETF"])
    submitted = st.form_submit_button("Lưu vào Bảng Giá", use_container_width=True)
    if submitted:
        if not symbol:
            st.error("Vui lòng nhập mã chứng khoán.")
        else:
            existing = next((i for i,x in enumerate(tickers) if x["symbol"] == symbol), None)
            new_entry = {
                "symbol":symbol,"name":name.strip() or f"Cổ phiếu / CCQ {symbol}",
                "type":ticker_type,"sector":"Chứng chỉ quỹ ETF" if ticker_type=="ETF" else "Cổ phiếu niêm yết",
                "exchange":"HOSE","ref":ref_value,"price":price_value,"open":ref_value,
                "high":max(ref_value,price_value),"low":min(ref_value,price_value),"volume":1250000,
                "foreignBuy":120000,"foreignSell":85000,"pe":None if ticker_type=="ETF" else 10.5,
                "pb":1.25,"marketCap":"15,000 tỷ","ceiling":calc_ceiling(ref_value),
                "floor":calc_floor(ref_value),"sparkline":[ref_value,ref_value,price_value,price_value],"flash":"up"
            }
            if existing is not None:
                tickers[existing] = new_entry
            else:
                tickers.append(new_entry)
            st.success(f"Đã lưu mã {symbol}.")
            st.rerun()

st.caption("Lưu ý: Dữ liệu khởi tạo và chế độ Realtime là dữ liệu mẫu/giả lập. Đồng bộ VNDirect phụ thuộc endpoint công khai, kết nối mạng và chính sách CORS/API.")

# Streamlit reruns the script on interaction. This lightweight refresh emulates
# the original 2.6-second simulated ticking when Realtime is enabled.
if st.session_state.live:
    time.sleep(2.6)
    simulated_tick(False)
    st.rerun()
