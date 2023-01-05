import logging
import math
import serial
from serial.tools import list_ports
from time import sleep

import colorsys
import random
from matrix import *

HANDSHAKE = bytearray([0xAF, 0xEA, 0x1F, 0x10, 0x05])
RESPONSE = bytearray([0xF1, 0x10])
VID = 0x2E8A
PID = 0x000A
BAUD = 115200
TIMEOUT = 1

logging.basicConfig(level=logging.INFO)

def beginMonitorThread(ser):
    from threading import Thread
    def f(serial):
        print("Serial init", flush = True)
        while True:
            print("Serial: " + str(serial.readline()), flush = True)
    
    Thread(target = f, args=(ser,)).start()

def connect():
    devices = list(map(lambda port : port.device, filter(lambda port : port.vid == 0x2E8A and port.pid == 0x000A, list_ports.comports())))

    def handshake(device):
        logging.debug(f"Attempting connection to {device}...")
        ser = serial.Serial(device, BAUD, timeout=TIMEOUT)
        logging.debug("Connected. Beginning handshake...")

        ser.write(HANDSHAKE)
        result = ser.readline()[:len(RESPONSE)]
        logging.debug(f"Device responded with [{result.hex()}]")

        if result == RESPONSE:
            logging.debug("Handshake success!")
            return ser
        
        logging.debug("Handshake fail!")
        return None

    logging.debug(f"Connected USB serial devices (VID={hex(VID)}, PID={hex(PID)}): {devices}")

    ser = None
    for d in devices:
        ser = handshake(d)
        if ser != None:
            break

    if ser == None:
        logging.error("No compatible devices found.")
        exit(-1)
    
    logging.info(f"Connected to serial port {ser.name} with baud rate {BAUD}, timeout={TIMEOUT}.")



    return ser

mapping = None
def ledMapping():
    global mapping
    if mapping != None:
        return mapping

    logging.debug("Initializing mapping")

    mapping = LedMapping()
    mapping.set(0, 0, 60)
    mapping.set(0, 1, 61)
    mapping.set(0, 2, 62)
    mapping.set(0, 3, 63)
    mapping.set(0, 4, 64)
    mapping.set(0, 5, 65)
    mapping.set(0, 6, 66)
    mapping.set(0, 7, 67)
    mapping.set(0, 8, 68)
    mapping.set(0, 9, 69)
    mapping.set(0, 10, 70)
    mapping.set(0, 11, 71)

    mapping.set(1, 0, 59)
    mapping.set(1, 1, 58)
    mapping.set(1, 2, 57)
    mapping.set(1, 3, 56)
    mapping.set(1, 4, 55)
    mapping.set(1, 5, 54)
    mapping.set(1, 6, 53)
    mapping.set(1, 7, 52)
    mapping.set(1, 8, 51)
    mapping.set(1, 9, 50)
    mapping.set(1, 10, 49)
    mapping.set(1, 11, 48)

    mapping.set(2, 0, 36)
    mapping.set(2, 1, 37)
    mapping.set(2, 2, 38)
    mapping.set(2, 3, 39)
    mapping.set(2, 4, 40)
    mapping.set(2, 5, 41)
    mapping.set(2, 6, 42)
    mapping.set(2, 7, 43)
    mapping.set(2, 8, 44)
    mapping.set(2, 9, 45)
    mapping.set(2, 10, 46)
    mapping.set(2, 11, 47)

    mapping.set(3, 0, 35)
    mapping.set(3, 1, 34)
    mapping.set(3, 2, 33)
    mapping.set(3, 3, 32)
    mapping.set(3, 4, 31)
    mapping.set(3, 5, 30)
    mapping.set(3, 6, 29)
    mapping.set(3, 7, 28)
    mapping.set(3, 8, 27)
    mapping.set(3, 9, 26)
    mapping.set(3, 10, 25)
    mapping.set(3, 11, 24)

    mapping.set(4, 0, 12)
    mapping.set(4, 1, 13)
    mapping.set(4, 2, 14)
    mapping.set(4, 3, 15)
    mapping.set(4, 4, 16)
    mapping.set(4, 5, 17)
    mapping.set(4, 6, 18)
    mapping.set(4, 7, 19)
    mapping.set(4, 8, 20)
    mapping.set(4, 9, 21)
    mapping.set(4, 10, 22)
    mapping.set(4, 11, 23)

    mapping.set(5, 0, 11)
    mapping.set(5, 1, 10)
    mapping.set(5, 2, 9)
    mapping.set(5, 3, 8)
    mapping.set(5, 4, 7)
    mapping.set(5, 5, 6)
    mapping.set(5, 6, 5)
    mapping.set(5, 7, 4)
    mapping.set(5, 8, 3)
    mapping.set(5, 9, 2)
    mapping.set(5, 10, 1)
    mapping.set(5, 11, 0)

    return mapping

