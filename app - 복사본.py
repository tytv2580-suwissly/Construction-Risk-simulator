import streamlit as st
import pandas as pd

st.set_page_config(page_title="구조 성능 시뮬레이터", layout="wide")
st.title("🏗️ 구조 성능 시뮬레이터 (3개 모델 지원)")
st.markdown("업로드한 엑셀 파일에서 모델과 항목을 선택하고, 응답값을 입력하면 자동으로 보강안을 제시합니다.")

uploaded_file = st.file_uploader("📂 엑셀 파일 업로드", type=["xlsx"])

if uploaded_file:
    try:
        # 두 개 시트 불러오기
        df_main = pd.read_excel(uploaded_file, sheet_name="시물레이터")
        df_ref = pd.read_excel(uploaded_file, sheet_name="보강안 및 근거")

        # 모델 목록
        models = df_main['모델 구분'].dropna().unique()
        selected_model = st.selectbox("모델 선택", models)

        # 항목 목록
        model_df = df_main[df_main['모델 구분'] == selected_model]
        items = model_df['항목'].dropna().unique()
        selected_item = st.selectbox("항목 선택", items)

        # 기준값
        try:
            row = model_df[model_df['항목'] == selected_item].iloc[0]
            standard_value = row['기준값']
            input_value = st.number_input(f"{selected_item}의 입력값", step=0.01)

            # 미달율 계산
            numeric_std = float(str(standard_value).replace('%','').replace('mm',''))
            numeric_in = float(str(input_value).replace('%','').replace('mm',''))
            rate = round(((numeric_in - numeric_std) / numeric_std) * 100, 1)

            if rate <= 10:
                range_str = '≤10%'
            elif rate <= 30:
                range_str = '10~30%'
            else:
                range_str = '>30%'

            # 보강안 시트에서 검색
            match_row = df_ref[
                (df_ref['모델 구분'] == selected_model) &
                (df_ref['항목'] == selected_item) &
                (df_ref['미달 범위'] == range_str)
            ]

            if not match_row.empty:
                st.success(f"📉 미달율: {rate:.1f}% → 보강 범위: {range_str}")
                st.markdown(f"**🔧 추천 보강안:** {match_row.iloc[0]['보강안 제안']}")
                st.markdown(f"**🧪 기술적 이유:** {match_row.iloc[0]['산정 근거나 기술적 이유']}")
                if '출처' in match_row.columns:
                    st.markdown(f"**📚 출처:** {match_row.iloc[0]['출처']}")
            else:
                st.warning("⚠️ 해당 구간에 맞는 보강안 정보가 없습니다.")

        except Exception as e:
            st.error(f"❌ 기준값 또는 입력값 처리 오류: {e}")

    except Exception as e:
        st.error(f"❌ 엑셀 파일 처리 중 오류 발생: {e}")