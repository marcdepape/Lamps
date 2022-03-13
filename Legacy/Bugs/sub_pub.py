from time import sleep
import subprocess
import zmq
import json

class LampSubPub(object):
    def __init__(self, this_lamp):
        # SERVER
        server_context = zmq.Context()
        self.server = server_context.socket(zmq.PUB)
        self.server.connect("tcp://armadillo.local:8101")
        #server.connect("tcp://bison.local:8101")
        self.server.set_hwm(1)

        # CLIENT
        client_context = zmq.Context()
        self.client = client_context.socket(zmq.SUB)
        self.client.connect("tcp://armadillo.local:8100")
        #client.connect("tcp://bison.local:8100")
        self.client.setsockopt(zmq.SUBSCRIBE, b'')
        self.client.set_hwm(1)

        lamp_ip = "000.000.000.000"
        print "GETTING IP ADDRESS..."
        while lamp_ip[:4] != "192.":
            net = subprocess.Popen(('ifconfig', 'wlan0'), stdout=subprocess.PIPE)
            ip = subprocess.check_output(('grep', 'addr'), stdin=net.stdout)
            net.wait()
            lamp_ip = ip.strip().split("addr:")
            lamp_ip = lamp_ip[1].split(" ")
            lamp_ip = lamp_ip[0]
        print "IP: " + str(lamp_ip)

        self.lamp_ip = lamp_ip
        self.this_lamp = this_lamp
        self.position = 0
        self.console = "waiting..."
        self.out_update = json.dumps({"ip": self.lamp_ip,"lamp": self.this_lamp, "position": self.position, "console": self.console}, sort_keys=True)
        print("DEF: " + str(self.out_update))
        self.in_update = ""

    def send(self, q):
        while True:
            self.console = q.get()
            self.out_update = json.dumps({"ip": self.lamp_ip,"lamp": self.this_lamp, "position": self.position, "console": self.console}, sort_keys=True)
            self.server.send_json(self.out_update)
            q.put("READY")
            sleep(0.05)

    def receive(self):
        update = self.client.recv_json()
        update = json.loads(update)
        if update["lamp"] == self.this_lamp:
            self.in_update = update
            return self.in_update
        else:
            return -1
