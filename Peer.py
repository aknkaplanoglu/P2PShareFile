import sys

__author__ = 'Akin_Kaplanoglu'

import socket
import threading
import os, fnmatch
import json, queue
import hashlib
from IpPortDto import IpPort
from FileMD5 import FileMd5
from time import ctime
from PySide.QtGui import *
downloadFileName=None
from apscheduler.schedulers.background import BackgroundScheduler

ipPortList = list()
alliPPortList = list()
icIpPortList = list()
FakeIpPortList = list()
FakeIpPortListIc = list()
sendList = list()
sendListIc = list()
fileSendList = list()
dict={}
mds5=None
chunkSize = 4096
hasMd5=list()
fileSizeForDownload=queue.Queue(1)
md5q=queue.Queue()
tempmd5=queue.Queue(1)
fileNameForDownload=queue.Queue(1)


def hasContain(ip, port, list):
    for i in list:
        if i.ip == ip and i.port == port:
            return True
    return False


def sendingList(list, ip, port):
    sendList.clear()
    for i in list:
        if not (i.ip == ip and i.port == port):
            sendList.append(i)
    return sendList


scheduler = BackgroundScheduler()


def testConnectionsThread():
    while True:
        try:
            if len(alliPPortList) < 1:
                break
            q = alliPPortList.pop()
            tuple = (q.ip, int(q.port))
            s_test = socket.socket()
            s_test.setblocking(True)
            s_test.settimeout(2)
            try:
                s_test.connect(tuple)
                q.time = ctime()
                FakeIpPortList.append(q)
                continue
            except socket.timeout:
                print('{} timed out on connect'.format(s.fileno()))
            except socket.error:
                print('{} threw a socket error'.format(s.fileno()))
            except:
                raise Exception
        except IndexError as e:
            continue
    for temp in FakeIpPortList:
        alliPPortList.append(temp)
    FakeIpPortList.clear()


scheduler.add_job(testConnectionsThread, 'interval', minutes=10)
scheduler.start()

if os.name != "nt":
    import fcntl
    import struct

    def get_interface_ip(ifname):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        return socket.inet_ntoa(fcntl.ioctl(s.fileno(), 0x8915, struct.pack('256s',
                                                                            ifname[:15]))[20:24])


def get_lan_ip():
    ip = socket.gethostbyname(socket.gethostname())
    if ip.startswith("127.") and os.name != "nt":
        interfaces = [
            "eth0",
            "eth1",
            "eth2",
            "wlan0",
            "wlan1",
            "wifi0",
            "ath0",
            "ath1",
            "ppp0",
        ]
        for ifname in interfaces:
            try:
                ip = get_interface_ip(ifname)
                break
            except IOError:
                pass
    return ip

# tempPort=None
portPeer = 1113

def testConnectionsThread1():
        while True:
            try:
                if len(icIpPortList) < 1:
                    break
                q = icIpPortList.pop()
                tuple = (q.ip, int(q.port))
                s_test = socket.socket()
                s_test.setblocking(True)
                s_test.settimeout(2)
                try:
                    s_test.connect(tuple)
                    q.time = ctime()
                    FakeIpPortListIc.append(q)
                    continue
                except socket.timeout:
                    print('{} timed out on connect'.format(s.fileno()))
                except socket.error:
                    print('{} threw a socket error'.format(s.fileno()))
                except:
                    raise Exception
            except IndexError as e:
                continue
        for temp in FakeIpPortListIc:
            icIpPortList.append(temp)
        FakeIpPortListIc.clear()

scheduler.add_job(testConnectionsThread1, 'interval', minutes=10)

def encode(response):
    return response.encode('utf-8')


class ServerPeer(threading.Thread):
    def __init__(self,app):
        threading.Thread.__init__(self)
        self.app=app

    def newSocket(self):
        sPeer = socket.socket()
        # hostPeer = host
        sPeer.bind((get_lan_ip(), portPeer))
        sPeer.listen(5)
        t = []
        filePath = "C:\\Users\Akin\Desktop\python_dir"
        while True:
            print("Waiting for connection iç bacak")
            c, addr = sPeer.accept()
            print('Got a connection from ', addr)
            tempIpPort = list()
            peerServerListen = PeerServerListen(c, addr, sPeer, tempIpPort, filePath)
            peerServerListen.start()
            peerClientIc = PeerClientIc(c, addr, sPeer, tempIpPort)
            peerClientIc.start()
            t.append(peerClientIc)
            t.append(peerServerListen)
        for a in t:
            a.join()
        sPeer.close()

    def run(self):
        self.newSocket()


dialogList = list()