class Renderer:
    def __init__(self, matrix: LedMatrix, mapping: LedMapping, serial: serial.Serial):
        self.matrix = matrix
        self.mapping = mapping
        self.serial = serial

    def clear(self, color = Color(0, 0, 0)):
        self.matrix.clear(color)
    
    def set(self, row, col, color):
        self.matrix.set(row, col, color)
    
    def draw(self):
        bytes = bytearray(mapMatrixToBytes(self.matrix, self.mapping))
        # for i in range(0, len(bytes)):
            # print(i, bytes[i])
        logging.debug("Writing mode 0 over serial")
        self.serial.write(b'0\r')
        logging.debug(f"Sending bytes (length={len(bytes)}) over serial")
        self.serial.write(bytes)
        self.serial.write(b'\r')

def state1(renderer: Renderer):
    color = 0
    for i in range(0, 12):
        renderer.clear()
        for j in range(0, 6):
            c = colorsys.hsv_to_rgb(color / 360.0, 1.0, 1.0)
            renderer.set(j, i, Color(c[0] * 255, c[1] * 255, c[2] * 255))
        
        renderer.draw()

        sleep(0.02)

        color = (color+20) % 360

    for i in range(0, 12):
        renderer.clear()
        for j in range(0, 6):
            c = colorsys.hsv_to_rgb(color / 360.0, 1.0, 1.0)
            renderer.set(j, 11-i, Color(c[0] * 255, c[1] * 255, c[2] * 255))
        
        renderer.draw()

        sleep(0.02)

        color = (color+20) % 360

def state1a(renderer: Renderer):
    color = 0
    for i in range(0, 6):
        renderer.clear()
        for j in range(0, 12):
            c = colorsys.hsv_to_rgb(color / 360.0, 1.0, 1.0)
            renderer.set(i, j, Color(c[0] * 255, c[1] * 255, c[2] * 255))
        
        renderer.draw()

        sleep(0.02)

        color = (color+20) % 360

    for i in range(0, 6):
        renderer.clear()
        for j in range(0, 12):
            c = colorsys.hsv_to_rgb(color / 360.0, 1.0, 1.0)
            renderer.set(5-i, j, Color(c[0] * 255, c[1] * 255, c[2] * 255))
        
        renderer.draw()

        sleep(0.02)

        color = (color+20) % 360


def state2(renderer: Renderer):
    color = 0
    for r in range(0, 6):
        for c in range(0, 12):
            renderer.clear()
        
            co = colorsys.hsv_to_rgb(color / 360.0, 1.0, 1.0)
            renderer.set(r, c, Color(co[0] * 255, co[1] * 255, co[2] * 255))
        
            renderer.draw()

            sleep(0.01)

            color = (color+20) % 360

