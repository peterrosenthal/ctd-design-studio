import nfc
from nfc.clf import RemoteTarget
from time import sleep
import subprocess
from gpiozero import Button

class SonatomeTeller:
    def __init__(self):
        self.lid = Button(27, pull_up=False)
        self.sonatome_ids = {
            '13A4F96E': 'Mansion',
            '500DBD5E': 'Stasis',
            '0065BA5E': 'Night',
        }
        self.options = {
            'targets': ('106A', '106B'),
            'on-connect': self.connect_callback,
            'on-release': self.release_callback,
            'interval': 0.1
        }
        self.sonatome_name = ''
        self.proccess = None
        self.clf = nfc.ContactlessFrontend()
        self.nfc_open = self.clf.open('tty:AMA0')
        if self.nfc_open:
            print('Device opened.')
        else:
            print('Couldn\'t open device')

    def connect_callback(self, tag):
        tag_id = str(tag).split('=')[1]
        for sonatome_id, sonatome_name in self.sonatome_ids.items():
            if sonatome_id == tag_id:
                self.sonatome_name = sonatome_name
        return True

    def release_callback(self, tag):
        if self.lid.value == 1 and self.sonatome_name != '' and self.proccess is None:
            self.proccess = subprocess.Popen(['aplay', '../../stories/' + self.sonatome_name + '.wav'])
        if self.lid.value == 0 and not self.proccess is None:
            self.proccess.kill()
            self.proccess = None

    def search_and_connect(self):
        self.clf.connect(rdwr=self.options)

    def close_nfc(self):
        self.clf.close()


sonatome_teller = SonatomeTeller()
try:
    while True:
        sleep(0.1)
        if sonatome_teller.nfc_open:
            sonatome_teller.search_and_connect()
        else:
            sonatome_teller = SonatomeTeller()
except:
    print('An unexpected error occurred... closing device.')
    sonatome_teller.close_nfc()

# the script should never really get here, but just in case...
sonatome_teller.close_nfc()