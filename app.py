import streamlit as st
import random
import pandas as pd

# Cấu hình trang Streamlit
st.set_page_config(
    page_title="VN-Stock Pro - Bảng Giá & Theo Dõi Chứng Khoán",
    page_icon="📈",
    layout="wide"
)

st.title("📊 VN-Stock Pro - Theo Dõi Chứng Khoán & Quỹ ETF")
st.markdown("Ứng dụng theo dõi trực quan chỉ số **VN-Index** và bảng giá chi tiết các mã **HPG, FUEVFVND, E1VFVN30, ACB, MBB, VIB**.")

# Khởi tạo dữ liệu mẫu cho các mã cổ phiếu & quỹ
if "stocks_data" not in st.session_state:
    st.session_state.stocks_data = [
        {"Mã": "HPG", "Tên": "Tập đoàn Hòa Phát", "Phân loại": "Cổ phiếu", "Tham chiếu": 27.15, "Giá": 27.65, "Trần": 29.05, "Sàn": 25.25, "Khối lượng": 24850600},
        {"Mã": "ACB", "Tên": "Ngân hàng Á Châu", "Phân loại": "Cổ phiếu", "Tham chiếu": 25.80, "Giá": 26.15, "Trần": 27.60, "Sàn": 24.00, "Khối lượng": 11640200},
        {"Mã": "MBB", "Tên": "Ngân hàng Quân Đội", "Phân loại": "Cổ phiếu", "Tham chiếu": 25.10, "Giá": 24.85, "Trần": 26.85, "Sàn": 23.35, "Khối lượng": 16320900},
        {"Mã": "VIB", "Tên": "Ngân hàng Quốc Tế", "Phân loại": "Cổ phiếu", "Tham chiếu": 19.25, "Giá": 19.25, "Trần": 20.60, "Sàn": 17.90, "Khối lượng": 8940100},
        {"Mã": "E1VFVN30", "Tên": "Quỹ ETF DCVFMVN30", "Phân loại": "Quỹ ETF", "Tham chiếu": 23.15, "Giá": 23.40, "Trần": 24.75, "Sàn": 21.55, "Khối lượng": 1950800},
        {"Mã": "FUEVFVND", "Tên": "Quỹ ETF Diamond", "Phân loại": "Quỹ ETF", "Tham chiếu": 33.20, "Giá": 33.75, "Trần": 35.50, "Sàn": 30.90, "Khối lượng": 1420500},
    ]

# Khởi tạo chỉ số VN-Index
if "vn_index" not in st.session_state:
    st.session_state.vn_index = {
        "val": 1268.45,
        "ref": 1259.10,
        "vol": "745.8 triệu CP",
        "val_money": "18,640 tỷ đ",
        "up": 268,
        "ref_count": 72,
        "down": 145
    }

# Nút cập nhật / làm mới dữ liệu
col_btn1, col_btn2 = st.columns([1, 5])
with col_btn1:
    if st.button("🔄 Cập nhật giá"):
        # Mô phỏng biến động ngẫu nhiên nhẹ khi bấm nút
        st.session_state.vn_index["val"] = round(st.session_state.vn_index["val"] + random.uniform(-2, 2), 2)
        for item in st.session_state.stocks_data:
            delta = round(random.uniform(-0.15, 0.15), 2)
            item["Giá"] = round(item["Giá"] + delta, 2)

# Tính toán thay đổi VN-Index
vn_change = round(st.session_state.vn_index["val"] - st.session_state.vn_index["ref"], 2)
vn_percent = round((vn_change / st.session_state.vn_index["ref"]) * 100, 2)
is_vn_up = vn_change >= 0

# Hiển thị khối VN-Index nổi bật
st.markdown("### 📈 Chỉ số thị trường")
metric_col1, metric_col2, metric_col3 = st.columns(3)

with metric_col1:
    st.metric(
        label="VN-INDEX (HOSE)",
        value=f"{st.session_state.vn_index['val']:.2f} điểm",
        delta=f"{vn_change:+.2f} ({vn_percent:+.2f}%)"
    )

with metric_col2:
    st.metric(
        label="Khối lượng & Giá trị GD",
        value=st.session_state.vn_index["vol"],
        delta=st.session_state.vn_index["val_money"]
    )

with metric_col3:
    st.metric(
        label="Độ rộng thị trường",
        value=f"Tăng: {st.session_state.vn_index['up']} | Giảm: {st.session_state.vn_index['decliners']}",
        delta=f"Đứng giá: {st.session_state.vn_index['ref_count']}"
    )

st.markdown("---")
st.markdown("### 📋 Bảng giá chi tiết danh mục trọng tâm")

# Xử lý dữ liệu hiển thị bảng
table_rows = []
for item in st.session_state.stocks_data:
    change = round(item["Giá"] - item["Tham chiếu"], 2)
    percent = round((change / item["Tham chiếu"]) * 100, 2)
    
    # Xác định trạng thái màu sắc theo chuẩn chứng khoán VN
    if item["Giá"] >= item["Trần"]:
        status = "🟣 Kịch trần"
    elif item["Giá"] <= item["Sàn"]:
        status = "🔵 Lau sàn"
    elif item["Giá"] > item["Tham chiếu"]:
        status = "🟢 Tăng"
    elif item["Giá"] < item["Tham chiếu"]:
        status = "🔴 Giảm"
    else:
        status = "🟡 Tham chiếu"

    table_rows.append({
        "Mã CK": item["Mã"],
        "Tên tài sản": item["Tên"],
        "Phân loại": item["Phân loại"],
        "Trần": item["Trần"],
        "Sàn": item["Sàn"],
        "Tham chiếu": item["Tham chiếu"],
        "Giá Khớp (k.đ)": item["Giá"],
        "Giá VNĐ": f"{int(item['Giá'] * 1000):,} đ",
        "Biến động": f"{change:+.2f} ({percent:+.2f}%)",
        "Trạng thái": status,
        "Khối lượng": f"{item['Khối lượng']:,}"
    })

df = pd.DataFrame(table_rows)
st.dataframe(df, use_container_width=True, hide_index=True)

st.info("💡 Mẹo: Bạn có thể nhấn nút **Cập nhật giá** ở phía trên để giả lập dòng tiền khớp lệnh mua bán trực tiếp của thị trường.")
