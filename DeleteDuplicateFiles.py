import os
import time
import psutil
import hashlib
import urllib.request
import urllib.error
import smtplib
import schedule
from sys import *
from email import encoders
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase

def is_connected():
    try:
        urllib.request.urlopen('http://www.gmail.com')
        return True
    except urllib.error.URLError as err:
        return False

def MailSender(filename,time,tomail):
    try:
        fromadd = "nirajpachpande1681@gmail.com"
        toadd = tomail

        msg = MIMEMultipart()

        msg['From'] = fromadd

        msg['To'] = toadd

        body = """
        Hello %s,
        Please find attached document which contains Log of Running process.
        Log file is created at : %s
        This is auto generated mail.
        Thanks :
        Niraj Pachpande
        """%(toadd,time) 

        Subject = """
        Process log generated at : %s
        """%(time)

        msg['Subject'] = Subject
        
        msg.attach(MIMEText(body,'plain'))
        
        attachment = open(filename,"rb")

        p= MIMEBase('application','octet-stream')
        
        p.set_payload((attachment).read())
        
        encoders.encode_base64(p)
        
        p.add_header('Content-Disposition',"attachment:filename = %s"%filename)
        
        msg.attach(p)
        
        s = smtplib.SMTP('smtp.gmail.com',587)

        s.starttls()

        s.login(fromadd,"ecrnamtlkflwxsma")

        text = msg.as_string()

        s.sendmail(fromadd,toadd,text)

        s.quit()
        
        print("Log File Successfully Send")

    except Exception as E:
        print("Unable to send mail.",E)
        
def DeleteFiles(dict1):
    results = list(filter(lambda x: len(x) > 1, dict1.values()))
    
    icnt = 0
    iFound = 0

    if len(results) > 0:
        for result in results:
            for subresult in result:
                icnt+=1
                if icnt >= 2:
                    os.remove(subresult)
                    iFound+=1
            icnt = 0
        
        print("Number of duplicate files found and deleted : ",iFound)
        
    else:
        print("No duplicate files found.")

def hashfile(path, blocksize = 1024):
    afile = open(path, 'rb')
    hasher = hashlib.md5()
    buf = afile.read(blocksize)

    while len(buf) > 0:
        hasher.update(buf)
        buf = afile.read(blocksize)
    afile.close()

    return hasher.hexdigest()

def findDup(path):
    flag = os.path.isabs(path)
    
    if flag == False:
        path = os.path.abspath(path)
    
    exists = os.path.isdir(path)

    dups = {}

    if exists:
        for dirName, subdirs, fileList in os.walk(path):
            print("Current folder is : "+dirName)
            for filen in fileList:
                path = os.path.join(dirName, filen)
                file_hash = hashfile(path)

                if file_hash in dups:
                    dups[file_hash].append(path)
                else:
                    dups[file_hash] = [path]

        return dups
    else:
        print("Invalid Path")

def StoreResultsInLog(dict1,log_dir):
    Count = 0
    results = list(filter(lambda x: len(x) > 1, dict1.values()))
    
    if not os.path.exists(log_dir):
        try:
            os.mkdir(log_dir)
        except:
            pass

    lines = "-"* 50
    log_path = os.path.join(log_dir,"LogFile%s.log"%(time.time()))

    f = open(log_path,'w')
    f.write(lines+"\n")
    f.write("Information About the Duplicate Files : "+time.ctime()+"\n")
    f.write(lines+"\n")

    if len(results) > 0:
        for result in results:
            for subresult in result:
                f.write("%s\n" % subresult)
                Count+=1
        f.write("The duplicates files found in the directory are :"+str(Count))        
    else:
        f.write("No duplicate files found.")
        connected = is_connected()

        if connected:
            startTime = time.time()
            schedule.every(int(argv[2])).minutes.do(MailSender(log_path,time.ctime(),argv[3]))
            while True:
                schedule.run_pending()
                time.sleep(1)
            endTime = time.time() 

            print('Took %s seconds to send mail'%(endTime-startTime))
        else:
            print("There is no internet connection")

def main():
    
    if (len(argv) != 4):
        print("Error : Invalid number of arguments")
        exit()
    
    if (argv[1] == "-h") or (argv[1] == "-H"):
        print("This Script is used to record running process.")
        exit()

    if (argv[1] == "-u") or (argv[1] == "-U"):
        print("Usage : ApplicationName AbsolutePath_of_Directory Extention")
        exit()

    try:
        arr = findDup(argv[1])
        StoreResultsInLog(arr,argv[1])
        DeleteFiles(arr)

    except ValueError:
        print("Error : Invalid datatype of input")

    except Exception as E:
        print("Error : Invalid input",E)

if __name__ == "__main__":
    main()

