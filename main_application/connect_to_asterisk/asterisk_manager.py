import asterisk.manager
import socket


class ConnectAsteriskManager:
    # Connect to Asterisk manager on current IP
    def connect_to_asterisk_manager(self):
        manager = asterisk.manager.Manager()
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        manager.connect(local_ip)
        manager.login('Asterisk13', 'AsteriskManager58')
        return manager