from flask import Flask, render_template, request, jsonify, redirect, Response, url_for
from pymongo import MongoClient 
from pymongo.errors import DuplicateKeyError
import json,os
from datetime import datetime

mongodb_hostname = os.environ.get("MONGO_HOSTNAME","localhost")
client = MongoClient('mongodb://'+mongodb_hostname+':27017/')


db=client['InfoCinemas']
users=db['Users']
movies=db['Movies']

app=Flask(__name__)

@app.route('/')
def home():
    
    return render_template('home.html')

@app.route('/login', methods=['GET','POST'])
def  login():
    
    if request.method == 'POST': #se periptwsh poy 8elw na kanw login sto systhma
        login_email = request.form['login_email']
        login_pass = request.form['login_password']
        exists0 = users.find_one({"email": {"$in": [login_email]}})
        exists1 = users.find_one({"password": {"$in": [login_pass]}})

        if exists0 is None or exists1 is None :
            return render_template('login.html', x=0)

        cur=users.find_one({"email": {"$in": [login_email]}})
        a=cur.get('category')
        u1=users.find_one({"email": {"$in": [login_email]}})
        nameu=u1.get('name')
        
        if a == 'user':
            return redirect(url_for('profile',mail=login_email,name=nameu))
        else:
            return redirect(url_for('adprofile',name=nameu))
    
    else:
        return render_template('login.html')

@app.route('/profile')
def profile():
    mmail=request.args['mail']
    nameu=request.args['name']
    return render_template('profile.html',mail=mmail,name=nameu)

@app.route('/adprofile')
def adprofile():
    nameu=request.args['name']
    return render_template('adprofile.html',name=nameu)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST': 

        register_name = request.form['name']  
        register_email = request.form['email']
        register_password = request.form['password']
        data = {}

        if users.find({}).count() == 0:
            
            data = { 
            "name":register_name,
            "email":register_email,
            "password":register_password,
            "movies_seen":[],
            "category":"admin"
                }
            users.insert_one(data)
            return redirect(url_for('login'))

        else:
            data = {
            "name":register_name,
            "email":register_email,
            "password":register_password,
            "movies_seen":[],
            "category":"user"
            }
           
            if users.find({"email": register_email}).count() == 0:
                users.insert_one(data)
                return redirect(url_for('login'))
            else:
                print('There is already a user with this email.Try again')
                return render_template('register.html', x=1,mail=register_email)
        return render_template('login.html')
    
    else:
        return render_template('register.html')

@app.route('/insertmovie', methods=['GET','POST'])
def insertmovie():
    if request.method == 'POST': 
        intitle=request.form['title']
        inyear=request.form['year']
        name=request.form['name']
        if movies.find({"title":intitle , "year":inyear}).count() != 0 :
            return render_template('insertmovie.html',x=0)
        else:
            a = request.form
            data = json.dumps(a)
            data = json.loads(data)
            tit = data.pop('title')
            desc = data.pop('description')
            ye = data.pop('year')
            na = data.pop('name')
            screening = []
            scrdict = {}
            print('data',data)
            for item in data.values():
                d = item.replace('T',',')
                scrdict[d]=50
            print(scrdict)
            screening.append(scrdict)    
            mdata = {
                "title":tit,
                "year":ye,
                "description":desc,
                "screening": screening
                }
            movies.insert_one(mdata)
            return render_template('insertmovie.html', x=1,name=name)
    
    else:
        name=request.args['name']
        return render_template('insertmovie.html',name=name)
      
@app.route('/deletemovie', methods=['GET','POST'])
def deletemovie():
    if request.method == 'POST':
        smovie = request.form['moviesearch']
        name=request.form['name']
        a=movies.find({"title":smovie}).count()

        if a == 0:
            return render_template('deletemovie.html',x=0,name=name)
        elif a == 1:
            movies.delete_one({'title':smovie})
            return render_template('deletemovie.html',x=1,name=name)
        else:
            miny= movies.find_one({"title":smovie},{"title":1 , "year":1 , "_id":0 }).get('year')
            print(movies.find({"title":smovie},{"title":1 , "year":1 , "_id":0 }))
            print(movies.find({"title":smovie},{"title":1 , "year":1 , "_id":0 })[0])
            print(miny)
            for x in movies.find({"title":smovie},{"title":1 , "year":1 , "_id":0 }):
                if x.get('year') < miny:
                    miny=x.get('year')
            movies.delete_one({'year':miny})
            return render_template('deletemovie.html',x=2 ,n=smovie ,y=miny,name=name)

    else:
        name=request.args['name']
        return render_template('deletemovie.html',name=name)

