from flask import Flask, request, abort
from flask_sqlalchemy import SQLAlchemy

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, ImageSendMessage, VideoSendMessage, StickerSendMessage, AudioSendMessage, JoinEvent, LeaveEvent
)
import os
import random

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
db = SQLAlchemy(app)
import time

class Room(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.String(80))
    phase = db.Column(db.String(80))
    player = db.Column(db.Integer)
    roomact = db.Column(db.Integer)

    def __init__(self, group_id,phase, player, roomact):
        self.group_id = group_id
        self.phase = phase
        self.player = player
        self.roomact = roomact  
        
    
# def thisRoom():
#   rooms = session.query(Room).filter(Room.id==event.source.group_id).all()
#   return rooms(0)


#環境変数取得
LINE_CHANNEL_ACCESS_TOKEN = os.environ["LINE_CHANNEL_ACCESS_TOKEN"]
LINE_CHANNEL_SECRET = os.environ["LINE_CHANNEL_SECRET"]

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)


@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

def show_room(event):
    # all_rooms = db.session.query(Room).all()
    # print(all_rooms)
    groupId = event.source.group_id
    return groupId

def record_room(event):
    groupId = event.source.group_id
    db.session.add(Room(groupId, "suspend", 0, 0))
    db.session.commit()
    message = "ゲームを開始する場合は「開始」と入力してください"
    return message

def receive_message(event):
    groupId = event.source.group_id
    userMessage = event.message.text
    if userMessage == "開始":
        f = db.session.query(Room).filter(Room.group_id == groupId)[0]
        f.phase = "invite"
        db.session.commit()
        message = "参加者は「参加」と入力してください"
    else: 
        message = "不正な入力です"
    return message

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    message = receive_message(event)
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text = message))

@handler.add(JoinEvent)
def handle_join(event):
    message = record_room(event)
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text = message))

if __name__ == "__main__":
#    app.run()
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
