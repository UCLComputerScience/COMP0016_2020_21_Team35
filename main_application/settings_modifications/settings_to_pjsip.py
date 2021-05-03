from requests import get
import socket
from main_application.connect_to_asterisk.asterisk_manager import ConnectAsteriskManager
import os
import sys


# Changing SIP Trunk settings
class SettingsToPjsip:
    def __init__(self, config_location, pjsip_port, provider_address, provider_port, provider_ip_addresses):
        if getattr(sys, 'frozen', False):
            self.application_path = os.path.dirname(sys.executable)
        else:
            self.application_path = os.path.dirname(__file__)
        self.config_location = os.path.join(self.application_path, config_location)
        self.pjsip_port = pjsip_port
        self.provider_address = provider_address
        self.provider_port = provider_port
        self.provider_ip_addresses = provider_ip_addresses

    def modify_transport_udp_nat(self, start):
        end = start
        public_ip = get('https://api.ipify.org').text

        for line in range(start, len(self.data)):
            end += 1
            if "bind" in self.data[line]:
                self.data[line] = 'bind=0.0.0.0:' + self.pjsip_port + '\n'
            elif "local_net" in self.data[line]:
                self.data[line] = 'local_net=' + self.local_ip + '\n'
            elif "external_media_address" in self.data[line]:
                self.data[line] = 'external_media_address=' + public_ip + '\n'
            elif "external_signaling_address" in self.data[line]:
                self.data[line] = 'external_signaling_address=' + public_ip + '\n'
                break

        return end

    def modify_provider_aors(self, start):
        end = start
        for line in range(start, len(self.data)):
            end += 1
            if "contact=sip:" in self.data[line]:
                self.data[line] = 'contact=sip:' + self.provider_address + ':' + self.provider_port + '\n'
                break

        return end

    def modify_provider_ident(self, start):
        match_index = 0
        line = start
        while line < len(self.data):
            if "match" in self.data[line]:
                if match_index == 0:
                    self.data[line] = ""
                    match_index = line
                else:
                    del self.data[line]
                    line -= 1
            elif not match_index == 0:
                break
            line += 1

        if not match_index == 0:
            for ip_address in self.provider_ip_addresses:
                self.data[match_index] += 'match=' + ip_address + '\n'
        else:
            i = 0
            for ip_address in self.provider_ip_addresses:
                if i == 0:
                    if not self.data[-1].strip():
                        self.data[-1] += 'match=' + ip_address + '\n'
                    else:
                        self.data.append('match=' + ip_address + '\n')
                    i += 1
                else:
                    self.data[-1] += 'match=' + ip_address + '\n'

    # Restarting Asterisk - easiest way to reload PJSIP totally, instantly
    def reload_pjsip(self):
        manager = ConnectAsteriskManager.connect_to_asterisk_manager()
        try:
            manager.command('core restart now')
        except:
            manager.close()

    def create_config(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        self.local_ip = s.getsockname()[0]
        s.close()

        with open(self.config_location, 'r') as file:
            self.data = file.readlines()
            file.close()

        data_index = self.modify_transport_udp_nat(0)
        data_index = self.modify_provider_aors(data_index)
        self.modify_provider_ident(data_index)

        with open(self.config_location, 'w') as file:
            file.writelines(self.data)
            file.close()

        self.reload_pjsip()

