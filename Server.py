__author__ = 'Akin_Kaplanoglu'

import socket, threading
from threading import Thread
import queue
import json
from IpPortDto import IpPort
from time import ctime
from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler()

lQueue = queue.Queue(32767)
akoQueue = queue.Queue(32767)
messageQueue = queue.Queue(32767)
IpPortList = list()
FakeIpPortList = list()
mapExample = {}
tempName = ""
queueList = list()


def hasContain(ip,port,list):
    for i in list:
        if i.ip==ip and i.port==port:
            return True
    return False

def encode(response):
    return response.encode('utf-8')



def testConnectionsThread():
    while True:
        try:
            if len(IpPortList)<1:
                break
            q = IpPortList.pop()
            tuple = (q.ip, int(q.port))
            s_test = socket.socket()
            s_test.setblocking(True)
            s_test.settimeout(2)
            try:
                s_test.connect(tuple)
                q.time=ctime()
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
        IpPortList.append(temp)
    FakeIpPortList.clear()


scheduler.add_job(testConnectionsThread, 'interval', minutes=10)
scheduler.start()


class AraServer(Thread):
    def __init__(self, name, cSocket, addr, lQueue, IpPortList_):
        Thread.__init__(self)
        self.name = name
        self.cSocket = cSocket
        self.addr = addr
        self.lQueue = lQueue
        self.messageQueue = messageQueue
        self.size = 2048
        self.IpPortList_ = IpPortList_


    def run(self):
        while True:
            try:
                receivedMessage = self.cSocket.recv(self.size)
                receivedMessage = str(receivedMessage)
                receivedMessage = receivedMessage.split("'", 2)[1]
                print(receivedMessage)
                if receivedMessage[0:5] == "REGME":
                    ip, port = receivedMessage[6:].split(":", 1)
                    ipPort = IpPort(ip, port, ctime(), "w")
                    self.IpPortList_.append(ipPort)
                    print(len(IpPortList_))
                    responseMessage = "REGWA"
                    responseMessage = str(responseMessage)
                    responseMessage = encode(responseMessage)
                    self.cSocket.send(responseMessage)
                if receivedMessage[0:5]=="GETNL":
                    if receivedMessage[6:]=="":
                        pickled_string = json.dumps([o.dump() for o in IpPortList])
                        pickled_string=encode(pickled_string)
                        self.cSocket.send(pickled_string)
                    else :
                        number=receivedMessage[6:]
                        try:
                            int(number)
                            if len(IpPortList)<=int(number):
                                pickled_string=json.dumps([IpPortList[i].dump() for i in range(number)])
                                pickled_string=encode(pickled_string)
                                self.cSocket.send(pickled_string)

                        except ValueError:
                            responseMessage="CMDER"
                            responseMessage=str(responseMessage)
                            responseMessage=str(responseMessage)
                            self.cSocket.send(responseMessage)


            except socket.timeout:
                print('{} timed out on connect'.format(s.fileno()))
                self.cSocket.close()
                break
            except socket.error:
                print('{} threw a socket error'.format(s.fileno()))
                self.cSocket.close()
                break
            except:
                self.cSocket.close()
                raise Exception
                break


class AraClient(Thread):
    def __init__(self, name, cSocket1, address, messageQueue, lQueue, IpPortList_):
        Thread.__init__(self)
        self.name = name
        self.cSocket1 = cSocket1
        self.address = address
        self.lQueue = lQueue
        self.messageQueue = messageQueue
        self.IpPortList_ = IpPortList_

    def raiseError(self):
        response = "REGER"
        response = encode(response)
        self.cSocket1.send(response)

    def run(self):
        while True:
            if len(self.IpPortList_) > 0:
                s_test = socket.socket()
                s_test.setblocking(True)
                s_test.settimeout(5)
                try:
                    list__pop0 = self.IpPortList_.pop()
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
                                    if not hasContain(list__pop0.ip, list__pop0.port,IpPortList):
                                        ipPort_ = IpPort(list__pop0.ip, list__pop0.port, now, "s")
                                        #                                     t_lock.acquire()
                                        IpPortList.append(ipPort_)
                                        #                                     t_lock.release()
                                    print("Ipportlistsayisi:" + str(len(IpPortList)))
                                    response = "REGOK " + now
                                    response = encode(response)
                                    self.cSocket1.send(response)  #serverdan clienta birsey yollarken csock kullanilir.
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
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = "0.0.0.0"  # socket.gethostname()
threadCounter = 0
port = 1112
s.bind((host, port))
s.listen(20)

threads = []
while True:
    print("Waiting for connection")
    c, addr = s.accept()
    print('Got a connection from ', addr)
    IpPortList_ = list()
    # Thread(target=readThread, args=(c, addr)).start()
    araServer = AraServer("AraServer", c, addr, lQueue, IpPortList_)
    araServer.start()
    araClient = AraClient("AraClient", c, addr, messageQueue, lQueue, IpPortList_)
    araClient.start()
    threads.append(araServer)
    threads.append(araClient)
# logThread = loggerThread("LOGTHREAD", lQueue, "log.txt")
# logThread.start()

for t in threads:
    t.join()
# logThread.join()
s.close()
