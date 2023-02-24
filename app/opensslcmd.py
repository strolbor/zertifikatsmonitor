import os

from app import helper 

import datetime as dt
from datetime import datetime
from app import mail, app
from flask_mail import Message
import re # RegEx

alertString = "Das Zertifikat (CN={}, DNS={}) im Speicherort {} laeuft am {} ab."

class certentry():
    """Ein Eintrag in der Liste."""
    global alertString
    expiredate = datetime.now()
    def __init__(self,name,expiredate,CN,DNS) -> None:
        self.name = name
        self.expiredate = expiredate
        self.CN = CN
        self.DNS = DNS
    def __repr__(self) -> str:
        return alertString.format(self.CN,self.DNS,self.name,self.expiredate)
    
    def get(self):
        if self.expiredate == "":
            return 0
        else:
            return (int(self.expiredate.timestamp()))


def generateKeys(path,keylen,keytype):
    """Wir generieren hiermit unsere Keys"""
    privkeyname = app.config['PRIVATEKEY']
    #Key generieren
    outputkey = os.path.join(path,privkeyname)
    outputpar = os.path.join(path,app.config['DSAPARAM'])
    # RSA
    print("Keytype: ",keytype)
    if keytype == "RSA":
        cmd = f"openssl genrsa -out \"{outputkey}\" {keylen}"
    elif keytype == "DSA":
        #openssl dsaparam -out dsaparam.pem 2048
        cmdparm = f"openssl dsaparam -out \"{outputpar}\" {keylen}"
        status = os.system(cmdparm)
        #openssl gendsa -out dsaprivkey.pem dsaparam.pem
        cmd = f"openssl gendsa -out \"{outputkey}\" \"{outputpar}\""
    print(cmd)
    status = os.system(cmd)
    return status

def generateCSR(Cs,STs,Ls,Os,OUs,DNSlist,CNSs,emails,path):
    """ Wir generieren den Request hier"""
    csrpem = app.config['CSRPEM']
    csrext = app.config['CSREXT']
    privkey = app.config['PRIVATEKEY']


    #1. Schritt Konfig erstellung
    journal_output = helper.write_file_from_template(
            template_path=os.path.join("app","cert","csr.t.ext"),
            output_name=csrext,
            template_variables={'C':Cs, 
                'ST':STs, 
                'L':Ls,
                'O':Os,
                'OU':OUs,
                'DNSlist': DNSlist.split(","),
                'CN':CNSs,
                'email': emails},
            output_directory=path)
    # 2. Schritt CSR-Request erstellen
    # Erstellung eines CSR
    cmd = f"openssl req -new -out \"{os.path.join(path,csrpem)}\" -key \"{os.path.join(path,privkey)}\" -config \"{os.path.join(path,csrext)}\""
    print(cmd)
    status = os.system(cmd)

    # Überprüfung des graden erstellten CSR
    verifiyREQ(path)
    return status

def verifiyREQ(path):
    """Mithilfe dieser Funktion wird OS-Seitig die Requests verifiziert."""
    cmd = f"openssl req -text -noout -verify -in \"{os.path.join(path,app.config['CSRPEM'])}\" > \"{os.path.join(path,app.config['VERIFIY'])}\""
    print(cmd)
    status = os.system(cmd)
    return status

def convertCERT(path):
    """Hiermit konvertieren, wir das p7b-Zertifkat in ein pem-Format"""
    certpem = app.config['CRTPEM']
    p7bfile = app.config['CRTP7B']
    # Wir konvertieren zuerst das Zertifikat in PEM File
    # Damit der Apache/NGINX/Webserver es lesen kann
    #cmd = f"openssl pkcs7 -inform DER -outform PEM -in {os.path.join(path,p7bfile)} -print_certs -out {os.path.join(path,certpem)}"
    # Der Confluence Befehl funktioniert nicht unter Windows, also inform und outform weg nehmen, dann funktioniert es
    
    #kaputteer CMD
    #cmd = f"openssl pkcs7 -in \"{os.path.join(path,p7bfile)}\" -print_certs -out \"{os.path.join(path,certpem)}\""
    #neuer CMD aus Confluence
    cmd = f"openssl pkcs7 -inform DER -outform PEM -in \"{os.path.join(path,p7bfile)}\" -print_certs > \"{os.path.join(path,certpem)}\""
    print(cmd)
    statusconvertierung = os.system(cmd)

    gettingData1(path,0)
    
    return statusconvertierung

