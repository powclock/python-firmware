# Author: Igor Ferreira
# License: MIT
# Version: 2.0.0
# Description: WiFi Manager for ESP8266 and ESP32 using MicroPython.

import machine
import network
import usocket
import ure
import utime as time
import env
from utils import url_decode


class WifiManager:

    def __init__(self, ssid='POW CLOCK', password=None):
        self.wlan_sta = network.WLAN(network.STA_IF)
        self.wlan_sta.active(True)
        self.wlan_ap = network.WLAN(network.AP_IF)

        self.ap_ssid = env.SSID
        self.ap_authmode = network.AUTH_OPEN

        self.sta_profiles = 'wifi.dat'

        # Prevents the device from automatically trying to connect to the last
        # saved network without first going through the steps defined in the
        # code.
        self.wlan_sta.disconnect()

        # Change to True if you want the device to reboot after configuration.
        # Useful if you're having problems with web server applications after
        # WiFi configuration.
        self.reboot = True

    def connect(self):
        if self.wlan_sta.isconnected():
            return
        profiles = self._read_profiles()
        for ssid, *_ in self.wlan_sta.scan():
            ssid = ssid.decode("utf-8")
            if ssid in profiles:
                password = profiles[ssid]
                if self._wifi_connect(ssid, password):
                    return

        # If we get here, no saved network was found.
        self._web_server()

    def disconnect(self):
        if self.wlan_sta.isconnected():
            self.wlan_sta.disconnect()

    def is_connected(self):
        return self.wlan_sta.isconnected()

    def get_address(self):
        return self.wlan_sta.ifconfig()

    def _write_profiles(self, profiles):
        lines = []
        for ssid, password in profiles.items():
            lines.append('{0};{1}\n'.format(ssid, password))
        with open(self.sta_profiles, 'w') as myfile:
            myfile.write(''.join(lines))

    def _read_profiles(self):
        try:
            with open(self.sta_profiles) as myfile:
                lines = myfile.readlines()
        except OSError:
            lines = []

        profiles = {}
        for line in lines:
            ssid, password = line.strip().split(';')
            profiles[ssid] = password
        return profiles

    def _wifi_connect(self, ssid, password):
        # for _ in range(100):
        #     try:
        #         routercon = network.WLAN(network.STA_IF)
        #         routercon.active(True)
        #         routercon.connect(ssid, password)
        #         ip_address = routercon.ifconfig()[0]
        #         if ip_address != '0.0.0.0':
        #             return True
        #     except Exception:
        #         time.sleep_ms(100)
        # return False

        print('Trying to connect to:', ssid)
        print(password)
        self.wlan_sta.connect(ssid, password)
        for _ in range(100):
            if self.wlan_sta.isconnected():
                print(
                    '\nConnected! Network information:',
                    self.wlan_sta.ifconfig()
                )
                return True
            else:
                print('.', end='')
                time.sleep_ms(100)
        print('\nConnection failed!')
        self.wlan_sta.disconnect()
        return False

    def _web_server(self):
        self.wlan_ap.active(True)
        self.wlan_ap.config(essid=self.ap_ssid, authmode=self.ap_authmode)
        server_socket = usocket.socket()
        server_socket.close()
        server_socket = usocket.socket(usocket.AF_INET, usocket.SOCK_STREAM)
        server_socket.setsockopt(usocket.SOL_SOCKET, usocket.SO_REUSEADDR, 1)
        server_socket.bind(('', 80))
        server_socket.listen(1)
        print(
            'Connect to', self.ap_ssid, 'with the password',
            'and access the captive portal at',
            self.wlan_ap.ifconfig()[0]
        )
        while True:
            if self.wlan_sta.isconnected():
                self.wlan_ap.active(False)
                if self.reboot:
                    print('The device will reboot in 5 seconds.')
                    time.sleep(5)
                    machine.reset()
                return
            self.client, addr = server_socket.accept()
            try:
                self.client.settimeout(5.0)
                self.request = b''
                try:
                    while True:
                        if '\r\n\r\n' in self.request:
                            # Fix for Safari browser
                            self.request += self.client.recv(512)
                            break
                        self.request += self.client.recv(128)
                except OSError:
                    # It's normal to receive timeout errors in this stage, we can safely ignore them.
                    pass
                if self.request:
                    url = ure.search(
                        '(?:GET|POST) /(.*?)(?:\\?.*?)? HTTP', self.request
                    ).group(1).decode('utf-8').rstrip('/')
                    if url == '':
                        self._handle_root()
                    elif url == 'configure':
                        self._handle_configure()
                    else:
                        self._handle_not_found()
            except Exception:
                print('Something went wrong! Reboot and try again.')
                return
            finally:
                self.client.close()

    def _send_header(self, status_code=200):
        self.client.send("""HTTP/1.1 {0} OK\r\n""".format(status_code))
        self.client.send("""Content-Type: text/html\r\n""")
        self.client.send("""Connection: close\r\n""")

    def _send_response(self, payload, status_code=200):
        self._send_header(status_code)
        self.client.sendall(
            """
            <!DOCTYPE html>
            <html lang="en">
                <head>
                    <title>WiFi Manager</title>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1">
                    <link rel="icon" href="data:,">
                </head>
                <body>
                    {0}
                </body>
            </html>
        """.format(payload)
        )
        self.client.close()

    def _handle_root(self):
        self._send_header()
        self.client.sendall(
            """
            <!DOCTYPE html>
            <html lang="en">
                <head>
                    <title>WiFi Manager</title>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1">
                    <link rel="icon" href="data:,">
                </head>
                <body>
                    <h1>{0}</h1>
                    <form action="/configure" method="post" accept-charset="utf-8">
        """.format(self.ap_ssid)
        )

        ssids = set()
        for ssid, *_ in self.wlan_sta.scan():
            ssid = url_decode(ssid.decode("utf-8").strip())
            if ssid and ssid not in ssids:
                print(f'>{ssid}<')
                self.client.sendall(
                    """
                        <p><input type="radio" name="ssid" value="{0}" id="{0}"><label for="{0}">&nbsp;{0}</label></p>
                    """.format(ssid)
                )
                ssids.add(ssid)

        self.client.sendall(
            """
                        <p><label for="password">Password:&nbsp;</label><input type="password" id="password" name="password"></p>
                        <p><input type="submit" value="Connect"></p>
                    </form>
                </body>
            </html>
        """
        )
        self.client.close()

    def _handle_configure(self):
        match = ure.search('ssid=([^&]*)&password=(.*)', self.request)
        if match:
            ssid = url_decode(match.group(1).decode('utf-8'))
            password = url_decode(match.group(2).decode('utf-8'))

            if len(ssid) == 0:
                self._send_response(
                    """<p>SSID must be providaded!</p><p>Go back and try again!</p>""",
                    400
                )
            elif self._wifi_connect(ssid, password):
                self._send_response(
                    """<p>Successfully connected to</p><h1>{0}</h1><p>IP address: {1}</p>"""
                    .format(ssid,
                            self.wlan_sta.ifconfig()[0])
                )
                profiles = self._read_profiles()
                profiles[ssid] = password
                self._write_profiles(profiles)
                time.sleep(5)
            else:
                self._send_response(
                    """<p>Could not connect to</p><h1>{0}</h1><p>Go back and try again!</p>"""
                    .format(ssid)
                )
                time.sleep(5)
        else:
            self._send_response("""<p>Parameters not found!</p>""", 400)
            time.sleep(5)

    def _handle_not_found(self):
        self._send_response("""<p>Path not found!</p>""", 404)
        time.sleep(5)
