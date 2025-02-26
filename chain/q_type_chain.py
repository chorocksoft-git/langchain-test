from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from datetime import datetime
from src.question_type import QuestionData


def create_question_classification_chain():
    '''
    질문을 분석하여 적절한 질문 유형을 분류하고, 관련 데이터를 추출하며, 검색 최적화된 질문을 생성하는 체인입니다.
    '''
    prompt = PromptTemplate.from_template(
        """
        당신은 스포츠 질문을 분석하여 적절한 질문 유형을 분류하고, 관련 정보를 추출하며, 검색에 최적화된 형태로 질문을 변환하는 전문가입니다.

        - 질문 유형을 식별하세요. (예: 경기 일정, 선수 기록, 경기 결과 등)
        - 질문에서 주요 정보를 추출하세요. (팀명, 선수명, 날짜, 시즌 등)
        - 상대적인 날짜 표현(어제, 오늘, 내일, 작년, 올해 등)을 현재 날짜({current_date}) 기준으로 변환하세요.
        - 검색 최적화된 질문을 생성하세요. (예: "손흥민 2025년 득점 기록", "KBO 2025년 개막 일정")
        - **LLM이 보다 상세한 답변을 제공할 수 있도록, 검색 최적화된 질문과 함께 문장형 질문을 생성하세요.**
            - 유저 질문이 모호한 경우, 보다 명확한 형태로 변환하세요.
            - 추가적인 맥락이 필요하면 보완하여 질문을 구성하세요.
        
        QUESTION:
        {question}

        출력 형식:
        {format}
        """
    )

    llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0)

    # 현재 날짜를 LLM에 전달하여 상대적 날짜 변환을 유도
    current_date = datetime.today().strftime("%Y-%m-%d")
    prompt = prompt.partial(format=PydanticOutputParser(pydantic_object=QuestionData).get_format_instructions(),
                            current_date=current_date)

    chain = prompt | llm | PydanticOutputParser(pydantic_object=QuestionData)

    return chain
