
import network
import display
import time
import display
import powRequests
import ntptime
import gc

config = {}

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

    print("Updating time zone")
    updateTimezoneOffset()

    print('Starting main loop')
    cycleCounter = 0
    sources = load_sources()
    while True:
        gc.collect()
        cycleCounter+=1
        if cycleCounter % config['cycles_to_update'] == 0:
            sources = load_sources(sources)
        
        # This shouldn't be necessary:
        if config['cycles_to_reboot'] != 0 and cycleCounter % config['cycles_to_reboot'] == 0:
            from utils import registerFile
            registerFile("silentReboot")
            import machine
            machine.reset()
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

# Enable WiFi client mode, connect and start loop
def normalBoot(localConfig, silentBoot=False):

    global config
    config = localConfig

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
        
        from utils import registerFile
        registerFile("successfulBoot")
        del registerFile

        loop()
    wclient.disconnect()
    wclient.active(False)
    print('Can\'t connect to', config['wificlient']['ssid'])
