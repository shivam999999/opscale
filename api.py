from flask import Flask,request,jsonify
from flask_sqlalchemy import SQLAlchemy
import re
import dns.resolver
import socket
import smtplib
from dns.resolver import NXDOMAIN
from celery_example import make_celery

app = Flask(__name__)

app.config['SECRET_KEY'] = 'opscale'
app.config['CELERY_BROKER_URL'] = 'amqp://localhost//'
app.config['CELERY_BACKEND'] = 'db+sqlite:///site.db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'

celery = make_celery(app)
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
    try:
            data = request.get_json()
    except:
            return jsonify({'status':'Invalid Json Entry'})

    try:

            eymail_id = data['email_id']
            print(eymail_id)
            try:
                emails = Echeck.query.all()
                for email in emails:
                    if email.email_id == eymail_id:
                        return jsonify({'status':'already exists'})
            except:
                return jsonify({'status':'server retrieving error'})
    except:
            return jsonify({'Status':'invalid key'})

    match = re.match('^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$',eymail_id)

    if match == None:
            output = 'bad'
            return jsonify({'email_syntax':output})



    strList = eymail_id.split('@')
    try:

            records = dns.resolver.query(str(strList[1]), 'MX')
    except NXDOMAIN :
            return jsonify({'DNS_status':'DNS does not exists'})
    except:
            return jsonify({'status':'wrong domain'})
    mxRecord = records[0].exchange
    mxRecord = str(mxRecord)

    host = socket.gethostname()

    server = smtplib.SMTP()
    server.set_debuglevel(0)

    try:
            server.connect(mxRecord)
            server.helo(host)


    except:

            return jsonify({'status':'the connection closed unexpectedly'})

    server.mail('me@domain.com')
    code, message = server.rcpt(str(eymail_id))
    server.quit()

    if code != 250:
	       return jsonify({'status':'Oops!! it does not exists'})
    else:

        insert.delay(data)
        return jsonify({'status':'Sent Async request to insert email into database '})

@celery.task(name='celery_example.insert')
def insert(data):

    new_id = Echeck(email_id=data['email_id'])
    db.session.add(new_id)
    db.session.commit()
    #return jsonify({'status':'Hooray!!it exists'})


if __name__=='__main__':
    app.run(debug=True,port=8800)
