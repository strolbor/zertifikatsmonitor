a = open('requirements.txt','r')
b = open("neu.txt",'w')
for line in a:
	b.write(line.split("=")[0])
    
a.close()
b.flush()
b.close()