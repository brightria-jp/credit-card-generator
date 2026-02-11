import streamlit as st
import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import io
import zipfile

# ページ設定
st.set_page_config(page_title="利用明細ジェネレーター", layout="wide")

st.title("💳 クレジットカード利用明細ジェネレーター")

# --- サイドバー設定 ---
with st.sidebar:
    st.header("⚙️ 出力設定")
    now = datetime.now()
    # 選択肢の作成
    month_options = [(now - relativedelta(months=i)).strftime("%Y-%m") for i in range(24)]
    
    start_month_str = st.selectbox("開始月", month_options, index=5)
    end_month_str = st.selectbox("終了月", month_options, index=0)
    
    st.divider()
    user_name = st.text_input("カード会員名", "SAMPLE USER")

# 日付オブジェクトに変換
start_dt = datetime.strptime(start_month_str, "%Y-%m")
end_dt = datetime.strptime(end_month_str, "%Y-%m")

# エラーチェック
if start_dt > end_dt:
    st.error("開始月は終了月より前の月を選択してください。")
else:
    # 1. 対象月のリスト作成
    target_months = []
    temp_dt = start_dt
    while temp_dt <= end_dt:
        target_months.append(temp_dt)
        temp_dt += relativedelta(months=1)

    # マスターデータ
    merchants = ["ｱﾏｿﾞﾝ ｼﾞﾔﾊﾟﾝ", "ｽﾀｰﾊﾞｯｸｽ", "JR東日本 ｽｲｶ", "ｱﾂﾌﾟﾙﾄﾞﾂﾄｺﾑ", "ｾﾌﾞﾝ-ｲﾚﾌﾞﾝ", "Uber Eats"]

    # 2. データ生成とZIP準備
    zip_buffer = io.BytesIO()
    total_all_months = 0
    
    # メモリ上にZIPを作成
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        for m in target_months:
            m_str = m.strftime("%Y-%m")
            num_tx = random.randint(8, 15)
            rows = []
            month_sum = 0
            
            for _ in range(num_tx):
                day = random.randint(1, 28)
                tx_date = m + timedelta(days=day-1)
                amt = random.randint(500, 20000)
                rows.append({
                    "利用日": tx_date.strftime("%Y/%m/%d"),
                    "利用先": random.choice(merchants),
                    "金額（円）": amt
                })
                month_sum += amt
            
            # 月ごとのDF作成
            df_m = pd.DataFrame(rows).sort_values("利用日")
            # 合計行を追加
            subtotal = pd.DataFrame([{"利用日": "---", "利用先": "【合計】", "金額（円）": month_sum}])
            df_final = pd.concat([df_m, subtotal], ignore_index=True)
            
            # 画面表示用のプレビュー
            with st.expander(f"📂 {m_str} の明細プレビュー"):
                st.dataframe(df_final, use_container_width=True)
            
            # CSVをZIPに書き込み
            csv_data = df_final.to_csv(index=False).encode('utf-8-sig')
            zf.writestr(f"statement_{m_str}.csv", csv_data)
            
            total_all_months += month_sum

    st.divider()
    
    # 3. 統計とダウンロード
    st.metric("選択期間の総利用額", f"¥{total_all_months:,}")
    
    st.download_button(
        label="📩 全月分の明細（ZIP形式）を一括ダウンロード",
        data=zip_buffer.getvalue(),
        file_name=f"card_statements_{datetime.now().strftime('%Y%m%d')}.zip",
        mime="application/zip",
        use_container_width=True
    )
