import streamlit as st
import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

st.set_page_config(page_title="AMEX風カード明細生成", layout="wide")

# --- UIデザイン ---
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    [data-testid="stMetric"] {
        background-color: #ffffff; border: 2px solid #006fcf; padding: 20px !important;
        border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .main { background-color: #f0f2f5; }
    </style>
    """, unsafe_allow_html=True)

st.title("🛡️ AMEX風・月次利用明細ジェネレーター")

# --- サイドバー設定 ---
with st.sidebar:
    st.header("⚙️ 出力設定")
    start_month = st.date_input("開始月", value=datetime.now() - relativedelta(months=5))
    end_month = st.date_input("終了月", value=datetime.now())
    st.divider()
    user_name = st.text_input("カード会員名", "SAMPLE USER")
    st.write("Ver.2.0: AMEX実データ準拠モデル")

# --- マスターデータ ---
merchants = [
    ("ｱﾏｿﾞﾝ ｼﾞﾔﾊﾟﾝ", "ｼｮｯﾋﾟﾝｸﾞ"), ("ｽﾀｰﾊﾞｯｸｽ ｺｰﾋｰ", "飲食"), ("JR東日本 ﾓﾊﾞｲﾙｽｲｶ", "交通"),
    ("ｱﾂﾌﾟﾙﾄﾞﾂﾄｺﾑ", "ｻﾌﾞｽｸ"), ("ｾﾌﾞﾝ-ｲﾚﾌﾞﾝ", "ｺﾝﾋﾞﾆ"), ("ﾆﾂﾎﾟﾝ ﾚﾝﾀｶｰ", "旅行"),
    ("Uber Eats", "飲食"), ("Google Cloud", "ﾋﾞｼﾞﾈｽ"), ("Microsoft 365", "ﾋﾞｼﾞﾈｽ")
]

# --- データ生成 ---
current = datetime(start_month.year, start_month.month, 1)
end = datetime(end_month.year, end_month.month, 1)
all_data = []

while current <= end:
    month_total = 0
    num_tx = random.randint(10, 20) # 1ヶ月の決済件数
    
    # その月の決済を生成
    month_items = []
    for _ in range(num_tx):
        day = random.randint(1, 28)
        tx_date = current + timedelta(days=day-1)
        merchant, cat = random.choice(merchants)
        amount = random.randint(500, 30000)
        
        month_items.append({
            "日付": tx_date.strftime("%Y/%m/%d"),
            "内容": merchant,
            "金額（円）": amount,
            "獲得ポイント": int(amount / 100),
            "備考": ""
        })
        month_total += amount
    
    # 日付順にソート
    month_items.sort(key=lambda x: x["日付"])
    all_data.extend(month_items)
    
    # 月の区切り（小計行）を追加
    all_data.append({
        "日付": f"--- {current.strftime('%Y年%m月')} ---",
        "内容": "【月間小計】",
        "金額（円）": month_total,
        "獲得ポイント": int(month_total / 100),
        "備考": f"支払予定日: {(current + relativedelta(months=1, day=10)).strftime('%m/%d')}"
    })
    
    current += relativedelta(months=1)

df = pd.DataFrame(all_data)

# --- UI表示 ---
m1, m2 = st.columns(2)
with m1: st.metric("期間中総利用額", f"¥{df[df['内容'] != '【月間小計】']['金額（円）'].sum():,}")
with m2: st.metric("累計獲得ポイント", f"{df[df['内容'] != '【月間小計】']['獲得ポイント'].sum():,} pt")

st.divider()
st.subheader("📋 利用履歴（月次フォーマット）")
# 表の表示。小計行を強調するためにスタイルを適用（簡易）
st.dataframe(df, use_container_width=True, height=600)

# CSVダウンロード
csv = df.to_csv(index=False).encode('utf-8-sig')
st.download_button("📩 AMEX形式CSVを保存", csv, "amex_dummy_data.csv", "text/csv", use_container_width=True)
