from flask import Flask, request, abort
from flask_sqlalchemy import SQLAlchemy

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, ImageSendMessage, VideoSendMessage, StickerSendMessage, AudioSendMessage
)
import os
import random

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
db = SQLAlchemy(app)
import time

class Room(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    phase = db.Column(db.String(80))
    player = db.Column(db.Integer)
    roomact = db.Column(db.Integer)

    def __init__(self, phase, player, roomact):
        self.phase = phase
        self.player = player
        self.roomact = roomact  
    
# def thisRoom():
#   rooms = session.query(Room).filter(Room.id==event.source.group_id).all()
#   return rooms(0)


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
def show_room(userMessage):
    all_rooms = db.session.query(Room).all()
    print(all_rooms)
    return "show_room"
    
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    message = show_room(event.message.text)
    line_bot_api.reply_message(
        event.reply_token,
        message)

if __name__ == "__main__":
#    app.run()
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
