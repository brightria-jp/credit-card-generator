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
    user_name = st.text_input("カード会員名", "ＨＩＤＥＮＯＲＩ　ＫＩＤＡ")
    card_no = st.text_input("会員番号末尾", "XXXX-XXXXXX-82001")

# 日付計算
start_dt = datetime.strptime(start_month_str, "%Y-%m")
end_dt = datetime.strptime(end_month_str, "%Y-%m")

if start_dt > end_dt:
    st.error("エラー：開始月は終了月より前の月を選択してください。")
else:
    # 加盟店名（実データを参考にリアル化）
    merchants = [
        "アマゾン　ＪＰ　マーケットプレイス", "アマゾン　シーオージェーピー", "セブンイレブン",
        "すき家　東京都　港区", "ＪＲ東日本モバイルＳｕｉｃａ", "丸源ラーメン",
        "目利きの銀次　新百合ヶ丘北口駅前店", "クリエイトエス・ディー", "ＳＢＩプリズム少短",
        "イデミツ　アポロステーション", "チケットぴあ"
    ]

    target_months = []
    curr = start_dt
    while curr <= end_dt:
        target_months.append(curr)
        curr += relativedelta(months=1)

    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        for m in target_months:
            m_str = m.strftime("%Y-%m")
            num_tx = random.randint(15, 25)
            rows = []
            
            for _ in range(num_tx):
                day = random.randint(1, 28)
                use_date = m + timedelta(days=day-1)
                process_date = use_date + timedelta(days=random.randint(0, 3)) # 処理日は0〜3日後
                
                # 5%の確率で返品（マイナス）を発生させる
                is_return = random.random() < 0.05
                amt = random.randint(500, 15000) * (-1 if is_return else 1)
                
                rows.append({
                    "ご利用日": use_date.strftime("%Y/%m/%d"),
                    "データ処理日": process_date.strftime("%Y/%m/%d"),
                    "金額": amt,
                    "ご利用内容": random.choice(merchants)
                })
            
            # 日付順にソート（最新が上という実データ形式）
            df_m = pd.DataFrame(rows).sort_values("ご利用日", ascending=False)
            
            # --- リアルなCSVヘッダーの作成 ---
            total_sum = df_m["金額"].sum()
            header_data = [
                ["ご利用履歴", f"カード明細 / {m_str}-01 - {m_str}-28", "", ""],
                ["カード会員様名", "", user_name, ""],
                ["会員番号", "", card_no, ""],
                ["", "", "", ""],
                ["ご利用合計金額", "", f"{total_sum:,}", ""],
                ["", "", "", ""],
                ["ご利用日", "データ処理日", "金額", "ご利用内容"] # 7行目にヘッダー
            ]
            
            # ヘッダーとデータを結合
            output_list = header_data + df_m.values.tolist()
            final_csv_df = pd.DataFrame(output_list)
            
            # プレビュー表示
            with st.expander(f"📂 {m_str} の明細プレビュー"):
                st.dataframe(df_m, use_container_width=True)
            
            # CSV化（ヘッダーなしで出力することで作成したoutput_listをそのまま出す）
            csv_data = final_csv_df.to_csv(index=False, header=False).encode('utf-8-sig')
            zf.writestr(f"statement_{m_str}.csv", csv_data)

    st.divider()
    st.download_button(
        label="📩 実データ形式・全月分CSV（ZIP）をダウンロード",
        data=zip_buffer.getvalue(),
        file_name=f"credit_card_data_{datetime.now().strftime('%Y%m%d')}.zip",
        mime="application/zip",
        use_container_width=True
    )
