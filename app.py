import streamlit as st
import pandas as pd

st.set_page_config(page_title="구조 성능 시뮬레이터", layout="wide")

st.title("🏗️ 구조 성능 시뮬레이터 (3개 모델 지원)")
st.markdown("모델과 항목을 선택하고, 응답값을 입력하면 자동으로 보강안을 제시합니다.")

# ✅ 엑셀 자동 로딩
EXCEL_FILE = "시뮬레이터 (3 모델 모델별_기준값_산정근거_상세설명 포함) - 복사본.xlsx"

try:
    df_main = pd.read_excel(EXCEL_FILE, sheet_name="simulator")
    df_ref = pd.read_excel(EXCEL_FILE, sheet_name="보강안 및 근거")

    # 모델 선택
    models = df_main['모델 구분'].dropna().unique()
    selected_model = st.selectbox("모델 선택", models)

    # 항목 선택
    model_df = df_main[df_main['모델 구분'] == selected_model]
    items = model_df['항목'].dropna().unique()
    selected_item = st.selectbox("항목 선택", items)

    # 기준값 불러오기
    row = model_df[model_df['항목'] == selected_item].iloc[0]
    standard_value = row['기준값']

    # 입력값 받기
    input_value = st.number_input(f"{selected_item}의 입력값", step=0.01)

    # 미달율 계산
    try:
        numeric_std = float(str(standard_value).replace('%','').replace('mm',''))
        numeric_in = float(str(input_value).replace('%','').replace('mm',''))
        rate = round(((numeric_in - numeric_std) / numeric_std) * 100, 1)

        if rate <= 10:
            range_str = '≤10%'
        elif rate <= 30:
            range_str = '10~30%'
        else:
            range_str = '>30%'

        # 보강안 및 기술적 이유 불러오기 from 참조 시트
        matched = df_ref[
            (df_ref['모델 구분'] == selected_model) &
            (df_ref['항목'] == selected_item) &
            (df_ref['미달 범위'] == range_str)
        ]

        if not matched.empty:
            st.success(f"📉 미달율: {rate:.1f}% → 보강 범위: {range_str}")
            st.markdown(f"**🔧 추천 보강안:** {matched.iloc[0]['보강안 제안']}")
            st.markdown(f"**🧪 기술적 이유:** {matched.iloc[0]['산정 근거나 기술적 이유']}")
        else:
            st.warning("⚠️ 해당 구간에 맞는 보강안 정보가 없습니다.")

    except:
        st.error("⚠️ 입력값 또는 기준값이 수치가 아니어서 비교가 어렵습니다.")

except Exception as e:
    st.error(f"📂 내부 엑셀 파일 로딩 중 오류: {e}")
