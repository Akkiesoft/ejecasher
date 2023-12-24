# Coin counter with seg14x4 display
# (You'll need the coins acceptor)

import time
import board
import busio
import digitalio
from adafruit_ht16k33 import segments
import uhat_porter_pico_type_p as board_bcm

i2c = busio.I2C(board_bcm.BCM3, board_bcm.BCM2)
display = segments.Seg14x4(i2c)
display.fill(0)

coin_sw = digitalio.DigitalInOut(board_bcm.BCM18)
coin_sw.switch_to_input(pull=digitalio.Pull.UP)

while True:
    coin_count = 0
    display.print("    .")
    balance = input("put balance: ")
    if balance == "":
        continue
    try:
        balance = int(balance)
        if balance < 100:
            continue
    except:
        continue
    print("please insert coin")
    display.print("    0")
    while balance:
        if not coin_sw.value:
            coin_count += 100
            balance -= 100
            #print(coin_count)
            display.print("    ")
            display.print(coin_count)
            time.sleep(0.2)
    print("OK")
    time.sleep(1)
    display.print(" THX.")
    time.sleep(3)
