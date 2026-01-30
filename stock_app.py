import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="高配当株チェッカー", layout="centered")

st.title("📈 高配当株 押し目検知")
st.caption("上昇トレンド中の『一時的な安値』を抽出します")

# 銘柄リスト
target_dict = {
    '4503.T': 'アステラス製薬', '9432.T': 'NTT', '8591.T': 'オリックス',
    '8306.T': '三菱UFJ FG', '2914.T': 'JT', '7203.T': 'トヨタ自動車',
    # ... 他の銘柄も同様に追加 ...
}

if st.button('最新データを取得して分析開始'):
    results = []
    with st.spinner('解析中...'):
        for ticker, name in target_dict.items():
            try:
                stock = yf.Ticker(ticker)
                hist = stock.history(period="6mo")
                if len(hist) < 75: continue

                current_price = hist['Close'].iloc[-1]
                ma75 = hist['Close'].rolling(window=75).mean().iloc[-1]
                ma25 = hist['Close'].rolling(window=25).mean()
                
                # 短期下落判定
                price_3d_ago = hist['Close'].iloc[-4]
                return_3d = (current_price - price_3d_ago) / price_3d_ago * 100

                if current_price > ma75 and return_3d < -1.0:
                    results.append({
                        'name': name, 'ticker': ticker, 'price': current_price,
                        'return_3d': return_3d, 'hist': hist.tail(60), 'ma25': ma25.tail(60)
                    })
            except:
                continue

    if results:
        for item in results:
            with st.expander(f"📌 {item['name']} ({item['return_3d']:+.2f}%)"):
                st.write(f"**現在値:** {item['price']:,.1f}円")
                
                # グラフ作成
                fig, ax = plt.subplots(figsize=(8, 4))
                ax.plot(item['hist']['Close'], label='株価', color='#1f77b4')
                ax.plot(item['ma25'], label='25日線', color='#ff7f0e', linestyle='--')
                ax.legend()
                st.pyplot(fig)
    else:
        st.write("該当する銘柄はありませんでした。")

