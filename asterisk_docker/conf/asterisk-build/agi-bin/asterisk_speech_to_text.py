#!/usr/bin/env python3
import sys
import warnings
warnings.simplefilter("ignore", DeprecationWarning)
warnings.simplefilter("ignore", UserWarning)
from tempfile import mkstemp, NamedTemporaryFile
import librosa
from scipy.signal import firwin, lfilter
import numpy as np
import math
import os
import pysndfile
import soundfile as sf
from pocketsphinx import AudioFile, get_model_path
from threading import Thread
import speech_to_text_constants as constants

# Record and translate speech to text from Asterisk call
class AsteriskSpeechToText:
        def __init__(self, raw_rate, chunk, vocal_range, threshold, timeout_signal,
                     timeout_no_speaking, short_normalise, last_block, last_last_block):
                Thread.__init__(self)
                self.daemon=True
                self.RAW_RATE = raw_rate
                self.CHUNK = chunk
                self.VOCAL_RANGE = vocal_range
                self.THRESHOLD = threshold
                self.TIMEOUT_SIGNAL = timeout_signal
                self.TIMEOUT_NO_SPEAKING = timeout_no_speaking
                self.SHORT_NORMALISE = short_normalise
                self.last_block = last_block
                self.last_last_block = last_last_block

        # Open the stream, allowing us to record call speech
        def open_asterisk_stream(self):
                # File Descriptor delivery in Asterisk
                FD = 3

                # Open File Descriptor
                file = os.fdopen(FD, 'rb')
                return file

        # Wait for Asterisk console, so we can start recording
        def wait_to_start(self):
                env = {}
                while 1:
                        line = sys.stdin.readline().strip()

                        if line == '':
                                break
                        key, data = line.split(':')
                        if key == "agi_arg_1":
                                self.agi_arg = data
                        if key[:4] == 'agi_':
                                continue
                        key = key.strip()
                        data = data.strip()
                        if key == '':
                                env[key] = data
                return env

        def play_stream(self, params):
                sys.stderr.write("STREAM FILE %s \"\"\n" % str(params))
                sys.stderr.flush()
                sys.stdout.write("STREAM FILE %s \"\"\n" % str(params))
                sys.stdout.flush()

        # Write Asterisk debugging to console
        def write_output_debug(self, env):
                for key in env.keys():
                        sys.stderr.write(" -- %s = %s\n" % (key, env[key]))
                        sys.stderr.flush()

        def create_audio_file(self, FileNameTmp, array):
                open(FileNameTmp, "w")
                # making the file .wav
                pysndfile.sndio.write(name=FileNameTmp, data=array, rate=self.RAW_RATE, format="wav", enc="pcm16")

        def delete_audio_file(self, FileNameTmp):
                if(os.path.exists(FileNameTmp)):
                        os.remove(FileNameTmp)
                else:
                        print("The file " + FileNameTmp + " does not exist")

        def filter(self, samps):
                FC = 0.05 / (0.5 * self.RAW_RATE)
                N = 200
                a = 1
                b = firwin(N, cutoff=FC, window='hamming')
                return lfilter(b, a, samps)

        def pitch(self, signal):
                if sys.version_info < (2, 6):
                        crossing = []
                        for s in signal:
                                crossing.append(s)
                else:
                        crossing = [math.copysign(1.0, s) for s in signal]
                index = np.nonzero(np.diff(crossing))
                index = np.array(index)[0].tolist()
                f0 = round(len(index) * self.RAW_RATE / (2 * np.prod(len(signal))))
                return f0

        # root mean square of sample
        def rms(self, shorts):
                rms2 = 0
                count = len(shorts) / 2
                sum_squares = 0.0
                for sample in shorts:
                        n = sample * self.SHORT_NORMALISE
                        sum_squares += n * n
                        rms2 = math.pow(sum_squares / count, 0.5)
                return rms2 * 1000

        # Check if caller is speaking
        def speaking(self, data):
                rms_value = self.rms(data)
                if rms_value > self.THRESHOLD:
                        return True
                else:
                        return False

        # Detect if voice activity
        def VAD(self, SumFrequency, data2):
                AVGFrequency = SumFrequency / (self.TIMEOUT_NO_SPEAKING + 1);
                if AVGFrequency > self.VOCAL_RANGE / 2:
                        S = self.speaking(data2)
                        if S:
                                return True;
                        else:
                                return False;
                else:
                        return False;

        def record_speech(self, file):
                all = []
                for s in self.last_last_block:
                        all.append(s)
                for s in self.last_block:
                        all.append(s)
                signal = 0;
                while signal <= self.TIMEOUT_SIGNAL:
                        raw_samps = file.read(self.TIMEOUT_NO_SPEAKING)
                        samps = np.fromstring(raw_samps, dtype=np.int16)
                        for s in samps:
                                all.append(s)
                        signal = signal + self.TIMEOUT_NO_SPEAKING
                        Speech = self.speaking(samps)

                        # if rms_value > Threshold:
                        if Speech:
                                sys.stdout.write("EXEC " + "\"" + "NOOP" + "\" \"" + "Speech Found ..." + "\" " + "\n")
                                sys.stdout.flush()
                        else:
                                sys.stdout.write(
                                        "EXEC " + "\"" + "NOOP" + "\" \"" + "End of the Speech..." + "\" " + "\n")
                                sys.stdout.flush()
                                signal = self.TIMEOUT_SIGNAL + 1
                return np.array(all)

        def waiting_for_speech(self, file):
                sys.stdout.write("EXEC " + "\"" + "NOOP" + "\" \"" + "Hello Waiting For Speech ..." + "\" " + "\n")
                sys.stdout.flush()
                silence = True
                while silence:
                        # Input Real-time Data Raw Audio from Asterisk
                        raw_samps = file.read(self.CHUNK)
                        samps = np.fromstring(raw_samps, dtype=np.int16)
                        samps2 = self.filter(samps)
                        frequency = self.pitch(samps2)
                        rms_value = self.rms(samps)
                        signal = self.CHUNK;
                        if (rms_value > self.THRESHOLD) and (frequency > self.VOCAL_RANGE):
                                silence = False
                                self.last_last_block = self.last_block
                                self.last_block = samps
                                sys.stdout.write(
                                        "EXEC " + "\"" + "NOOP" + "\" \"" + "Speech Detected Recording..." + "\" " + "\n")
                                sys.stdout.flush()
                        if (signal > self.TIMEOUT_SIGNAL):
                                sys.stdout.write(
                                        "EXEC " + "\"" + "NOOP" + "\" \"" + "Time Out No Speech Detected ..." + "\" " + "\n")
                                sys.stdout.flush()
                                sys.exit()

        # Conduct speech to text, send result to Asterisk through channel variable
        def send_speech(self, File):
                model_path = get_model_path()
                y, s = librosa.load(File, sr=16000)
                sf.write(File, y, s)
                config = {
                        'lm': False,
                        'audio_file': File,
                        'hmm': constants.POCKET_SPHINX_MODEL_FILEPATH,
                        'dict': os.path.join(model_path, 'cmudict-en-us.dict')
                }

                yes_result = 0
                no_result = 0
                audio = AudioFile(kws=constants.YES_WORDS_FILEPATH, **config)
                for phrase in audio:
                        yes_result += 1

                audio = AudioFile(kws=constants.NO_WORDS_FILEPATH, **config)
                for phrase in audio:
                        no_result += 1
                os.remove(File)

                if yes_result == 0 and no_result == 0:
                        result = "unsure"

                if yes_result > no_result:
                        result = "yes"
                else:
                        result = "no"

                sys.stdout.write('SET VARIABLE GoogleUtterance "%s"\n' % str(result))
                sys.stdout.flush()
                sys.stdout.write("EXEC " + "\"" + "NOOP" + "\" \"" "%s \n" % str(result))
                sys.stdout.flush()

