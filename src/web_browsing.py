import os
from serpapi import GoogleSearch
from langchain_community.document_loaders import AsyncChromiumLoader
from langchain.schema import Document
import trafilatura
from bs4 import BeautifulSoup
import json
from dotenv import load_dotenv
from chain.search_chain import create_special_search_chain


"""
- 현재 뉴스 기사 정도만 깔끔하게 추출가능
- html table 형태는 가져오긴 하지만 구분하기 힘듦
- js로 데이터를 불러오는 페이지에서 간혹 정보가 누락되어 가져와지는 원인 파악 필요 
"""


def google_web_browsing(user_input):

    # load_dotenv()
    # api_key = os.environ("SERPAPI_API_KEY")
    # print(f"param : {param}")
    spec_search_chain = create_special_search_chain()
    search_comment = spec_search_chain.invoke({"question": user_input})
    # param = search_comment
    # print(f"param : {param}")

    # 구글 검색
    params = {
        "engine": "google",
        "q": search_comment,
        "gl": "KR",
        "hl": "ko",
        "api_key": "d5a3d6ce59b748413835bb36be6dca36a8742670e347e9c34f4a426f9cec280e",
        # "api_key": "ea2397acd164f428f4f61362101600ac097bc109ef9e7a59b49aa37907955f22",
    }
    search = GoogleSearch(params)
    search_results = search.get_dict()

    # 링크 추출
    urls = [result["link"] for result in search_results.get("organic_results", [])[:5]]

    # # 크롤링할 URL 리스트
    # urls = [
    #     "https://www.koreabaseball.com/Record/Player/HitterBasic/Basic1.aspx?sort=HRA_RT"
    # ]

    # AsyncChromiumLoader를 이용해 HTML 문서를 로드합니다.
    loader = AsyncChromiumLoader(urls)
    html_docs = loader.load()

    # RAG에서 사용할 Document 객체 리스트
    documents = []

    # 각 Document 객체의 HTML에서 trafilatura를 이용해 본문 추출
    for doc in html_docs:
        # BeautifulSoup으로 푸터, 스크립트 등 불필요한 요소 제거
        soup = BeautifulSoup(doc.page_content, "html.parser")
        for tag in soup.find_all(["footer", "nav", "aside", "script", "style"]):
            tag.extract()

        cleaned_html = str(soup)

        # 본문 추출
        main_content = trafilatura.extract(
            cleaned_html,
            output_format="json",
            include_comments=False,
            include_links=False,
            with_metadata=True,
        )

        if main_content:  # None 방지
            json_output = json.loads(main_content)

            # 본문 텍스트 추출 (없으면 빈 문자열)
            text = json_output.get("text", "").strip()
            title = json_output.get("title", "제목 없음")
            date = json_output.get("date", "날짜 없음")
            url = json_output.get("source", "URL 없음")

            if text:  # 본문이 있을 경우만 Document 생성
                doc_obj = Document(
                    page_content=text,
                    metadata={"title": title, "date": date, "url": url},
                )
                documents.append(doc_obj)

    # # Document 객체 리스트 출력
    # for i, doc in enumerate(documents):
    #     print(f"----- 문서 {i+1} (RAG용) -----")
    #     print(f"제목: {doc.metadata['title']}")
    #     print(f"날짜: {doc.metadata['date']}")
    #     print(f"URL: {doc.metadata['url']}")
    #     print(f"본문:\n{doc.page_content}...")  # 본문의 일부만 출력
    #     print(f"="*50)

    return documents