class ClientDialog(QDialog):
    def __init__(self):
        self.qt_app = QApplication(sys.argv)
        QDialog.__init__(self, None)
        self.listWidget = QListWidget()
        self.setWindowTitle('IRC Client')
        self.setMinimumSize(500, 200)
        self.vbox = QVBoxLayout()
        self.sender = QLineEdit("", self)
        self.channel = QTextBrowser()
        self.send_button = QPushButton('&Send')
        self.send_button.clicked.connect(self.outgoing_parser)
        self.vbox.addWidget(self.listWidget)
        self.listWidget.itemActivated.connect(self.takeItem)
        self.vbox.addWidget(self.channel)
        self.vbox.addWidget(self.sender)
        self.vbox.addWidget(self.send_button)
        self.setLayout(self.vbox)


    def cprint(self, data):
        self.channel.append(data)

    def fillListWidget(self,dict_):
        c=None
        if len(dict_)>0:
            for key in dict_.keys():
                value=dict_[key]
                fileName,md5,fileSize=value.split(":",2)
                fileName=QListWidgetItem(fileName)
                self.listWidget.addItem(fileName)

    def bekleme(self):
        self.cprint("Downloading...Please wait...")

    def takeItem(self,item):
        fileName_=item.text()#tıkladıgın şey
        for key in dict.keys():
            value=dict[key]
            fileName,md5,fileSize=value.split(":",2)
            mds5=md5
            self.bekleme()
            if fileName==fileName_:
                md5q.put("FINDM "+md5)
                self.cprint(md5)
                fileSizeForDownload.put(fileSize)
                fileNameForDownload.put(fileName)
                downloadFileName=fileName
        #scheduler.add_job(self.bekleme, 'interval', seconds=5)


    def outgoing_parser(self):
        data = self.sender.text()
        dialogList.append(data)
        print(len(dialogList))
        self.sender.clear()

    def run(self):
        self.show()
        self.qt_app.exec_()


