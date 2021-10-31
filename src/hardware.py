from machine import Pin
from constants import (
    D4,
    D7,
    D6,
    D5
)


class Led:
    state = False
    led = Pin(D4, Pin.OUT)

    @classmethod
    def on(cls):
        cls.led.off()
        cls.state = True

    @classmethod
    def off(cls):
        cls.led.on()
        cls.state = False

    @classmethod
    def toggle(cls):
        if cls.state:
            cls.off()
            cls.state = False
        else:
            cls.on()
            cls.state = True


data = Pin(D7, Pin.OUT)
clock = Pin(D6, Pin.OUT)
latch = Pin(D5, Pin.OUT)
