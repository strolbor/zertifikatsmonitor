# Python version holen
FROM ubuntu:latest

# Enviroment setzen
WORKDIR /etc/certmon

# Argumente setzen

#Requirements kopieren
COPY requirements.txt requirements.txt
# benötige Programme installieren
RUN apt update && \
    apt install -y openssl && \
    apt install -y gcc g++ python3-dev musl-dev python3 python3-pip && \

    pip3 install --no-cache-dir --upgrade pip && \
    pip3 install --no-cache-dir -r requirements.txt && \
    apt purge -y gcc g++ python3-dev musl-dev && \
    rm -rf requirements.txt

# Zertifikatsmonitor installieren
COPY certmon.py certmon.py
COPY app/ app/

# Zertifikatsmonitor starten
EXPOSE 5000

CMD ["gunicorn","-b","0.0.0.0:5000","-w","2","certmon:app","--preload","--log-level","debug"]
#CMD ["python3","certmon.py"]