import gc
from config import loadConfig, config
import display
import powRequests
import json
import network
import time
import ntptime
import machine

def testDisplay():
    for i in range(20):
        display.nightRefreshDelay = (i+1)*100
        print("night", display.nightRefreshDelay)
        display.night = True
        display.displayString("888-"+f'{display.nightRefreshDelay:04d}',6000)
        display.dayRefreshDelay = (i+1)*100
        print("day", display.dayRefreshDelay)
        display.night = False
        display.displayString("888-"+f'{display.dayRefreshDelay:04d}',6000)

# Creates a file to prepare a silent reboot (less verbose at start time)
def silentReboot():
    print("Silent reboot")
    try:
        open("silentReboot","x").close()
    except:
        pass
    machine.reset()

# Creates a file to register a succesful boot
def registerSuccessfulInitialization():
    try:
        open("successfulBoot","x").close()
    except:
        print("Couldn't register successful boot")

# Returns true if file exists at the removal time
def checkAndRemoveFile(filename):
    import os
    try:
        os.remove(filename)
        return True
    except:
        return False

# Use worldtimeapi.org to adjust time
def updateTimezoneOffset():
    if not config['utc_offset_update']:
        return
    url = "http://worldtimeapi.org/api/ip"
    update_reason = "ip"
    if config['timezone'] != "":
        url = "http://worldtimeapi.org/api/timezone/"+config['timezone']
        update_reason = config['timezone']
    try:
        response = powRequests.request('GET', url)
        parsed_response = response.json()
        response.close()
        new_offsets = parsed_response['utc_offset'].split(':')
        config['utc_offset'] = int(new_offsets[0])*3600 + int(new_offsets[1])*60
        print('New timezone offset for', update_reason, 'is', config['utc_offset'])
    except:
        print("Couldn't update timezone offset")

# Download information from webservers in JSON format
def load_sources(oldSources=None):
    print('Loading sources')
    display.displayAnimation(config['animations']['loading_2'], 2)

    if not network.WLAN(network.STA_IF).isconnected():
        sources = {}
        print('WiFi not connected. Showing errors.')
        for source, source_config in config['sources'].items():
            sources[source] = {}
            for attribute, fields in config['sources'][source]['attributes'].items():
                sources[source][attribute] = "conn err"
        if oldSources != None:
            return oldSources
        return sources

    # Sync time
    try:
        ntptime.settime()
    except Exception as error:
        print("Couldn't sync time")
        print(error)

    sources = {}
    for source, source_config in config['sources'].items():
        sources[source] = {}

        # Prepare request
        data = None
        if 'data' in source_config:
            data = json.dumps(source_config['data'])
        headers = {}
        if 'headers' in source_config:
            headers = source_config['headers']
        
        # Download source
        try:
            print('Requesting', source_config['url'])
            response = powRequests.request(source_config['method'].upper(),
                            source_config['url'], data=data, headers=headers)
            parsed_response = response.json()
            response.close()
            print('Request complete')
        except Exception as error:
            print("Error requesting " + source_config['url'], error)
            if oldSources != None:
                sources[source] = oldSources[source]
            else:
                for attribute, fields in config['sources'][source]['attributes'].items():
                    sources[source][attribute] = "http err"
            continue

        # Parse response
        try:
            for attribute, fields in config['sources'][source]['attributes'].items():
                value = parsed_response
                for field in fields:
                    value = value[field]
                sources[source][attribute] = value
        except Exception as error:
            print("Error parsing response", error)
            if oldSources != None:
                sources[source] = oldSources[source]
            else:
                for attribute, fields in config['sources'][source]['attributes'].items():
                    sources[source][attribute] = "resp err"
            continue

    return sources

# Decide whether to run with full brightness or not
def checkNightMode():
    if config['night_mode'] == [] or len(config['night_mode']) != 2:
        return True
    start_str = config['night_mode'][0].split(':')
    end_str = config['night_mode'][1].split(':')
    start_hour = int(start_str[0])
    end_hour = int(end_str[0])
    if start_hour < end_hour:
        print('Night mode is inverted. Error')
        return True
    now = time.gmtime(time.time() + int(config['utc_offset']))
    if now[3] > start_hour or now[3] < end_hour:
        return True
    if now[3] == start_hour and now[4] >= int(start_str[1]):
        return True
    if now[3] == end_hour and now[4] < int(end_str[1]):
        return True
    return False

