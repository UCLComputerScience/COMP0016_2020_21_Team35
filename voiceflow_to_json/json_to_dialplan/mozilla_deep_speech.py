# import deepspeech
# import wave
#
# import librosa
# import numpy as np
# import wave
# import soundfile as sf
#
# model_file_path = "mozilla_deepspeech_models/deepspeech-0.8.2-models/deepspeech-0.8.1-models.pbmm"
# model = deepspeech.Model(model_file_path)
# scorer_file_path = "mozilla_deepspeech_models/deepspeech-0.8.2-models/deepspeech-0.8.1-models.scorer"
# model.enableExternalScorer(scorer_file_path)
# lm_alpha = 0.75
# lm_beta = 1.85
# model.setScorerAlphaBeta(lm_alpha, lm_beta)
#
# beam_width = 500
# model.setBeamWidth(beam_width)
#
# filename = "mozilla_deepspeech_models/audio/record.wav"
# y, s = librosa.load(filename, sr=16000)
# sf.write(filename, y, s)
# w = wave.open(filename, "r")
# frames = w.getnframes()
# buffer = w.readframes(frames)
# data16 = np.frombuffer(buffer, dtype=np.int16)
#
# text = model.stt(data16)
# print
import wave

import librosa
from pocketsphinx import AudioFile, get_model_path, get_data_path, LiveSpeech
import speech_recognition as sr
import os
import numpy as np
import soundfile as sf

model_path = get_model_path()
data_path = get_data_path()
print(model_path)
# #
# r = sr.Recognizer()
# test = sr.AudioFile("mozilla_deepspeech_models/audio/TmpSpeechFile.wav")
# with test as source:
#     audio = r.record(source)
#
# print(r.recognize_google(audio))

filename = "mozilla_deepspeech_models/audio/TmpSpeechFile.wav"
y, s = librosa.load(filename, sr=16000)
sf.write(filename, y, s)
model_path = get_model_path()
config = {
        'lm': False,
        'audio_file': filename,
        'hmm': "cmusphinx-en-us-8khz-5.2",
        'dict': os.path.join(model_path, 'cmudict-en-us.dict')
}

yes_result = 0
no_result = 0
audio = AudioFile(**config, kws="yes_words.list")
for phrase in audio:
        print(phrase)
        yes_result += 1

audio = AudioFile(**config, kws="no_words.list")
for phrase in audio:
        print(phrase)
        no_result += 1

if(yes_result > no_result):
        result = "yes"
else:
        result = "no"

print(yes_result)
print(no_result)
print(result)



