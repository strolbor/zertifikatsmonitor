from flask.helpers import  url_for
from flask import redirect, render_template,request, flash
import os

from app import opensslcmd, helper, app, forms,helper

@app.route('/index',methods=['GET','POST'])
@app.route('/',methods=['GET','POST'])
def listserver():
    """Alle Zertifikate auflisten. """
    mode =  request.args.get('mode', 0, type=int)
    path = os.path.join(app.config['UPLOAD_FOLDER'],app.config['CERT'])
    print(path)
    array = []
    if not os.path.exists(path):
        # Es wurden keine Server gefunden.
        flash('Fehler: Kein Server gefunden!')
    else:
        # Alle Ordner auflisten
        dirList = os.listdir(path)
        array = opensslcmd.listserver(dirList,path)
    return render_template('listserver.html',serverlist=array,mode=mode)



@app.route("/ablauf")
def listalerts():
    """Alle Zertifikate, die ablaufen werden, auflisten. """
    mode =  request.args.get('mode', 0, type=int)
    path = os.path.join(app.config['UPLOAD_FOLDER'],app.config['CERT'])
    if not os.path.exists(path):
        # Es wurden keine Server gefunden.
        flash('Fehler: Kein Server gefunden!')
        return render_template('listserver.html',serverlist=[])
    # Alle Ordner auflisten
    dirList = os.listdir(path)
    alerting = opensslcmd.alerting(dirList,path,0)
    return render_template('listserver.html',serverlist=alerting,Aler=True)

@app.route("/alerting")
def alert():
    """Hiermit wird die Seite des Alertings erstellt als einfache Liste"""
    
    path = os.path.join(app.config['UPLOAD_FOLDER'],app.config['CERT'])
    helper.createFolderIfNotExists(path)
    dirList = os.listdir(path)
    #array = opensslcmd.alerting(dirList,path,0)
    array = opensslcmd.alerting(dirList,path,1)
    opensslcmd.sendmail(array,"Drohender Ablauf von Zertifikaten")
    return render_template('for.html',array=array)



@app.route('/upload/p7b',methods=['GET','POST'])
def pbupload():
    """Zertifikat hochlade Funktionen"""
    mode =  request.args.get('mode', 0, type=int)
    ort =  request.args.get('ort', "0", type=str)
    form = forms.certupload()
    print(ort)
    if ort != "0":
        form.Speicherort.data = ort
    
    # Path findeun und die Ordner auflsiten
    path1 = os.path.join(app.config['UPLOAD_FOLDER'],app.config['CERT'])
    helper.createFolderIfNotExists(path1)
    form.Speicherort.choices = os.listdir(os.path.join(path1))

    # Formular wurde abgesendet
    if form.validate_on_submit():
        # Neuen Path mit Speicherort
        path2 = os.path.join(path1,form.Speicherort.data)
        ort = form.Speicherort.data
        status = helper.save("certupload",request.files,path2,app.config['CRTP7B'],app.config['UPLOAD_EXTENSIONS'])
        if status == "not-allowed":
            flash("Fehler: Es wurde keine .p7b Datei ausgewählt.")
        elif status == "A" or status == "B":
            flash("Fehler: Es wurde keine Datei hochgeladen.")
        else:
            flash("Datei erfolgreich gespeichert!")
            status = opensslcmd.convertCERT(path2,request.files["certupload"].filename)
            pathfile = os.path.join(path2,app.config['ISINFO'])
            if os.path.exists(pathfile):
                os.remove(pathfile)
            if status != 0:
                flash("Fehler: Fehler in der Konvertierung. Bitte erneut versuchen!")
        print("Ort",ort)
        if ort == "0":
            return redirect(url_for('pbupload'))
        else:
            return redirect(url_for('pbupload',ort=form.Speicherort.data))
    print("Ort draußen:",ort)
    return render_template('p7b.html',form=form)

