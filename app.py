import streamlit as st
import streamlit.components.v1 as components

# Cấu hình trang
st.set_page_config(
    page_title="VN-Stock Pro Tracker",
    page_icon="📈",
    layout="wide"
)

# Giao diện HTML/JS hoàn chỉnh cho Bảng giá chứng khoán
html_code = """
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>VN-Stock Pro</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://unpkg.com/react@18/umd/react.production.min.js"></script>
    <script src="https://unpkg.com/react-dom@18/umd/react-dom.production.min.js"></script>
    <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/lucide@latest/dist/umd/lucide.js"></script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        body { font-family: 'Inter', sans-serif; background-color: #0f172a; color: #f8fafc; }
        /* Hiệu ứng nhấp nháy khi giá thay đổi */
        @keyframes flashGreen { 0% { background-color: rgba(34, 197, 94, 0.6); } 100% { background-color: transparent; } }
        @keyframes flashRed { 0% { background-color: rgba(239, 68, 68, 0.6); } 100% { background-color: transparent; } }
        .flash-green { animation: flashGreen 1s ease-out; }
        .flash-red { animation: flashRed 1s ease-out; }
    </style>
</head>
<body class="bg-slate-950 text-slate-100 min-h-screen">
    <div id="root"></div>

    <script type="text/babel">
        const { useState, useEffect } = React;

        function App() {
            const [vnIndex, setVnIndex] = useState({
                val: 1268.45,
                change: +12.30,
                percent: +0.98,
                status: 'up',
                vol: '18,520 tỷ',
                shares: { up: 285, ref: 65, down: 110 }
            });

            const [stocks, setStocks] = useState([
                { code: 'HPG', name: 'Tập đoàn Hòa Phát', type: 'Cổ phiếu', ref: 28.55, ceiling: 30.50, floor: 26.60, price: 29.10, change: +0.55, percent: +1.93, vol: '24.5M' },
                { code: 'ACB', name: 'Ngân hàng Á Châu', type: 'Cổ phiếu', ref: 24.10, ceiling: 25.75, floor: 22.45, price: 24.50, change: +0.40, percent: +1.66, vol: '12.1M' },
                { code: 'MBB', name: 'Ngân hàng Quân Đội', type: 'Cổ phiếu', ref: 23.40, ceiling: 25.00, floor: 21.80, price: 23.40, change: 0.00, percent: 0.00, vol: '15.8M' },
                { code: 'VIB', name: 'Ngân hàng Quốc Tế', type: 'Cổ phiếu', ref: 19.80, ceiling: 21.15, floor: 18.45, price: 19.50, change: -0.30, percent: -1.52, vol: '8.4M' },
                { code: 'E1VFVN30', name: 'ETF VFMVN30', type: 'Quỹ ETF', ref: 22.50, ceiling: 24.05, floor: 20.95, price: 22.80, change: +0.30, percent: +1.33, vol: '5.2M' },
                { code: 'FUEVFVND', name: 'ETF VNDONE', type: 'Quỹ ETF', ref: 28.10, ceiling: 30.05, floor: 26.15, price: 28.45, change: +0.35, percent: +1.25, vol: '3.9M' }
            ]);

            // Mô phỏng cập nhật giá ngẫu nhiên theo thời gian thực (giống bảng điện tử)
            useEffect(() => {
                const interval = setInterval(() => {
                    setStocks(prevStocks => 
                        prevStocks.map(stock => {
                            if (Math.random() > 0.6) {
                                const delta = (Math.random() * 0.2 - 0.1).toFixed(2);
                                const newPrice = Number((stock.price + parseFloat(delta)).toFixed(2));
                                const diff = Number((newPrice - stock.ref).toFixed(2));
                                const pct = Number(((diff / stock.ref) * 100).toFixed(2));
                                return {
                                    ...stock,
                                    price: newPrice,
                                    change: diff,
                                    percent: pct,
                                    flash: diff > 0 ? 'up' : diff < 0 ? 'down' : 'ref'
                                };
                            }
                            return { ...stock, flash: null };
                        })
                    );
                }, 3000);
                return () => clearInterval(interval);
            }, []);

            return (
                <div className="p-4 max-w-7xl mx-auto">
                    <header className="flex justify-between items-center mb-6 pb-4 border-b border-slate-800">
                        <div>
                            <h1 className="text-2xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-emerald-400">
                                📊 VN-Stock Pro Tracker
                            </h1>
                            <p className="text-sm text-slate-400">Bảng giá trực tuyến & Theo dõi danh mục chứng khoán</p>
                        </div>
                        <div className="text-right">
                            <span className="inline-block px-3 py-1 bg-emerald-950 text-emerald-400 border border-emerald-800 rounded-full text-xs font-semibold animate-pulse">
                                ● Thị trường đang mở cửa
                            </span>
                        </div>
                    </header>

                    {/* Khối hiển thị VN-Index */}
                    <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
                        <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 shadow-lg">
                            <span className="text-slate-400 text-sm font-medium">Chỉ số VN-INDEX</span>
                            <div className="flex items-baseline space-x-3 mt-1">
                                <span className="text-3xl font-extrabold text-emerald-400">{vnIndex.val}</span>
                                <span className="text-emerald-400 font-bold text-sm">+{vnIndex.change} (+{vnIndex.percent}%)</span>
                            </div>
                            <div className="text-xs text-slate-500 mt-2">Khối lượng: {vnIndex.vol}</div>
                        </div>

                        <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 shadow-lg flex flex-col justify-between">
                            <span className="text-slate-400 text-sm font-medium">Độ rộng thị trường</span>
                            <div className="flex justify-between text-center my-auto">
                                <div>
                                    <div className="text-emerald-400 font-bold text-lg">{vnIndex.shares.up}</div>
                                    <div className="text-xs text-slate-500">Tăng</div>
                                </div>
                                <div>
                                    <div className="text-amber-400 font-bold text-lg">{vnIndex.shares.ref}</div>
                                    <div className="text-xs text-slate-500">Tham chiếu</div>
                                </div>
                                <div>
                                    <div className="text-rose-500 font-bold text-lg">{vnIndex.shares.down}</div>
                                    <div className="text-xs text-slate-500">Giảm</div>
                                </div>
                            </div>
                        </div>

                        <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 md:col-span-2 flex items-center justify-between shadow-lg">
                            <div>
                                <h3 className="text-sm font-semibold text-slate-300">💡 Gợi ý đầu tư nhanh</h3>
                                <p className="text-xs text-slate-400 mt-1">Theo dõi sát sao nhóm ngân hàng (ACB, MBB, VIB) và Thép (HPG) trong các nhịprung lắc của thị trường.</p>
                            </div>
                            <button onClick={() => alert("Dữ liệu được cập nhật liên tục từ hệ thống mô phỏng chuẩn HOSE.")} className="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold rounded-lg transition">
                                Làm mới dữ liệu
                            </button>
                        </div>
                    </div>

                    {/* Bảng giá chi tiết */}
                    <div className="bg-slate-900 border border-slate-800 rounded-xl shadow-xl overflow-hidden">
                        <div className="px-6 py-4 border-b border-slate-800 flex justify-between items-center">
                            <h2 className="font-semibold text-lg text-slate-200">Danh mục theo dõi (Cổ phiếu & Quỹ ETF)</h2>
                            <span className="text-xs text-slate-400">* Đơn vị giá: 1,000 VNĐ</span>
                        </div>
                        <div className="overflow-x-auto">
                            <table className="w-full text-left border-collapse">
                                <thead>
                                    <tr className="bg-slate-950 text-slate-400 text-xs uppercase tracking-wider border-b border-slate-800">
                                        <th className="p-3 font-semibold">Mã</th>
                                        <th className="p-3 font-semibold">Tên tài sản</th>
                                        <th className="p-3 font-semibold text-right">Trần</th>
                                        <th className="p-3 font-semibold text-right">Sàn</th>
                                        <th className="p-3 font-semibold text-right">Tham chiếu</th>
                                        <th className="p-3 font-semibold text-right">Giá Khớp</th>
                                        <th className="p-3 font-semibold text-right">Tăng/Giảm (+/-)</th>
                                        <th className="p-3 font-semibold text-right">Khối lượng</th>
                                    </tr>
                                </thead>
                                <tbody className="divide-y divide-slate-800/60 text-sm">
                                    {stocks.map((item) => {
                                        const colorClass = item.change > 0 ? 'text-emerald-400 font-bold' : item.change < 0 ? 'text-rose-500 font-bold' : 'text-amber-400 font-bold';
                                        return (
                                            <tr key={item.code} className="hover:bg-slate-800/40 transition">
                                                <td className="p-3 font-bold text-white flex items-center space-x-2">
                                                    <span>{item.code}</span>
                                                    <span className="text-[10px] px-1.5 py-0.5 rounded bg-slate-800 text-slate-400 font-normal">{item.type}</span>
                                                </td>
                                                <td className="p-3 text-slate-300 text-xs">{item.name}</td>
                                                <td className="p-3 text-right text-purple-400 font-medium">{item.ceiling.toFixed(2)}</td>
                                                <td className="p-3 text-right text-cyan-400 font-medium">{item.floor.toFixed(2)}</td>
                                                <td className="p-3 text-right text-amber-400 font-medium">{item.ref.toFixed(2)}</td>
                                                <td className={`p-3 text-right ${colorClass}`}>{item.price.toFixed(2)}</td>
                                                <td className={`p-3 text-right ${colorClass}`}>
                                                    {item.change > 0 ? `+${item.change}` : item.change} ({item.percent > 0 ? `+${item.percent}%` : `${item.percent}%`})
                                                </td>
                                                <td className="p-3 text-right text-slate-400 text-xs">{item.vol}</td>
                                            </tr>
                                        );
                                    })}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            );
        }

        ReactDOM.render(<App />, document.getElementById('root'));
    </script>
</body>
</html>
"""

# Hiển thị trực tiếp nội dung HTML/JS chuẩn đẹp trong ứng dụng Streamlit
components.html(html_code, height=750, scrolling=True)
