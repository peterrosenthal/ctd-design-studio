import board
from gpiozero import Button
import math
import neopixel
import nfc
from nfc.clf import RemoteTarget
import signal
import subprocess
import sys
from time import sleep, time
import traceback

class SonatomeTeller:
    def __init__(self):
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)
        self.kill_program = False
        self.lid = Button(27, pull_up=False)
        self.framecount_LED = 0
        self.neopixels = neopixel.NeoPixel(board.D12, 2, auto_write=False, pixel_order=neopixel.RGB)
        self.sonatome_ids = {
            '13A4F96E': 'Mansion',
            '20BDBA5E': 'Lights',
            '0065BA5E': 'Night',
            '901CBB5E': 'Stasis',
            'E0CDBA5E': 'Mountain',
            '9018BA5E': 'Morning',
            'F08DBE5E': 'f1s1',
            '703AC95E': 'f1s2',
            '500DBD5E': 'f1s3',
            '6067BA5E': 'v1s1',
            '2066BA5E': 'v1s3',
            '2023BF5E': 'v1s2',
            '40F3BB5E': 'v2s3',
            '40B0BE5E': 'v3s2',
            '206ABA5E': 'v3s4',
            'B068BA5E': 'v3s5'
        }
        self.options = {
            'targets': ('106A', '106B'),
            'on-connect': self.connect_callback,
            'on-release': self.release_callback,
            'interval': 0.02
        }
        self.sonatome_name = ''
        self.proccess = None
        self.clf = nfc.ContactlessFrontend()
        self.open_nfc()

    def exit_gracefully(self, signum, frame):
        print('Sonatome Teller program is attempting to exit gracefully')
        self.close()

    def open_nfc(self):
        self.nfc_is_open = self.clf.open('tty:AMA0')
        if self.nfc_is_open:
            print('Device opened.')
        else:
            print('Couldn\'t open device')
            self.clf.close()

    def connect_callback(self, tag):
        tag_id = str(tag).split('=')[1]
        try:
            self.sonatome_name = self.sonatome_ids[tag_id]
        except KeyError:
            print(tag_id)
        return True

    def release_callback(self, tag):
        if self.lid.value == 1 and self.sonatome_name != '' and self.proccess is None:
            print(self.sonatome_name)
            self.proccess = subprocess.Popen(['aplay', '/home/pi/git/ctd-design-studio/stories/' + self.sonatome_name + '.wav'])
        if self.lid.value == 0 and not self.proccess is None:
            self.proccess.kill()
            self.proccess = None

    def search_and_connect(self):
        started = time()
        termination_lambda = lambda: (time() - started) > 0.04 or self.kill_program == True
        self.clf.connect(rdwr=self.options, terminate=termination_lambda)

    def close(self):
        self.kill_program = True
        self.nfc_is_open = False
        self.lid.close()
        self.clf.close()
        self.neopixels.fill((0, 0, 0))
        self.neopixels.show()
    
    def update_leds(self):
        if self.framecount_LED <= 200:
            red = min(max(1 - self.framecount_LED / 200, 0), 1)
            green = min(max(self.framecount_LED / 200, 0), 1)
            blue = 0
        elif self.framecount_LED <= 400:
            red = 0
            green = min(max(1 - (self.framecount_LED - 200) / 200, 0), 1)
            blue = min(max((self.framecount_LED - 200) / 200, 0), 1)
        else:
            red = min(max((self.framecount_LED - 400) / 200, 0), 1)
            green = 0
            blue = min(max(1 - (self.framecount_LED - 400) / 200, 0), 1)
        color = (math.floor(red * 255), math.floor(green * 255), math.floor(blue * 255))
        self.neopixels.fill(color)
        self.neopixels.brightness = 0.5 + 0.3 * math.sin(self.framecount_LED * math.pi / 20)
        self.neopixels.show()
        self.framecount_LED = (self.framecount_LED + 1) % 600

if __name__ == '__main__':
    attepts_to_open = 10
    sonatome_teller = SonatomeTeller()
    while not sonatome_teller.kill_program and attepts_to_open > 0:
        sleep(0.4)
        sonatome_teller.update_leds()
        if sonatome_teller.nfc_is_open:
            try:
                sonatome_teller.search_and_connect()
            except:
                print('An unexpetced error occurred... closing device.\nError traceback:\n')
                traceback.print_exc()
                sonatome_teller.close()
        else:
            sonatome_teller.open_nfc()
            attepts_to_open -= 1
    print('Program should have exited gracefully by now.\nClosing device one last time just to be sure...\n')
    sonatome_teller.close()
