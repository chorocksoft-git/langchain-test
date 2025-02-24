import os
import tempfile

import streamlit as st
from dotenv import load_dotenv
from langchain_core.messages.chat import ChatMessage

from log import langsmith
from src.module.A01_1_country_chain import extract_chain, answer_chain
from src.util import resize_and_pad_custom

load_dotenv()

project_name = "POC"
langsmith(project_name)
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = project_name

st.title("이미지인식 테스트")

# 세션 상태 초기화
if "messages" not in st.session_state:
    st.session_state["messages"] = []
if "assistant_content" not in st.session_state:
    st.session_state["assistant_content"] = None
if "last_uploaded_name" not in st.session_state:
    st.session_state["last_uploaded_name"] = None


def print_messages():
    for chat_message in st.session_state["messages"]:
        # assistant_content 역할은 채팅창에 출력하지 않음
        if chat_message.role == "assistant_content":
            continue
        st.chat_message(chat_message.role).write(chat_message.content)


def add_message(role, message):
    st.session_state["messages"].append(ChatMessage(role=role, content=message))


print_messages()

# 파일 업로더 추가
uploaded_file = st.file_uploader(
    "이미지를 업로드해주세요",
    type=["png", "jpg", "jpeg"],
    help="PNG, JPG 형식의 이미지 파일을 업로드할 수 있습니다.",
)

# 새로운 파일이 업로드된 경우, 혹은 이전에 분석 결과가 없으면 이미지 분석 수행
if uploaded_file:
    # 새 업로드된 파일 이름과 이전 파일 이름이 다르면 새 이미지로 판단
    if st.session_state["last_uploaded_name"] != uploaded_file.name:
        st.session_state["assistant_content"] = None
        st.session_state["last_uploaded_name"] = uploaded_file.name

    if st.session_state["assistant_content"] is None:
        # 업로드된 파일 객체를 임시 파일로 저장 (MultiModal은 파일 경로를 기대함)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            tmp_file_path = tmp_file.name

        # 전처리된 이미지를 저장할 임시 파일 경로 생성
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as out_file:
            processed_file_path = out_file.name

        # 이미지 리사이즈 및 패딩 적용
        resize_and_pad_custom(
            tmp_file_path, processed_file_path, target_width=1024, target_height=1024
        )

        # 결과 이미지 출력 (옵션)
        st.image(tmp_file_path, caption="업로드된 이미지")

        chain = extract_chain()
        response = chain.stream(processed_file_path)
        assistant_container = st.empty()

        assistant_response = ""
        for token in response:
            assistant_response += token.content  # token.text 인 경우도 있음
            assistant_container.chat_message("assistant").write(assistant_response)

        # 분석 결과 저장 (채팅용과 내부용 두 역할로 저장)
        add_message("assistant", assistant_response)
        # add_message("assistant_content", assistant_response)
        st.session_state["assistant_content"] = assistant_response

# assistant_content가 세션 상태에 저장되어 있다면 이를 변수로 사용
assistant_content = st.session_state["assistant_content"]


user_input = st.chat_input("궁금한것 입력")
if user_input:
    st.chat_message("user").write(user_input)
    add_message("user", user_input)

    chain = answer_chain()
    response = chain.stream(
        {"assistant_content": assistant_content, "question": user_input}
    )

    container = st.empty()
    ai_answer = ""

    for token in response:
        ai_answer += token
        container.chat_message("assistant").write(ai_answer)

    # 대화 기록에 답변 추가
    add_message("assistant", ai_answer)
