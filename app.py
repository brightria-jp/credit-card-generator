import streamlit as st
import pandas as pd
import numpy as np
import random
from datetime import datetime
from dateutil.relativedelta import relativedelta
import io
import zipfile

st.set_page_config(page_title="利用明細ジェネレーター", layout="wide")

# --- UIデザイン ---
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    [data-testid="stMetric"] {
        background-color: #ffffff; border: 2px solid #333; padding: 20px !important;
        border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    </style>
    """, unsafe_allow_html=True)

st.title("💳 クレジットカード利用明細ジェネレーター")

# --- サイドバー設定 ---
with st.sidebar:
    st.header("⚙️ 出力設定")
    
    # 月選択のリスト作成
    now = datetime.now()
    month_options = [(now - relativedelta(months=i)).strftime("%Y-%m") for i in range(24)]
    
    start_month_str = st.selectbox("開始月", month_options, index=5)
    end_month_str = st.selectbox("終了月", month_options, index=0)
    
    st.divider()
    user_name = st.text_input("カード会員名", "SAMPLE USER")

# --- マスターデータ ---
merchants = [
    ("ｱﾏｿﾞﾝ ｼﾞﾔﾊﾟﾝ", "ｼｮｯﾋﾟﾝｸﾞ"), ("ｽﾀｰﾊﾞｯｸｽ ｺｰﾋｰ", "飲食"), ("JR東日本 ﾓﾊﾞｲﾙｽｲｶ", "交通"),
    ("ｱﾂﾌﾟﾙﾄﾞﾂﾄｺﾑ", "ｻﾌﾞｽｸ"), ("ｾﾌﾞﾝ-イレブン", "ｺﾝﾋﾞﾆ"), ("ﾆﾂﾎﾟﾝ ﾚﾝﾀｶｰ", "旅行"),
    ("Uber Eats", "飲食"), ("Google Cloud", "ﾋﾞｼﾞﾈｽ"), ("Microsoft 365", "ﾋﾞｼﾞﾈｽ")
]

# --- データ生成ロジック ---
start_dt = datetime.strptime(start_month_str, "%Y-%m")
end_dt = datetime.strptime(end_month_str, "%Y-%m")

# 月リストの作成
current = start_dt
target_months = []
while current <= end_dt:
    target_months.append(current)
    current += relativedelta(months=1)

# 各月のデータを保持する辞書
monthly_dfs = {}

for m in target_months:
    num_tx = random.randint(10, 25)
    month_items = []
    for _ in range(num_tx):
        day = random.randint(1, 28)
        tx_date = m + timedelta(days=day-1)
        merchant, cat = random.choice(merchants)
        amount = random.randint(500, 45000)
        
        month_items.append({
            "利用日": tx_date.strftime("%Y/%m/%d"),
            "利用先": merchant,
            "金額（円）": amount,
            "獲得ポイント": int(amount / 100),
            "備考": ""
        })
    
    df_m = pd.DataFrame(month_items).sort_values("利用日")
    # 小計行を追加
    subtotal = pd.DataFrame([{
        "利用日": "---", "利用先": "【月間合計】", "金額（円）": df_m["金額（円）"].sum(),
        "獲得ポイント": df_m["獲得ポイント"].sum(), "備考": f"{m.strftime('%m')}月分請求予定"
    }])
    monthly_dfs[m.strftime("%Y-%m")] = pd.concat([df_m, subtotal], ignore_index=True)

# --- UI表示 ---
st.subheader(f"📊 生成結果：{len(target_months)}ヶ月分")

# ZIPファイルの作成
buf = io.BytesIO()
with zipfile.ZipFile(buf, "x") as csv_zip:
    for month_str, df_month in monthly_dfs.items():
        # プレビュー表示（最初の数ヶ月分のみ）
        with st.expander(f"📁 {month_str} の明細プレビュー"):
            st.dataframe(df_month, use_container_width=True)
        
        # ZIP用にCSV変換
        csv_data = df_month.to_csv(index=False).encode('utf-8-sig')
        csv_zip.writestr(f"statement_{month_str}.csv", csv_data)

st.divider()

# ダウンロードボタン
st.download_button(
    label="📩 全月分のCSV（ZIP形式）をダウンロード",
    data=buf.getvalue(),
    file_name=f"credit_card_statements_{datetime.now().strftime('%Y%m%d')}.zip",
    mime="application/zip",
    use_container_width=True
)
