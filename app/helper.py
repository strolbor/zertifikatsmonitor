from jinja2 import Template
import os

from werkzeug.exceptions import abort
from werkzeug.utils import secure_filename
from flask import request

# Function creating from template files.
def write_file_from_template(template_path, output_name, template_variables, output_directory):
    """Mithilfe dieser Funktion, wird die Konfig erstellt."""
    template_read = open(template_path).read()
    template = Template(template_read)
    rendered = template.render(template_variables)
    output_path = os.path.join(output_directory, output_name)
    print("Output-Path:",output_path)
    output_file = open(output_path, 'w')
    output_file.write(rendered)
    output_file.close()
    print('Created file at  %s' % output_path)
    return output_path

def createFolderIfNotExists(name):
    """Zum erstellen eines Ordners"""
    if not os.path.exists(name):
        os.makedirs(name)

def deleteFct(path,mode):
    """ Lösch Funktion:
    0 => File löschen
    1 => Ordner löschen"""
    print("Path to delete:",path)
    if os.path.exists(path):
        if mode == 0:
            # File löschen
            os.remove(path)
        else:
            ldir = os.listdir(path)
            for entry in ldir:
                os.remove(os.path.join(path,entry))
            os.rmdir(path)
        print("removed")

def save(feldname, rfiles ,path,dateiname, allowsFiles) -> str:
    """Datei Speichern unter path"""
    if feldname not in rfiles:
        """ Datei wurde garnicht erst hochgeladen"""
        return "A"
    file = rfiles[feldname]
    if file.filename == '':
        """ Es wurde kein Datei genommen."""
        return "B"
    if file:
        """ Datei ist vorhanden"""
        file = request.files[feldname]
        filename = secure_filename(dateiname)#"cert.p7b")# file.filename)
        fileext = secure_filename(file.filename).split(".")
        if fileext[1] not in allowsFiles:
            return "not-allowed"
        paths = os.path.join(path,filename)
        file.save(paths)
        return paths

def writeLine(filename,content : str):
    """Mit dieser Funktion wird eine Zeile geschrieben"""
    file = open(filename,"w")
    file.write(content)
    file.flush()
    file.close

def writeLines(filename,contentarray : list):
    """Mit dieser Funktion können mehrere Funktionen geschrieben werden"""
    file = open(filename,"w")
    #file.writelines(contentarray)
    for content in contentarray:
        file.write(content+"\n")
    file.flush()
    file.close

def readLine(filename):
    """Mit dieser Funktion wird eine Line geschrieben."""
    file = open(filename,"r")
    string = file.readline()
    file.close()
    return string