# Complete who speech to text process, using key values for Asterisk audio
class OutputYesNoResult:
        def __init__(self, raw_rate, chunk, vocal_range, threshold, timeout_signal,
                     timeout_no_speaking, short_normalise, last_block, last_last_block):
                Thread.__init__(self)
                self.daemon = True
                self.RAW_RATE = raw_rate
                self.CHUNK = chunk
                self.VOCAL_RANGE = vocal_range
                self.THRESHOLD = threshold
                self.TIMEOUT_SIGNAL = timeout_signal
                self.TIMEOUT_NO_SPEAKING = timeout_no_speaking
                self.SHORT_NORMALISE = short_normalise
                self.last_block = last_block
                self.last_last_block = last_last_block
                self.output_result()

        def output_result(self):
                FileNameTmp = constants.TMP_SPEECH_FILE_PATH
                stt = AsteriskSpeechToText(self.RAW_RATE, self.CHUNK, self.VOCAL_RANGE, self.THRESHOLD,
                                           self.TIMEOUT_SIGNAL, self.TIMEOUT_NO_SPEAKING, self.SHORT_NORMALISE,
                                           self.last_block, self.last_last_block)
                file = stt.open_asterisk_stream()
                env = stt.wait_to_start()
                stt.write_output_debug(env)
                sys.stdout.flush()
                stt.waiting_for_speech(file)
                array = stt.record_speech(file)

                FileNameTmp = FileNameTmp + stt.agi_arg.split("/")[1] + ".wav"
                stt.create_audio_file(FileNameTmp, array)
                stt.send_speech(FileNameTmp)
                stt.delete_audio_file(FileNameTmp)


recogniser = OutputYesNoResult(constants.RAW_RATE, constants.CHUNK, constants.VOCAL_RANGE, constants.THRESHOLD,
                               constants.TIMEOUT_SIGNAL, constants.TIMEOUT_NO_SPEAKING, constants.SHORT_NORMALISE, "", "")




