from json_to_dialplan.generate_voice_files import GenerateVoiceFiles
import asterisk.manager
import socket
import os
import sys

class Dialplan:
    def __init__(self, config_location, diagram_json):
        if getattr(sys, 'frozen', False):
            self.application_path = os.path.dirname(sys.executable)
        else:
            self.application_path = os.path.dirname(__file__)
        self.config_location = os.path.join(self.application_path, config_location)
        self.diagram_json = diagram_json

    def create_incoming(self):
        config_file = open(self.config_location, "w")
        config_file.write('[from-twilio]\n\n')
        config_file.write('exten => _+44XXXXXXXXXX,1,Goto(ivr,' + next(iter(self.diagram_json["nodes"])) + ',1)\n')
        config_file.write('same => n,Hangup\n\n')
        config_file.close()

    def create_ivr(self):
        voice_files = GenerateVoiceFiles(self.diagram_json, os.path.join(self.application_path, 'asterisk_docker/conf/asterisk-build/voice'))
        voice_files.create_IVR_files()
        config_file = open(self.config_location, "a")
        config_file.write('[ivr]\n\n')
        for node in self.diagram_json["nodes"]:
            if("dialogs" in self.diagram_json["nodes"][node]):
                config_file.write('exten => ' + node + ',1,Answer\n')
                config_file.write('same => n,Playback(voice/' + node + ')\n')

                #Change implementation - there should only ever be a max of one child and it should never be none.
                if("children" in self.diagram_json["nodes"][node]):
                    child = self.diagram_json["nodes"][node]["children"][0]
                    if(child is not None and "choices" in self.diagram_json["nodes"][child]):
                        config_file.write('same => n(record' + node + '),EAGI(asterisk_speech_to_text.py,${CHANNEL})\n')
                        config_file.write('same => n,Verbose(1, ${GoogleUtterance})\n')
                        config_file.write('same => n,GotoIf($["${GoogleUtterance}" = "yes"]?' + self.diagram_json["nodes"][child]["choices"][0] + ',1)\n')
                        config_file.write('same => n,GotoIf($["${GoogleUtterance}" = "no"]?' + self.diagram_json["nodes"][child]["choices"][1] + ',1)\n')
                        config_file.write('same => n,Playback(voice/repeat)\n')
                        config_file.write('same => n,Goto(record' + node + ')\n\n')
                    elif child is not None:
                        config_file.write('same => n,Goto(ivr,' + child + ',1)\n\n')
                    else:
                        # config_file.write('same => n,Goto(phones,100,1)\n')
                        config_file.write(';Goto\n')
                        config_file.write('same => n,Hangup\n\n')
        config_file.write(';eof\n')
        config_file.close()
        manager = asterisk.manager.Manager()
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        print(local_ip)
        s.close()
        manager.connect(local_ip)
        manager.login('max', '12345678')
        manager.command('dialplan reload')
        response = manager.status()
        print(response)
        manager.close()


    def create_config(self):
        self.create_incoming()
        self.create_ivr()

# with open('/home/max/Documents/GP_IVR/voiceflow.json') as json_file:
#     test_json = json.load(json_file)
# test = Dialplan("/etc/asterisk/extensions.conf", test_json)
# test.create_config()
