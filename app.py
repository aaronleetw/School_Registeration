from flask import *
import pyrebase
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from collections import OrderedDict

app = Flask(__name__, static_url_path='/static')
firebaseConfig = {
    "apiKey": "AIzaSyDmNQPA1B_KqPc1pk0O-cvrNTTl95wYJQg",
    "authDomain": "enter-school-9298e.firebaseapp.com",
    "databaseURL": "https://enter-school-9298e-default-rtdb.firebaseio.com",
    "projectId": "enter-school-9298e",
    "storageBucket": "enter-school-9298e.appspot.com",
    "messagingSenderId": "57868613354",
    "appId": "1:57868613354:web:107d8ca011108a483c0993",
    "measurementId": "G-Z3BBK6J19Q"
}
firebase = pyrebase.initialize_app(firebaseConfig)
db = firebase.database()


def send_email(to, subject, html_content):
    message = Mail(
        from_email='system@em249.enter.aaronlee.tech',
        to_emails=to,
        subject=subject,
        html_content=html_content + "<hr>若你還沒有選擇進校時間，請至 <a href=\"http://enter.aaronlee.tech/\"> enter.aaronlee.tech </a> <br> 這是一封自動產生的信件，請勿回覆")
    try:
        sg = SendGridAPIClient(
            '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')
        sg.send(message)
    except Exception as e:
        print(e)


@ app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        return render_template('login.html', failed=False)
    else:
        number = request.form['number']
        studID = request.form['studID']
        if (str(db.child("Person").child(number).child("stud_ID").get().val()) == studID):
            if (db.child("Person").child(number).child("status").get().val() == "unk"):
                return render_template('newsubmit.html', number=number, time1=db.child('result').child("1000").get().val(), time2=db.child('result').child("1030").get().val())
            else:
                data = db.child("Person").child(number).get().val()
                return render_template('viewres.html', data=data, number=number)
        else:
            return render_template('login.html', failed=True)


@ app.route('/newsubmit', methods=['POST'])
def newsubmit():
    typeO = request.form['typeO']
    number = request.form['number']
    if (typeO == 'self-pickup'):
        time = request.form['time']
        if (time == 'early'):
            curr = db.child("result").child("1000").get().val() + 1
            db.child("result").child("1000").set(curr)
            db.child("Person").child(number).child("time").set(time)
            send_email(str(db.child("Person").child(number).child("stud_ID").get().val(
            )) + "@st.fhjh.tp.edu.tw", "確認信", "您剛剛在八平學生進校登記系統登記在 8/11 星期三 10:00 ~ 10:30 自行拿取。請勿遲到！<hr>請記得攜帶註冊費繳費收據，紙本或電子檔均可")
        elif (time == 'later'):
            curr = db.child("result").child("1030").get().val() + 1
            db.child("result").child("1030").set(curr)
            db.child("Person").child(number).child("time").set(time)
            send_email(str(db.child("Person").child(number).child("stud_ID").get().val(
            )) + "@st.fhjh.tp.edu.tw", "確認信", "您剛剛在八平學生進校登記系統登記在 8/11 星期三 10:30 ~ 11:00 自行拿取。請勿遲到！<hr>請記得攜帶註冊費繳費收據，紙本或電子檔均可")
        db.child("Person").child(number).child("status").set("self-pickup")
    elif (typeO == 'other-pickup'):
        helper = request.form['helper']
        db.child("Person").child(number).child("status").set("other-pickup")
        db.child("Person").child(number).child("helper").set(int(helper))
        db.child("Person").child(int(helper)).child(
            "needToHelp").child(number).set(0)
        send_email(str(db.child("Person").child(number).child("stud_ID").get().val(
        )) + "@st.fhjh.tp.edu.tw", "確認信", "您剛剛在八平學生進校登記系統登記在讓 " + helper + "為代領人。請務必和代領者溝通！<br>重要：請將繳費證明傳給那位幫忙拿的同學!! (紙本或電子檔均可)")
        send_email(str(db.child("Person").child(int(helper)).child("stud_ID").get().val(
        )) + "@st.fhjh.tp.edu.tw", "委託代領", "剛剛 "+str(number)+"號同學 在八平學生進校登記系統登記你為代領人。請記得幫忙代領！")
    data = db.child("Person").child(number).get().val()
    return render_template('viewres.html', data=data, number=number)


@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'GET':
        return render_template('adminlogin.html', failed=False)
    password = request.form['password']
    if password == 'detective':
        early = OrderedDict()
        late = OrderedDict()
        other = OrderedDict()
        nosubmit = OrderedDict()
        for i in range(1, 35):
            d = db.child("Person").child(i).get().val()
            if (d['status'] == 'self-pickup'):
                if (d['time'] == 'early'):
                    early[i] = d
                elif (d['time'] == 'later'):
                    late[i] = d
            elif (d['status'] == 'other-pickup'):
                other[i] = d
            elif (d['status'] == 'unk'):
                nosubmit[i] = d
        return render_template('admin.html', early=early, late=late, other=other, nosubmit=nosubmit, password=password)
    else:
        return render_template('adminlogin.html', failed=True)


@app.route('/admin/addnote', methods=['POST'])
def addnote():
    number = request.form['number']
    note = request.form['note']
    password = request.form['password']
    db.child("Person").child(number).child("note").set(note)
    return render_template('showsucc.html', password=password)


if __name__ == '__main__':
    app.run(debug=True)
