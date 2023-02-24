# Python version holen
FROM python:alpine3.15

# Enviroment setzen
WORKDIR /etc/certmon

# Argumente setzen

#Requirements kopieren
COPY requirements.txt requirements.txt
# benötige Programme installieren
RUN apk add --update openssl && \
    apk add --update gcc g++ python3-dev musl-dev && \

    pip3 install --no-cache-dir --upgrade pip && \
    pip3 install --no-cache-dir -r requirements.txt && \
    apk del gcc g++ python3-dev musl-dev && \
    rm -rf /var/cache/apk/*  && \
    rm -rf requirements.txt

# Zertifikatsmonitor installieren
COPY certmon.py certmon.py
COPY app/ app/

# Zertifikatsmonitor starten
EXPOSE 5000

CMD ["gunicorn","-b","0.0.0.0:5000","-w","2","certmon:app","--preload","--log-level","debug"]
#CMD ["python3","certmon.py"]