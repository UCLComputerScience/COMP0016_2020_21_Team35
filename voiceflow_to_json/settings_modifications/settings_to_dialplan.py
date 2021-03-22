import asterisk.manager
import socket
import os
import sys

class SettingsToDialplan:
    def __init__(self, filepath, node_ids, phone_numbers, provider_number):
        if getattr(sys, 'frozen', False):
            self.application_path = os.path.dirname(sys.executable)
        else:
            self.application_path = os.path.dirname(__file__)
        self.filepath = os.path.join(self.application_path, filepath)
        self.node_ids = node_ids
        self.phone_numbers = phone_numbers
        self.provider_number = provider_number
        self.number_extension = 5000


    def create_go_to_lines(self, data):
        node_iterator = 0
        node_found = False
        number_extension = self.number_extension
        for line in range(0, len(data)):
            if node_found:
                if 'Goto' in data[line]:
                    data[line] = 'same => n,Goto(from-phones,' + str(number_extension) + ',1)\n'
                    node_found = False
                    number_extension += 1
                    continue

            if (node_iterator < len(self.node_ids) and not node_found):
                if (self.node_ids[node_iterator] + ",1,Answer") in data[line]:
                    node_found = True
                    node_iterator += 1
                    continue

            if ';eof' in data[line]:
                if len(data) > line + 1:
                    del data[line + 1:]
                    break

        return number_extension


    def create_from_phones(self, data, number_extension):
        last_number_extension = number_extension
        number_extension = self.number_extension
        with open(self.filepath, 'w') as file:
            file.writelines(data)
            file.write('[from-phones]\n')
            while (number_extension < last_number_extension):
                if self.phone_numbers[number_extension - self.number_extension] == "-1":
                    file.write('exten => ' + str(number_extension) + ',1,Hangup()\n\n')
                else:
                    file.write('exten => ' + str(
                        number_extension) + ',1,Set(CALLERID(all)="GP Surgery" <44' + self.provider_number + '>)\n')
                    file.write('same => n,Dial(PJSIP/+44' + self.phone_numbers[
                        number_extension - self.number_extension] + '@twilio0)\n\n')
                number_extension += 1
            file.close()

    def reload_dialplan(self):
        manager = asterisk.manager.Manager()
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        manager.connect(local_ip)
        manager.login('max', '12345678')
        manager.command('dialplan reload')
        response = manager.status()
        print(response)
        manager.close()


    def configure_dialplan(self):
        with open(self.filepath, 'r') as file:
            data = file.readlines()
            file.close()

        number_extension = self.create_go_to_lines(data)
        self.create_from_phones(data, number_extension)

        self.reload_dialplan()

