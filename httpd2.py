import os
import sys
import pytz
import time
import json
import datetime 

from flask import Flask
from flask import request
from flask import jsonify
from flask_sqlalchemy import SQLAlchemy

from sqlalchemy.orm import sessionmaker
from pytz import timezone

app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

from models import *

class BadRequest(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv

@app.errorhandler(BadRequest)
def handle_bad_request(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response

@app.route('/', methods = ['POST'])
def main():
    messages = []
    try:
        jsn =  request.get_json()
    except ValueError:
        raise  BadRequest('Malformed json', status_code=400)
    print ("received request: " + str(jsn), file=sys.stderr)
    sn = jsn.get('sn')
    type = jsn.get('type')
    try:
        ctrl = db.session.query(Controller).filter(Controller.serial==sn, Controller.type==type).first()
    
        for msg_json in jsn['messages']:
            operation = msg_json.get('operation')
            req_id = msg_json.get('id')
            if operation == None:
               if msg_json.get('success')== 1:
                    print("ANSWER TO %d FROM CONTROLLER %d" % (req_id,sn),file=sys.stderr )
                    db.session.query(Task).filter(id==req_id).delete()
                    db.session.commit()
               else:
                    print("UNKNOWN ANSWER:\n%s" % (msg_json),file=sys.stderr)

            elif operation == 'power_on':
                print('CONTROLLER %d POWER ON' % sn,file=sys.stderr)
                fw = msg_json.get('fw')
                conn_fw = msg_json.get('conn_fw')
                active = msg_json.get('active')
                mode = msg_json.get('mode')
                if ctrl == None:
                    print('UNKNOWN CONTROLLER ADD TO BASE',file=sys.stderr)
                    controller = Controller(serial=sn,type=type, fw=fw, conn_fw=conn_fw,active=mode, last_conn=int(time.time())  )
                    db.session.add(controller)
                    db.session.commit()
                    ctrl =  db.session.query(Controller).filter(Controller.serial==sn, Controller.type==type).first()

                else:
                    controller = db.session.query(Controller).filter(Controller.serial==sn, Controller.type==type).first()
                    controller.fw = fw
                    controller.conn_fw = conn_fw
                    controller.mode = mode
                    controller.last_conn = int(time.time()),
                    db.session.commit()

                if active != ctrl.active:
                    messages.append(
                        dict (
                            id = '0',
                            operation = 'set_active',
                            active = ctrl.active,
                            online = '0'
                         )
                     )
                 
            elif operation == "ping":
                print("PING FROM CONTROLLER %d" % sn , file=sys.stderr)
                active = msg_json.get('active')
                mode = msg_json.get('mode')
                controller = db.session.query(Controller).filter(Controller.serial==sn, Controller.type==type).first()
                controller.mode = mode
                controller.last_conn = int(time.time())
                db.session.commit()
           
                if active != ctrl.active:
                    messages.append(
                        dict (
                            id='0',
                            operation='set_active',
                            active=ctrl.active
                        )
                    )
                  
            elif operation == "check_access":
                card = msg_json.get('card')
                reader = msg_json.get('reader')
                print("CHECK ACCESS FROM CONTROLLER %d [%s on %d]" % (sn,card,reader),file=sys.stderr)
                granted = 1
                messages.append(
                    dict(
                        id=req_id,
                        operation='check_access',
                        granted=granted
                     )
                )

            elif operation == "events":
                print("EVENTS FROM CONTROLLER %d" % sn, file=sys.stderr)
                tz = app.config.get('TZ')
                event_cnt = len(msg_json.get('events'))
                for event in msg_json.get('events'):
                    ev_time = pytz.timezone(tz).localize(datetime.datetime.strptime(event.get('time'), "%Y-%m-%d %H:%M:%S"))
                    e = Event( event=event.get('event'), flags=event.get('flag'),card = event.get('card'), time=ev_time)
                    db.session.add(e)
                db.session.commit()
                print("EVENT_SUCCESS: %d" % event_cnt, file=sys.stderr)
                messages.append(
                    dict(
                        id = req_id,
                        operation = 'events',
                        events_success = event_cnt
                    )
                 )
            else:
                print('UNKNOWN OERATION',file=sys.stderr)

        for task_jsn in db.session.query(Task.json).filter(Task.serial==sn, Task.type==type):
            task = json.loads(task_jsn['json'])
            task['id'] = task_jsn['id']
            messages.append(task)

        print ("reponse:"+ str (dict ( date=time.strftime("%Y-%m-%d %H:%M:%S"),interval=ctrl.interval, messages = messages )),file=sys.stderr)
        return json.dumps(
            dict (
                date=time.strftime("%Y-%m-%d %H:%M:%S"),
                interval=ctrl.interval,
                messages = messages
            )
        )
    except :
        raise  BadRequest('Genetal error', status_code=400)
    finally:
        db.session.close()
        