@app.route("/ctl/csrimport",methods=['GET','POST'])
def csrimport():
    """Hiermit wird das Formular um alle Cert-Bestandteile zu importieren."""
    form = forms.importer()
    # Übersicht der existierende Ordner
    path1 = os.path.join(app.config['UPLOAD_FOLDER'],app.config['CERT'])
    helper.createFolderIfNotExists(path1)
    if form.validate_on_submit():
        path2 = os.path.join(path1,form.Speicherort.data)
        # Ordner erstellen
        if os.path.exists(path2):
            # Ordner existiert schon
            flash("Fehler: Ordner existiert schon. Upload wurde abgebrochen.")
        else:
            # Ordner exisitert nicht
            os.makedirs(path2)

            file4 = helper.save("extupload",request.files,path2,app.config['CSREXT'],app.config['EXTUPLOAD_EXT'])
            if file4 == "A" or file4 == "B":
                pass
            else:
                flash("Extfile wurde erfolgreich hochgeladen.")
            
            # Private Key Upload
            file1 = helper.save("keyupload",request.files,path2,app.config['PRIVATEKEY'],app.config['KEYUPLOAD_EXT'])
            if file1 == "A" or file1 == "B":
                pass
            else: 
                flash("Key wurde erfolgreich hochgeladen.")
            # CSR upload
            file2 = helper.save("requpload",request.files,path2,app.config['CSRPEM'],app.config['REQUPLOAD_EXT'])
            if file2 == "A" or file2 == "B":
                pass
            else:
                flash("Requests wurde erfolgreich hochgeladen.")
                opensslcmd.verifiyREQ(path2)
                # Daten erhalten aus Zertifikatsrequest
                opensslcmd.gettingData1(path2,1)

            # CRT in p7b upload
            print(request.files["certupload"])
            file3 = helper.save("certupload",request.files,path2,app.config['CRTP7B'],app.config['UPLOAD_EXTENSIONS'])
            print("file3",file3)
            if file3 == "A" or file3 == "B":
                print("Kein File im Feld file3.")
                pass
            else:
                if file3 == "not-allowed":
                    flash("Fehler: Es wurde kein Zertifikat im .p7b Dateiformat ausgewählt.")
                else:
                    status = opensslcmd.convertCERT(path2,request.files["certupload"].filename)
                    if status != 0:
                        flash("Fehler: Fehler in der Konvertierung. Bitte erneut versuchen!")
                    else:
                        flash("Cert-Konvertierung abgeschlossen.")
            return redirect(url_for('csrimport'))

    return render_template('csr_import.html',form=form)
 

@app.route('/generate/certificate',methods=['GET','POST'])
def createcsr():
    """ Hiermit wird ein Cert-Request erstellt, inklusive einen Privates Keys """
    mode =  request.args.get('mode', 0, type=int)
    
    form = forms.certcreate()
    path = os.path.join(app.config['UPLOAD_FOLDER'],app.config['CERT'])
    helper.createFolderIfNotExists(path)
    ldir = os.listdir(path)
    
    if request.method == 'POST':
        if form.validate_on_submit():
            # Falls Ordner existiert breche Import ab
            name = str(form.nameinput.data)
            if os.path.exists(os.path.join(path,name)):
                flash("Fehler: Ordner exisstiert schon! - Import wurde abgebrochen.")
            else:
                if name.endswith(" "):
                    name = name[:len(name)-1]
                    form.nameinput.data = name
                name = name.replace(" ","-")
                name = name.replace("*","")

                # Wir bilden den Upload Folder
                path = os.path.join(app.config['UPLOAD_FOLDER'],app.config['CERT'],name)
                os.makedirs(path)

                #Key Generieren
                s1 = opensslcmd.generateKeys(path,form.keylengh.data,form.keytyp.data)

                #CSR erstellen anhand des Templates (mit Jinja2)
                s2 = opensslcmd.generateCSR(form.C.data,form.ST.data,form.L.data,form.O.data,form.OU.data,form.DNS.data,form.CN.data,\
                    form.emailAdress.data,path)

                helper.writeLine(os.path.join(path,app.config['DNSFILE']),form.DNS.data)
                
                #CN namen schreiben
                helper.writeLine(os.path.join(path,app.config['CNname']),form.CN.data)
                if s1 == 0 and s2 == 0:
                    flash("Generierung wurde fertig gestellt.")
                else:
                    flash("Fehler: Generierung fehlgeschlagen! openSSL wurde nicht gefunden.")
        else:
            flash("Fehler: Generierung fehlgeschlagen!")
    return render_template('createcsr.html',form=form)
    




