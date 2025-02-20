import os
import streamlit as st
from langchain_core.messages.chat import ChatMessage
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_community.utilities import SerpAPIWrapper
from langchain.output_parsers import EnumOutputParser, PydanticOutputParser
from question_type import QuestionData
from dotenv import load_dotenv
import sys
import asyncio

from chain.search_chain import create_special_search_chain
from chain.q_type_chain import create_question_classification_chain
from chain.res_chain import create_response_chain
from log import langsmith
from src.web_browsing import google_web_browsing

load_dotenv()

project_name = "SAI"

langsmith(project_name=project_name)

os.environ["LANGCHAIN_TRACING_V2"] = "true"  # true: 활성화
os.environ["LANGCHAIN_PROJECT"] = project_name  # 프로젝트명

if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

st.title(project_name)

if "messages" not in st.session_state:
    # 대화 기록을 저장하기위한 용도
    st.session_state["messages"] = []

with st.sidebar:
    clear_btn = st.button("대화초기화")
    selected_prompt = st.selectbox(
        "스포츠 종목을 선택해주세요", ("야구", "축구", "농구"), index=0
    )


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

    # 질문의 유형과 질문속 정보를 추출하는 chain
    question_classification_chain = create_question_classification_chain(
        selected_prompt
    )
    question_information = question_classification_chain.invoke(
        {"question": user_input}
    )

    # q_data = QuestionData(**question_information)
    # print(question_information.to_search_query())
    # print("=" * 50)
    # 질문에 관한 정보를 검색
    search_documents = google_web_browsing(user_input)

    for i in search_documents:
        print(i.page_content)

    # 질문과의 연관성

    # 적절한 답변을 생성하는 chain
    response_chain = create_response_chain()
    response = response_chain.stream(
        {"reference": search_documents, "question": question_information}
    )
    with st.chat_message("assistant"):
        container = st.empty()
        ai_answer = ""
        # for _, v in enumerate(question_information.dict()):
        #     if question_information.dict()[v] is not None:
        #         ai_answer += str(v) + " : "
        #         ai_answer += str(question_information.dict()[v])
        #     ai_answer += "\n"
        # print(ai_answer, type(ai_answer))
        for token in response:
            ai_answer += token
            formatted_answer = f"```markdown\n{ai_answer}\n```"
            # Markdown 강제 렌더링
            container.markdown(formatted_answer, unsafe_allow_html=True)

        # ai_answer += "\n"
        # for i in search_documents:
        #     ai_answer += "\n"
        #     ai_answer += i.metadata['url']

    # 대화기록을 저장
    add_message("user", user_input)
    add_message("assistant", ai_answer)