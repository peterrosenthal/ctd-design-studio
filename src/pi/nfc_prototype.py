import nfc
from nfc.clf import RemoteTarget
import time

class Pn532UartTtyAma0:
    def __init__(self):
        self.options = {
                'targets': ['106A', '106B'],
                'on-connect': self.on_conect,
                'interval': 0.1
        }
        self.message = ""
        self.clf = nfc.ContactlessFrontend()
        self.open = self.clf.open('tty:AMA0')
        if self.open:
            print('Device opened.')
        else:
            print('Couldn\'t open device')

    def on_conect(self, tag):
        print(tag)

    def connect(self):
        started = time.time()
        after5s = lambda: time.time() - started > 5
        tag = self.clf.connect(rdwr=self.options, terminate=after5s)
        if tag.ndef:
            print(tag.ndef.message.pretty())

    def close(self):
        self.clf.close()


pn_532_uart_tty_ama0 = Pn532UartTtyAma0()
if pn_532_uart_tty_ama0.open:
    try:
        pn_532_uart_tty_ama0.connect()
    except:
        print('An unexpected error occurred... closing device.')
pn_532_uart_tty_ama0.close()
