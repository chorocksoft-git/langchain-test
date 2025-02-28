from langchain.schema import Document
from langchain_core.prompts import PromptTemplate

def generate_sql_query(llm, table_info, question):
    """스키마 정보와 사용자의 질문을 바탕으로 SQL 쿼리를 생성하고 Document 객체로 반환"""
    sql_prompt_template = """
    당신은 SQL 전문가입니다. 아래 데이터베이스 스키마 정보를 참고하여 사용자의 질문에 맞는 SQL 쿼리를 작성하세요. 
    무조건 baseball_game_info 테이블에서만 조회해줘.
    날짜 관련된 컬럼은 LIKE 조회해줘. 
    질문에 날짜가 없으면 '2024-09-28' 날짜로 해줘. 오늘은 '2024-09-28' 이다.
    최근 경기 결과를 묻는 질문은 오늘('2024-09-28 23:59:59') 이하에 열린 경기 중 regist_time 순으로 정렬해서 가장 마지막 결과를 알려줘.

    스키마 정보:
    {table_info}

    질문:
    {question}

    SQL 쿼리 (마크다운형식 없이 주석 없이 오직 순수 쿼리만 출력):
    """
    prompt = PromptTemplate(
        template=sql_prompt_template, input_variables=["table_info", "question"]
    )
    sql_generation_chain = LLMChain(llm=llm, prompt=prompt)

    # SQL 쿼리 생성
    sql_query = sql_generation_chain.run(table_info=table_info, question=question)

    # Document 객체로 변환
    sql_document = Document(
        page_content=sql_query,  # SQL 쿼리를 문서 내용으로 저장
        metadata={
            "source": "SQL_Generation",
            "table_info": table_info[:500],  # 메타데이터 크기를 제한 (너무 길면 문제 발생 가능)
            "question": question,
        }
    )

    return sql_document
