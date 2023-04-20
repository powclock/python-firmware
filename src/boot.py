import esp
import machine
import network
import gc
import display

# Enable debugging
esp.osdebug(0)

# Set the CPU freq to 160 MHz
machine.freq(int(16e7))

# Enable garbage collector
gc.enable()
gc.collect()

# Disable WiFi
network.WLAN(network.STA_IF).active(False)
network.WLAN(network.AP_IF).active(False)

# Shutdown lights
display.displayOff()
display.noled.on()

print('\n\n\nBooting PowClock')