def state3(renderer: Renderer):
    hueOffset = 360
    for i in range(0, 100):
        for r in range(0, 6):
            for c in range(0, 12):
                hue = (hueOffset - c * 10) % 360
                co = colorsys.hsv_to_rgb(hue / 360.0, 1.0, 1.0)
                renderer.set(r, c, Color(co[0] * 255, co[1] * 255, co[2] * 255))

        renderer.draw()
        hueOffset += 10
        sleep(0.05)

def clamp(v, a, b):
    if v < a:
        return a
    if v > b:
        return b
    return v

def state4(renderer: Renderer):
    loop = 0
    x = 0
    y = 50
    vx = 200
    vy = 0
    ay = -4000
    
    mx = 120.0
    my = 60.0

    delta = 0.02

    color = Color(255, 255, 255)
    while loop < 200:
        x += vx * delta
        vy += ay * delta
        y += vy * delta

        # vy = clamp(vy, -600, 600)

        if x >= mx:
            x = mx - (x - mx)
            vx = -vx
            color = Color(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        elif x < 0:
            x = -x
            vx = -vx
            color = Color(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        
        if y < 0:
            y = -y
            vy = -vy
            # color = Color(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        
        px = clamp(int(x / 10), 0, 11)
        py = clamp(int(y / 10), 0, 5)

        renderer.clear()
        renderer.set(5-py, px, color)
        renderer.draw()

        loop += 1

        sleep(delta)

def state5(renderer: Renderer):
    t = 0
    for a in range(0, 500):
        v = 0.5 + 0.5 * math.sin(t / 180 * math.pi)
        color = Color(v * 255, v * 255, v * 255)
        renderer.clear()
        for r in range(0, 6):
            for c in range(0, 12):
                renderer.set(r, c, color)
        
        renderer.draw()

        t += 10

        if t > 360:
            break

        sleep(0.02)

    t = 0
    h = random.random()
    s = random.random()
    for a in range(0, 100):
        if t > 360:
            h = random.random()
            s = random.random()
            t -= 360

        v = 0.5 + 0.5 * math.cos(t / 180 * math.pi)
        co = colorsys.hsv_to_rgb(h, 1, v)
        color = Color(co[0] * 255, co[1] * 255, co[2] * 255)
        renderer.clear()
        for r in range(0, 6):
            for c in range(0, 12):
                renderer.set(r, c, color)
        
        renderer.draw()

        t += 10



        sleep(0.05)

def state6(renderer: Renderer):
    for _ in range(0, 500):
        for r in range(0, 6):
            for c in range(0, 12):
                co = colorsys.hsv_to_rgb(random.random(), 1.0, 1.0)
                color = Color(co[0] * 255, co[1] * 255, co[2] * 255)
                renderer.set(r, c, color)
        renderer.draw()
        sleep(0.02)



def begin(serial):
    logging.debug("Performing initial setup")
    mapping = ledMapping()
    matrix = LedMatrix(12, 6)

    renderer = Renderer(matrix, mapping, serial)
    hueOffset = 360
    while True:
        hue = (hueOffset) % 360
        co = colorsys.hsv_to_rgb(hue / 360.0, 0.6, 0.4)
        for r in range(0, 6):
            for c in range(0, 12):
                renderer.set(r, c, Color(co[0] * 255, co[1] * 255, co[2] * 255))

        renderer.draw()
        hueOffset += 2
        sleep(0.02)

    while True:
        # state6(renderer)
        # state5(renderer)
        state1(renderer)
        state1a(renderer)

        state2(renderer)
        state3(renderer)
        state4(renderer)

    # matrix.set(0, 0, Color(255, 0, 255))
    # matrix.set(0, 1, Color(255, 0, 0))
    # matrix.set(5, 11, Color(255, 255, 255))
    # bytes = bytearray(mapMatrixToBytes(matrix, mapping))
    # for i in range(0, len(bytes)):
    #     print(i, bytes[i])
    # serial.write(b'0\r')
    # serial.write(bytes)
    # serial.write(b'\r')




if __name__ == "__main__":
    logging.debug("LedController started")
    ser = connect()

    begin(ser)