class ClientPeer(threading.Thread):
    def __init__(self, s, dialogList,app):
        threading.Thread.__init__(self)
        self.size = 2048
        self.s = s
        self.dialogList = dialogList
        self.app=app

    def fileTestList(self):
        for i in alliPPortList:
            tuple = (i.ip, int(i.port))
            s_test = socket.socket()
            s_test.setblocking(True)
            s_test.settimeout(2)
            try:
                s_test.connect(tuple)
                fileSendList.append(i)
                s_test.close()
            except socket.timeout:
                print('{} timed out on connect'.format(s.fileno()))
                continue
            except socket.error:
                print('{} threw a socket error'.format(s.fileno()))
                continue
            except:
                raise Exception
                continue


    def findMd5(self,input_):
        input_ = encode(input_)
        for f in alliPPortList:
            tuple = (f.ip, int(f.port))
            s_test_ = socket.socket()
            s_test_.settimeout(5)
            try:
                s_test_.connect(tuple)
                s_test_.send(input_)
                while True:
                    try:
                        testResponse = s_test_.recv(1024)
                        testResponse = str(testResponse)
                        testResponse = testResponse.split("'", 2)[1]
                        if testResponse[0:5]== "MSUMY":
                            hasMd5.append(f.ip+":"+str(f.port))
                    except socket.timeout:
                        print('{} timed out on connect'.format(s.fileno()))
                        break
                    except socket.error:
                        print('{} threw a socket error'.format(s.fileno()))
                        break
                    except:
                        raise Exception
                        break
            except socket.timeout:
                print('{} timed out on connect'.format(s.fileno()))
            except socket.error:
                print('{} threw a socket error'.format(s.fileno()))
            except:
                raise Exception
        fileSendList.clear()


    def sendFindFile(self, input_):
        input_ = encode(input_)
        for f in fileSendList:
            tuple = (f.ip, int(f.port))
            s_test_ = socket.socket()
            s_test_.settimeout(2)
            try:
                s_test_.connect(tuple)
                s_test_.send(input_)
                while True:
                    try:
                        testResponse = s_test_.recv(1024)
                        testResponse = str(testResponse)
                        testResponse = testResponse.split("'", 2)[1]
                        print(testResponse)
                        if testResponse[0:5]=="NAMEY":
                            testResponse=testResponse.replace("NAMEY BEGIN","")
                            testResponse=testResponse.replace("NAMEY END","")
                            m=list()
                            m=testResponse.split(" ",-1)
                            print(m[0])
                            i=0
                            for a in m:
                                c=list()
                                if ":" in a :
                                    c=a.split(":",-1)
                                    dict[f.ip+":"+str(f.port)+str(i)]=c[0]+":"+c[1]+":"+str(c[2])
                                i+=1
                            self.app.fillListWidget(dict)
                            app.cprint(testResponse)
                            s_test_.close()
                        else:
                            app.cprint(testResponse)
                        break
                    except socket.timeout:
                        print('{} timed out on connect'.format(s.fileno()))
                        s_test_.close()
                        break
                    except socket.error:
                        print('{} threw a socket error'.format(s.fileno()))
                        s_test_.close()
                        break
                    except:
                        s_test_.close()
                        raise Exception
                        break
            except socket.timeout:
                print('{} timed out on connect'.format(s.fileno()))
                s_test_.close()
            except socket.error:
                print('{} threw a socket error'.format(s.fileno()))
                s_test_.close()
            except:
                raise Exception
                s_test_.close()
        fileSendList.clear()



    def run(self):

        portPeer1 = str(portPeer)
        firstRequest = "REGME " + get_lan_ip() + ":" + portPeer1
        firstRequest = encode(firstRequest)
        self.s.send(firstRequest)
        while True:
            received = s.recv(1024)  # clien
            received = str(received)
            received = received.split("'", 2)[1]
            app.cprint(received)
            if received[0:5]=="REGOK":
                print(received)
                break

        firstRequest = "GETNL"
        firstRequest = encode(firstRequest)
        self.s.send(firstRequest)
        while True:
            received = s.recv(1024)  # clien
            received = str(received)
            received = received.split("'", 2)[1]
            if received[0:1] == "[":
                    ipPortList = json.loads(received)
                    print(ipPortList)
                    for k in ipPortList:
                        alliPPortList.append(
                            IpPort(k["IpPortList"]["ip"], k["IpPortList"]["port"], k["IpPortList"]["time"],
                                    k["IpPortList"]["status"]))
                    break

        while True:
            if len(dialogList) > 0:
                input_ = dialogList.pop()
                if input_[0:5] == "FINDF":
                    self.fileTestList()
                    if input_[6:] != "":
                        self.sendFindFile(input_)

            if md5q.qsize()>0:
                input_=md5q.get()
                print(input_)
                tempmd5.put(input_[6:])
                self.findMd5(input_)
            if len(hasMd5)>0:
                threads=[]
                imlec=0
                tempMd5=tempmd5.get()
                fileSize_ = fileSizeForDownload.get()
                for a in hasMd5:
                    ip,port=a.split(":",1)
                    totalChunkPart= int(fileSize_) //chunkSize
                    threadForDownload=threadForDownloadClient(imlec,ip,port,totalChunkPart,len(hasMd5),tempMd5,imlec+1)
                    threadForDownload.start()
                    imlec+=1
                    threads.append(threadForDownload)
                hasMd5.clear()
                for b in threads:
                    b.join()




class threadForDownloadClient(threading.Thread):
    def __init__(self,imlec,ip,port,totalChunkSize,hasmd5,md5,threadId):
        threading.Thread.__init__(self)
        self.imlec=imlec
        self.ip=ip
        self.port=port
        self.totalChunkSize=totalChunkSize
        self.hasmd5=hasmd5
        self.md5=md5
        self.threadId=threadId

    def run(self):
            openFile = fileNameForDownload.get()
            while True:
                try:
                    tuple = (self.ip, int(self.port))
                    s_test_ = socket.socket()
                    s_test_.settimeout(10)
                    print(self.totalChunkSize)
                    if self.totalChunkSize<self.imlec:
                        break
                    print(str(self.threadId)+".thread-->"+"imlec-->"+str(self.imlec))
                    s_test_.connect(tuple)
                    sending="GETCH "+self.md5+":"+str(self.imlec)
                    sending=encode(sending)
                    s_test_.send(sending)
                    while True:
                        try:
                            testResponse = s_test_.recv(chunkSize)
                            f = open(openFile,'wb+')
                            if self.imlec==0:
                                f.seek(self.imlec*chunkSize)
                                f.write(testResponse)
                                f.flush()
                                print(testResponse)
                                print("imlec-->"+str(self.imlec)+" yazıldı")
                                self.imlec+=self.hasmd5
                                f.close()
                            else:
                                f.seek(self.imlec*chunkSize-1)
                                f.write(testResponse)
                                f.flush()
                                print(testResponse)
                                print("imlec-->"+str(self.imlec)+" yazıldı")
                                self.imlec+=self.hasmd5
                            break
                        except socket.timeout:
                            print('{} timed out on connect'.format(s.fileno()))
                            break
                        except socket.error:
                            print('{} threw a socket error'.format(s.fileno()))
                            break
                        except:
                            raise Exception
                            break
                except socket.timeout:
                    print('{} timed out on connect'.format(s.fileno()))
                    s_test_.close()
                except socket.error:
                    print('{} threw a socket error'.format(s.fileno()))
                    s_test_.close()
                except:
                    raise Exception
                    s_test_.close()




