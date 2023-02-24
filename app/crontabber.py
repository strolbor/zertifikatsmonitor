from app import app, helper, opensslcmd,mail
from flask_mail import Message
import os
import datetime

# Schedular
def scheduled_task(task_id):
    """Diese Funktion steuert den automatischen Versand der E-Mail"""
    helper.writeLines("lstcron.txt",'Task {} running iteration {}'.format(task_id, datetime.datetime.now()))
    app.app_context()
    path = os.path.join(app.config['UPLOAD_FOLDER'],app.config['CERT'])
    helper.createFolderIfNotExists(path)
    dirList = os.listdir(path)
    #array = opensslcmd.alerting(dirList,path,0)
    array = opensslcmd.alerting(dirList,path,1)
    with app.app_context():
        msg = Message ("Zertifikatsmonitor: Drohender Ablauf von Zertifikaten",sender=app.config['MAIL_SENDER'] ,recipients=app.config['MAIL_RECIPIENTS'])
        stringc = ""
        for entry in array:
            stringc = stringc + "\n" + str(entry)
        msg.body = stringc
        if len(array) > 0:
            mail.send(msg)
            print(">> E-Mail gesendet")
            return 0

    

#app.apscheduler.add_job(func=scheduled_task, trigger='interval',minutes=1, args=[1], id='j')
app.apscheduler.add_job(func=scheduled_task, trigger='cron',hour=0,minute=0,args=[2],id='k')
#scheduler.start()
print("[API] Automated Task init")