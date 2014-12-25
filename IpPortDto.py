__author__ = 'Akin'

class IpPort:

    def __init__(self,ip,port,time,status):
        self.ip=ip
        self.port=port
        self.time=time
        self.status=status
    def dump(self):
        return {"IpPortList": {'ip': self.ip,
                               'port': self.port,
                               'time': self.time,
                               'status': self.status}}