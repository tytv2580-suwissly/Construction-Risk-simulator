import streamlit as st
import pandas as pd

# 🔐 비밀번호 인증
st.sidebar.title("🔐 로그인")
password = st.sidebar.text_input("비밀번호를 입력하세요", type="password")

# 설정한 비밀번호 (원하는 값으로 변경 가능)
PASSWORD = "crs911**"

if password != PASSWORD:
    st.warning("올바른 비밀번호를 입력해야 시뮬레이터를 사용할 수 있습니다.")
    st.stop()

# ✅ 본문 시작
st.set_page_config(page_title="구조 성능 시뮬레이터", layout="wide")

st.title("🏗️ 구조 성능 시뮬레이터 (3개 모델 지원)")
st.markdown("모델과 항목을 선택하고 응답값을 입력하면, 기준 초과 여부에 따른 보강안을 제안합니다.")

# 자동 로딩 엑셀 파일 경로
DEFAULT_EXCEL_PATH = "시뮬레이터 (3 모델 모델별_기준값_산정근거_상세설명 포함) - 복사본.xlsx"

try:
    df_main = pd.read_excel(DEFAULT_EXCEL_PATH, sheet_name="시뮬레이터")
    df_ref = pd.read_excel(DEFAULT_EXCEL_PATH, sheet_name="보강안 및 근거")
except Exception as e:
    st.error(f"엑셀 파일을 불러오는 데 실패했습니다: {e}")
    st.stop()

# 모델 선택
models = df_main['모델 구분'].dropna().unique()
selected_model = st.selectbox("모델 선택", models)

# 항목 선택
model_df = df_main[df_main['모델 구분'] == selected_model]
items = model_df['항목'].dropna().unique()
selected_item = st.selectbox("항목 선택", items)

# 기준값 추출
row = model_df[model_df['항목'] == selected_item].iloc[0]
standard_value = row['기준값']

# 입력값 받기
input_value = st.number_input(f"{selected_item}의 입력값을 입력하세요", step=0.01)

# 미달율 계산 및 보강안 검색
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

    result_row = df_ref[
        (df_ref['모델 구분'] == selected_model) &
        (df_ref['항목'] == selected_item) &
        (df_ref['미달 범위'] == range_str)
    ]

    if not result_row.empty:
        r = result_row.iloc[0]
        st.success(f"📉 미달율: {rate:.1f}% → 보강 범위: {range_str}")
        st.markdown(f"**🔧 추천 보강안:** {r['보강안 제안']}")
        st.markdown(f"**🧪 기술적 이유:** {r['산정 근거나 기술적 이유']}")
        if '출처' in r:
            st.markdown(f"**📚 출처:** {r['출처']}")
    else:
        st.warning("해당 구간에 맞는 보강안 정보가 없습니다.")

except:
    st.error("기준값이나 입력값이 수치로 변환되지 않아 비교가 어렵습니다.")
