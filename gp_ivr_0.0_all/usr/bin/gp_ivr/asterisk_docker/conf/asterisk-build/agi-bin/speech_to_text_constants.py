
#Constants for the asterisk speech to text agi script

POCKET_SPHINX_MODEL_FILEPATH = "/var/lib/asterisk/agi-bin/cmusphinx-en-us-8khz-5.2"
YES_WORDS_FILEPATH = "/var/lib/asterisk/agi-bin/yes_words.list"
NO_WORDS_FILEPATH = "/var/lib/asterisk/agi-bin/no_words.list"
TMP_SPEECH_FILE_PATH = "/var/lib/asterisk/agi-bin/TmpSpeechFile"

RAW_RATE = 8000
CHUNK = 1024
VOCAL_RANGE = 75.0
THRESHOLD = 15
TIMEOUT_SIGNAL = 160768
TIMEOUT_NO_SPEAKING = 16384
SHORT_NORMALISE = (1.0/32768.0)