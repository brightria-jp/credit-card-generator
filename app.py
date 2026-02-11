import streamlit as st
import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import io
import zipfile

st.set_page_config(page_title="利用明細ジェネレーター", layout="wide")

st.title("💳 クレジットカード利用明細ジェネレーター")

# --- 設定エリア ---
with st.sidebar:
    st.header("⚙️ 出力設定")
    now = datetime.now()
    month_options = [(now - relativedelta(months=i)).strftime("%Y-%m") for i in range(24)]
    start_month_str = st.selectbox("開始月", month_options, index=5)
    end_month_str = st.selectbox("終了月", month_options, index=0)
    user_name = st.text_input("カード会員名", "SAMPLE USER")
    card_no = st.text_input("会員番号末尾", "XXXX-XXXXXX-00000")

# 日付計算
start_dt = datetime.strptime(start_month_str, "%Y-%m")
end_dt = datetime.strptime(end_month_str, "%Y-%m")

if start_dt > end_dt:
    st.error("エラー：開始月は終了月より前の月を選択してください。")
else:
    # 固有名詞を排除したカテゴリーリスト
    categories = [
        "レストラン", "回転寿司", "スーパーマーケット", "ネット通販", "交通費（電車・バス）",
        "ガソリン代", "駐車場代", "チケット購入", "コンビニエンスストア", "自動車保険料",
        "ペット保険料", "ラーメン屋", "高速道路料金", "サブスクリプション費用", "宿泊・トラベル"
    ]

    target_months = []
    curr = start_dt
    while curr <= end_dt:
        target_months.append(curr)
        curr += relativedelta(months=1)

    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        for m in target_months:
            m_str = m.strftime("%Y/%m") # ② YYYY/MM 形式
            num_tx = random.randint(15, 25)
            rows = []
            
            # 前月の残高などをダミー生成
            prev_balance = random.randint(50000, 200000)
            payment_amt = prev_balance * -1 # 全額支払いと仮定
            
            current_month_amt = 0
            for _ in range(num_tx):
                day = random.randint(1, 28)
                use_date = m + timedelta(days=day-1)
                process_date = use_date + timedelta(days=random.randint(0, 3))
                
                is_return = random.random() < 0.03
                amt = random.randint(500, 20000) * (-1 if is_return else 1)
                current_month_amt += amt
                
                rows.append([
                    use_date.strftime("%Y/%m/%d"),
                    process_date.strftime("%Y/%m/%d"),
                    amt,
                    random.choice(categories)
                ])
            
            # 日付順（降順）
            rows.sort(key=lambda x: x[0], reverse=True)
            
            # --- AMEXのデザインを参考にした上部集計ブロック ---
            header_rows = [
                ["カード利用履歴", f"対象期間: {m_str}", "", ""],
                ["カード会員様名", user_name, "", ""],
                ["会員番号", card_no, "", ""],
                ["", "", "", ""],
                ["【集計情報】", "", "金額(円)", ""], # ① 小計・合計を上部に配置
                ["前回締め日金額", "", f"{prev_balance:,}", ""],
                ["お支払い金額/調整金額", "", f"{payment_amt:,}", ""],
                ["今回ご利用分合計", "", f"{current_month_amt:,}", ""],
                ["今回ご請求金額合計", "", f"{current_month_amt:,}", ""],
                ["", "", "", ""],
                ["ご利用日", "データ処理日", "金額", "ご利用内容"]
            ]
            
            # 結合
            final_data = header_rows + rows
            df_final = pd.DataFrame(final_data)
            
            # プレビュー用（生データのみ表示）
            with st.expander(f"📂 {m_str} の明細プレビュー"):
                preview_df = pd.DataFrame(rows, columns=["ご利用日", "データ処理日", "金額", "ご利用内容"])
                st.dataframe(preview_df, use_container_width=True)
            
            # CSV出力（index=FalseでA列の数字を消去）
            csv_data = df_final.to_csv(index=False, header=False).encode('utf-8-sig')
            zf.writestr(f"statement_{m.strftime('%Y%m')}.csv", csv_data)

    st.divider()
    st.download_button(
        label="📩 実データ形式・全月分CSV（ZIP）をダウンロード",
        data=zip_buffer.getvalue(),
        file_name=f"credit_card_data_{datetime.now().strftime('%Y%m%d')}.zip",
        mime="application/zip",
        use_container_width=True
    )
