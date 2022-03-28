from flask import Flask, jsonify, request, render_template,Flask,url_for,request,redirect,make_response,session, flash
from pymongo import MongoClient
import requests,json
import qrcode, os
import datetime

app = Flask(__name__)
app.secret_key = '123321'

app.config["MONGO_URI"] = "mongodb+srv://codesploit:codesploit@cluster0.xcehq.mongodb.net/test"
client = MongoClient("mongodb+srv://codesploit:codesploit@cluster0.xcehq.mongodb.net/test")
db = client['Surplussuppliers']
coll = db["users"]
clien = db["client"]
col = db["workers"]
co = db["food"]
c = db["organizer"]

def algo(valuv):
    print(valuv)
    details = []
    word = []
    bc=0
    colom = 0
    for i in valuv:
        if(i == '['):             #['sdfs','zsfzzx']
            bc+=1
        if(bc==1):
            if(i=="'" and colom==1):
                colom=0
                det = ''.join(word)
                if(det!=''):
                    details.append(det)
                word=[]
            if(i=="'" and colom==0):
                colom+=1
            if(colom==1 and i!="'" and i!=',' and i!=' '):
                word.append(i)
        if(i==']'):
            break
    return details


@app.route('/',methods=['GET','POST'])
def index():
    return render_template('index.html')

@app.route('/signin',methods=['GET','POST'])
def signin():
    chk = ["Ngo", "Biogas", "Fertilizer"]
    if(request.method == "POST"):
        pas = request.form.get("logpass")
        name = request.form.get("logname")
        num = request.form.get("lognum")
        addr = request.form.get("logaddr")
        roll = request.form.get("roll")
        if(num == None):
            detail = coll.find_one({"Name": name, "password":pas})
            print(detail)
            if(detail != None):
                detail = list(detail.values())
                data = [name, pas]
                QRCodefile = "/static/qr.png"
                QRimage = qrcode.make(data)
                QRimage.save(os.getcwd() + QRCodefile)
                print("HIII")
                coll.find_one_and_update({"Name":name}, {"$set": {"QRcode": str(QRimage) }})
                print("BYEEE")
                session['uname']=name
                session['upas']=pas
                session['val']=detail[6]
                return redirect(url_for('location'))
            else:
                return render_template('signin.html', msg="Invalid login details!!")
        else:
            if(roll in chk):
                coll.insert_one({"Name": name ,"Number": num , "Address": addr ,"password": pas, "Roll":roll, "Recieve Count":"0", "Total Quantity":"0", "QRcode":"null", "Time": datetime.datetime.now(), "Activity":[] })
            elif(roll=="Houseold"):
                coll.insert_one({"Name": name ,"Number": num , "Address": addr ,"password": pas, "Roll":roll, "Redeem Points":"0", "Donation":"0", "Total Quantity":"0", "QRcode":"null", "Time": datetime.datetime.now(), "Activity":[] })
            else:
                coll.insert_one({"Name": name ,"Number": num , "Address": addr ,"password": pas, "Roll":roll, "Tax Reduction":"0", "Donation":"0", "Total Quantity":"0", "QRcode":"null", "Time": datetime.datetime.now(), "Activity":[] })

    return render_template('signin.html')



@app.route('/signinemp',methods=['GET','POST'])
def signinemp():
     if(request.method == "POST"):
        global loca
        name = request.form.get("empname")
        passw = request.form.get("emppass")
        loca = request.form.get("dropdown")
        session ['location'] = loca
        print(name,passw,loca)
        check = col.find_one({"name": name,"location":loca ,"password":passw})
        print(check)
        if(check != None):
            return redirect(url_for('worker'))
        else:
            return render_template('signinemp.html', msg="Invalid login details!!")
     return render_template('signinemp.html')


@app.route('/signinorg',methods=['GET','POST'])
def signinorg():
     if(request.method == "POST"):
        global loca
        name = request.form.get("orgname")
        passw = request.form.get("orgpass")
        print(name,passw)
        check = c.find_one({"name": name,"password":passw})
        print(check)
        if(check != None):
            return render_template('organizer.html')
        else:
            return render_template('signinorg.html', msg="Invalid login details!!")
     return render_template('signinorg.html')


