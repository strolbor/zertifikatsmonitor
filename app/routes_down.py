from flask.helpers import send_from_directory, url_for
from flask import redirect, render_template,request, abort
import os
from app import opensslcmd, helper, app,helper


@app.route('/ctl/delete/<path:speicherort>')
def ctldelete(speicherort):
    """Hiermit wird ein Speicherort eines Zertifikats gelöscht"""
    path = os.path.join(app.config['UPLOAD_FOLDER'],app.config['CERT'],speicherort)
    mode =  request.args.get('mode', 0, type=int)
    # Ordner löschen
    helper.deleteFct(path=path,mode=1)
    return redirect(url_for('listserver',mode=mode))

# Send from Direcktory
@app.route("/downloader/<path:file>")
def downloader(file):
    """Hiermit wird eine Datei aus dem css/ Ordner gesendet"""
    return send_from_directory(os.path.join(app.config['BASE_FOLDER'],"css"),file,as_attachment=False)

@app.route("/download/<path:ordner>/<path:filename>")
def downctl(ordner,filename):
    """Hiermit darf eine Datei, außer der private Schlüssel, gedownloadet werden"""
    mode =  request.args.get('mode', 0, type=int)
    path = os.path.join(app.config['UPLOAD_FOLDER'],app.config['CERT'],ordner)
    paths = os.path.join(path,filename)
    #if filename == app.config['PRIVATEKEY']:
    #    abort(403)
    
    if mode == 1:
         return send_from_directory(path,filename,as_attachment=True)
    else:
        array = []
        try:
            for line in open(paths,"r"):
                array.append(line)
        except FileNotFoundError:
            abort(404)

        return render_template('for.html',array=array)