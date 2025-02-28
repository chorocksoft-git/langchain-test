import os
from dotenv import load_dotenv
from langchain.sql_database import SQLDatabase
from sqlalchemy import text


class DatabaseManager:
    """데이터베이스 연결 및 쿼리 실행을 담당하는 클래스"""

    def __init__(self):
        self.username = os.getenv("DBUSERNAME")
        self.password = os.getenv("PASSWORD")
        self.host = os.getenv("HOST")
        self.port = os.getenv("PORT")
        self.database = os.getenv("DATABASE")

        if not self.username or not self.password or not self.host or not self.database:
            raise Exception("DB 접속 정보가 .env 파일에 완전히 설정되어 있지 않습니다.")

        self.db_uri = f"mysql+mysqldb://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}?charset=utf8mb4"
        self.db = SQLDatabase.from_uri(self.db_uri)

    def get_table_info(self):
        """데이터베이스 스키마 정보를 가져옴"""
        return self.db.get_table_info()

    def execute_sql_query(self, sql_query):
        """SQL 쿼리를 실행하고 결과를 반환"""
        with self.db.engine.connect() as conn:
            result_proxy = conn.execute(text(sql_query))
            columns = result_proxy.keys()
            query_result = result_proxy.fetchall()
        return columns, query_result