def gettingData1(path,mode):
    """Daten aus (0) Zertifikat bzw. (1) CSR erhalten"""
    csrpem = app.config['CSRPEM']
    expireN = app.config['EXPIRE']
    helpfilename = app.config['HELPFILE']
    CNn = app.config['CNname']
    dnsfile = app.config['DNSFILE']
    certpem = app.config['CRTPEM']
    certp7b = app.config['CRTP7B']
    # Die Expire Date
    helpfile =os.path.join(path,helpfilename)
    #cmd = f"openssl x509 -noout -text -in os.path.join(path,certpem) | head -n 15 | grep \"Not After\" > {helpfile}"
    # Der obengenannte Befehl funktioniert nur unter Linux
    if mode == 0:
        # Mode == 0 => zertifikat
        cmd = f"openssl x509 -noout -text -in \"{os.path.join(path,certpem)}\" > \"{helpfile}\""
    elif mode == 1:
        cmd = f"openssl req -text -noout -verify -in \"{os.path.join(path,csrpem)}\" > \"{helpfile}\""
    print(cmd)
    os.system(cmd)

    helpfile = open(helpfile,"r")
    for line in helpfile:
        # Regular Expression:
        #zum finden des Expiredate des Certs
        findinfoExpire = re.search("Not After : ",line)
            
        if findinfoExpire is not None:
            startpos = findinfoExpire.span()[1]
            # Jul 21 07:37:01 2022
            #  %b %d %H:%M:%S %Y
            # Wir lesen zuerst das Datum aus der Datei und konvertieren es zum Datetime Objekt
            expiredate = datetime.strptime(line[startpos:-5],"%b %d %H:%M:%S %Y")
            # Dann konvertieren das eine Format in das andere Format, dass ich benutze
            expire2 = expiredate = datetime.strftime(expiredate,"%Y-%m-%d")
            # Wir speichern das neue Format ab.
            helper.writeLine(os.path.join(path,expireN),expire2)

        #zum finden des Subjects Name
        findinfoCN = re.search("Subject:",line)
        if findinfoCN is not None:
            startpos = findinfoCN.span()[1]
            newLine = line[startpos:]
            # Wir nehmen an, wenn der Subject gefunden ist, dass auch der CN in der Line drin steht
            findinfoL = re.search("CN =",newLine)
            startpos = findinfoL.span()[1]
            # Wir schreiben den CN als Extra Datei, um ihn schneller auszulesen zu können.
            helper.writeLine(os.path.join(path,CNn),newLine[startpos:].split(",")[0])
        
        # DNS finden
        dnsar = ""
        findinfoDNS = re.search("DNS:",line)
        
        if findinfoDNS is not None:
            print(findinfoDNS)
            stri = findinfoDNS.string[findinfoDNS.span()[1]:]
            arr = stri.split(", DNS:")
            for entry in arr:
                entry.replace(",","")
                entry.replace(" ","")
                entry.replace("\n","")
                dnsar = dnsar + entry + ","
            
            helper.writeLine(os.path.join(path,dnsfile),dnsar)
            break
            # Der erste DNS ist Subjectr
            # der zweite DNS ist Issuer
            # den brauche ich nciht
    helpfile.close()

    #Helpfile loeschen, um Platz zu sparen.
    helper.deleteFct(path=os.path.join(path,helpfilename),mode=0)


