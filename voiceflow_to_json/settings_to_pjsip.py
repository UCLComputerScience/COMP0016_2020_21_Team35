from requests import get
import asterisk.manager
import socket
import os

class SettingsToPjsip:
    def __init__(self, config_location, pjsip_port, provider_address, provider_port, provider_ip_addresses):
        self.dirname = os.path.dirname(__file__)
        self.config_location = os.path.join(self.dirname, config_location)
        self.pjsip_port = pjsip_port
        self.provider_address = provider_address
        self.provider_port = provider_port
        self.provider_ip_addresses = provider_ip_addresses
        self.config_file = open(self.config_location, "w")

    def create_transport_udp_nat(self):
        self.config_file.write('[tansport-udp-nat]\n')
        self.config_file.write('type=transport\n')
        self.config_file.write('protocol=udp\n')
        self.config_file.write('bind=0.0.0.0:' + self.pjsip_port + '\n')
        public_ip = get('https://api.ipify.org').text
        self.config_file.write('external_media_address=' + public_ip + '\n')
        self.config_file.write('external_signaling_address=' + public_ip + '\n\n')

    def create_trunk(self):
        self.config_file.write('[twilio-trunks](!)\n')
        self.config_file.write('type=endpoint\n')
        self.config_file.write('transport=transport-udp-nat\n')
        self.config_file.write('context=from-twilio\n')
        self.config_file.write('disallow=all\n')
        self.config_file.write('allow=ulaw\n\n')

    def create_auth_out(self):
        self.config_file.write('[auth-out](!)\n')
        self.config_file.write('type=auth\n')
        self.config_file.write('auth_type=userpass\n\n')

    def create_provider(self):
        self.config_file.write('[twilio0](twilio-trunks)\n')
        self.config_file.write('aors=twilio0-aors\n\n')

    def create_provider_aors(self):
        self.config_file.write('[twilio0-aors]\n')
        self.config_file.write('type=aor\n')
        self.config_file.write('contact=sip:' + self.provider_address + ':' + self.provider_port + '\n\n')

    def create_provider_ident(self):
        self.config_file.write('[twilio0-ident]\n')
        self.config_file.write('type=identify\n')
        self.config_file.write('endpoint=twilio0\n')
        for ip_address in self.provider_ip_addresses:
            self.config_file.write('match=' + ip_address + '\n')
        self.config_file.write('\n')

    def create_endpoint(self):
        self.config_file.write('[endpoint-basic](!)\n')
        self.config_file.write('type=endpoint\n')
        self.config_file.write('transport=transport-udp-nat\n')
        self.config_file.write('context=from-phones\n')
        self.config_file.write('disallow=all\n')
        self.config_file.write('allow=ulaw\n\n')

    def create_auth_userpass(self):
        self.config_file.write('[auth-userpass](!)\n')
        self.config_file.write('type=auth\n')
        self.config_file.write('auth_type=userpass\n\n')

    def create_aor_single_reg(self):
        self.config_file.write('[aor-single-reg](!)\n')
        self.config_file.write('type=aor\n')
        self.config_file.write('max_contacts=1\n\n')

    def create_1001(self):
        self.config_file.write('[1001](endpoint-basic)\n')
        self.config_file.write('auth=auth1001\n')
        self.config_file.write('aors=1001\n\n')
        self.config_file.write('[auth1001](auth-userpass)\n')
        self.config_file.write('password=Asterisk15\n')
        self.config_file.write('username=1001\n\n')
        self.config_file.write('[1001](aor-single-reg)')

    def create_config(self):
        self.create_transport_udp_nat()
        self.create_trunk()
        self.create_auth_out()
        self.create_provider()
        self.create_provider_aors()
        self.create_provider_ident()
        self.create_endpoint()
        self.create_auth_userpass()
        self.create_aor_single_reg()
        self.create_1001()
        self.config_file.close()
        manager = asterisk.manager.Manager()
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        manager.connect(local_ip)
        manager.login('max', '12345678')
        manager.command('pjsip reload')
        response = manager.status()
        print(response)
        manager.close()