@app.route('/addadmin' , methods=['GET','POST'])
def addadmin():
    if request.method == 'POST':
        usname = request.form['usersname']
        name=request.form['name']
        a=users.find({"email":usname}).count()
        if a == 0:
            return render_template('addadmin.html',x=0 ,n=usname,name=name)
        else:
            users.update_one({"email":usname}, {"$set":{'category':'admin'}})
            return render_template("addadmin.html" ,x=1 ,n=usname,name=name)

    else:
        name=request.args['name']
        return render_template('addadmin.html',name=name)

@app.route('/updatemovie' , methods=['GET','POST'])
def updatemovie():
    if request.method == 'POST':
        mtitle=request.form['movieupsname']
        myear=request.form['movieupsyear']
        choice = request.form['choices']
        name=request.form['name']
        a=movies.find({"title":mtitle},{"ryear":myear}).count()
        if a == 0:
            return render_template('updatemovie.html',x=0,name=name)
        else:
            if choice == 'title':
                print('1')
                return redirect(url_for('uptitle', ot=mtitle ,oy=myear,name=name))
            elif choice == 'year':
                print('2')
                return redirect(url_for('upyear', ot=mtitle ,oy=myear,name=name))
            elif choice == 'desc':
                print('3')
                return redirect(url_for('updescr', ot=mtitle ,oy=myear,name=name))
            elif choice == 'scr' :
                print('4')
                return redirect(url_for('chscr' ,ot=mtitle ,oy=myear,name=name)) 
    else:
        name=request.args['name']
        return render_template('updatemovie.html',name=name)

@app.route('/chscr', methods=['GET','POST'])
def chscr():
    oldtitle = request.args['ot']
    year = request.args['oy']
    
    return render_template("chscr.html", ot = oldtitle, oy = year)

@app.route('/uptitle' , methods=['GET','POST'])
def uptitle():
    
    if request.method == 'POST':
        newtitle = request.form["ntitle"]
        oldtitle = request.form["ot"]
        year = request.form["oy"]
        name = request.form['name']
        movies.update_one({"title":oldtitle,"year":year},{"$set":{"title":newtitle}})
        return render_template("uptitle.html", ot= oldtitle, oy= year,name=name, k=1)
    else:
        name=request.args['name']
        k = request.args['ot']
        l = request.args['oy']
        return render_template("uptitle.html", ot= k, oy= l, name=name)
    
@app.route('/updescr', methods=['GET','POST'])
def updescr():
     if request.method == 'POST':
        newdescr = request.form["ndesc"]
        oldtitle = request.form["ot"]
        year = request.form["oy"]
        name=request.form['name']
        movies.update_one({"title":oldtitle,"year":year},{"$set":{"description":newdescr}})
        return render_template("updescr.html", ot = oldtitle, oy = year ,name = name, k=1)
     else:
        name=request.args['name']
        k = request.args['ot']
        l = request.args['oy']
        return render_template("updescr.html", ot= k, oy= l,name=name)

@app.route('/upyear' , methods=['GET' , 'POST'])
def upyear():
    if request.method == 'POST':
        newyar = request.form["nyear"]
        oldtitle = request.form["ot"]
        year = request.form["oy"]
        name=request.form['name']
        movies.update_one({"title":oldtitle,"year":year},{"$set":{"year":newyar}})
        return  render_template("upyear.html", ot= oldtitle, oy= year, name=name,k=1)

    else:
        k = request.args['ot']
        l = request.args['oy']
        name=request.args['name']
        return render_template("upyear.html", ot= k, oy= l,name=name)

@app.route('/upscr' , methods=['GET' , 'POST'])
def upscr():
    if request.method == 'POST':
        nscr = request.form['nscr']
        oldtitle = request.form['ot']
        year = request.form['oy']
        od=request.form['choice']
        a=movies.find_one({"title":oldtitle,"year":year})
        a=a["screening"]
        print(od)
        movies.update_one({ "title":oldtitle , "year":year }, { "$unset" : { "screening.0."+od : 1} })
        movies.update_one({"title":oldtitle , "year":year} , {"$set": {"screening.0."+nscr: 50}})

        return render_template('upscr.html', k=1, ot=oldtitle, oy=year ,a=a)
    else:
        k = request.args['ot']
        l = request.args['oy']
        a=movies.find_one({"title":k,"year":l})
        a=a["screening"]

        return render_template("upscr.html" , ot=k , oy=l , a=a)

