 
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tweets.db'
db = SQLAlchemy(app)

class Tweet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(280))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', backref=db.backref('tweets', lazy=True))

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    password = db.Column(db.String(80))
    
    def __repr__(self):
        return '<User %r>' % self.username

@app.route('/')
def index():
    tweets = Tweet.query.order_by(Tweet.id.desc()).all()
    return render_template('index.html', tweets=tweets)

@app.route('/profile/<username>')
def profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    tweets = Tweet.query.filter_by(user_id=user.id).order_by(Tweet.id.desc()).all()
    return render_template('profile.html', user=user, tweets=tweets)

@app.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first_or_404()
        user.password = request.form['password']
        db.session.commit()
        return redirect(url_for('profile', username=user.username))
    else:
        user = User.query.filter_by(username=request.args.get('username')).first_or_404()
        return render_template('edit_profile.html', user=user)

@app.route('/follow/<username>')
def follow(username):
    user = User.query.filter_by(username=username).first_or_404()
    current_user = User.query.filter_by(username=request.args.get('username')).first_or_404()
    current_user.following.append(user)
    db.session.commit()
    return redirect(url_for('profile', username=user.username))

@app.route('/followers/<username>')
def followers(username):
    user = User.query.filter_by(username=username).first_or_404()
    followers = user.followers.all()
    return render_template('followers.html', user=user, followers=followers)

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
