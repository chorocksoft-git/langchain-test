from langchain_community.utilities import SerpAPIWrapper
from langchain_community.document_loaders import AsyncChromiumLoader
from langchain.schema import Document
import trafilatura
from bs4 import BeautifulSoup
import json
from urllib.parse import urlparse
import pandas as pd
import io

"""
HTML table 정보를 잘 못뽑아 와서 만든 코드 
해당 코드가 있을시 정확도는 올라가지만 토큰 사용량이 너무 많이 올라감 타협점을 찾아야할듯
"""


async def google_web_browsing(search_query):
    """ SerpAPI를 이용해 웹 검색을 수행하고, 검색된 URL에서 본문을 크롤링하는 함수 """

    # 검색 파라미터 지정
    search = SerpAPIWrapper(params={
        "engine": "google",
        "q": search_query,
        "gl": "KR",
        "hl": "ko",
        "num": 10,
    })

    # 검색 실행
    search_results = search.results(query=search_query)
    organic_results = search_results.get("organic_results", [])

    # 제외할 도메인 목록
    exclude_domains = {"namu.wiki", "x.com"}  # set을 사용하여 빠른 검색 가능

    # 필터링된 URL 리스트
    urls = []

    for result in organic_results:
        link = result.get("link")
        if link:
            parsed_url = urlparse(link)
            domain = parsed_url.netloc  # 도메인만 추출 (예: 'x.com', 'namu.wiki')

            if domain not in exclude_domains:
                urls.append(link)

    if not urls:
        return []  # 검색 결과가 없으면 빈 리스트 반환

    # AsyncChromiumLoader를 이용해 HTML 문서를 로드합니다.
    loader = AsyncChromiumLoader(urls)
    html_docs = await loader.aload()

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
            title = json_output.get("title", "Unknown")
            date = json_output.get("date", "Unknown")
            source = json_output.get("source", "Unknown")

            # Document 객체 생성
            doc_obj = Document(
                page_content=text,  # 테이블 제거된 본문만 저장
                metadata={
                    "title": title,
                    "date": date,
                    "source": source,
                    "table": tables if tables else "Unknown"  # 테이블 데이터 추가
                }
            )
            documents.append(doc_obj)

    return documents
