from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser


def create_special_search_chain():
    """
    검색에 적합한 형태로 유저 인풋을 변환
    """
    prompt = PromptTemplate.from_template(
        """
        당신은 웹 브라우징에서 검색에 적합한 형태로 질문을 정리하는 AI 어시스턴트입니다.  
        사용자가 입력한 질문에서 불필요한 부분을 제거하고, 핵심적인 키워드만 남긴 형태로 변환하세요.

        **출력 형식:**
        - 질문에서 요청하는 핵심 정보만 남기고 나머지는 제거
        - 문장은 짧고 간결하게 변환
        - 존댓말을 사용하지 않고, 핵심 정보만 나열

        **예시:**
        - 입력: "2025 KBO 개막 일정 좀 알려줘"
        - 출력: "2025년 KBO 개막 일정"

        - 입력: "레알 마드리드가 맨시티를 이긴 경기에서 음바페 해트트릭 했어?"
        - 출력: "레알 마드리드 맨시티 음바페 해트트릭"

        **질문:**
        {question}
        """
    )

    llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0)

    output_parser = StrOutputParser()
    chain = prompt | llm | output_parser

    return chain
