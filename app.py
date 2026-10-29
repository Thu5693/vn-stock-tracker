import streamlit as st
import streamlit.components.v1 as components

# Cấu hình trang Streamlit
st.set_page_config(
    page_title="VN-Stock Pro - Bảng Giá & Theo Dõi Chứng Khoán",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Giao diện HTML/React hoàn chỉnh được nhúng trực tiếp vào Streamlit
html_code = """
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>VN-Stock Pro Tracker</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://unpkg.com/react@18/umd/react.production.min.js"></script>
    <script src="https://unpkg.com/react-dom@18/umd/react-dom.production.min.js"></script>
    <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/lucide@latest/dist/umd/lucide.js"></script>
    <script src="https://unpkg.com/recharts/umd/Recharts.js"></script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;600;700&display=swap');
        body { font-family: 'Inter', sans-serif; background-color: #070b14; color: #f8fafc; }
        .font-mono { font-family: 'JetBrains Mono', monospace; }
        /* Tùy chỉnh thanh cuộn */
        ::-webkit-scrollbar { width: 6px; height: 6px; }
        ::-webkit-scrollbar-track { background: #070b14; }
        ::-webkit-scrollbar-thumb { background: #1e293b; border-radius: 3px; }
        ::-webkit-scrollbar-thumb:hover { background: #334155; }
    </style>
</head>
<body class="bg-[#070b14] text-slate-100 min-h-screen">
    <div id="root"></div>

    <script type="text/babel">
        const { useState, useEffect, useMemo } = React;
        const { 
            TrendingUp, TrendingDown, Minus, RefreshCw, Activity, BarChart2, 
            PieChart, Layers, Plus, Search, Clock, Calculator, X, 
            ArrowUpRight, ArrowDownRight, Zap, Globe, Briefcase, ChevronRight 
        } = lucide;
        const { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer, ReferenceLine } = Recharts;

        const INITIAL_VNINDEX = {
            symbol: 'VN-INDEX',
            name: 'Chỉ số VN-Index (HOSE)',
            price: 1268.45,
            ref: 1259.10,
            open: 1261.20,
            high: 1272.80,
            low: 1258.50,
            volume: 745820300,
            value: 18640.5,
            advancers: 268,
            ceilingCount: 14,
            unchanged: 72,
            decliners: 145,
            history: [
                { time: '09:00', value: 1259.10 }, { time: '09:15', value: 1261.20 },
                { time: '09:30', value: 1263.40 }, { time: '09:45', value: 1260.80 },
                { time: '10:00', value: 1262.15 }, { time: '10:15', value: 1265.00 },
                { time: '10:30', value: 1264.20 }, { time: '10:45', value: 1266.90 },
                { time: '11:00', value: 1265.70 }, { time: '11:30', value: 1266.10 },
                { time: '13:00', value: 1266.50 }, { time: '13:15', value: 1268.90 },
                { time: '13:30', value: 1270.40 }, { time: '13:45', value: 1267.80 },
                { time: '14:00', value: 1269.20 }, { time: '14:15', value: 1271.10 },
                { time: '14:30', value: 1268.45 }
            ]
        };

        const INITIAL_TICKERS = [
            { symbol: 'HPG', name: 'CTCP Tập đoàn Hòa Phát', type: 'STOCK', sector: 'Thép & Vật liệu', exchange: 'HOSE', ref: 27.15, price: 27.65, open: 27.20, high: 27.80, low: 27.10, volume: 24850600, foreignBuy: 3450200, foreignSell: 1820100, pe: 15.4, pb: 1.68, marketCap: '176,880 tỷ', sparkline: [27.15, 27.2, 27.35, 27.3, 27.45, 27.6, 27.55, 27.7, 27.65] },
            { symbol: 'FUEVFVND', name: 'Quỹ ETF DCVFMVN Diamond', type: 'ETF', sector: 'Chứng chỉ quỹ ETF', exchange: 'HOSE', ref: 33.20, price: 33.75, open: 33.25, high: 33.85, low: 33.20, volume: 1420500, foreignBuy: 680200, foreignSell: 410000, pe: null, pb: 1.01, nav: '33,780 đ', marketCap: '12,450 tỷ', sparkline: [33.20, 33.30, 33.28, 33.45, 33.60, 33.55, 33.70, 33.80, 33.75] },
            { symbol: 'E1VFVN30', name: 'Quỹ ETF DCVFMVN30', type: 'ETF', sector: 'Chứng chỉ quỹ ETF', exchange: 'HOSE', ref: 23.15, price: 23.40, open: 23.15, high: 23.50, low: 23.10, volume: 1950800, foreignBuy: 890000, foreignSell: 720500, pe: null, pb: 1.00, nav: '23,420 đ', marketCap: '7,820 tỷ', sparkline: [23.15, 23.18, 23.22, 23.20, 23.30, 23.35, 23.32, 23.42, 23.40] },
            { symbol: 'ACB', name: 'Ngân hàng TMCP Á Châu', type: 'STOCK', sector: 'Ngân hàng', exchange: 'HOSE', ref: 25.80, price: 26.15, open: 25.85, high: 26.30, low: 25.75, volume: 11640200, foreignBuy: 1250000, foreignSell: 1250000, pe: 6.4, pb: 1.42, marketCap: '116,800 tỷ', sparkline: [25.80, 25.85, 25.90, 26.05, 26.00, 26.10, 26.20, 26.10, 26.15] },
            { symbol: 'MBB', name: 'Ngân hàng TMCP Quân Đội', type: 'STOCK', sector: 'Ngân hàng', exchange: 'HOSE', ref: 25.10, price: 24.85, open: 25.15, high: 25.25, low: 24.75, volume: 16320900, foreignBuy: 950400, foreignSell: 1420000, pe: 6.1, pb: 1.29, marketCap: '131,900 tỷ', sparkline: [25.10, 25.15, 25.05, 24.95, 25.00, 24.90, 24.80, 24.90, 24.85] },
            { symbol: 'VIB', name: 'Ngân hàng TMCP Quốc Tế Việt Nam', type: 'STOCK', sector: 'Ngân hàng', exchange: 'HOSE', ref: 19.25, price: 19.25, open: 19.30, high: 19.45, low: 19.15, volume: 8940100, foreignBuy: 410000, foreignSell: 530000, pe: 6.8, pb: 1.35, marketCap: '57,350 tỷ', sparkline: [19.25, 19.30, 19.35, 19.25, 19.20, 19.25, 19.30, 19.20, 19.25] }
        ];

        const calcCeiling = (ref) => Number((Math.floor(ref * 1.07 * 20) / 20).toFixed(2));
        const calcFloor = (ref) => Number((Math.ceil(ref * 0.93 * 20) / 20).toFixed(2));

        const getVNStockColor = (price, ref, ceiling, floor) => {
            if (price >= ceiling) return { text: 'text-fuchsia-400', badge: 'bg-fuchsia-500/20 text-fuchsia-300 border-fuchsia-500/40', hex: '#e879f9', label: 'Kịch trần' };
            if (price <= floor) return { text: 'text-cyan-400', badge: 'bg-cyan-500/20 text-cyan-300 border-cyan-500/40', hex: '#22d3ee', label: 'Lau sàn' };
            if (price > ref) return { text: 'text-emerald-400', badge: 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40', hex: '#34d399', label: 'Đang tăng' };
            if (price < ref) return { text: 'text-rose-400', badge: 'bg-rose-500/20 text-rose-300 border-rose-500/40', hex: '#fb7185', label: 'Đang giảm' };
            return { text: 'text-amber-400', badge: 'bg-amber-500/20 text-amber-300 border-amber-500/40', hex: '#fbbf24', label: 'Tham chiếu' };
        };

        const formatNumber = (num, decimals = 2) => {
            if (num === null || num === undefined || isNaN(num)) return '-';
            return Number(num).toLocaleString('vi-VN', { minimumFractionDigits: decimals, maximumFractionDigits: decimals });
        };

        const formatVolume = (vol) => {
            if (!vol) return '0';
            return Number(vol).toLocaleString('vi-VN');
        };

        function App() {
            const [vnIndex, setVnIndex] = useState(INITIAL_VNINDEX);
            const [tickers, setTickers] = useState(() => INITIAL_TICKERS.map(item => ({
                ...item, ceiling: calcCeiling(item.ref), floor: calcFloor(item.ref), flash: null
            })));

            const [activeCategory, setActiveCategory] = useState('ALL');
            const [searchQuery, setSearchQuery] = useState('');
            const [isLiveSim, setIsLiveSim] = useState(true);
            const [marketMood, setMarketMood] = useState('BULL');
            const [timeframe, setTimeframe] = useState('1D');
            const [selectedTickerSymbol, setSelectedTickerSymbol] = useState(null);
            const [lastUpdated, setLastUpdated] = useState(new Date());

            const [showAddModal, setShowAddModal] = useState(false);
            const [newTickerForm, setNewTickerForm] = useState({ symbol: '', name: '', type: 'STOCK', ref: '', price: '' });

            const [portfolioHoldings, setPortfolioHoldings] = useState({
                HPG: { qty: 2000, avgPrice: 26.50 },
                FUEVFVND: { qty: 1000, avgPrice: 31.80 },
                E1VFVN30: { qty: 1500, avgPrice: 22.50 },
                ACB: { qty: 3000, avgPrice: 25.20 },
                MBB: { qty: 2000, avgPrice: 25.00 },
                VIB: { qty: 2500, avgPrice: 19.10 }
            });
            const [showPortfolioModal, setShowPortfolioModal] = useState(false);

            useEffect(() => {
                if (!isLiveSim) return;
                const interval = setInterval(() => {
                    const moodBias = marketMood === 'BULL' ? 0.58 : marketMood === 'BEAR' ? 0.38 : 0.5;
                    
                    setVnIndex(prev => {
                        const isUp = Math.random() < moodBias;
                        const step = Number(((Math.random() * 0.85 + 0.05) * (isUp ? 1 : -1)).toFixed(2));
                        const nextPrice = Number(Math.max(1150, prev.price + step).toFixed(2));
                        const nowStr = new Date().toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
                        return {
                            ...prev,
                            price: nextPrice,
                            high: Math.max(prev.high, nextPrice),
                            low: Math.min(prev.low, nextPrice),
                            volume: prev.volume + Math.floor(Math.random() * 450000 + 80000),
                            value: Number((prev.value + Math.random() * 14.5 + 2.1).toFixed(1)),
                            history: [...prev.history.slice(-24), { time: nowStr, value: nextPrice }],
                            flash: step > 0 ? 'up' : 'down'
                        };
                    });

                    setTickers(prevTickers => prevTickers.map(t => {
                        if (Math.random() > 0.55) return { ...t, flash: null };
                        const isUp = Math.random() < moodBias;
                        const delta = (Math.floor(Math.random() * 2) + 1) * 0.05 * (isUp ? 1 : -1);
                        let nextPrice = Number((t.price + delta).toFixed(2));
                        if (nextPrice > t.ceiling) nextPrice = t.ceiling;
                        if (nextPrice < t.floor) nextPrice = t.floor;
                        return {
                            ...t,
                            price: nextPrice,
                            high: Math.max(t.high, nextPrice),
                            low: Math.min(t.low, nextPrice),
                            volume: t.volume + Math.floor(Math.random() * 18500 + 1200) * 10,
                            sparkline: [...t.sparkline.slice(-11), nextPrice],
                            flash: nextPrice !== t.price ? (nextPrice > t.price ? 'up' : 'down') : null
                        };
                    }));
                    setLastUpdated(new Date());
                }, 2600);
                return () => clearInterval(interval);
            }, [isLiveSim, marketMood]);

            const vnIndexMetrics = useMemo(() => {
                const change = Number((vnIndex.price - vnIndex.ref).toFixed(2));
                const percent = Number(((change / vnIndex.ref) * 100).toFixed(2));
                const isUp = change > 0;
                const isDown = change < 0;
                return {
                    change, percent, isUp, isDown,
                    statusText: isUp ? 'ĐANG TĂNG' : isDown ? 'ĐANG GIẢM' : 'ĐỨNG GIÁ',
                    colorClass: isUp ? 'text-emerald-400' : isDown ? 'text-rose-400' : 'text-amber-400',
                    bgClass: isUp ? 'from-emerald-500/15 via-emerald-950/20 to-slate-900/90 border-emerald-500/30' : 'from-rose-500/15 via-rose-950/20 to-slate-900/90 border-rose-500/30',
                    strokeHex: isUp ? '#10b981' : isDown ? '#f43f5e' : '#f59e0b'
                };
            }, [vnIndex]);

            const chartData = useMemo(() => {
                if (timeframe === '1D') return vnIndex.history;
                const count = timeframe === '1W' ? 7 : timeframe === '1M' ? 22 : timeframe === '3M' ? 60 : 120;
                const startBase = vnIndex.ref - 20;
                const points = [];
                let current = startBase;
                for (let i = count; i >= 1; i--) {
                    current = Number((current + (Math.sin(i * 0.6) * 4.5)).toFixed(2));
                    points.push({ time: `Ngày -${i}`, value: Math.max(1100, current) });
                }
                points.push({ time: 'Hôm nay', value: vnIndex.price });
                return points;
            }, [timeframe, vnIndex]);

            const filteredTickers = useMemo(() => {
                return tickers.filter(t => {
                    const matchesCat = activeCategory === 'ALL' || t.type === activeCategory;
                    const matchesQuery = t.symbol.toLowerCase().includes(searchQuery.toLowerCase()) || t.name.toLowerCase().includes(searchQuery.toLowerCase());
                    return matchesCat && matchesQuery;
                });
            }, [tickers, activeCategory, searchQuery]);

            const selectedTicker = useMemo(() => tickers.find(t => t.symbol === selectedTickerSymbol) || null, [tickers, selectedTickerSymbol]);

            const portfolioSummary = useMemo(() => {
                let totalCost = 0, totalMarketValue = 0;
                tickers.forEach(t => {
                    const h = portfolioHoldings[t.symbol];
                    if (h && h.qty > 0) {
                        totalCost += h.qty * h.avgPrice * 1000;
                        totalMarketValue += h.qty * t.price * 1000;
                    }
                });
                const profit = totalMarketValue - totalCost;
                const profitPercent = totalCost > 0 ? (profit / totalCost) * 100 : 0;
                return { totalCost, totalMarketValue, profit, profitPercent };
            }, [tickers, portfolioHoldings]);

            const handleAddCustomTicker = (e) => {
                e.preventDefault();
                const sym = newTickerForm.symbol.trim().toUpperCase();
                if (!sym) return;
                const refVal = parseFloat(newTickerForm.ref) || 25.0;
                const priceVal = parseFloat(newTickerForm.price) || refVal;
                const newEntry = {
                    symbol: sym, name: newTickerForm.name.trim() || sym, type: newTickerForm.type,
                    sector: 'Cổ phiếu niêm yết', exchange: 'HOSE', ref: refVal, price: priceVal,
                    open: refVal, high: Math.max(refVal, priceVal), low: Math.min(refVal, priceVal),
                    volume: 1250000, foreignBuy: 1200
