from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from datetime import datetime
from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum


class QuestionType(Enum):
    GAME_PREDICTION = "game_prediction"  # 경기 예측
    PLAYER_STATS = "player_stats"  # 선수 기록
    GAME_SCHEDULE = "game_schedule"  # 경기 일정
    GAME_RESULTS = "game_results"  # 과거 경기 성적
    LINEUP_INFO = "lineup_info"  # 라인업 및 선수 상태
    TEAM_STRATEGY = "team_strategy"  # 팀 전략 및 트레이드
    RULES_EXPLANATION = "rules_explanation"  # 규정 및 기타 설명
    NEWS_HIGHLIGHTS = "news_highlights"  # 뉴스/하이라이트
    HISTORY_RECORDS = "history_records"  # 역사 및 기록


class QuestionData(BaseModel):
    question_type: QuestionType
    teams: Optional[List[str]] = Field(default=None, description="경기 관련 팀 이름")
    player_name: Optional[str] = Field(default=None, description="특정 선수 이름")
    date: Optional[str] = Field(default=None, description="경기 날짜 (YYYY-MM-DD)")
    season: Optional[str] = Field(default=None, description="시즌 정보 (YYYY)")
    stats_type: Optional[str] = Field(default=None, description="통계 유형 (득점, 도움 등)")
    location: Optional[str] = Field(default=None, description="경기 장소 (홈/원정)")
    context: Optional[str] = Field(default=None, description="질문을 이해하는 데 필요한 추가적인 맥락")
    search_query: str = Field(default="", description="웹 검색 최적화된 질문")
    llm_query: str = Field(default="", description="LLM이 답변을 쉽게 생성할 수 있도록 변환된 질문")


def create_question_classification_chain():
    '''
    질문을 분석하여 적절한 질문 유형을 분류하고, 관련 데이터를 추출하며, 검색 최적화된 질문을 생성하는 체인입니다.
    '''
    prompt = PromptTemplate.from_template(
        """
        당신은 스포츠 질문을 분석하여 적절한 질문 유형을 분류하고, 관련 정보를 추출하며, 검색에 최적화된 형태로 질문을 변환하는 전문가입니다.

        - 질문 유형을 식별하세요. (예: 경기 일정, 선수 기록, 경기 결과 등)
        - 질문에서 주요 정보를 추출하세요. (팀명, 선수명, 날짜, 시즌 등)
        - 상대적인 날짜 표현(어제, 오늘, 내일, 작년, 올해 등)을 현재 날짜({current_date}) 기준으로 변환하세요.
        - 검색 최적화된 질문을 생성하세요. 
            - 예시 : "손흥민 득점 기록 2025년", "KBO 개막 일정 2025년", "스프링 캠프를 따듯한 나라에서 하는 이유", ""
        - **LLM이 보다 상세한 답변을 제공할 수 있도록, 검색 최적화된 질문과 함께 문장형 질문을 생성하세요.**
            - 유저 질문이 모호한 경우, 보다 명확한 형태로 변환하세요.
            - 추가적인 맥락이 필요하면 보완하여 질문을 구성하세요.
        
        QUESTION:
        {question}

        FORMAT:
        {format}
        """
    )

    llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0)

    # 현재 날짜를 LLM에 전달하여 상대적 날짜 변환을 유도
    current_date = datetime.today().strftime("%Y-%m-%d")
    prompt = prompt.partial(format=PydanticOutputParser(pydantic_object=QuestionData).get_format_instructions(),
                            current_date=current_date)

    chain = prompt | llm | PydanticOutputParser(pydantic_object=QuestionData)

    return chain