@app.route('/receving',methods=['GET','POST'])
def receving():
     if(request.method == "POST"):
        food = request.form.get("food")
        loca=session['location']
        username = session['name']
        compoi = session['compoi']
        donate = session['donote']
        totaldontion = session['Total']
        print(food,loca)
        pre = col.find_one({"location":loca})['Quantity']
        col.find_one_and_update({"location":loca}, {"$set":{"Quantity": float(pre)+float(food) }})
        coll.find_one_and_update({"Name":username}, {"$set": {"Donation": int(donate)+1, "Total Quantity": float(totaldontion)+float(food), "Tax Reduction": float(compoi)+float(food)*3}})
        coll.find_one_and_update({"Name":username}, {"$push":{"Activity":{"quantity":food, "Time":datetime.datetime.now(), "Location":loca}}})
        flash("Donation Successfull !!")
        return redirect(url_for('worker'))


@app.route('/recieve',methods=['GET','POST'])
def recieve():
    if(request.method == "POST"):
        food = request.form.get('food')
        loca = session['location']
        store = col.find_one({"location":loca})
        store = list(store.values())
        username = session['name']
        rec = session['reccount']
        tot = session['totquant']

        col.find_one_and_update({"location":loca}, {"$set":{"Quantity": float(store[5])-float(food) }})
        coll.find_one_and_update({"Name":username}, {"$set": {"Recieve Count": int(rec)+1, "Total Quantity": float(tot)+float(food)}})
        coll.find_one_and_update({"Name":username}, {"$push":{"Activity":{"quantity":food, "Time":datetime.datetime.now(), "Location":loca}}})
        flash("Selected Successfully !!")
        return redirect(url_for('worker'))


@app.route('/worker',methods=['GET','POST'])
def worker():
    chk = ["Ngo", "Biogas", "Fertilizer"]
    loca = session['location']
    store = col.find_one({"location":loca})
    store = list(store.values())
    tes = store[4]

    print(tes)

    if(request.method=="POST"):
        value = request.form.get("hidden")
        details = algo(value)
        print(details)
        detail = coll.find_one({"Name": details[0], "password":details[1]})
        print(detail)
        info = list(detail.values())
        session['name'] = info[1]
        session['compoi'] = info[6]
        session['donote'] = info[7]
        session['Total'] = info[8]
        newdet = [info[1], info[5], info[6], info[7], info[8]]
        if(info[5] in chk):
            newdet2 = [info[1], info[2], info[3], info[5], info[6], info[7]]
            session['reccount']=info[6]
            session['totquant']=info[7]
            return render_template('worker.html', det = newdet2, deta=[], store=tes, conrole = info[5] )
        else:
            return render_template('worker.html', deta = newdet, det = [], store=tes)

    return render_template('worker.html', det=[], deta=[], store=tes)


@app.route('/location',methods=['GET','POST'])
def location():
    if(request.method == "POST"):
        name = session['uname']
        pas = session['upas']
        pre_val = session['val']
        detail = coll.find_one({"Name": name, "password":pas})
        detail = list(detail.values())
        if(detail[6] != pre_val):
            return render_template('success.html', comp = detail[5])
    return render_template('map.html')


@app.route('/success',methods=['GET','POST'])
def success():
    return render_template('success.html')


@app.route('/register',methods=['GET','POST'])
def register():
    if(request.method == 'POST'):
        firstn = request.form.get("fn")
        lastn = request.form.get("ln")
        mothern = request.form.get("mn")
        fathern = request.form.get("fan")
        add = request.form.get("add")
        gender = request.form.get("inlineRadioOptions")
        state = request.form.get("state")
        city = request.form.get("city")
        dob = request.form.get("dob")
        pin = request.form.get("pin")
        clien.insert_one({"FirstName": firstn ,"LastName": lastn , "MotherName": mothern ,"Fathername": fathern, "Address": add, "Gender":gender, "State": state, "city":city, "Date of Birth":dob, "Pincode": pin, "Time":datetime.datetime.now() ,"Activity":[]})
        data = [firstn, lastn, mothern, fathern, add, gender, state, city, dob, pin]
        QRCodefile = "client_qr.png"
        QRimage = qrcode.make(data)
        QRimage.save(QRCodefile)
        return redirect(url_for('worker'))


if __name__ == "__main__":
    app.run()


#
