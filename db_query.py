import os

from dotenv import load_dotenv
from langchain.chains.llm import LLMChain
from langchain.prompts import PromptTemplate
from langchain.sql_database import SQLDatabase
from langchain_openai import ChatOpenAI
from sqlalchemy import text


def load_env_variables():
    """
    .env 파일에서 OPENAI_API_KEY와 DB 접속 정보를 각각 로드합니다.
    PORT는 기본값으로 3306을 사용합니다.
    """
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    username = os.getenv("DBUSERNAME")
    password = os.getenv("PASSWORD")
    host = os.getenv("HOST")
    port = os.getenv("PORT")
    database = os.getenv("DATABASE")

    if not api_key:
        raise Exception("OPENAI_API_KEY가 .env 파일에 설정되어 있지 않습니다.")
    if not username or not password or not host or not database:
        raise Exception("DB 접속 정보가 .env 파일에 완전히 설정되어 있지 않습니다.")

    return api_key, username, password, host, port, database


def connect_to_database(db_uri):
    """SQLAlchemy URI 형식으로 데이터베이스에 연결합니다."""
    return SQLDatabase.from_uri(db_uri)


def get_table_info(db):
    """데이터베이스 스키마 정보를 문자열 형태로 가져옵니다."""
    return db.get_table_info()


def generate_sql_query(llm, table_info, question):
    """스키마 정보와 사용자의 질문을 바탕으로 SQL 쿼리를 생성합니다."""
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
    # llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0)
    prompt = PromptTemplate(
        template=sql_prompt_template, input_variables=["table_info", "question"]
    )
    sql_generation_chain = LLMChain(llm=llm, prompt=prompt)
    return sql_generation_chain.run(table_info=table_info, question=question)


def execute_sql_query(db, sql_query):
    """
    SQLAlchemy 엔진을 통해 쿼리 문자열(sql_query)을 실행하고,
    컬럼 정보와 결과 행들을 추출합니다.
    """
    with db._engine.connect() as conn:
        result_proxy = conn.execute(text(sql_query))
        columns = result_proxy.keys()
        query_result = result_proxy.fetchall()
    return columns, query_result


def generate_natural_language_answer(llm, query_result, column_names, question):
    """
    쿼리 결과와 컬럼 정보를 받아 LLM을 통해 자연어 답변을 생성합니다.
    """
    # 결과를 보기 좋은 문자열로 변환
    formatted_result = "\n".join([", ".join(map(str, row)) for row in query_result])

    nl_prompt_template = """
    아래는 SQL 쿼리 실행 결과입니다.

    컬럼: {columns}
    결과:
    {result}

    위 결과를 바탕으로 사용자에게 이해하기 쉬운 자연스러운 문장을 작성해주세요. (2줄 이내로)
    참고로 win_rate는 AI 예측 승률이다.
    결과가 없을 경우 사용자 질문: {question}에 대한 정보를 찾을 수 없다고 말해줘.
    작성된 답변:
    """
    nl_prompt = PromptTemplate(
        template=nl_prompt_template, input_variables=["columns", "result"]
    )
    nl_chain = LLMChain(llm=llm, prompt=nl_prompt)
    answer = nl_chain.run(
        columns=", ".join(column_names), result=formatted_result, question=question
    )
    return answer


def main2(question):
    # 1. 환경 변수(.env)에서 API 키와 DB 접속 정보를 로드합니다.
    api_key, username, password, host, port, database = load_env_variables()

    # 2. DB URI 구성 및 데이터베이스 연결 (charset 옵션 포함)
    db_uri = f"mysql+mysqldb://{username}:{password}@{host}:{port}/{database}?charset=utf8mb4"
    print("db_uri", db_uri)
    db = connect_to_database(db_uri)
    table_info = get_table_info(db)

    # # 3. OpenAI LLM 설정
    # llm = OpenAI(temperature=0, openai_api_key=OPENAI_API_KEY)

    # 3. 최신 ChatOpenAI (예: GPT-4 또는 gpt-3.5-turbo)로 LLM 인스턴스 생성
    llm = ChatOpenAI(
        temperature=0,
        openai_api_key=api_key,
        model_name="gpt-4o-mini",  # 또는 "gpt-3.5-turbo"
    )

    # 4. 사용자의 질문에 대해 SQL 쿼리 생성
    # question = "2024년 9월 28일에 열린 야구 경기 결과를 알려주세요."
    sql_query = generate_sql_query(llm, table_info, question)
    print("생성된 SQL 쿼리:\n", sql_query)

    # 5. SQL 쿼리 실행 및 컬럼/결과 정보 추출
    columns, query_result = execute_sql_query(db, sql_query)
    # print("컬럼 이름:", columns)
    # print("쿼리 결과:", query_result)
    return columns, query_result

    # # 6. 쿼리 결과를 자연어 답변으로 변환
    # final_answer = generate_natural_language_answer(
    #     llm, query_result, columns, question
    # )
    # print("자연어 답변:\n", final_answer)
    # return final_answer


if __name__ == "__main__":
    pass
