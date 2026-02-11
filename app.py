import streamlit as st
import pandas as pd
import numpy as np
import random
from datetime import datetime
from dateutil.relativedelta import relativedelta
import io
import zipfile

st.set_page_config(page_title="利用明細ジェネレーター", layout="wide")

# UIカスタマイズ
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    [data-testid="stMetric"] {
        background-color: #ffffff; border: 2px solid #333; padding: 20px !important;
        border-radius: 8px;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("💳 クレジットカード利用明細ジェネレーター")

# --- 設定エリア ---
with st.sidebar:
    st.header("⚙️ 出力設定")
    now = datetime.now()
    month_options = [(now - relativedelta(months=i)).strftime("%Y-%m") for i in range(24)]
    
    start_month_str = st.selectbox("開始月", month_options, index=5)
    end_month_str = st.selectbox("終了月", month_options, index=0)
    
    st.divider()
    user_name = st.text_input("カード会員名", "SAMPLE USER")

# 日付計算
start_dt = datetime.strptime(start_month_str, "%Y-%m")
end_dt = datetime.strptime(end_month_str, "%Y-%m")

if start_dt > end_dt:
    st.error("エラー：開始月は終了月より前の月を選択してください。")
else:
    # 1. データの生成
    merchants = [
        ("ｱﾏｿﾞﾝ ｼﾞﾔﾊﾟﾝ", "ｼｮｯﾋﾟﾝｸﾞ"), ("ｽﾀｰﾊﾞｯｸｽ ｺｰﾋｰ", "飲食"), ("JR東日本 ﾓﾊﾞｲﾙｽｲｶ", "交通"),
        ("ｱﾂﾌﾟﾙﾄﾞﾂﾄｺﾑ", "ｻﾌﾞｽｸ"), ("ｾﾌﾞﾝ-ｲﾚﾌﾞﾝ", "ｺﾝﾋﾞﾆ"), ("ﾆﾂﾎﾟﾝ ﾚﾝﾀｶｰ", "旅行")
    ]

    target_months = []
    curr = start_dt
    while curr <= end_dt:
        target_months.append(curr)
        curr += relativedelta(months=1)

    all_monthly_data = {}
    total_amt = 0

    for m in target_months:
        num_tx = random.randint(10, 20)
        items = []
        for _ in range(num_tx):
            day = random.randint(1, 28)
            tx_date = m + timedelta(days=day-1)
            merchant, _ = random.choice(merchants)
            amt = random.randint(500, 30000)
            items.append({
                "利用日": tx_date.strftime("%Y/%m/%d"),
                "利用先": merchant,
                "金額（円）": amt,
                "備考": ""
            })
            total_amt += amt
        
        df_m = pd.DataFrame(items).sort_values("利用日")
        # 合計行の追加
        subtotal = pd.DataFrame([{"利用日": "---", "利用先": "【合計】", "金額（円）": df_m["金額（円）"].sum(), "備考": ""}])
        all_monthly_data[m.strftime("%Y-%m")] = pd.concat([df_m, subtotal], ignore_index=True)

    # 2. 画面表示
    c1, c2 = st.columns(2)
    c1.metric("選択期間の総額", f"¥{total_amt:,}")
    c2.metric("生成月数", f"{len(target_months)}ヶ月分")

    st.divider()

    # 3. ZIPファイルの作成（ここを修正しました）
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        for m_str, df_target in all_monthly_data.items():
            # プレビュー表示
            with st.expander(f"📂 {m_str} の明細を確認"):
                st.dataframe(df_target, use_container_width=True)
            
            # 各月のCSVをZIPに追加
            csv_data = df_target.to_csv(index=False).encode('utf-8-sig')
            zf.writestr(f"statement_{m_str}.csv", csv_data)

    st.divider()

    # 4. ダウンロードボタン
    st.download_button(
        label="📩 全月分の明細（ZIP形式）をダウンロード",
        data=zip_buffer.getvalue(),
        file_name=f"credit_card_data_{datetime.now().strftime('%Y%m%d')}.zip",
        mime="application/zip",
        use_container_width=True
    )
