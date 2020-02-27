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

playerdict = {}   #playerID(user_id)とPlayerインスタンスの紐付け

playerIDs_SO = []   #ShuffleされたplayerIDs

playerIDs_DO =[]    #参加順のplayerIDs

actedNum = 0    #status中で行動を終えたプレイヤーの数

themes1 = ['a','b','c','d','e']

themes2 = ['f','g','h','i','j']

f = thisRoom()
f.phase = 'suspend'
db.session.commit()
class Room(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    phase = db.Column(db.String(80))
    player = db.Column(db.Integer)
    roomact = db.Column(db.Integer)
    
def thisRoom():
  rooms = session.query(Room).filter(Room.id==event.source.group_id).all()
  return rooms(0)


  # def question(num):
  #       text ='お題は「%s × %s」です。'%(
  #         themes1[random.randint(0, len(themes1)-1)], 
  #         themes2[random.randint(0, len(themes2)-1)]
  #         )
  #       TextSendMessage('%sさんの番です'%playerdict{playerIDs_SO[num]}.name)
  #       TextSendMessage('抽選中・・・')
  #       time.sleep(3.0)
  #       TextSendMessage(text)
  #       global actedNum
  #       actedNum+=1

def createConfirm():
  confirm_temprate_message = TemplateSendMessage(
      alt_text='Confirm template',
      template=ConfirmTemplate(
          text='参加する？',
          actions=[
              PostbackAction(
                  label='参加',
                  data='participate'
              ),
              PostbackAction(
                  label='締め切り',
                  data='close'
              )
          ]
      )
  )


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

@handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event):
  global playerdict
  global playerIDs_SO
  global playerIDs_DO
  global actedNum
  global status
  text = event.message.text
  profile = line_bot_api.get_profile(event.source.user_id)

  if text == '強制終了':
    TextSendMessage('強制終了')
    f = thisRoom()
    f.phase = 'suspend'
    db.session.commit()
  else:
    if status == 'suspend':
      if text =='開始':
        playerdict = {}
        playerIDs_SO = []
        playerIDs_DO = []
        actedNum = 0
        TextSendMessage('「開始」はOK')
        createConfirm()
        line_bot_api.reply_message(
          event.reply_token,confirm_temprate_message
        )
        status = 'inviting'

    elif status == 'playing':
      if actedNum == len(playerIDs_SO):
        TextSendMessage('回答終了。投票に移る')
        actedNum = 0
        text =''
        i = 1
        for playerID in playerIDs_SO:
          text += ('answer%d: %s\n'%(i, playerdict{playerID}.answer))
          i+=1
        text.rstrip('\n')
        TextSendMessage(text)
        status = 'voting'
      else:
        if profile.user_id == playerIDs_SO[actedNum]:
          playerdict{profile.user_id}.answer = text
          question(actedNum)
        else:
          TextSendMessage('%sさんの番です'%playerdict{playerIDs_SO[actedNum]}.name)

    elif status == 'voting':
      if not playerdict{profile.user_id}.voted:
        vote_num = int(text)
        if 1 <= vote_num and vote_num <= len(playerIDs_SO):
          playerdict{playerIDs_SO[vote_num-1]}.ansVote+=1
          playerdict{profile.user_id}.voted = True
          actedNum+=1
        else:
          TextSendMessage('answer%s is not exists'%text)
      else:
        TextSendMessage('already voted')
      if actedNum == len(playerIDs_SO):
        text = '勝者は'
        winnerIDs = []
        most = 0
        for playerID in playerIDs_DO:
          if playerdict{playerID}.ansVote == most:
            winnerIDs.append(playerID)
          elif playerdict{playerID}.ansVote > most:
            winnerIDs = [playerID]
            most = playerdict{playerID}.ansVote
        for winnerID in winnerIDs:
          text+= 'と%sさん'%playerdict{winnerID}.name
        text.lstrip('と')
        text+='です。'
        TextSendMessage(text)
        status = 'suspend'

  @handler.add(PostbackEvent)
  def on_postback(event):
    global status
    global playerIDs_SO
    global playerIDs_DO
    global playerdict

    if status == 'inviting':
      profile = line_bot_api.get_profile(event.source.user_id)
      reply_token = event.reply_token
      postback_msg = event.postback.data
      if postback_msg == 'participate':
        TextSendMessage('「参加」はOK')
        if not profile.user_id in playerIDs_SO:
          playerdict{profile.user_id} = Player(profile.display_name)
          playerIDs_SO.append(profile.user_id)
      elif postback_msg == 'close':
        TextSendMessage('「締め切り」はOK')
        TextSendMessage('募集終了')
        text = '参加メンバーは以下の通り\n'
        for playerId in playerIDs_SO:
          i = 1
          text += '%d. %s/n'%(i, playerdict{playerId}.display_name)
        text.rstrip('\n')
        TextSendMessage(text)
        playerIDs_DO = playerIDs_SO
        random.shuffle(playerIDs_SO)
        question(actedNum)
        status = 'playing'

if __name__ == "__main__":
#    app.run()
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
