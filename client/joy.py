import serial
import pygame as pg
import time
import os

state = 0

port = os.environ.get('DTV2SER_PORT','/dev/ttyUSB0')
speed = os.environ.get('DTV2SER_SPEED',250000)

ser = serial.Serial(port=port,baudrate=speed,rtscts=1)
time.sleep(2)
ser.write('j\n') # enter joystream mode

def emit():
    global ser
    print state
    ser.write(chr(state))

keys = { pg.K_w:1, pg.K_s:2, pg.K_a:4, pg.K_d:8, pg.K_RETURN:16 }

def down(key):
    global state
    state |= keys.get(key,0)
    emit()

def up(key):
    global state
    state &= ~keys.get(key,0)
    emit()

pg.init()
pg.display.set_mode((320,240))
pg.event.set_allowed([pg.QUIT,pg.KEYDOWN,pg.KEYUP])

while True:
    event = pg.event.wait()
    if event.type == pg.KEYDOWN:
        down(event.key)
    elif event.type == pg.KEYUP:
        up(event.key)
    elif event.type == pg.QUIT:
        break

ser.write(chr(0x80))
