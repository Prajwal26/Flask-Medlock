from flask import Flask, render_template, request,session,redirect
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from werkzeug import secure_filename
import json
import os
from datetime import datetime

with open("h:/COA/config.json", 'r') as c:
    params = json.load(c)["params"]

local_server=True
app = Flask(__name__)
app.secret_key="super-secret-key"

app.config['UPLOAD_FOLDER']=params['upload_location']

app.config.update(
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT='465',
    MAIL_USE_SSL=True,
    MAIL_USERNAME=params['gmail-user'],
    MAIL_PASSWORD=params['gmail-password']
)
mail=Mail(app)

app.config['SQLALCHEMY_DATABASE_URI'] = params['local_uri']
db = SQLAlchemy(app)


class Contacts(db.Model):
    '''
    sno, name phone_num, msg, date, email
    '''
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    phone_num = db.Column(db.String(12), nullable=False)
    message = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(20), nullable=False)

class blog_content(db.Model):
    '''
    sno, name phone_num, msg, date, email
    '''
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    slug = db.Column(db.String(12), nullable=False)
    content = db.Column(db.String(120), nullable=False)
    date = db.Column(db.String(12), nullable=True)


@app.route("/home1")
def home1():
     posts = blog_content.query.filter_by().all()
     return render_template('myfirst.html', params=params, posts=posts)

@app.route("/")
def home():
     posts = blog_content.query.filter_by().all()
     return render_template('index.html', params=params, posts=posts)




@app.route("/post/<string:post_slug>", methods=['GET'])
def post_route(post_slug):
    post = blog_content.query.filter_by(slug=post_slug).first()
    return render_template('post.html', params=params, post=post)



@app.route("/dashboard", methods = ['GET', 'POST'])
def dashboard():
    if ('user' in session and session['user']==params['admin_user']):
        posts=blog_content.query.all()
        return render_template("dashboard.html",params=params,posts=posts)
    if(request.method=='POST'):
        username=request.form.get('uname')
        password=request.form.get('pass')
        if (username==params['admin_user'] and password==params['admin_pass']):
            session['user']=username
            posts=blog_content.query.all()
            return render_template("dashboard.html",params=params,posts=posts)

        elif (username=="patient1" and password=="1234"):
            session['user']=username
            posts = blog_content.query.filter_by().all()
            return render_template('index.html', params=params, posts=posts)
        
    return render_template("login.html",params=params)
    




@app.route("/edit/<string:sno>",methods=['GET','POST'])
def edit(sno):
    if ('user' in session and session['user']==params['admin_user']):
        if request.method=='POST':
            box_title = request.form.get('title')
            slug = request.form.get('slug')
            content = request.form.get('content')
            date=datetime.now()

            if sno=="0":
                post=blog_content(title=box_title,slug=slug,content=content,date=date)
                db.session.add(post)
                db.session.commit()
            else:
                post=blog_content.query.filter_by(sno=sno).first()
                post.title=box_title
                post.slug=slug
                post.content=content
                post.date=date
                db.session.commit()
                return redirect('/edit/'+sno)
        post=blog_content.query.filter_by(sno=sno).first()

       # mail.send_message('New message for user admin',recipients=[params['gmail-user']],sender="admin",body="new update")
        return render_template("edit.html",params=params,post=post,sno=sno)

    



@app.route("/about")
def about():
    return render_template('about.html', params=params)
    


@app.route("/uploader",methods =['GET','POST'])
def uploader():
    if ('user' in session and session['user']==params['admin_user']):
        if(request.method=='POST'):
            f=request.files['file1']
            f.save(os.path.join(app.config['UPLOAD_FOLDER'],secure_filename(f.filename)))
            return('Uploaded succesfully')

@app.route("/logout")
def logout():
    session.pop('user')
    return redirect('/dashboard')

@app.route("/delete/<string:sno>",methods=['GET','POST'])
def delete(sno):
    if('user' in session and session['user']==params['admin_user']):
        post=blog_content.query.filter_by(sno=sno).first()
        db.session.delete(post)
        db.session.commit()
    return redirect("/dashboard")



@app.route("/contact", methods = ['GET', 'POST'])
def contact():
    if(request.method=='POST'):
        '''Add entry to the database'''
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        message = request.form.get('message')
        entry = Contacts(name=name, phone_num = phone, message = message,email = email )
        db.session.add(entry)
        db.session.commit()
        mail.send_message('New message for user admin',recipients=[params['gmail-user']],sender=email,body=message+"\n"+phone)
    return render_template('contact.html',params=params)


app.run(debug=True)