# Loop to run indefinetly during the normal operation
def loop():
    print('Starting main loop')
    cycleCounter = 0
    sources = load_sources()
    while True:
        gc.collect()
        cycleCounter+=1
        if cycleCounter % config['cycles_to_update'] == 0:
            sources = load_sources(sources)
        
        #This shouldn't be necessary:
        if config['cycles_to_reboot'] != 0 and cycleCounter % config['cycles_to_reboot'] == 0:
            silentReboot()
        display.night = checkNightMode()

        for slide in config['slides']:
            print("Cycle", cycleCounter, slide)

            # Show the initial animation if exists
            try:
                display.displayAnimation(
                    config['animations'][slide['transitions'].get('in')['animation']],
                    slide['transitions']['in'].get('cycles', 1)
                )
            except:
                pass #No initial transition

            # Decide how much time the message will be posted
            millis = slide['millis'] if 'millis' in slide else 1000

            # Show the time updating it each second
            if slide['message'] == '{time}':
                for _ in range(millis / 1000):
                    now = time.gmtime(time.time() + int(config['utc_offset']))
                    display.displayString(f'{now[3]:02d}.{now[4]:02d}.{now[5]:02d}', 1000)
            # Show date
            elif slide['message'] == '{date}':
                now = time.gmtime(time.time() + int(config['utc_offset']))
                display.displayString(f'{now[2]:02d}-{now[1]:02d}-{(now[0] % 100):02d}', millis)
            # Show any other message
            else:
                message = slide['message']
                # Process the message (variables are processed between {} )
                if '{' in message:
                    source = slide['source']
                    message = message.replace(
                        '{', "sources['" + source + "']['"
                    )
                    message = message.replace('}', "']")
                    try:
                        message = eval(message, {'sources': sources})
                    except:
                        print("Eval error", message, sources)
                        message = "eual err"
                display.displayString(str(message), millis)

            # Show the final animation if exists
            try:
                display.displayAnimation(
                    config['animations'][slide['transitions'].get('out')['animation']],
                    slide['transitions'].get('out').get('cycles', 1)
                )
            except:
                pass #No final transition

# Enables AP mode to allow configuration
def configBoot():
    ap = network.WLAN(network.AP_IF) # create access-point interface
    ap.active(True)
    ap.config(essid=config['setup']['ssid'], \
                password=config['setup']['password'], \
                authmode=3) # authmode=3 means WPA2
    display.displayString("setup", 2000)
    display.displayString("192.168.4.1", 2000)
    print('Connect to http://192.168.4.1')
    registerSuccessfulInitialization()
    import httpServer
    httpServer.HTTPServer().listenAndServe()

# Enable WiFi client mode, connect and start loop
def normalBoot():
    print('Trying to connect to', config['wificlient']['ssid']) #, 'with password', config['wificlient']['password'])
    wclient = network.WLAN(network.STA_IF)
    wclient.active(True)
    wclient.connect(config['wificlient']['ssid'], config['wificlient']['password'])

    # Let it try to connect for 30 seconds
    startTime = time.ticks_ms()
    if not silentBoot:
        display.displayString("scanning", 1000)
    while not wclient.isconnected() and time.ticks_diff(time.ticks_ms(), startTime) < 30000:
        display.displayAnimation(config['animations']['loading_1'], 3)
    if wclient.isconnected():
        netconf = wclient.ifconfig()
        print(netconf)
        if not silentBoot:
            display.displayString("paired", 1000)
            display.displayString(netconf[0], 1000)
        registerSuccessfulInitialization()
        updateTimezoneOffset()
        loop()
    wclient.disconnect()
    wclient.active(False)
    print('Can\'t connect to', config['wificlient']['ssid'])





# Initialize
print('Loading config')
loadConfig()

previousBootSuccessful = checkAndRemoveFile("successfulBoot")
silentBoot = checkAndRemoveFile("silentBoot")

if previousBootSuccessful and silentBoot:
    print("Silent rebooting")
else:
    display.displayLogo()

if previousBootSuccessful and config['wificlient']['ssid'] != '':
    normalBoot()

print('Enabling AP to allow configuration')
configBoot()
