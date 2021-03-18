import nfc
from nfc.clf import RemoteTarget
import os
import time

story_id_pairs = {
    '13A4F96E': 'Mansion',
    '500DBD5E': 'Stasis'
}

class Pn532UartTtyAma0:
    def __init__(self):
        self.options = {
                'targets': ('106A', '106B'),
                'on-connect': self.on_conect,
                'on-release': self.on_release,
                'interval': 0.1
        }
        self.story = ''
        self.clf = nfc.ContactlessFrontend()
        self.open = self.clf.open('tty:AMA0')
        if self.open:
            print('Device opened.')
        else:
            print('Couldn\'t open device')

    def on_conect(self, tag):
        tag_id = str(tag).split('=')[1]
        for story_id, story_name in story_id_pairs.items():
            if story_id == tag_id:
                self.story = story_name
        print('Preparing story for tag ' + tag_id + ': ' + self.story)
        return True

    def on_release(self, tag):
        os.system('aplay ../../stories/' + self.story + '.wav')
        self.search_and_connect()


    def search_and_connect(self):
        started = time.time()
        self.clf.connect(rdwr=self.options)

    def close(self):
        self.clf.close()


pn_532_uart_tty_ama0 = Pn532UartTtyAma0()
try:
    if pn_532_uart_tty_ama0.open:
        pn_532_uart_tty_ama0.search_and_connect()
except:
    print('An unexpected error occurred... closing device.')
pn_532_uart_tty_ama0.close()
