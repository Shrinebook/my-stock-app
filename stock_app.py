import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="高配当株・押し目検知", layout="centered")

# 【修正点1】タイトルを小さく表示 (subheaderを使用)
st.markdown("### 📈 高配当株 押し目検知")
st.caption("上昇トレンド中の『一時的な安値』を抽出")

# ==========================================
# 銘柄リスト（全73銘柄に更新）
# ==========================================
target_dict = {
    '4503.T': 'アステラス製薬', '7476.T': 'アズワン', '2502.T': 'アサヒグループHD',
    '3407.T': '旭化成', '9202.T': 'ANA HD', '3292.T': 'イオンリート',
    '9882.T': 'イエローハット', '8001.T': '伊藤忠商事', '1605.T': 'INPEX',
    '4661.T': 'オリエンタルランド', '8591.T': 'オリックス', '4452.T': '花王',
    '7012.T': '川崎重工業', '9503.T': '関西電力', '2801.T': 'キッコーマン',
    '9986.T': '蔵王産業', '3405.T': 'クラレ', '6301.T': '小松製作所',
    '8130.T': 'サンゲツ', '9989.T': 'サンドラッグ', '8801.T': '三井不動産',
    '8031.T': '三井物産', '8316.T': '三井住友FG', '8058.T': '三菱商事',
    '8306.T': '三菱UFJ FG', '8593.T': '三菱HCキャピタル', '5192.T': '三ツ星ベルト',
    '7762.T': 'シチズン時計', '4063.T': '信越化学工業', '4507.T': '塩野義製薬',
    '1911.T': '住友林業', '7839.T': 'SHOEI', '3092.T': 'ZOZO',
    '9434.T': 'ソフトバンク', '3817.T': 'SRA HD', '8750.T': '第一生命HD',
    '6367.T': 'ダイキン工業', '1925.T': '大和ハウス工業', '4502.T': '武田薬品工業',
    '7921.T': 'TAKARA & COMPANY', '4519.T': '中外製薬', '9513.T': '電源開発',
    '4812.T': '電通総研', '1882.T': '東亜道路工業', '8766.T': '東京海上HD',
    '8035.T': '東京エレクトロン', '3289.T': '東急不動産HD', '3433.T': 'トーカロ',
    '7203.T': 'トヨタ自動車', '2871.T': 'ニチレイ', '4516.T': '日本新薬',
    '2914.T': '日本たばこ産業', '8697.T': '日本取引所G', '2353.T': '日本駐車場開発',
    '5401.T': '日本製鉄', '9432.T': 'NTT', '7240.T': 'NOK',
    '3231.T': '野村不動産HD', '4928.T': 'ノエビアHD', '2674.T': 'ハードオフ',
    '3003.T': 'ヒューリック', '4481.T': 'ベース', '3287.T': '星野リゾート・リート',
    '7267.T': '本田技研工業', '7148.T': 'FPG', '9983.T': 'ファーストリテイリング',
    '7730.T': 'マニー', '1417.T': 'ミライト・ワン', '8725.T': 'MS&AD',
    '2267.T': 'ヤクルト本社', '4732.T': 'ユー・エス・エス', '8051.T': '山善',
    '7164.T': '全国保証' # 追加しました
}

# 【修正点2】コア銘柄のリスト
core_tickers = [
    '7267.T', '8766.T', '3231.T', '9513.T', '5401.T', '7839.T', '7164.T', 
    '7762.T', '9434.T', '2914.T', '5192.T', '2674.T', '1882.T', '8306.T', 
    '6301.T', '4928.T', '8130.T', '4502.T'
]

if st.button('分析を開始する'):
    results = []
    status_text = st.empty()
    progress_bar = st.progress(0)
    
    tickers = list(target_dict.items())
    for i, (code, name) in enumerate(tickers):
        status_text.text(f"解析中: {name} ({i+1}/{len(tickers)})")
        progress_bar.progress((i + 1) / len(tickers))
        
        try:
            stock = yf.Ticker(code)
            hist = stock.history(period="6mo")
            if len(hist) < 75: continue

            current_price = hist['Close'].iloc[-1]
            ma75 = hist['Close'].rolling(window=75).mean().iloc[-1]
            ma25 = hist['Close'].rolling(window=25).mean()
            
            # 前日比
            prev_close = hist['Close'].iloc[-2]
            daily_change = (current_price - prev_close) / prev_close * 100
            
            # 直近3日騰落率
            price_3d_ago = hist['Close'].iloc[-4]
            return_3d = (current_price - price_3d_ago) / price_3d_ago * 100

            # 判定: 75日線より上 かつ 直近3日で-1.5%以上の下落
            if current_price > ma75 and return_3d < -1.5:
                results.append({
                    'name': name,
                    'code': code,
                    'short_code': code.replace('.T', ''),
                    'price': current_price,
                    'daily': daily_change,
                    'return_3d': return_3d,
                    'hist': hist.tail(60),
                    'ma25': ma25.tail(60)
                })
        except:
            continue

    status_text.text("解析完了！")
    
    if results:
        results.sort(key=lambda x: x['return_3d'])
        st.success(f"{len(results)}銘柄見つかりました")
        
        for item in results:
            # 【修正点3】コア銘柄かどうかでラベルを分岐
            is_core = item['code'] in core_tickers
            core_mark = " ★(コア銘柄)" if is_core else ""
            label = f"📌 {item['short_code']} {item['name']}{core_mark} (3日:{item['return_3d']:+.2f}%)"
            
            with st.expander(label):
                c1, c2, c3 = st.columns(3)
                c1.metric("価格", f"{item['price']:,.0f}")
                c2.metric("前日比", f"{item['daily']:+.2f}%")
                c3.metric("3日騰落", f"{item['return_3d']:+.2f}%")
                
                fig, ax = plt.subplots(figsize=(8, 4))
                ax.plot(item['hist']['Close'], label='Price', color='#1f77b4', linewidth=2)
                ax.plot(item['ma25'], label='MA25', color='#ff7f0e', linestyle='--')
                ax.set_title(f"Trend: {item['short_code']}")
                ax.grid(True, alpha=0.3)
                ax.legend()
                st.pyplot(fig)
                plt.close(fig)
    else:
        st.warning("現在、条件に合う銘柄はありません。")
