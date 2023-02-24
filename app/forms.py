
from flask_wtf import FlaskForm
from flask_wtf.file import FileField
from wtforms import SubmitField
from wtforms.fields.choices import SelectField
from wtforms.fields.simple import PasswordField, StringField
from wtforms.validators import DataRequired
from app import app

class certupload(FlaskForm):
    """Mit diesen Formularr kann ein p7b Zertifikat hochgeladen werden."""
    Speicherort     = SelectField("Speicherort des Zertifikats")
    certupload      = FileField('Zertifikat in p7b hochladen',validators=[DataRequired()])
    submit          = SubmitField("Hochladen")

class certcreate(FlaskForm):
    """Mit hilfe dieses Formular kann eine Zertifikat-Request erstellt werden."""
    # Server name wird als Ordnername verwendet
    #Speicherort     = SelectField("Speicherort des Zertifikats")
    nameinput       = StringField("Name des neuen Speicherort*",validators=[DataRequired()])
    #entscheidung    = SelectField("Darf das Programm existierende Daten überschreiben?",choices=["Nein","Ja"])#,validators=[DataRequired()])
    
    # Keylange
    keylenga = []
    for i in range(4,app.config['MAXLENGH']):
        keylenga.append(i*1024)
    keylengh        = SelectField("Länge des Keys",choices=keylenga)

    keytyp          = SelectField("Typ des Schlüssels",choices=["RSA","DSA"])

    # CSR Daten
    C               = StringField("Land (C)",default="DE")
    ST              = StringField("Bundesland (ST)",default="Bremen")
    L               = StringField("Land (L)",default="Bremen")
    O               = StringField("Organisation (O)",default="Dataport")
    OU              = StringField("Organisations Einheit (OU)",default="System Z")
    CN              = StringField("Allgeminer Name (CN)*",validators=[DataRequired()])
    emailAdress     = StringField("E-Mail (email)*",default="dataportzlinuxbasisbetrieb@dataport.de",validators=[DataRequired()])

    # Domains
    DNS             = StringField("DNS (mit ',' getrennt)*",validators=[DataRequired()])
    submit          = SubmitField("Erstellen")

class importer(FlaskForm):
    """Mit diesen Formular kann ein bestehendes Zertifikat mit Key, Request, conf hochgeladen werden."""
    Speicherort     = StringField("Name des neuen Speicherort")
    keyupload       = FileField('Private-Key (pem,key)  hochladen')
    requpload       = FileField('Request (pem, req) hochladen')
    certupload      = FileField('Zertifikat (p7b) hochladen')
    extupload       = FileField('Zertifikat-Konfig (ext, conf)')
    submit          = SubmitField("Hochladen")

class enterpw(FlaskForm):
    passworde       = PasswordField("Passwort eingeben.")
    submit          = SubmitField("Eingabe")

class enterlogin(FlaskForm):
    username        = StringField("Nutzer eingaben.")
    password        = PasswordField("Passwort eingeben.")
    submit          = SubmitField("Login")

class changepw(FlaskForm):
    passwordold       = PasswordField("Das alte Passwort eingeben.")
    passwordnew       = PasswordField("Das neue Passwort eingeben.")
    passwordnew2      = PasswordField("Das neue Passwort Passwort bestätigen.")
    submit            = SubmitField("Eingabe")

class newuser(FlaskForm):
    username        = StringField("Nutzer eingaben.")
    password        = PasswordField("Passwort eingeben.")
    password2       = PasswordField("Passwort eingeben.")
    submit          = SubmitField("Nutzerkonto erstellen")