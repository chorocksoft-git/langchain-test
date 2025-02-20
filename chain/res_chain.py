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


def predict_response_chain():
    """
    현재는 예측 결과를 지어서 답변
    향후 예측 모델 연동
    """
    prompt = PromptTemplate.from_template(
        #
        """
        당신은 스포츠 경기결과를 예측하는 AI 어시스턴트입니다.
        오늘 날짜를 확인하고 해당 정보가 없으면 가상으로 지어내서 답변하세요.
        모든 답변을 일관된 Markdown 스타일로 제공하세요.  

        **QUESTION:**  
        {question}
        """
    )
    llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0)
    answer_parser = StrOutputParser()
    chain = prompt | llm | answer_parser
    return chain


def generate_natural_language_answer():
    """
    쿼리 결과와 컬럼 정보를 받아 LLM을 통해 자연어 답변을 생성합니다.
    """
    # 결과를 보기 좋은 문자열로 변환
    prompt = PromptTemplate.from_template(
        """
        아래는 SQL 쿼리 실행 결과입니다.

        컬럼: {columns}
        결과:
        {result}

        위 결과를 바탕으로 사용자에게 이해하기 쉬운 자연스러운 문장을 작성해주세요. (2줄 이내로)
        참고로 win_rate는 AI 예측 승률이다.
        결과가 없을 경우 사용자 질문: {question}에 대한 정보를 찾을 수 없다고 말해줘.
        작성된 답변:
        """
    )
    llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0)

    # nl_prompt = PromptTemplate(template=nl_prompt_template, input_variables=["columns", "result"])
    # nl_chain = LLMChain(llm=llm, prompt=nl_prompt)
    answer_parser = StrOutputParser()
    chain = prompt | llm | answer_parser
    return chain
