# Enables AP mode to allow configuration
def configBoot(config):
    import network
    import display
    ap = network.WLAN(network.AP_IF) # create access-point interface    
    ap.active(True)
    ap.config(essid=config['setup']['ssid'], \
                password=config['setup']['password'], \
                hidden=False,
                authmode=3) # authmode=3 means WPA2
    display.displayString("setup", 2000)
    display.displayString("192.168.4.1", 2000)

    from utils import registerFile
    registerFile("successfulBoot")
    del registerFile
    del network
    del display

    print('Connect to http://192.168.4.1')
    HTTPServer().listenAndServe()

class HTTPServer:
    def __init__(self):
        try:
            with open('./index.html', 'r') as indexFile:
                self._getResponse = indexFile.read()
        except Exception as error:
            print('Error reading file ./index.html')
            self._getResponse = '{{ INPUT }}'
        try:
            with open('./config.json', 'r') as configFile:
                print("Opened config file and embedding contents")
                self._getResponse = self._getResponse.replace('{{ INPUT }}', configFile.read(-1))
        except Exception as error:
            print('Error reading file ./config.json')
            self._getResponse = self._getResponse.replace('{{ INPUT }}', '')
        
    def listenAndServe(self):
        import socket
        import gc
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(('', 80))
        s.listen(5)
        s.settimeout(600) #Accept configurations during 10 minutes
        pendingConfig = True
        while pendingConfig:
            gc.collect()
            print("Available memory:", gc.mem_free())
            try:
                conn, addr = s.accept()
            except Exception as error:
                print('Error accepting connections:', error)
                break
            print('Got a connection from %s' % str(addr))
            conn.settimeout(10)
            request = b''
            partialRequest = conn.readline()
            request += partialRequest
            contentLength = 0
            while True:
                if not partialRequest or partialRequest == b'\r\n':
                    break
                try:
                    partialRequest = conn.readline()
                except Exception as error:
                    print('Error receiving')
                    partialRequest = b''
                    break
                if 'Content-Length: ' in partialRequest:
                   try:
                       contentLength = int(partialRequest[16:-2])
                       print ('Content Length is : ', contentLength)
                   except:
                       continue
                request += partialRequest
            if contentLength:
                partialRequest = conn.read(contentLength)
                request += partialRequest
            firstLineLength = request.find(b'\r\n')
            requestPath = request[:firstLineLength].split(b' ')[1].decode('ascii')
            print(request)
            print('Entire request:',len(request))
            response = 'Data received'
            if request[:4] == b'POST':
                print('Setting data')
                dataStart = request.find(b'\r\n\r\n')
                if dataStart != -1 and dataStart+4 != len(request):
                    print('Writing new config (',len(request[dataStart+4:]),'):', request[dataStart+4:])
                    try:
                        with open('.'+requestPath, 'w') as configFile:
                            configFile.write(request[dataStart+4:])
                        pendingConfig = False
                    except Exception as error:
                        print('Couldn\'t write data to', requestPath)
                        response = 'Couldn\'t write data to', requestPath
                else:
                    response = 'Error reading message'
            else:
                response = self._getResponse
            conn.write('HTTP/1.1 200 OK\n')
            conn.write('Content-Type: text/html\n')
            conn.write('Connection: close\n\n')
            conn.write(response)
            conn.close()
        
        del socket
        
        # Wait 2 seconds to sync filesystem
        from network import WLAN, AP_IF
        from utils import checkAndRemoveFile
        import time
        import machine

        print("Rebooting...")
        WLAN(AP_IF).active(False)
        checkAndRemoveFile("apMode")
        time.sleep(2)
        machine.reset()
        

