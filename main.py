import os
import streamlit as st
from langchain_core.messages.chat import ChatMessage
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import load_prompt
from langchain.prompts import PromptTemplate

from dotenv import load_dotenv
from log import langsmith

# from src.util import load_prompt

load_dotenv()

project_name = "LS전선 POC"

langsmith(project_name)
os.environ["LANGCHAIN_TRACING_V2"] = "true"  # true: 활성화
os.environ["LANGCHAIN_PROJECT"] = project_name  # 프로젝트명


st.title("이미지인식 테스트")

# 파일 업로더 추가
uploaded_file = st.file_uploader(
    "이미지를 업로드해주세요",
    type=["png", "jpg", "jpeg"],
    help="PNG, JPG 형식의 이미지 파일을 업로드할 수 있습니다.",
)

# 업로드된 이미지 표시
if uploaded_file is not None:
    st.image(uploaded_file, caption="업로드된 이미지")

if "messages" not in st.session_state:
    # 대화 기록을 저장하기위한 용도
    st.session_state["messages"] = []


def print_messages():
    for chat_message in st.session_state["messages"]:
        st.chat_message(chat_message.role).write(chat_message.content)


# 새로운 메시지를 추가
def add_message(role, message):
    st.session_state["messages"].append(ChatMessage(role=role, content=message))


print(st.session_state["messages"])

print_messages()


user_input = st.chat_input("궁금한것 입력")

if user_input:
    st.chat_message("user").write(user_input)

    llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0)
    # prompt = load_prompt("src/prompts/extract_info_from_image.yaml", encoding="utf8")
    # formatted_prompt = prompt.format(country=user_input)
    # prompt_template = PromptTemplate.from_template(
    #     template=prompt.template, input_variables=prompt.input_variables
    # )
    # formatted_prompt = prompt_template.format(country=user_input)  # PromptTemplate 사용

    response_chain = llm | prompt
    response = response_chain.stream(user_input)
    # response = chain.stream(input=user_input)
    # add_message("assistant", ai_answer)
    # 적절한 답변을 생성하는 chain
    with st.chat_message("assistant"):
        container = st.empty()
        # ai_answer = response.content
        ai_answer = ""
        for token in response:
            print(token, type(token))
            ai_answer += str(token)
            container.markdown(ai_answer, unsafe_allow_html=True)
        # container.markdown(ai_answer, unsafe_allow_html=True)

    # 대화기록을 저장
    add_message("user", user_input)
    add_message("assistant", ai_answer)
