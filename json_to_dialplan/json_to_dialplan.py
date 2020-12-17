import json

class Dialplan:
    def __init__(self, config_location, diagram_json):
        self.config_location = config_location
        self.diagram_json = diagram_json

    def create_incoming(self):
        config_file = open(self.config_location, "w")
        config_file.write('[incoming]\n\n')
        config_file.write('exten => 017123123,1,Goto(ivr,' + next(iter(self.diagram_json["nodes"])) + ',1)\n')
        config_file.write('same => n,Hangup\n\n')
        config_file.close()

    def create_phones(self):
        config_file = open(self.config_location, "a")
        config_file.write('[phones]\n\n')
        config_file.write('exten => 100,1,NoOp(Call for Max)\n')
        config_file.write('same => n,Dial(SIP/max,5)\n')
        config_file.write('same => n,Hangup\n\n')
        config_file.close()

    def create_ivr(self):
        config_file = open(self.config_location, "a")
        config_file.write('[ivr]\n\n')
        for node in self.diagram_json["nodes"]:
            if("dialogs" in self.diagram_json["nodes"][node]):
                config_file.write('exten => ' + node + ',1,Answer\n')
                for dialog in self.diagram_json["nodes"][node]["dialogs"]:
                    config_file.write('same => n,agi(googletts.agi,"' + dialog + '",en)\n')
                #Change implementation - there should only ever be a max of one child and it should never be none.
                if("children" in self.diagram_json["nodes"][node]):
                    child = self.diagram_json["nodes"][node]["children"][0]
                    if(child is not None and "choices" in self.diagram_json["nodes"][child]):
                        config_file.write('same => n(record' + node + '),agi(speech-recog.agi,en-UK)\n')
                        config_file.write('same => n,Verbose(1, ${utterance})\n')
                        config_file.write('same => n,GotoIf($["${utterance}" = "yes"]?' + self.diagram_json["nodes"][child]["choices"][0] + ',1)\n')
                        config_file.write('same => n,GotoIf($["${utterance}" = "no"]?' + self.diagram_json["nodes"][child]["choices"][1] + ',1)\n')
                        config_file.write('same => n,agi(googletts.agi,"Can you please repeat more clearly?", en)\n')
                        config_file.write('same => n,Goto(record' + node + ')\n\n')
                    else:
                        config_file.write('same => n,Goto(phones,100,1)\n')
                        config_file.write('same => n,Hangup\n\n')
        config_file.close()


    def create_config(self):
        self.create_incoming()
        self.create_phones()
        self.create_ivr()

with open('/home/max/Documents/GP_IVR/voiceflow.json') as json_file:
    test_json = json.load(json_file)
test = Dialplan("/etc/asterisk/extensions.conf", test_json)
test.create_config()
