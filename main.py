from dotenv import load_dotenv
import os
import openai
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from flask import Flask, request, abort

# 載入`.env`文件中的環境變數
load_dotenv()

# 使用環境變數管理敏感資料
env_vars = {
    "OPENAI_API_KEY": "",
    "CHANNEL_ACCESS_TOKEN": "",
    "CHANNEL_SECRET": "",
}

for key in env_vars:
    value = os.environ.get(key, "")
    if value:
        env_vars[key] = value
        print(f"{key}: {value}")
    else:
        print(f"Error: {key} is not set")

openai.api_key = env_vars["OPENAI_API_KEY"]
line_bot_api = LineBotApi(env_vars["CHANNEL_ACCESS_TOKEN"])
handler = WebhookHandler(env_vars["CHANNEL_SECRET"])

app = Flask(__name__)

# LINE Bot 的 Webhook 接口，用於接收 LINE 平台的訊息事件
@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers["X-Line-Signature"]
    body = request.data.decode("utf-8")
    app.logger.info("Request body: " + body)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return "OK"

# 處理 LINE 平台傳來的文字訊息
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    # 將接收到的文字訊息傳遞至 OpenAI 的 ChatGPT 模型，取得回應訊息
    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=event.message.text,
        max_tokens=60,
        n=1,
        stop=None,
        temperature=0.5,
    )

    # 取得回應訊息中的文字部分
    message = response.choices[0].text.strip()
    print("chatGPT回覆:")
    print(message)

    # 將回應訊息傳送至 LINE 平台
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=message)
    )

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

