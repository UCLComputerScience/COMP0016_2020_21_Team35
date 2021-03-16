import os
from picotts import PicoTTS
import librosa
import soundfile as sf
import sys

# path = "../../asterisk_docker/conf/asterisk-build/voice"
class GenerateVoiceFiles:
    def __init__(self, diagram_json, asterisk_sound_path):
        if getattr(sys, 'frozen', False):
            self.application_path = os.path.dirname(sys.executable)
        else:
            self.application_path = os.path.dirname(__file__)
        self.diagram_json = diagram_json
        self.asterisk_sound_path = os.path.join(self.application_path, asterisk_sound_path)

    def create_voice_directory(self):
        try:
            if not os.path.exists(self.asterisk_sound_path):
                os.makedirs(self.asterisk_sound_path)
        except:
            print("Creation of the directory %s failed" % self.asterisk_sound_path)

    def delete_all_voice_files(self):
        for file_name in os.listdir(self.asterisk_sound_path):
            file_path = os.path.join(self.asterisk_sound_path, file_name)
            try:
                os.unlink(file_path)
            except Exception as e:
                print('Failed to delete %s. Reason: %s' % (file_path, e))

    def create_voice_file(self, voice_text, voice_type, file_path):
        picotts = PicoTTS()
        picotts.voice = voice_type
        wavs = picotts.synth_wav(voice_text)
        with open(file_path, mode="wb") as f:
            f.write(wavs)
            f.close()
        y, s = librosa.load(file_path, sr=8000)
        sf.write(file_path, y, s)

    def create_IVR_files(self):
        self.create_voice_directory()
        self.delete_all_voice_files()
        for node in self.diagram_json["nodes"]:
            if ("dialogs" in self.diagram_json["nodes"][node]):
                i = 0;
                for dialog in self.diagram_json["nodes"][node]["dialogs"]:
                    file_path = self.asterisk_sound_path + "/" + node + str(i) + ".wav"
                    self.create_voice_file(dialog, "en-GB", file_path)
                    i += 1;
        self.create_voice_file("Can you please repeat more clearly?", "en-GB", self.asterisk_sound_path + "/repeat.wav")



# with open('/home/max/Documents/GP_IVR/voiceflow.json') as json_file:
#     test_json = json.load(json_file)
# test = GenerateVoiceFiles(test_json, path)
# test.create_voice_directory()
# test.create_voice_file("Hello World, My Name Is Max!", "en-GB", "test1.wav");



# picotts = PicoTTS()
# picotts.voice = 'en-GB'
# wavs = picotts.synth_wav("Do you have a new persistent cough, or high temperature")
# with open("test.wav", mode="wb") as f:
#     f.write(wavs)
#     f.close()
# print(wavs)
# wav = wave.open(io.BytesIO(wavs))
# print (wav.getnchannels(), wav.getframerate(), wav.getnframes())