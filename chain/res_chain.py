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
        주어진 정보에 맞게 답변해줘. 해당 정보가 없으면 모른다고 답변해줘.

        REFERENCE:
        {reference}

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
