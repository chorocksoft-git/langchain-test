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

load_dotenv()

project_name = "SAI"
os.environ["LANGCHAIN_TRACING_V2"] = "true"  # true: 활성화
os.environ["LANGCHAIN_PROJECT"] = project_name  # 프로젝트명

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


# 체인 생성
def create_question_classification_chain(prompt_type):
    prompt = PromptTemplate.from_template(
        """
        You are a helpful assistant. Please answer the following questions in KOREAN.

        QUESTION:
        {question}

        FORMAT:
        {format}
        """
    )

    # format 에 PydanticOutputParser의 부분 포맷팅(partial) 추가

    llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0)

    question_parser = PydanticOutputParser(pydantic_object=QuestionData)
    prompt = prompt.partial(format=question_parser.get_format_instructions())

    chain = prompt | llm | question_parser

    return chain


def create_response_chain():
    """
    1. 주어진 정보에 맞게 스포츠 뉴스 or DB 검색
    2. 해당 정보를 기반으로 적절한 답변
    """
    prompt = PromptTemplate.from_template(
        """
        오늘 날짜를 확인하고 해당 정보가 없으면 가상으로 지어내서 답변해줘.

        QUESTION:
        {question}
        """
        # FORMAT:
        # {format}
    )
    llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0)
    answer_parser = StrOutputParser()
    chain = prompt | llm | answer_parser
    return chain


user_input = st.chat_input("궁금한 내용을 물어보세요!")


if user_input:
    # 웹에 대화를 출력
    st.chat_message("user").write(user_input)
    # chain 생성
    question_classification_chain = create_question_classification_chain(
        selected_prompt
    )

    question_information = question_classification_chain.invoke(
        {"question": user_input}
    )

    response_chain = create_response_chain()
    response = response_chain.stream({"question": question_information})
    with st.chat_message("assistant"):
        container = st.empty()
        ai_answer = ""
        for _, v in enumerate(question_information.dict()):
            if question_information.dict()[v] != None:
                ai_answer += str(v) + " : "
                ai_answer += str(question_information.dict()[v])
            ai_answer += "\n"
        # print(ai_answer, type(ai_answer))
        for token in response:
            ai_answer += token
            container.markdown(ai_answer)

    # 대화기록을 저장
    add_message("user", user_input)
    add_message("assistant", ai_answer)
