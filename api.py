from flask import Flask,request,jsonify
from flask_sqlalchemy import SQLAlchemy
import re
import dns.resolver
import socket
import smtplib

app = Flask(__name__)

app.config['SECRET_KEY'] = 'opscale'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'


db = SQLAlchemy(app)

class Echeck(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    email_id = db.Column(db.String(50),unique=True)

    def __repr__(self):
        return f"Echeck('{self.email_id}')"


@app.route('/email',methods=['GET'])
def get_all_id():
    emails = Echeck.query.all()
    output = []
    for email in emails:
        email_data = {}
        email_data['email_id'] = email.email_id
        output.append(email_data)
    return jsonify({'email_id':output})

@app.route('/email',methods=['POST'])
def prompte_validity():
    data = request.get_json()
    eymail_id = data['email_id']
    match = re.match('^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$',eymail_id)

    if match == None:
            output = 'bad'
            return jsonify({'email_syntax':output})


    strList = eymail_id.split('@')
    records = dns.resolver.query(str(strList[1]), 'MX')
    mxRecord = records[0].exchange
    mxRecord = str(mxRecord)

    host = socket.gethostname()


    server = smtplib.SMTP()
    server.set_debuglevel(0)


    server.connect(mxRecord)
    server.helo(host)
    server.mail('me@domain.com')
    code, message = server.rcpt(str(eymail_id))
    server.quit()

    if code != 250:
	       return jsonify({'status':'Oops!! it does not exists'})
    else:
            new_id = Echeck(email_id=data['email_id'])
            db.session.add(new_id)
            db.session.commit()
            return jsonify({'status':'Hooray!!it exists'})

if __name__=='__main__':
    app.run(debug=True,port=8000)
