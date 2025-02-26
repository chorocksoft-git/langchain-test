from langchain_community.utilities import SerpAPIWrapper
from langchain_community.document_loaders import AsyncChromiumLoader
from langchain.schema import Document
import trafilatura
from bs4 import BeautifulSoup
import json


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

    # 특정 도메인을 제외하고 링크 추출
    exclude_domains = ["namu.wiki"]
    urls = []
    for result in organic_results:
        link = result.get("link")
        if link and not any(domain in link for domain in exclude_domains):
            urls.append(link)

    if not urls:
        return []  # 검색 결과가 없으면 빈 리스트 반환

    # AsyncChromiumLoader를 이용해 HTML 문서를 비동기적으로 로드
    loader = AsyncChromiumLoader(urls)
    html_docs = await loader.aload()  # 비동기 로드

    # RAG에서 사용할 Document 객체 리스트
    documents = []

    # 본문 크롤링 및 정제
    for doc in html_docs:
        try:
            # BeautifulSoup으로 푸터, 스크립트 등 불필요한 요소 제거
            soup = BeautifulSoup(doc.page_content, "html.parser")
            for tag in soup.select("footer, nav, aside, script, style"):
                tag.extract()

            cleaned_html = str(soup)

            # 본문 추출 (trafilatura 사용)
            main_content = trafilatura.extract(
                cleaned_html,
                output_format="json",
                include_comments=False,
                include_links=False,
                with_metadata=True,
            )

            if main_content:
                json_output = json.loads(main_content)

                # 본문 텍스트 추출 (없으면 빈 문자열)
                text = json_output.get("text", "").strip()
                title = json_output.get("title", "제목 없음")
                date = json_output.get("date", "날짜 없음")
                url = json_output.get("source", "URL 없음")

                if text:  # 본문이 있을 경우만 Document 생성
                    doc_obj = Document(
                        page_content=text,
                        metadata={"title": title, "date": date, "source": url},
                    )
                    documents.append(doc_obj)

        except Exception as e:
            print(f"crawling error : {e}")  # 크롤링 중 오류 발생 시 출력

    return documents
