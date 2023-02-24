from flask import Flask
from flask_apscheduler import APScheduler
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

import os
# Flask APP
app = Flask(__name__)


app.config['UPLOAD_FOLDER']     = os.path.abspath(app.instance_path)
app.config['BASE_FOLDER']       = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    SCHEDULER_API_ENABLED = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(app.config['UPLOAD_FOLDER'], 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False



# Mail Server settings
app.config['MAIL_SERVER']       = 'smtp.mgmt.dpaor.org'
app.config['MAIL_PORT']         = 25
app.config['MAIL_USE_TLS']      = False
app.config['MAIL_USE_SSL']      = False

# E-Mail Sender
app.config['MAIL_SENDER']       = "dataportzlinuxbasisbetrieb@dataport.de"
# E-Mail Empfänger
app.config['MAIL_RECIPIENTS']   = ["dataportzlinuxbasisbetrieb@dataport.de"]

mail = Mail(app)
scheduler = APScheduler()
login = LoginManager(app)

# Schedular starten
scheduler.init_app(app)
from app import crontabber
scheduler.start()

#Konfig
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Flask Settings
app.config["SECRET_KEY"]        = "b2d0d27ef077658e274ef787c1002a814ab23b7485c734bb8b9d2fcf27000c1c"


# Zertifikatsmonitor Settings
# Ordnername
app.config['CERT']              = "certificates"
# Welche Daten dürfen als Zertifikatstyp hochgeladen werden
app.config['UPLOAD_EXTENSIONS'] = ['p7b']

# Extfile Upload Format Endungen
app.config['EXTUPLOAD_EXT']     = ['conf','ext']
# Keyupload Upload Format Endungen
app.config['KEYUPLOAD_EXT']     = ['pem','req','key']
# Zertifikatsrequest Upload Format Endungen
app.config['REQUPLOAD_EXT']     = ['pem','req']

# Bei der Key-Generierung die maximale Zertifikatslänge einstellung
app.config['MAXLENGH']          = 9
# Am wann hingewiesen wird, dass ein Zertifikat abläuft
app.config['WARNINGDAYS']       = 60

# Dateinamen der Zertifikate und deren zugehörigen Daten
# Privater Key
app.config['PRIVATEKEY']        = "private.key"
# Zertifikatsrequest
app.config['CSRPEM']            = "csr.req"
# Zertifikatsrequest-Konfig
app.config['CSREXT']            = "csr.ext"
# Zertifikatsfile in p7b Format
app.config['CRTP7B']            = "cert.p7b"
# Zertifikatsfile in pem Format
app.config['CRTPEM']            = "cert.pem"
# DSA-Param file 
app.config['DSAPARAM']          = "dsaparam.pem"

#Dateinamen der Hilfsdaten
app.config['EXPIRE']            = "expire.txt"
app.config['HELPFILE']          = "helper.txt"
app.config['CNname']            = "name.txt"
app.config['EMAILFILE']         = "email.txt"
app.config['DNSFILE']           = "DNS.txt"
app.config['VERIFIY']           = "verify.txt"
app.config['ISINFO']            = "is_informed.txt"





app.debug = True

from app import routes, routes_down, routes_show, forms