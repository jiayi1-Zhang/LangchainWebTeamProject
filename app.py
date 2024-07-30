# 导包
import os
import json
import requests
import threading
import shutil
from flask import Flask, jsonify, request
from langchain_community.chat_models import ChatZhipuAI
from langchain_community.document_loaders import (
    PyPDFLoader,
    Docx2txtLoader,
    TextLoader,
    CSVLoader,
)
from langchain.document_loaders import UnstructuredFileLoader
from langchain_community.document_loaders import WebBaseLoader
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import create_history_aware_retriever
from langchain_core.prompts import (
    MessagesPlaceholder,
    ChatPromptTemplate,
)
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.retrieval import create_retrieval_chain
from langchain.retrievers.multi_query import MultiQueryRetriever
from langchain.chains.retrieval_qa.base import RetrievalQA
from langchain_core.messages import HumanMessage, AIMessage
from langchain.memory import ConversationBufferMemory
from langchain_community.chat_message_histories import RedisChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory

# 环境变量设置
import modelchoice

modelchoice.setenv()

os.environ['SERPAPI_API_KEY'] = 'a3a020895a0debde83c3a13b048ce4c3fb97151dcd1ccd1769ed0a8a8abe1858'


class SourceService(object):
    def __init__(self, db_path):
        self.vector_store = None
        self.embeddings = HuggingFaceEmbeddings(
            model_name='D:\\WorkSpace\\PyCharm\\flask_teamProject_02\\m3e-base',
            model_kwargs={'device': 'cpu'})
        self.vector_store_path = db_path

    # 初始化向量数据库
    def init_source_vector(self, document_dir):
        documents = []
        for filename in os.listdir(document_dir):
            file_path = os.path.join(document_dir, filename)
            if filename.endswith('.pdf'):
                loader = PyPDFLoader(file_path)
                documents.extend(loader.load())
            elif filename.endswith('.docx'):
                loader = Docx2txtLoader(file_path)
                documents.extend(loader.load())
            elif filename.endswith('.txt'):
                loader = TextLoader(file_path)
                documents.extend(loader.load())
            elif filename.endswith('.csv'):
                loader = CSVLoader(file_path)
                documents.extend(loader.load())
        self.vector_store = FAISS.from_documents(documents, self.embeddings)
        self.vector_store.save_local(self.vector_store_path)

    # 添加文件数据
    def add_document(self, document_path):
        loader = UnstructuredFileLoader(document_path, mode='elements')
        doc_data = loader.load()
        self.vector_store.add_documents(doc_data)
        self.vector_store.save_local(self.vector_store_path)

    def load_vector_store(self, path):
        if path is not None:
            self.vector_store = FAISS.load_local(path, self.embeddings)
        else:
            self.vector_store = FAISS.load_local(self.vector_store_path, self.embeddings)
        return self.vector_store

    # 从网页上爬取数据
    def search_web(self, web_path):
        loader = WebBaseLoader(web_path)
        web_data = loader.load()
        self.vector_store.add_documents(web_data)
        self.vector_store.save_local(self.vector_store_path)


class ChatModel(object):
    def __init__(self, chat_llm, db_path, doc_path):
        self.llm = chat_llm
        self.source_service = SourceService(db_path)
        self.source_service.init_source_vector(document_dir=doc_path)
        self.history = []

    # 创建模型框架
    def create_llm(self):
        # 提示词工程
        history_prompt = ChatPromptTemplate.from_messages([
            ('system', '根据以上对话历史，生成一个检索查询，以便查找与对话相关的信息'),
            MessagesPlaceholder(variable_name='history'),
            ('human', '{input}'),
        ])
        # 生成含有历史信息的检索链
        retriever_history_chain = create_history_aware_retriever(self.llm,
                                                                 self.source_service.vector_store.as_retriever(),
                                                                 history_prompt)
        # 继续对话 记住检索到的文档等信息
        totol_prompt = ChatPromptTemplate.from_messages([
            ('system', "Answer the user's questions based on the below context:\n\n{context}"),
            MessagesPlaceholder(variable_name='history'),
            ('human', '{input}')
        ])
        # 生成 Retrieval 模型
        document_chain = create_stuff_documents_chain(self.llm, totol_prompt)
        retrieval_chain = create_retrieval_chain(retriever_history_chain, document_chain)
        return retrieval_chain

    def get_llm_answer(self, query):
        chat_ai = self.create_llm()
        result = chat_ai.invoke({
            'history': self.history,
            'input': query,
        })
        answer = result['answer']
        self.history.append(HumanMessage(content=query))
        self.history.append(AIMessage(content=answer))
        return answer


# main
doc_path = 'D:\\team_project\\uploads'
db_path = 'D:\\team_project\\vector_store'
if not os.path.exists(doc_path):
    os.makedirs(doc_path)

if not os.path.exists(db_path):
    os.makedirs(db_path)
else:
    shutil.rmtree(db_path)
    os.makedirs(db_path)

chat_llm = ChatZhipuAI(model="glm-4")
chat_model = ChatModel(chat_llm=chat_llm, db_path=db_path, doc_path=doc_path)


from flask import Flask, render_template, request, jsonify
app = Flask(__name__)


@app.route('/')
def index():
    return render_template("chatbot.html")


question = "你好"
result = "暂无"


@app.route('/submit-form', methods=['POST'])
def submit_form():
    # 从请求中解析JSON数据
    data = request.get_json()
    question = data.get('question')
    print(question)
    global result
    result = chat_model.get_llm_answer(question)
    # print(result)
    # 返回响应
    return jsonify({'status': 'success', 'message': 'Form data received'}), 200


@app.route('/get-data')
def get_data():
    # 准备数据
    global result
    data = {
        'message': result,
    }
    # 返回JSON数据
    return jsonify(data)


if __name__ == "__main__":
    app.run()
