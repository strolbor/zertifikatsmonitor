# SSL CMDs

## Private Key erstellen
openssl genrsa -out <keyname>.pem 4096

## CSR erstellen
openssl req -new -out <csrname>.pem -key <keyname>.pem -config <confname>.conf

## CSR Verifizieren
openssl req -text -noout -verify -in <csrname>.pem

## CERT: Self-Sign
.\openssl x509 -days 36 -signkey .\instance\certificates\Sign\private.key -extfile .\instance\certificates\Sign\csr.ext -req -in .\instance\certificates\Sign\csr.req -out .\instance\certificates\Sign\cert36.pem 

.\openssl x509 -days 61 -signkey ".\instance\certificates\Sign\private.key" -req -in ".\instance\certificates\Sign\csr.req" -out ".\instance\certificates\Sign\cert.pem"

### kd
openssl x509 -req -in .\instance\certificates\Sign\csr.req -signkey .\instance\certificates\Sign\private.key -out .\instance\certificates\Sign\cert.crt -days 3650 -sha256 -extfile .\instance\certificates\Sign\sign.ext

## CERT: p7b -> pem
openssl pkcs7 -inform DER -outform PEM -in <crtname>.p7b -print_certs > <crtname>.pem # Funktioniert nicht unter Windows
openssl pkcs7 -in <crtname>.p7b -print_certs > <crtname>.pem

## CERT:   pem -> p7b
.\openssl crl2pkcs7 -nocrl -certfile .\instance\certificates\Test3\cert.pem -out .\instance\certificates\Test3\cert.p7b

cert36.pem

.\openssl crl2pkcs7 -nocrl -certfile .\instance\certificates\sign\cert36.pem -out .\instance\certificates\Sign\cert36.p7b

## CERT: pem Verifizieren
.\openssl x509 -noout -text -in .\instance\certificates\Test1\cert.pem

## CERT: pem Expire Date holen
.\openssl x509 -noout -text -in .\instance\certificates\Test1\cert.pem | head -n 15 | grep "Not After"