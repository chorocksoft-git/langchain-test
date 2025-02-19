from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser

from question_type import QuestionData


def create_question_classification_chain(prompt_type):
    '''
    prompt_type 변수는 향후에 야구, 축구, 등의 종목을 선택하게 되면 그에 맞게 할당될 예정.
    '''
    prompt = PromptTemplate.from_template(
        """
        You are a helpful assistant. Please answer the following questions in KOREAN.

        QUESTION:
        {question}

        FORMAT:
        {format}
        """
    )

    # format 에 PydanticOutputParser의 부분 포맷팅(partial) 추가

    llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0)

    question_parser = PydanticOutputParser(pydantic_object=QuestionData)
    prompt = prompt.partial(format=question_parser.get_format_instructions())

    chain = prompt | llm | question_parser

    return chain
