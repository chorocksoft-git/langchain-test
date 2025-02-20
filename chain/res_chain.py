from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser


def create_response_chain():
    """
    1. 주어진 정보에 맞게 스포츠 뉴스 or DB 검색
    2. 해당 정보를 기반으로 적절한 답변
    """
    prompt = PromptTemplate.from_template(
        # 오늘 날짜를 확인하고 해당 정보가 없으면 가상으로 지어내서 답변해줘.
                """
        당신은 스포츠 정보를 제공하는 AI 어시스턴트입니다.
        사용자의 질문에 대해 핵심 정보를 정리하여 **Markdown 형식으로 간결하게 출력**하세요.

        **출력 규칙:**  
        - 제목을 활용하여 가독성을 높이세요.  
        - 리스트(`-`), 굵은 글씨(`**`), 이모지(`⚽`, `📅`, `🏟️`) 등을 활용하세요.  
        - 불필요한 설명은 최소화하고, **핵심 정보만 요약**하세요.  
        - 모든 답변을 일관된 Markdown 스타일로 제공하세요.  

        **REFERENCE:**  
        {reference}

        **QUESTION:**  
        {question}
        """
    )
    llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0)
    answer_parser = StrOutputParser()
    chain = prompt | llm | answer_parser
    return chain
