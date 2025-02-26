import os
import streamlit as st
from langchain_core.messages.chat import ChatMessage
from dotenv import load_dotenv
import sys
import asyncio

from chain.q_type_chain import create_question_classification_chain
from chain.res_chain import (
    create_response_chain,
)
from log import langsmith
from src.web_browsing import google_web_browsing

# res_chian.py에 HuggingFaceEmbeddings 추가하니까 에러나서 넣은 코드
# 에러 난 이후로 streamlit이 살짝 맛탱이가 가서 출력을 이상하게 함
# import torch
# torch.classes.__path__ = [os.path.join(torch.__path__[0], torch.classes.__file__)]

# python -m streamlit run main.py

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
username = os.getenv("DBUSERNAME")
password = os.getenv("PASSWORD")
host = os.getenv("HOST")
port = os.getenv("PORT")
database = os.getenv("DATABASE")

project_name = "SAI"

langsmith(project_name=project_name)

os.environ["LANGCHAIN_TRACING_V2"] = "true"  # true: 활성화
os.environ["LANGCHAIN_PROJECT"] = project_name  # 프로젝트명

if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

st.title("SAI RAG test")

if "messages" not in st.session_state:
    # 대화 기록을 저장하기위한 용도
    st.session_state["messages"] = []

with st.sidebar:
    clear_btn = st.button("대화초기화")


# 이전 대화를 출력
def print_messages():
    for chat_message in st.session_state["messages"]:
        st.chat_message(chat_message.role).write(chat_message.content)


# 새로운 메시지를 추가
def add_message(role, message):
    st.session_state["messages"].append(ChatMessage(role=role, content=message))


# 초기화 버튼이 눌리면...
if clear_btn:
    st.session_state["messages"] = []

# 이전 대화 기록 출력
print_messages()

user_input = st.chat_input("궁금한 내용을 물어보세요!")

if user_input:
    # 웹에 대화를 출력
    st.chat_message("user").write(user_input)

    # 질문의 유형 분류, 정보 추출, 검색 쿼리 변환
    question_classification_chain = create_question_classification_chain()
    question_information = question_classification_chain.invoke({"question": user_input})
    print(f"question_information : {question_information}")

    # 웹 브라우징 (Documents 반환)
    print(f"question_information.search_query : {question_information.search_query}")
    reference = asyncio.run(google_web_browsing(question_information.search_query))

    # 변경된 체인 생성 (documents를 인자로 전달)
    response_chain = create_response_chain(reference)

    # 질문만 전달하면 retriever가 내부적으로 관련 reference를 채워줌
    response = response_chain.stream({"query": question_information.llm_query})

    with st.chat_message("assistant"):
        container = st.empty()
        ai_answer = ""
        for token in response:
            if isinstance(token, dict):
                token_text = token.get("result", "")
            else:
                token_text = token
            ai_answer += token_text
            container.markdown(ai_answer, unsafe_allow_html=True)

    # 대화기록을 저장
    add_message("user", user_input)
    add_message("assistant", ai_answer)