def listserver(dirList :list, path):
    """Hiermit werden alle Zertifikate aufgelistet"""
    DNSfile = app.config['DNSFILE']
    expireName = app.config['EXPIRE']
    CNn = app.config['CNname']

    array = []
    # Wir listen alle Ordner im Ordner der Zertifikate auf
    for entry in dirList:
        try:
            # Wir lesen die Expire.txt Datei jeden Unterordners
            expireString = helper.readLine(os.path.join(path,entry,expireName))
            date = datetime.strptime(expireString,"%Y-%m-%d")
        except FileNotFoundError:
            date = ""
        try:
            # Wir versuchen die CN zu lesen
            CN = helper.readLine(os.path.join(path,entry,CNn))
        except FileNotFoundError:
            CN = ""
        try:
            # Wir lesen die DNS Liste ein
            DNS = helper.readLine(os.path.join(path,entry,DNSfile))
        except FileNotFoundError:
            DNS = ""
        # Entry = Speicherort
        # date = Ablaufdatum
        # CN= Name des Zertifikats
        # DNS = DNS Eintrgäe aus DNS.txt
        a = certentry(name=entry,expiredate=date,CN=CN,DNS=DNS)
        array.append(a)
    array.sort(key=certentry.get)
    return array


def alerting(dirList : list,path,emailmode : int):
    """ Hiermit wird die Liste, deren Zertifikate erstellt, die bald ablaufen werden."""
    expireN = app.config['EXPIRE']
    CNn = app.config['CNname']
    DNSfile = app.config['DNSFILE']
    warningDays = app.config['WARNINGDAYS']
    isinfo = app.config['ISINFO'] 

    array = []
    for entry in dirList:
        try:
            # Das Ablaufdatum aus der expire.txt holen
            stringExpireDat = open(os.path.join(path,entry,expireN),"r").readline()
            # Das Datum in ein Date-Format umwandeln, um damit Rechnen zu können
            expiredate = datetime.strptime(stringExpireDat,"%Y-%m-%d")
            CN = open(os.path.join(path,entry,CNn),"r").readline()
            # Alerting Logik
            # Das heutige Datum holen
            heute = datetime.today() 
            # 2 Wochen als Summe addieren
            delta = dt.timedelta(days=warningDays) 
            # In die Zukunftreisen, um richtig zu triggern
            zukunft = heute + delta 

            # DNS Namen herausfinden
            try:
                DNS = helper.readLine(os.path.join(path,entry,DNSfile))
                DNS = DNS.replace("\n","")
            except FileNotFoundError:
                DNS = ""

            # Wenn das Zukunftsdatum größer ist, als das Expiredate aus der expire.txt, somit ist das Zertifikat abgelaufen
            # Darauf hin muss die Station benachrichtig werden.
            if emailmode == 0:
                # Für Webanzeige
                if expiredate < zukunft:
                    a = certentry(name=entry,expiredate=expiredate,CN=CN,DNS=DNS)
                    array.append(a)
            else:
                # Für die E-Mail
                path4 = os.path.join(path,entry,isinfo)
                if expiredate < zukunft:
                    if not os.path.exists(path4):
                        # Wenn Zertifikat bald abläuft nehme es auf.
                        # Und nicht schon informiert wurde.
                        b = certentry(name=entry,expiredate=expiredate,CN=CN,DNS=DNS)
                        array.append(b)
                        print(entry,"wurde hinzugefügt.")
                        helper.writeLine(path4,"yes")
        except FileNotFoundError:
            string = ""
            date = ""
    array.sort(key=certentry.get)
    return array

def sendmail(array,subject):
    """Multi-Tasking E-Mail sending"""
    try:
        """Mail wird von Python-Flask versendet."""
        msg = Message ("Zertifikatsmonitor: "+subject,sender=app.config['MAIL_SENDER'] ,recipients=app.config['MAIL_RECIPIENTS'])
        stringc = ""
        for entry in array:
            stringc = stringc + "\n" + str(entry)
        msg.body = stringc
        if len(array) > 0:
            mail.send(msg)
            print(">> E-Mail gesendet")
            return 0
    except ConnectionRefusedError as e:
        return 1
    