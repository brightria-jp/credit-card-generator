import streamlit as st
import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta

st.set_page_config(page_title="カード明細ジェネレーター", layout="wide")

# --- UIデザイン（右上のメニュー非表示とスタイリング） ---
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    [data-testid="stMetric"] {
        background-color: #ffffff; border: 2px solid #d0d0d0; padding: 20px !important;
        border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); min-height: 160px;
    }
    [data-testid="stMetricLabel"] { color: #1a1a1a !important; font-weight: bold !important; font-size: 1.1rem !important; }
    [data-testid="stMetricValue"] { color: #000000 !important; font-weight: 800 !important; }
    </style>
    """, unsafe_allow_html=True)

st.title("💳 クレジットカード利用明細ジェネレーター")

# --- サイドバー設定 ---
with st.sidebar:
    st.header("⚙️ 明細設定")
    brand = st.selectbox("国際ブランド", ["Visa", "Mastercard", "JCB", "AMEX"])
    card_last4 = st.text_input("カード番号末尾4桁", "1234")
    years = st.slider("生成期間（年）", 1, 3, 1)
    max_rows = st.number_input("表示・保存する最大件数", min_value=1, max_value=5000, value=500)
    
    st.divider()
    st.write("Ver.1.0: カード利用明細シミュレーター")

# --- 加盟店データ ---
merchants = {
    "飲食": ["ｽﾀｰﾊﾞｯｸｽC", "ﾏｸﾄﾞﾅﾙﾄﾞ", "ｻｲｾﾞﾘﾔ", "居酒屋○○", "ｳｰﾊﾞｰｲｰﾂ"],
    "交通": ["JR東日本", "東京ﾒﾄﾛ", "ﾀｸｼｰｺﾞｰ", "ANA", "JAL"],
    "ｼｮｯﾋﾟﾝｸﾞ": ["ｱﾏｿﾞﾝJAPAN", "楽天市場", "ﾕﾆｸﾛｵﾝﾗｲﾝ", "ﾖﾄﾞﾊﾞｼｶﾒﾗ", "ｺﾝﾋﾞﾆ"],
    "ｻﾌﾞｽｸ/固定費": ["NETFLIX", "Apple.com/bill", "Spotify", "電力会社", "ｶﾞｽ料金"]
}

# --- データ生成ロジック ---
today = datetime.now()
start_date = today - timedelta(days=365 * years)
current_date = start_date

data = []

while current_date <= today:
    # 毎日使うわけではない
    if random.random() > 0.3: 
        num_tx_today = random.randint(1, 4)
        for _ in range(num_tx_tx_today := num_tx_today):
            category = random.choice(list(merchants.keys()))
            merchant = random.choice(merchants[category])
            
            # 金額設定（カテゴリー別）
            if category == "飲食": amount = random.randint(500, 8000)
            elif category == "交通": amount = random.choice([1000, 2000, 3000, 5000, 15000])
            elif category == "ｼｮｯﾋﾟﾝｸﾞ": amount = random.randint(1000, 50000)
            else: amount = random.randint(1000, 15000)
            
            # ポイント計算 (1%)
            points = int(amount * 0.01)
            
            data.append({
                "利用日": current_date.strftime('%Y/%m/%d'),
                "利用先": merchant,
                "利用者": "本人",
                "支払区分": "1回払い",
                "金額(円)": amount,
                "獲得ポイント": points,
                "カテゴリー": category
            })

    current_date += timedelta(days=1)

# DataFrame化して最新分を切り出し
df = pd.DataFrame(data)
df = df.tail(max_rows)

# --- UI表示 ---
m1, m2, m3 = st.columns(3)
with m1: st.metric("期間中総支払額", f"¥{int(df['金額(円)'].sum()):,}")
with m2: st.metric("獲得予定ポイント", f"{int(df['獲得ポイント'].sum()):,} pt")
with m3: st.metric("利用件数", f"{len(df)}件")

st.divider()
c1, c2 = st.columns([1, 1])
with c1:
    st.subheader("📊 カテゴリー別支出")
    cat_summary = df.groupby("カテゴリー")["金額(円)"].sum()
    st.bar_chart(cat_summary)
with c2:
    st.subheader("📋 利用明細（最新順）")
    st.dataframe(df.sort_index(ascending=False), use_container_width=True)

csv = df.to_csv(index=False).encode('utf-8-sig')
st.download_button("📩 カード明細CSVをダウンロード", csv, f"credit_card_statement_{today.strftime('%Y%m%d')}.csv", "text/csv", use_container_width=True)
