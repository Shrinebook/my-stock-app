import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

# 日本語表示の設定（Streamlit Cloudでも動作するように調整）
try:
    import japanize_matplotlib
except:
    pass

st.set_page_config(page_title="高配当株・押し目検知", layout="centered")

st.title("📈 高配当株 押し目検知")
st.caption("数ヶ月は右肩上がり、直近3日は安い銘柄を抽出")

# ==========================================
# 銘柄リスト（全72銘柄）
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
    '2267.T': 'ヤクルト本社', '4732.T': 'ユー・エス・エス', '8051.T': '山善'
}

# --- 解析実行ボタン ---
if st.button('分析を開始する (全72銘柄)'):
    results = []
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    tickers = list(target_dict.keys())
    for i, ticker in enumerate(tickers):
        status_text.text(f"解析中: {target_dict[ticker]} ({i+1}/{len(tickers)})")
        progress_bar.progress((i + 1) / len(tickers))
        
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period="6mo")
            if len(hist) < 75: continue

            current_price = hist['Close'].iloc[-1]
            ma75 = hist['Close'].rolling(window=75).mean().iloc[-1]
            ma25 = hist['Close'].rolling(window=25).mean()
            
            # 直近3日騰落率
            price_3d_ago = hist['Close'].iloc[-4]
            return_3d = (current_price - price_3d_ago) / price_3d_ago * 100

            # ロジック: 長期上昇トレンド中 且つ 直近3日で-1.5%以上の押し目
            if current_price > ma75 and return_3d < -1.5:
                results.append({
                    'name': target_dict[ticker],
                    'ticker': ticker,
                    'price': current_price,
                    'return_3d': return_3d,
                    'hist': hist.tail(60),
                    'ma25': ma25.tail(60)
                })
        except:
            continue

    status_text.text("解析完了！")
    
    if results:
        # 下げ幅が大きい順に並べ替え
        results.sort(key=lambda x: x['return_3d'])
        
        st.success(f"{len(results)}銘柄の押し目候補が見つかりました")
        
        for item in results:
            # スマホで見やすいアコーディオン形式
            with st.expander(f"📌 {item['name']} ({item['return_3d']:+.2f}%)"):
                st.write(f"**現在値:** {item['price']:,.1f}円")
                
                # グラフ描画
                fig, ax = plt.subplots(figsize=(8, 4))
                ax.plot(item['hist']['Close'], label='株価', color='#1f77b4', linewidth=2)
                ax.plot(item['ma25'], label='25日線', color='#ff7f0e', linestyle='--')
                ax.set_title(f"{item['name']} の推移")
                ax.grid(True, alpha=0.3)
                ax.legend()
                st.pyplot(fig)
                plt.close()
    else:
        st.warning("現在、条件に合致する銘柄はありません。")
