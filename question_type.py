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


# Define a Pydantic model for the data required for each question type
class QuestionData(BaseModel):
    question_type: QuestionType
    teams: Optional[List[str]] = Field(default=None, description="경기 관련 팀 이름")  #
    player_name: Optional[str] = Field(default=None, description="특정 선수 이름")
    date: Optional[str] = Field(default=None, description="경기 날짜 (YYYY-MM-DD)")
    season: Optional[str] = Field(default=None, description="시즌 정보 (YYYY)")
    stats_type: Optional[str] = Field(
        default=None, description="통계 유형 (득점, 도움 등)"
    )
    location: Optional[str] = Field(default=None, description="경기 장소 (홈/원정)")
    context: Optional[str] = Field(
        default=None,
        description="질문을 이해하는 데 필요한 추가적인 맥락. 없으면 None을 반환.",
    )

    def to_search_query(self) -> str:
        terms = []
        for field_name, model_field_value in self.dict().items():
            if model_field_value is not None:
                if isinstance(model_field_value, Enum):
                    # Enum인 경우, .value를 사용하여 문자열로 변환
                    terms.append(model_field_value.value)
                elif isinstance(model_field_value, list):
                    # 리스트인 경우, 내부 문자열들을 공백으로 연결
                    terms.append(" ".join(model_field_value))
                else:
                    # 그 외의 경우, 문자열로 변환
                    terms.append(str(model_field_value))
        return " ".join(terms)
