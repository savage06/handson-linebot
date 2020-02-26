from flask.ext.sqlalchemy import SQLAlchemy
from flask import Flask, render_template, request

# DB接続に関する部分
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
db = SQLAlchemy(app)

# モデル作成
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    email = db.Column(db.String(80), unique=True)

    def __init__(self, username, email):
        self.username = username
        self.email = email

    def __repr__(self):
        return '<User %r>' % self.username

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tasks = db.Column(db.String(80))
    user_id = db.Column(db.Integer,db.ForeignKey('user.id'))

    def __init__(self, tasks, user_id):
        self.tasks = tasks
        self.user_id = user_id

    def __repr__(self):
        return '<Task %r>' % self.tasks

# データベースに追加するコード例
@app.route("/", methods=['POST'])
def register():
    if request.method == 'POST':
        name= request.form['name']
        email = request.form['email']
        task = request.form['task']
        # emailが未登録ならユーザー追加
        if not db.session.query(User).filter(User.email == email).count():
            reg = User(name, email)
            db.session.add(reg)
            db.session.commit()


        # タスク追加
        user_id= User.query.filter_by(User.email == email).first().id
        task = Task(text, user_id)
        db.session.add(task)
        db.session.commit()

        return render_template('success.html')  return render_template('index.html')

if __name__ == '__main__':
    app.debug = True
    app.run()
    