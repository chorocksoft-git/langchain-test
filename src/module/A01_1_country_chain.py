from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_teddynote.models import MultiModal

from src.prompts.extract_info_from_image import SYSTEM_PROMPT as image_prompt
from src.prompts.extract_info_from_json import SYSTEM_PROMPT as json_prompt


def extract_chain():
    llm = ChatOpenAI(
        temperature=0,
        model_name="gpt-4o",
    )

    chain = MultiModal(llm, system_prompt=image_prompt)

    return chain


def answer_chain():
    llm = ChatOpenAI(model_name="gpt-4o", temperature=0)

    prompt = PromptTemplate.from_template(json_prompt)

    answer_parser = StrOutputParser()
    chain = prompt | llm | answer_parser
    return chain
