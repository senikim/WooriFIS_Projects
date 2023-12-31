import streamlit as st
import pandas as pd
import datetime
from io import BytesIO
import pandas as pd
import plotly.io as pio
import plotly.express as px
import plotly.graph_objects as go
from elastic_api import search_index, get_total_price, search_index2, remove_content
from streamlit_js_eval import streamlit_js_eval

st.header("월 별 가계부")
def format_currency(value):
    return f"{int(value):,}원"

def set_summary(month, total_profit, total_loss):
    st.text(f"{month}월 총 수입: {format_currency(total_profit)}")
    st.text(f"{month}월 총 지출: {format_currency(total_loss)}")
    if total_profit > abs(total_loss):
        st.text("=> 수입이 지출보다 많네요. 잘 하고 계세요!")
    else:
        st.text("=> 지출을 좀 줄이셔야 할 것 같습니다..")

month = st.selectbox("월을 선택해 주세요", list(range(1, 13)))
print(month)
result = search_index(month)
if result:
    st.subheader(f"{month}월 소비 요약")
    # st.write(result.to_dict()["hits"]["hits"])
    print(result["hits"])
    source_data = [entry["_source"] for entry in result.to_dict()["hits"]["hits"]]
    df = pd.DataFrame(source_data)

    # 월별 수입, 지출 요약
    total_profit, total_loss = get_total_price(month)
    set_summary(month, total_profit, total_loss)

    # 월별 지출 추이 시각화
    # (1) 일별 지출 금액 선 그래프
    date_sum=df.groupby('날짜')[['금액']].sum()
    fig1 = px.line(date_sum)

    # (2) 한달 간 지출 대분류의 비중을 나타낸 파이차트
    payment=df[df.타입=='지출']
    payment.금액=abs(payment.금액)
    payment_sum=payment.groupby('대분류')[['금액']].sum()
    payment_sum.reset_index(inplace=True)
    fig2=px.pie(payment_sum, values='금액', names='대분류')
    # st.dataframe(payment_sum)

    # 양 쪽에 그래프 병렬시키기
    col1, col2, = st.columns(2)
    with col1:
        st.subheader('일별 수입/지출')
        st.plotly_chart(fig1, use_container_width=True)
    with col2:
        st.subheader('대분류별 소비 비중')
        st.plotly_chart(fig2, use_container_width=True)
    st.subheader(f"전체 거래 내역")
    st.data_editor(df, num_rows="dynamic") 

    #######
else:
    st.text(f"{month}월에는 입력된 데이터가 없어요")
    # [Error 2. 값이 없는 달 분기처리 => 해결 : result 보일 때, 안보일 때 경우를 나눠서 진행]
    # [ex. 4월 데이터는 없어서 result 값이 없기 때문에 error가 발생 -> result False인 경우에는 "입력된 데이터 없다"는 메세지 출력]

# 삽입/삭제/새로고침
with st.sidebar:
    # 가계부 표에 있는 변수 순서대로 데이터를 입력하고 '삽입' 버튼을 누르면
    # 가계부 표 밑에 새로운 소비 데이터가 추가됨
    transection_date = st.date_input("거래가 발생한 날짜를 입력해 주세요")
    transection_type = st.selectbox("타입을 선택해 주세요", ["지출", "수입", "이체"])
    transection_category = st.selectbox("지출 분류를 선택하세요", ["온라인쇼핑", "이체", "생활", "금융", "카페/간식", "식비", "금융수입", "교통", "카드대금", "기타수입", "Other"])
    transection_small_category = st.text_input("지출 분류의 세부 내용이 있다면 적어주세요")
    transection_content = st.text_input("지출 내용을 입력하세요")
    transection_method = st.text_input("결제 수단을 입력하세요")
    transection_bill = st.number_input("금액을 입력하세요")

    st.title("가계부에 새로운 내역 추가하기")
    insert_transection = st.button("가계부에 추가하기")

    st.title("가계부에서 원하는 내역 삭제하기")
    del_index = st.text_input("삭제하려는 거래 내역의 index값을 입력하세요")
    delete_transection = st.button("가계부 내용 삭제하기")
    if(delete_transection):
        remove_content(del_index)
        # st.experimental_rerun()
        # 새로고침
        streamlit_js_eval(js_expressions="parent.window.location.reload()")

# 새로운 데이터 원본 데이터에 삽입
if insert_transection == True:
    insert_result = search_index2(transection_category, transection_content, transection_date, transection_method, transection_bill, transection_small_category, transection_type)
    # 새로고침
    streamlit_js_eval(js_expressions="parent.window.location.reload()")


    

    


# import streamlit as st
# import pandas as pd
# import datetime
# from io import BytesIO
# import pandas as pd
# from elastic_api import search_index
# from elastic_api import search_index2
# # from elastic_api import search_index3

# month = st.selectbox("월을 선택해 주세요", list(range(1, 13)))
# print(month)
# result = search_index(month)
# st.write(result.to_dict()["hits"]["hits"])
# source_data = [entry["_source"] for entry in result.to_dict()["hits"]["hits"]]
# df = pd.DataFrame(source_data)
# st.dataframe(df)

# # # sidebar 만들기
# with st.sidebar:
#     # 가계부 표에 있는 변수 순서대로 데이터를 입력하고 '삽입' 버튼을 누르면
#     # 가계부 표 밑에 새로운 소비 데이터가 추가됨
#     transection_date = st.date_input("거래가 발생한 날짜를 입력해 주세요")
#     transection_type = st.selectbox("타입을 선택해 주세요", ["지출", "수입", "이체"])
#     transection_category = st.selectbox("지출 분류를 선택하세요", ["온라인쇼핑", "이체", "생활", "금융", "카페/간식", "식비", "금융수입", "교통", "카드대금", "기타수입", "Other"])
#     transection_small_category = st.text_input("지출 분류의 세부 내용이 있다면 적어주세요")
#     transection_content = st.text_input("지출 내용을 입력하세요")
#     transection_method = st.text_input("결제 수단을 입력하세요")
#     transection_bill = st.number_input("금액을 입력하세요")

#     st.title("가계부에서 새로운 내역 추가하기")
#     insert_transection = st.button("가계부에 추가하기")
#     search_transection = st.button("새로고침")

#     st.title("가계부에서 원하는 내역 삭제하기")
#     del_index = st.text_input("삭제하려는 거래 내역의 index값을 입력하세요")
#     delete_transection = st.button("가계부 내용 삭제하기")

# if insert_transection == True:
#     # df2에 추가하기
#     insert_result = search_index2(transection_category, transection_content, transection_date, transection_method, transection_bill, transection_small_category, transection_type)

########################################################  
# if search_transection == True:
#     # 조회
#     result3 = search_index3()
#     # result2 = search_index2()
#     st.write(result3.to_dict()["hits"]["hits"])
#     source_data2 = [entry["_source"] for entry in result3.to_dict()["hits"]["hits"]]  
#     df2 = pd.DataFrame(source_data2)
#     st.dataframe(df2) 

# month_account = df.loc[:,["날짜", "타입", "대분류", "소분류", "내용", "결제수단", "금액"]]
# st.dataframe(month_account)
    
# if delete_transection == True:
#     resp = es.delete(index="test-index", id=1) # elasticsearch - GET test-index/_doc/1
#     print(resp['result'])