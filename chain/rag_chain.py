import os
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document as LC_Document
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI


def create_rag_chain(documents):
    """
    웹 브라우징 결과(Document 객체 리스트)를 입력받아,
    가장 유사한 텍스트 청크들을 검색한 후 각 청크를 요약하여
    토큰 사용을 최적화하면서 최종 프롬프트를 구성하는 진정한 RAG 체인을 생성합니다.
    프롬프트 요구사항은 그대로 유지합니다.
    """
    # 1. 문서 청크 분할 (출처(metadata) 유지)
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=100,
        length_function=len,
        separators=["\n\n", "\n", " ", ""],
        is_separator_regex=False
    )

    chunked_docs = text_splitter.split_documents(documents)

    # 2. 임베딩 및 벡터 스토어 구축 (HuggingFaceEmbeddings 사용)
    model_name = "jhgan/ko-sroberta-multitask"
    encode_kwargs = {'normalize_embeddings': True}
    embeddings = HuggingFaceEmbeddings(model_name=model_name, encode_kwargs=encode_kwargs)
    vector_store = FAISS.from_documents(documents=chunked_docs, embedding=embeddings)
    retriever = vector_store.as_retriever(search_type="mmr", search_kwargs={"fetch_k": 10, "k": 5})

    # 4. 최종 프롬프트 템플릿 (출력 규칙 그대로 유지)
    prompt = PromptTemplate.from_template(
        """당신은 스포츠 정보를 제공하는 AI 어시스턴트입니다.  
        당신의 임무는 주어진 문맥(context)에서 사용자의 질문(question)에 대해 정확하고 친절한 답변을 제공하는 것입니다.

        주어진 문맥(context)을 사용하여 질문(question)에 답하세요.  
        만약 문맥(context)에서 질문에 대한 정보를 찾을 수 없다면,  
        `주어진 정보에서 질문에 대한 정보를 찾을 수 없습니다.`라고 답하세요.  
        단, 너무 딱딱한 표현 대신 친절하고 자연스러운 응답을 제공하세요.  
        예: "현재 관련된 정보가 확인되지 않아요. 하지만 다른 궁금한 점이 있다면 알려주세요!"  

        ### **출력 규칙:**  
        - **모든 답변을 Markdown 스타일로 제공하세요.**  
        - **소 제목을 활용하여 가독성을 높이세요.**  
        - **리스트(`-`), 굵은 글씨(`**`), 이모지 등을 활용하세요.**  
        - **각 문장이 참조한 출처를 해당 문장 끝에 `[출처](URL)` 형식으로 반드시 포함하세요.**  
          - 예: `SSG 랜더스는 2025년 Frontier 회원을 모집합니다. [출처](https://example.com)`
          - **출처가 없는 경우 표기하지 마세요.**

        ### **질문 (Question):**  
        {question}  

        ### **문맥 (Context):**  
        {context}  

        ### **답변 (Answer):**
        """
    )
    llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0)

    rag_chain = (
            {"context": retriever, "question": RunnablePassthrough()}
            | prompt
            | llm
            | StrOutputParser()
    )
    return rag_chain
