import pyfirmata
import time
from pyfirmata import util

board = pyfirmata.Arduino("COM8")
it = util.Iterator(board)
it.start()

servo9 = board.get_pin('d:9:s')
servo10 = board.get_pin('d:10:s')

while True:
    servo9.write(0)
    servo10.write(0)
    time.sleep(1)

    servo9.write(90)
    servo10.write(90)
    time.sleep(1)

    servo9.write(180)
    servo10.write(180)
    time.sleep(1)
