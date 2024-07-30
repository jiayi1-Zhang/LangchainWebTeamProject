import os
# zhipuai
os.environ["ZHIPUAI_API_KEY"] = "53ca6a88a682be774f7c07ad856b5d42.5Hczmqc5Cz3d4WBM"

from langchain_community.chat_models import ChatZhipuAI
zhipuai_model = ChatZhipuAI(model="glm-4",)

chat_model = zhipuai_model

response = chat_model.invoke("你是什么模型？介绍一下自己")

from flask import Flask, render_template, request, jsonify
app = Flask(__name__)


@app.route("/")
def hello():
    return render_template("chatbot.html", response=response.content)


question = "我不好"
result = "暂无"
@app.route('/submit-form', methods=['POST'])
def submit_form():
    # 从请求中解析JSON数据
    data = request.get_json()
    question = data.get('question')
    print(question)
    global result
    result = chat_model.invoke(question)
    result = result.content

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