class PeerServerListen(threading.Thread):
    def __init__(self, csock, adrr, sPeer, tempIpPort, filePath):
        threading.Thread.__init__(self)
        self.csock = csock
        self.addr = adrr
        self.sPeer = sPeer
        self.tempIpPort = tempIpPort
        self.filePath = filePath

    def find_files(self, pattern):
        for root, dirs, files in os.walk(self.filePath):
            for basename in files:
                if fnmatch.fnmatch(basename, pattern):
                    filename = os.path.join(root, basename)
                    yield filename

    def checksum_md5(self, filename):
        md5 = hashlib.md5()
        with open(filename, 'rb') as f:
            for chunk in iter(lambda: f.read(128 * md5.block_size), b''):
                md5.update(chunk)
        return md5.digest()

    def md5_for_file(path, block_size=256 * 128, hr=False):
        '''
        Block size directly depends on the block size of your filesystem
        to avoid performances issues
        Here I have blocks of 4096 octets (Default NTFS)
        '''
        md5 = hashlib.md5()
        with open(path, 'rb') as f:
            for chunk in iter(lambda: f.read(block_size), b''):
                md5.update(chunk)
        if hr:
            return md5.hexdigest()
        return md5.digest()


    def run(self):
        while True:
            try:
                received = self.csock.recv(1024)
                received = str(received)
                received = received.split("'", 2)[1]
                received_ = received[0:5]
                print(received)

                if received_=="GETCH":
                    md5,chunkPart=received[6:].split(":",1)
                    chunkPart=int(chunkPart)
                    for file in self.find_files("*"):  # regular expression kullanıldı.Dosya adına benzeyenler bulundu.
                        mdsum5 = hashlib.md5(open(file, 'rb').read()).hexdigest()
                        if mdsum5==md5:
                            f=open(file,"rb")
                            print(file)
                            if chunkPart==0:
                                f.seek(chunkPart*chunkSize)
                                byte=f.read(chunkSize)
                                print(byte)
                                self.csock.send(byte)
                            else:
                                f.seek(chunkPart*chunkSize-1)
                                byte=f.read(4096)
                                print(byte)
                                self.csock.send(byte)


                if received_=="FINDM":
                    mdsum5=received[6:]
                    for file in self.find_files("*"):  # regular expression kullanıldı.Dosya adına benzeyenler bulundu.
                        md5 = hashlib.md5(open(file, 'rb').read()).hexdigest()
                        if mdsum5==md5:
                            response="MSUMY "+mdsum5
                            response=encode(response)
                            self.csock.send(response)
                        else:
                            response="MSUMN "+mdsum5
                            response=encode(response)
                            self.csock.send(response)




                if received_ == "FINDF" and received[6:] != "":
                    fileName = received[6:]
                    resp="NAMEY BEGIN "
                    for file in self.find_files(
                                            "*" + fileName + "*"):  # regular expression kullanıldı.Dosya adına benzeyenler bulundu.
                        # fileNames.append(file.replace(self.filePath,"")[1:])
                        # checksumMd5=self.checksum_md5(file)
                        # md5=str(self.checksum_md5(file))
                        md5 = hashlib.md5(open(file, 'rb').read()).hexdigest()
                        fileSize = str(os.path.getsize(file))
                        fileName_ = file.replace(self.filePath, "")[1:]
                        resp += fileName_ + ":" + md5 + ":" + fileSize + " "
                    resp += " NAMEY END"
                    resp = encode(resp)
                    self.csock.send(resp)
                    # if len(fileNames)==0:
                    # resp="NAMEN"+fileName
                    # resp=encode(resp)
                    #   self.csock.send(resp)

                if received_ == "GETNL":
                    if received[6:] == "":
                        icIpPortList.extend(alliPPortList)
                        sendListIc = sendingList(icIpPortList, get_lan_ip(), port)
                        a = IpPort(get_lan_ip(), portPeer, ctime(), "s")
                        sendListIc.append(a)
                        pickled_string = json.dumps([o.dump() for o in sendListIc])
                        sendListIc.clear()
                        pickled_string = encode(pickled_string)
                        self.csock.send(pickled_string)
                    else:
                        number = received[6:]
                        try:
                            int(number)
                            if len(icIpPortList) <= int(number):
                                sendListIc = sendingList(icIpPortList, get_lan_ip(), port)
                                pickled_string = json.dumps([sendListIc[i].dump() for i in range(number)])
                                sendListIc.clear()
                                pickled_string = encode(pickled_string)
                                self.cSocket.send(pickled_string)

                        except ValueError:
                            responseMessage = "CMDER"
                            responseMessage = str(responseMessage)
                            responseMessage = str(responseMessage)
                            self.cSocket.send(responseMessage)

                if received_ == "REGME":
                    ip, port = received[6:].split(":", 1)
                    ipPort = IpPort(ip, port, ctime(), "w")
                    self.tempIpPort.append(ipPort)
                    print(len(self.tempIpPort))
                    responseMessage = "REGWA"
                    responseMessage = str(responseMessage)
                    responseMessage = encode(responseMessage)
                    self.csock.send(responseMessage)

                if received_ == "HELLO":
                    print(received)
                    sendMessage = "SALUT"
                    sendMessage = encode(sendMessage)
                    self.csock.send(sendMessage)
                    close = self.csock.recv(1024)
                    close = str(close)
                    close = close.split("'", 2)[1]
                    print(close)

                    if close == "CLOSE":
                        sendMessage = "BUBYE"
                        sendMessage = encode(sendMessage)
                        self.csock.send(sendMessage)
                        break
            except socket.timeout:
                print('{} timed out on connect'.format(fileSize.fileno()))
                break
            except socket.error:
                print('{} threw a socket error'.format(fileSize.fileno()))
                break
            except:
                raise Exception
                break


