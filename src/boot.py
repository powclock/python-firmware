print('\n\n\nBooting PowClock')

# Disable debugging
import esp
esp.osdebug(None)
del esp

# Set the CPU freq to 160 MHz
import machine
machine.freq(int(16e7))
del machine

# Shutdown lights
import display
display.displayOff()
display.noled.on()
del display

# Enable garbage collector
import gc
gc.enable()
gc.collect()
#print("Mem after free", gc.mem_free())
