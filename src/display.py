import micropython
import time
from machine import Pin, WDT

# Quick reference for screen bits order:
#     0
#   5   1
#     6
#   4   2
#     3   7

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

class PowDisplay:
    noled = Pin(2, Pin.OUT) # This led is reversed: it is turned on when the .off method is invoked
    data = Pin(13, Pin.OUT)
    clock = Pin(12, Pin.OUT)
    latch = Pin(14, Pin.OUT)
    night = False
    refreshDelay = 1200

    # off turns off the entire display
    @micropython.native
    def off():
        clock = PowDisplay.clock
        data = PowDisplay.data
        # The "latch" Pin needs to be turned off to allow display modifications
        PowDisplay.latch.off()
        for _ in range(16):
            # This display works by sending each 16 bits in a row through the Pin "data".
            # To separate each bit, it is necessary to turn on "clock", set the "data" bit and
            # then turn again the "clock"
            clock.off()
            data.on()
            clock.on()
        # After sending the modification, the latch turns on again
        PowDisplay.latch.on()
    
    # displayBitLines should receive a list of 8 arrays of bits
    @micropython.native
    def displayBitLines(bit_lines, millis=1000):
        clock = PowDisplay.clock
        data = PowDisplay.data
        latch = PowDisplay.latch
        night = PowDisplay.night
        screen_lines = []
        for bit_line_index, bit_line in enumerate(bit_lines):
            values = [
                # First 8 bits are the inverted leds positions
                bit_line[7] ^ 1,
                bit_line[6] ^ 1,
                bit_line[5] ^ 1,
                bit_line[4] ^ 1,
                bit_line[3] ^ 1,
                bit_line[2] ^ 1,
                bit_line[1] ^ 1,
                bit_line[0] ^ 1,
                # Final 8 bits are for the position, having the order 4 3 2 1 8 7 6 5
                0, 0, 0, 0, 0, 0, 0, 0
            ]
            values[15 - bit_line_index^4] = 1
            screen_lines.append(values)
        startTime = time.ticks_ms()
        while (time.ticks_diff(time.ticks_ms(), startTime) < millis):
            for screen_line in screen_lines:
                # Apply character per character
                latch.off()
                for bit in screen_line:
                    clock.off()
                    data.value(bit)
                    clock.on()
                latch.on()
                if night:
                    # This is the night mode
                    latch.off()
                    for _ in range(16):
                        clock.off()
                        data.on()
                        clock.on()
                    latch.on()
                time.sleep_us(PowDisplay.refreshDelay)
        PowDisplay.off()

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
            bitLines = [ _symbols[' '] ] * int(spacesLeft/2) + bitLines \
                        + [ _symbols[' '] ] * (spacesLeft%2 + int(spacesLeft/2))
            PowDisplay.displayBitLines(bitLines, millis)
        # If length is bigger than the screen size, move the message
        elif messageLen > 8:
            iterations = messageLen - 8
            for iteration in range(iterations):
                PowDisplay.displayBitLines(bitLines[iteration:iteration+8], millis)
            PowDisplay.displayBitLines(bitLines[messageLen-8:], millis)
        # If length is exactly 8, just show it
        else:
            PowDisplay.displayBitLines(bitLines, millis)
    
    def displayAnimation(animation, cycles=1):
        millis = animation['millis']
        for _ in range(cycles):
            for value in animation['messages']:
                PowDisplay.displayString(value, millis)
    def displayLogo(millis=1000):
        PowDisplay.displayBitLines(_logo, millis)