class PeerClientIc(threading.Thread):
    def __init__(self, csock, adrr, sPeer, tempIpPort):
        threading.Thread.__init__(self)
        self.csock = csock
        self.addr = adrr
        self.sPeer = sPeer
        self.tempIpPort = tempIpPort

    def run(self):
        while True:
            if len(self.tempIpPort) > 0:
                s_test = socket.socket()
                s_test.setblocking(True)
                s_test.settimeout(5)
                try:
                    list__pop0 = self.tempIpPort.pop()
                    s_test.connect((list__pop0.ip, int(list__pop0.port)))
                    testMessage = "HELLO " + list__pop0.ip + ":" + str(list__pop0.port)
                    testMessage = encode(testMessage)
                    s_test.send(testMessage)
                    while True:
                        try:
                            testResponse = s_test.recv(1024)
                            testResponse = str(testResponse)
                            testResponse = testResponse.split("'", 2)[1]
                            print(testResponse)
                            if testResponse[0:5] == "SALUT":
                                testResponse = "CLOSE"
                                testResponse = encode(testResponse)
                                s_test.send(testResponse)
                                buby = s_test.recv(1024)
                                buby = str(buby)
                                buby = buby.split("'", 2)[1]
                                print(buby)
                                if buby == "BUBYE":
                                    now = ctime()
                                    if not hasContain(list__pop0.ip, list__pop0.port, icIpPortList):
                                        ipPort_ = IpPort(list__pop0.ip, list__pop0.port, now, "s")
                                        # t_lock.acquire()
                                        icIpPortList.append(ipPort_)
                                        # t_lock.release()
                                    print("Ipportlistsayisi:" + str(len(icIpPortList)))
                                    response = "REGOK " + now
                                    response = encode(response)
                                    self.csock.send(response)  # serverdan clienta birsey yollarken csock kullanilir.
                                    s_test.close()
                                    break
                        except socket.timeout:
                            self.raiseError()
                            print('{} timed out on connect'.format(s.fileno()))
                            s_test.close()
                            break
                        except socket.error:
                            self.raiseError()
                            print('{} threw a socket error'.format(s.fileno()))
                            s_test.close()
                            break
                        except:
                            self.raiseError()
                            s_test.close()
                            raise Exception
                            break
                except socket.timeout:
                    self.raiseError()
                    print('{} timed out on connect'.format(s.fileno()))
                    s_test.close()
                    break
                except socket.error:
                    self.raiseError()
                    print('{} threw a socket error'.format(s.fileno()))
                    s_test.close()
                    break
                except:
                    self.raiseError()
                    s_test.close()
                    raise Exception
                    break


t_lock = threading.Lock()
s = socket.socket()
host = get_lan_ip()  # socket.gethostname()
port = 1112
# s.bind((host,port))
s.connect((host, port))
app = ClientDialog()
serverPeer = ServerPeer(app)
serverPeer.start()
clientPeer = ClientPeer(s, dialogList,app)
clientPeer.start()
app.run()
clientPeer.join()
serverPeer.join()
s.close()
