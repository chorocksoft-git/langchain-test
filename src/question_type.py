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

