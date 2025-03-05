from langchain_community.utilities import SerpAPIWrapper
from langchain_community.document_loaders import AsyncChromiumLoader
from langchain.schema import Document
import trafilatura
from bs4 import BeautifulSoup
import json
from urllib.parse import urlparse
import pandas as pd
import io


# 필터링된 URL 리스트
urls = ["https://www.koreabaseball.com/Record/Player/HitterBasic/Basic1.aspx?sort=HRA_RT"]

# AsyncChromiumLoader를 이용해 HTML 문서를 로드합니다.
loader = AsyncChromiumLoader(urls)
html_docs = loader.load()

# RAG에서 사용할 Document 객체 리스트
documents = []

# 각 Document 객체의 HTML에서 trafilatura를 이용해 본문 추출
for doc in html_docs:
    # BeautifulSoup으로 HTML 파싱
    soup = BeautifulSoup(doc.page_content, "html.parser")

    # 테이블 추출 및 제거 (본문과 분리)
    tables = []
    for table in soup.find_all("table"):
        table_html = str(table)  # HTML을 문자열로 변환
        table_io = io.StringIO(table_html)  # StringIO 객체로 감싸기
        df = pd.read_html(table_io, header=0)[0]  # pandas로 읽기
        table_dict = df.to_dict(orient="records")  # JSON 변환
        tables.append(table_dict)  # 리스트에 추가
        table.extract()  # HTML에서 테이블 제거

    # 테이블이 제거된 HTML로 본문 추출
    cleaned_html = str(soup)

    # 본문 텍스트 추출
    main_content = trafilatura.extract(
        cleaned_html, output_format="json",
        include_comments=False, include_links=False, with_metadata=True
    )

    if main_content:  # None 방지
        json_output = json.loads(main_content)

        # 본문 텍스트 추출
        text = json_output.get("text", "").strip()
        title = json_output.get("title", "제목 없음")
        date = json_output.get("date", "날짜 없음")
        source = json_output.get("source", "URL 없음")

        # Document 객체 생성
        doc_obj = Document(
            page_content=text,  # 테이블 제거된 본문만 저장
            metadata={
                "title": title,
                "date": date,
                "source": source,
                "tables": tables if tables else None  # 테이블 데이터 추가
            }
        )
        documents.append(doc_obj)

