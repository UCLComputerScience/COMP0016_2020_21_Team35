from requests import get
import asterisk.manager
import socket
import os
import sys

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

        # self.config_file.write('[transport-udp-nat]\n')
        # self.config_file.write('type=transport\n')
        # self.config_file.write('protocol=udp\n')
        # self.config_file.write('bind=0.0.0.0:' + self.pjsip_port + '\n')
        # self.config_file.write('local_net=' + self.local_ip + '\n')
        # public_ip = get('https://api.ipify.org').text
        # self.config_file.write('external_media_address=' + public_ip + '\n')
        # self.config_file.write('external_signaling_address=' + public_ip + '\n\n')

    # def create_trunk(self):
    #     self.config_file.write('[twilio-trunks](!)\n')
    #     self.config_file.write('type=endpoint\n')
    #     self.config_file.write('transport=transport-udp-nat\n')
    #     self.config_file.write('context=from-twilio\n')
    #     self.config_file.write('disallow=all\n')
    #     self.config_file.write('allow=ulaw\n\n')

    # def create_auth_out(self):
    #     self.config_file.write('[auth-out](!)\n')
    #     self.config_file.write('type=auth\n')
    #     self.config_file.write('auth_type=userpass\n\n')

    # def create_provider(self):
    #     self.config_file.write('[twilio0](twilio-trunks)\n')
    #     self.config_file.write('aors=twilio0-aors\n\n')

    def modify_provider_aors(self, start):
        end = start
        for line in range(start, len(self.data)):
            end += 1
            if "contact=sip:" in self.data[line]:
                self.data[line] = 'contact=sip:' + self.provider_address + ':' + self.provider_port + '\n'
                break

        return end
        # self.config_file.write('[twilio0-aors]\n')
        # self.config_file.write('type=aor\n')
        # self.config_file.write('contact=sip:' + self.provider_address + ':' + self.provider_port + '\n\n')

    def modify_provider_ident(self, start):
        match_index = 0
        for line in range(start, len(self.data)):
            if line >= len(self.data):
                break
            if "match" in self.data[line]:
                if match_index == 0:
                    self.data[line] = ""
                    match_index = line
                else:
                    del self.data[line]
            elif not match_index == 0:
                break

        for ip_address in self.provider_ip_addresses:
            self.data[match_index] += 'match=' + ip_address + '\n'

        # self.config_file.write('[twilio0-ident]\n')
        # self.config_file.write('type=identify\n')
        # self.config_file.write('endpoint=twilio0\n')
        # for ip_address in self.provider_ip_addresses:
        #     self.config_file.write('match=' + ip_address + '\n')
        # self.config_file.write('\n')

    # def create_endpoint(self):
    #     self.config_file.write('[endpoint-basic](!)\n')
    #     self.config_file.write('type=endpoint\n')
    #     self.config_file.write('transport=transport-udp-nat\n')
    #     self.config_file.write('context=from-phones\n')
    #     self.config_file.write('disallow=all\n')
    #     self.config_file.write('allow=ulaw\n\n')

    # def create_auth_userpass(self):
    #     self.config_file.write('[auth-userpass](!)\n')
    #     self.config_file.write('type=auth\n')
    #     self.config_file.write('auth_type=userpass\n\n')

    # def create_aor_single_reg(self):
    #     self.config_file.write('[aor-single-reg](!)\n')
    #     self.config_file.write('type=aor\n')
    #     self.config_file.write('max_contacts=1\n\n')

    # def create_1001(self):
    #     self.config_file.write('[1001](endpoint-basic)\n')
    #     self.config_file.write('auth=auth1001\n')
    #     self.config_file.write('aors=1001\n\n')
    #     self.config_file.write('[auth1001](auth-userpass)\n')
    #     self.config_file.write('password=Asterisk15\n')
    #     self.config_file.write('username=1001\n\n')
    #     self.config_file.write('[1001](aor-single-reg)')

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


        # data_index = self.modify_transport_udp_nat(0)
        # self.create_trunk()
        # self.create_auth_out()
        # self.create_provider()
        # self.modify_provider_aors()
        # self.modify_provider_ident()
        # self.create_endpoint()
        # self.create_auth_userpass()
        # self.create_aor_single_reg()
        # self.create_1001()
        # self.config_file.close()
        manager = asterisk.manager.Manager()
        manager.connect(self.local_ip)
        manager.login('max', '12345678')
        try:
            manager.command('core restart now')
        except:
            pass
        # manager.command('pjsip reload')
        # response = manager.status()
        # print(response)
        # manager.close()