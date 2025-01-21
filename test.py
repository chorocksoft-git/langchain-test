# from serpapi import GoogleSearch

# params = {
#   "engine": "naver",
#   "query": "paris",
#   "api_key": "d5a3d6ce59b748413835bb36be6dca36a8742670e347e9c34f4a426f9cec280e"
# }

# search = GoogleSearch(params)
# results = search.get_dict()
# organic_results = results["organic_results"]
import os

from langchain_community.utilities import SerpAPIWrapper

os.environ["SERPAPI_API_KEY"] = (
    "e76de14ee240e0051ed8bb05d5db568dd1dc9cfcaa2b51fd83613829a85bf244"
)

params = {"engine": "google", "gl": "kr", "hl": "ko", "num": "3"}  # 검색 파라미터

search = SerpAPIWrapper(params=params)  # 검색 객체 생성
search_query = f"{question}"  # 검색 쿼리
search_result = search.run(search_query)  # 검색 실행
search_result = eval(search_result)  # list 형태로 변환

print(search_result)
