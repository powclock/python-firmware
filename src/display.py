import micropython
import time
from machine import Pin

# The following process is needed to display just only one character at the display.
# To display 8 characters, this process needs to be repeated 8 times
    # The "latch" Pin needs to be turned off to allow display modifications
    # This display works by sending each 16 bits in a row through the Pin "data".
    # To separate each bit, it is necessary to turn on "clock", set the "data" bit and
    # then turn again the "clock"
    # After sending the modification, the latch turns on again

# The 16 bits sent to modify one character, mean the following:
    # The first 8 bits are for the segments of the number and the point. Distributed in this way:
    #     0
    #   5   1
    #     6
    #   4   2
    #     3   7
    # These initial 8 bits must be inverted: 1 or on() means turn off the led and vice versa
    # Final 8 bits are for the position of the displayed character, having the order 4 3 2 1 8 7 6 5

# Night mode is intended to lower brightness. To use it, just write a character without position
# (final characters at 0) with first 8 bits at 0 too.

# The display must be refreshed after "refreshDelay" to maintain characters displayed.

_logo = [
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [1, 1, 0, 0, 1, 1, 1, 0],
    [1, 1, 0, 0, 0, 1, 1, 0],
    [0, 1, 0, 0, 0, 1, 1, 0],
    [0, 1, 0, 0, 0, 0, 1, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
]

_symbols = { #To do: implement Siekoo alphabet
    '0': [1, 1, 1, 1, 1, 1, 0, 0],
    '1': [0, 1, 1, 0, 0, 0, 0, 0],
    '2': [1, 1, 0, 1, 1, 0, 1, 0], # Also valid for z
    '3': [1, 1, 1, 1, 0, 0, 1, 0],
    '4': [0, 1, 1, 0, 0, 1, 1, 0],
    '5': [1, 0, 1, 1, 0, 1, 1, 0], # Also valid for s
    '6': [1, 0, 1, 1, 1, 1, 1, 0],
    '7': [1, 1, 1, 0, 0, 0, 0, 0],
    '8': [1, 1, 1, 1, 1, 1, 1, 0],
    '9': [1, 1, 1, 1, 0, 1, 1, 0],
    ".": [0, 0, 0, 0, 0, 0, 0, 1],
    "-": [0, 0, 0, 0, 0, 0, 1, 0],
    '_': [0, 0, 0, 1, 0, 0, 0, 0],
    ' ': [0, 0, 0, 0, 0, 0, 0, 0],
    '?': [1, 1, 0, 0, 1, 0, 1, 0],
    'a': [1, 1, 1, 1, 1, 0, 1, 0],
    'b': [0, 0, 1, 1, 1, 1, 1, 0],
    'c': [0, 0, 0, 1, 1, 0, 1, 0],
    'd': [0, 1, 1, 1, 1, 0, 1, 0],
    'e': [1, 0, 0, 1, 1, 1, 1, 0],
    'f': [1, 0, 0, 0, 1, 1, 1, 0],
    'g': [1, 0, 1, 1, 1, 1, 0, 0],
    'h': [0, 0, 1, 0, 1, 1, 1, 0],
    'i': [0, 0, 0, 0, 1, 0, 0, 0],
    'j': [0, 1, 1, 1, 1, 0, 0, 0],
    'k': [1, 0, 1, 0, 1, 1, 1, 0],
    'l': [0, 0, 0, 0, 1, 1, 0, 0],
    'm': [0, 0, 1, 0, 0, 0, 1, 0], # Second part of the m. First part is n
    'n': [0, 0, 1, 0, 1, 0, 1, 0],
    'o': [0, 0, 1, 1, 1, 0, 1, 0],
    'p': [1, 1, 0, 0, 1, 1, 1, 0],
    'q': [1, 1, 1, 0, 0, 1, 1, 0],
    'r': [0, 0, 0, 0, 1, 0, 1, 0],
    's': [1, 0, 1, 1, 0, 1, 1, 0],
    't': [0, 0, 0, 1, 1, 1, 1, 0],
    'u': [0, 0, 1, 1, 1, 0, 0, 0], # Also valid for v
    'v': [0, 0, 1, 1, 1, 0, 0, 0],
    'w': [0, 0, 1, 1, 0, 0, 0, 0], # Second part of the w. First part is u
    'y': [0, 1, 1, 1, 0, 1, 1, 0],
    'z': [1, 1, 0, 1, 1, 0, 1, 0],
    "↙": [0, 0, 0, 0, 1, 0, 0, 0],
    "↖": [0, 0, 0, 0, 0, 1, 0, 0],
    "⬆": [1, 0, 0, 0, 0, 0, 0, 0],
    "⬇": [0, 0, 0, 1, 0, 0, 0, 0],
    "↗": [0, 1, 0, 0, 0, 0, 0, 0],
    "↘": [0, 0, 1, 0, 0, 0, 0, 0],
}

# Quick reference for pins:
# Pin.on() Set pin to “1” output level.
# Pin.off() Set pin to “0” output level.
# Pin.value() Get value
#Change pin value with .on() and .off() is faster than .value() -> https://github.com/micropython/micropython/blob/master/ports/esp8266/machine_pin.c

# Powclock pinout
#D0 = 16
#D1 = 5
#D2 = 4
#D3 = 0
#D4 = 2
#D5 = 14
#D6 = 12
#D7 = 13
#D8 = 15
#D9 = 3
#D10 = 1

noled = Pin(2, Pin.OUT) # This led is reversed: it is turned on when the .off method is invoked
data = Pin(13, Pin.OUT)
clock = Pin(12, Pin.OUT)
latch = Pin(14, Pin.OUT)
night = False
dayRefreshDelay = 1000
nightRefreshDelay = 700

# displayOff turns off the entire display
@micropython.native
def displayOff():
    latch.off()
    for _ in range(16):
        clock.off()
        data.on()
        clock.on()
    latch.on()

# _raw_display accepts screen_lines as sl and millis as m
@micropython.native
def _raw_display(sl, m):
    start = time.ticks_ms()
    while (time.ticks_diff(time.ticks_ms(), start) < m):
        for char in sl:
            latch.off()
            for bit in char:
                clock.off()
                data.value(bit)
                clock.on()
            latch.on()
            if night:
                displayOff()
                time.sleep_us(nightRefreshDelay)
            else:
                time.sleep_us(dayRefreshDelay)
    displayOff()

# displayBitLines should receive a list of 8 arrays of bits
@micropython.native
def displayBitLines(bit_lines, millis=1000):
    screen_lines = []
    for bit_line_index, bit_line in enumerate(bit_lines):
        values = [
            bit_line[7] ^ 1,
            bit_line[6] ^ 1,
            bit_line[5] ^ 1,
            bit_line[4] ^ 1,
            bit_line[3] ^ 1,
            bit_line[2] ^ 1,
            bit_line[1] ^ 1,
            bit_line[0] ^ 1,
            0, 0, 0, 0, 0, 0, 0, 0
        ]
        values[15 - bit_line_index^4] = 1
        screen_lines.append(values)
    _raw_display(screen_lines, millis)

# displayString will print only characters in the symbols array
def displayString(message, millis=1000):
    messageChars = [char for char in message.lower()]
    current = messageChars[0]
    if current not in _symbols:
        bitLines = [ _symbols['?'] ]
    if current == 'm':
        bitLines = [ _symbols['n'], _symbols['m'] ]
    elif current == 'w':
        bitLines = [ _symbols['u'], _symbols['w'] ]
    else:
        bitLines = [ _symbols[current] ]

    for i in range(len(messageChars)-1):
        current = messageChars[i+1]
        if current == '.' and messageChars[i] != '.':
            # Add a dot to the previous character after making a copy
            last = len(bitLines) - 1
            bitLines[last] = bitLines[last].copy()
            bitLines[last][7] = 1
            del last
        elif current not in _symbols:
            bitLines.append( _symbols['?'] )
        else:
            if current == 'm':
                bitLines.append( _symbols['n'] )
            elif current == 'w':
                bitLines.append( _symbols['u'] )
            bitLines.append( _symbols[current] )
    del current
    del messageChars
            
    messageLen = len(bitLines)
    # If length is less than the screen size, add space to center the message
    if messageLen < 8:
        spacesLeft = 8 - messageLen
        bitLines = [ _symbols[' '] ] * (spacesLeft%2 + int(spacesLeft/2)) \
                    + bitLines \
                    + [ _symbols[' '] ] * int(spacesLeft/2)
        displayBitLines(bitLines, millis)
    # If length is bigger than the screen size, move the message
    elif messageLen > 8:
        for i in range(messageLen - 8):
            displayBitLines(bitLines[i:i+8], millis)
        displayBitLines(bitLines[messageLen-8:], millis)
    # If length is exactly 8, just show it
    else:
        displayBitLines(bitLines, millis)

def displayAnimation(animation, cycles=1):
    millis = animation['millis']
    for _ in range(cycles):
        for value in animation['messages']:
            displayString(value, millis)
def displayLogo(millis=1000):
    displayBitLines(_logo, millis)
