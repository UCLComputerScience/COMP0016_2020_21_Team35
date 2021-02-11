FROM ubuntu:18.04
ARG DEBIAN_FRONTEND=noninteractive

ADD ./json_to_dialplan/generate_voice_files.py /tmp/json_to_dialplan/
ADD ./json_to_dialplan/json_to_dialplan.py /tmp/json_to_dialplan/
ADD ./UI.py /tmp
ADD ./voiceflow_to_json.py /tmp

ENV LIBGL_ALWAYS_INDIRECT=1

RUN apt-get update && apt-get install -y python3  python3-dbg  python3-pip
RUN apt-get update
RUN apt-get -y --no-install-recommends install libgl1-mesa-glx libsndfile1-dev libxkbcommon-x11-0 python3-pyqt5
RUN apt-get install --reinstall libxcb-xinerama0

RUN pip3 install -U pip
RUN pip3 install py-picotts sndfile librosa SoundFile requests PyQt5 pyst2

CMD ["python3", "./tmp/UI.py"]