@app.route('/addscr' , methods=['GET' , 'POST'])
def addscr():
    if request.method == 'POST':
        dates = request.form
        data = json.dumps(dates)
        data = json.loads(data)
        tit = data.pop('ot')  
        ye = data.pop('oy')
        for item in data.values():
            v=item.replace('T',',')
            movies.update_one({"title":tit , "year":ye}, {"$set": {"screening.0."+v:50}})
        
        return render_template('addscr.html',k=1,ot = tit, oy = ye)
    else:    
        k = request.args['ot']
        l = request.args['oy']

        return render_template('addscr.html',ot = k, oy = l)

@app.route('/delscr' , methods=['GET','POST'])
def delscr():
    if request.method == 'POST':
        year = request.form['oy']
        oldtitle = request.form['ot']
        od=request.form['choice']
        print(od)
        movies.update_one({ "title":oldtitle , "year":year }, { "$unset" : { "screening.0."+od : 1} })

        return redirect(url_for('updatemovie'))
    else:
        k = request.args['ot']
        l = request.args['oy']
        a=movies.find_one({"title":k,"year":l})
        a=a["screening"]
        print(a)
        return render_template("delscr.html" , ot=k , oy=l , a=a)
        
@app.route('/searchmovie',methods=['GET','POST'])
def searchmovie():

    if request.method == 'POST':
        stitle=request.form['stitle']
        mail=request.form['mail']
        name = request.form['name']
        lista1=[]

        if movies.find({"title":stitle}).count() == 0:
            return render_template("searchmovie.html",a=1,tit=stitle , mail=mail , name=name )
        else:
            counter=movies.find({"title":stitle}).count()
            for i in range(0,counter):
                lista1.append(movies.find({"title":stitle},{"title":1 , "year":1 , "_id":0 })[i])

            return render_template('searchmovie.html',counter=counter,lista=lista1 , mail=mail , name=name)
    else:
        mail=request.args['mail']
        name=request.args['name']
        return render_template('searchmovie.html',mail=mail, name=name)

@app.route('/moviedetails',methods=['GET','POST'])
def moviedetails():
    if request.method == 'POST':
        nt=request.form['nt']
        od=request.form['choice']
        tit=request.form['title']
        ye=request.form['year']
        mail=request.form['mail']
        name=request.form['name']
        sl=movies.find_one({ "title":tit , "year":ye },{"screening":1 , "_id":0}).get('screening')[0]
        print(sl)
        b=sl[od]
        c=int(b)-int(nt)
        d=request.form['d']
        a=movies.find_one({"title":tit,"year":ye})
        a=a["screening"]

        if c < 0:
            return render_template('moviedetails.html', tit=tit, ye=ye, d=d , a=a , mail=mail, k=1)

        movies.update_one({ "title":tit , "year":ye }, { "$unset" : { "screening.0."+od : 1} })
        movies.update_one({"title":tit , "year":ye} , {"$set": {"screening.0."+od: c}})
        ms=users.find_one({"email":mail},{"movies_seen":1,"_id":0}).get('movies_seen')
        iterable = tit+ '(' + ye + ')'

        if iterable not in ms: 
            users.update_one({"email":mail},{"$push":{"movies_seen": iterable }})
        
        return render_template('moviedetails.html',tit=tit,ye=ye,d=d,a=a,mail=mail,b=1,name=name)

    else:
        mail=request.args['mail']
        tit=request.args['title']
        ye=request.args['year']
        name=request.args['name']
        d=movies.find_one({"title":tit,"year":ye}).get('description')
        a=movies.find_one({"title":tit,"year":ye})
        a=a["screening"]

        return render_template('moviedetails.html', tit=tit, ye=ye, d=d , a=a , mail=mail,name=name)

@app.route('/view_history',methods=['GET','POST'])
def view_history():
    mail=request.args['mail']
    name=request.args['name']
    ms=users.find_one({"email":mail},{"movies_seen":1,"_id":0}).get('movies_seen')
    
    return render_template('view_history.html',hlist=ms,mail=mail,name=name)
    
if __name__=='__main__':
    app.run(debug=True,host='0.0.0.0',port=9000)