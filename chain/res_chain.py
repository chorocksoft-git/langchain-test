from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

from langchain.docstore.document import Document as LC_Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import OpenAIEmbeddings
from langchain.chains import RetrievalQA
from langchain_huggingface import HuggingFaceEmbeddings


def create_response_chain(documents):
    """
    웹 브라우징 결과(Document 객체 리스트)를 입력받아,
    가장 유사한 텍스트 청크만 LLM에 전달하는 Retrieval 기반 체인을 생성합니다.
    """

    # 📌 문서를 작은 청크로 분할
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=100,
        length_function=len,
        separators=["\n\n", "\n", " ", ""],  # 문단 > 줄바꿈 > 공백 순으로 분리
        is_separator_regex=False
    )

    # 📌 모든 문서를 청크로 변환하고, 출처(metadata)를 함께 포함
    chunked_docs = []
    for doc in documents:
        chunks = text_splitter.split_text(doc.page_content)
        source_title = doc.metadata.get("title", "Unknown")  # 출처 URL 가져오기
        source_date = doc.metadata.get("date", "Unknown")
        source_url = doc.metadata.get("source", "Unknown")

        for chunk in chunks:
            # ✅ 청크 데이터에 출처 직접 포함
            chunk_with_source = f"{chunk}\n\n(출처:{source_url})"
            chunked_docs.append(LC_Document(
                page_content=chunk_with_source,
                metadata={"title": source_title, "date": source_date, "source": source_url}
            ))

    # 📌 임베딩을 생성하여 벡터 스토어(FAISS)에 저장
    model_name = "jhgan/ko-sroberta-multitask"
    encode_kwargs = {'normalize_embeddings': True}
    embeddings = HuggingFaceEmbeddings(
        model_name=model_name,
        encode_kwargs=encode_kwargs
    )
    # embeddings = OpenAIEmbeddings()
    vector_store = FAISS.from_documents(chunked_docs, embeddings)

    # 📌 질문과의 유사도 기준으로 상위 k개 청크 검색 (예: k=5)
    retriever = vector_store.as_retriever(search_type="mmr", search_kwargs={"fetch_k": 10, "k": 5})

    # 📌 프롬프트 템플릿 구성
    prompt = PromptTemplate.from_template(
        """
        당신은 스포츠 정보를 제공하는 AI 어시스턴트입니다.  
        사용자의 질문에 대해 핵심 정보를 정리하여 **Markdown 형식으로 간결하게 출력**하세요.

        ### **출력 규칙:**  
        - **제목을 활용하여 가독성을 높이세요.**  
        - **리스트(`-`), 굵은 글씨(`**`), 이모지(`⚽`, `📅`, `🏟️`) 등을 활용하세요.**  
        - **각 문장은 해당하는 출처 URL을 포함하세요.**  
        - **문장 끝에 `[출처](URL)` 형식으로 출처를 표기하세요.**  
            - 레퍼런스에 출처가 없을 경우 출처는 표기하지 마세요.
        - **모든 답변을 Markdown 스타일로 제공하세요.**  
        - **레퍼런스에 정보가 없을 경우, 딱딱한 표현 대신 친절한 서비스 말투를 사용하세요.**  
          - 예: "오늘은 편성된 경기가 없습니다. 하지만 다음 경기 일정은 다음과 같습니다."  
          - 예: "현재 관련된 정보가 확인되지 않아요. 하지만 다른 궁금한 점이 있다면 알려주세요!" 
          - 레퍼런스가 없을 경우 출처는 표기하지 마세요.

        ### **REFERENCE:**  
        {context}

        ### **QUESTION:**  
        {question}
        """
    )

    # 📌 LLM과 Retrieval 체인 생성
    llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0.1)
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",  # 단순 삽입 방식
        retriever=retriever,
        chain_type_kwargs={"prompt": prompt}
    )

    return qa_chain


def predict_response_chain():
    """
    현재는 예측 결과를 지어서 답변
    향후 예측 모델 연동
    """
    prompt = PromptTemplate.from_template(
        #
        """
        당신은 스포츠 경기결과를 예측하는 AI 어시스턴트입니다.
        오늘 날짜를 확인하고 해당 정보가 없으면 가상으로 지어내서 답변하세요.
        모든 답변을 일관된 Markdown 스타일로 제공하세요.  

        **QUESTION:**  
        {question}
        """
    )
    llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0)
    answer_parser = StrOutputParser()
    chain = prompt | llm | answer_parser
    return chain


def generate_natural_language_answer():
    """
    쿼리 결과와 컬럼 정보를 받아 LLM을 통해 자연어 답변을 생성합니다.
    """
    # 결과를 보기 좋은 문자열로 변환
    prompt = PromptTemplate.from_template(
        """
        아래는 SQL 쿼리 실행 결과입니다.

        컬럼: {columns}
        결과:
        {result}

        위 결과를 바탕으로 사용자에게 이해하기 쉬운 자연스러운 문장을 작성해주세요. (2줄 이내로)
        참고로 win_rate는 AI 예측 승률이다.
        결과가 없을 경우 사용자 질문: {question}에 대한 정보를 찾을 수 없다고 말해줘.
        작성된 답변:
        """
    )
    llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0)

    # nl_prompt = PromptTemplate(template=nl_prompt_template, input_variables=["columns", "result"])
    # nl_chain = LLMChain(llm=llm, prompt=nl_prompt)
    answer_parser = StrOutputParser()
    chain = prompt | llm | answer_parser
    return chain
