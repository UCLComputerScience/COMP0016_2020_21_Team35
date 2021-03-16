import sys
import os
import shutil

class ModifyVoiceFiles:
    def __init__(self, asterisk_voice_filepath, node_ids, voice_file_paths):
        self.node_ids = node_ids
        self.voice_file_paths = voice_file_paths
        if getattr(sys, 'frozen', False):
            self.application_path = os.path.dirname(sys.executable)
        else:
            self.application_path = os.path.dirname(__file__)
        self.asterisk_voice_filepath = os.path.join(self.application_path, asterisk_voice_filepath)

    def get_asterisk_voice_file_path(self, node_id):
        voice_file_name = node_id + ".wav"
        voice_file_path = os.path.join(self.asterisk_voice_filepath, voice_file_name)

        return voice_file_path

    def copy_and_replace_file(self, voice_file_path, node_id, asterisk_voice_file_path):
        new_file_name = node_id + ".wav"
        new_file_path = os.path.join(os.path.dirname(voice_file_path), new_file_name)
        shutil.copyfile(voice_file_path, new_file_path)
        shutil.move(new_file_path, asterisk_voice_file_path)

    def replace_asterisk_voice_files(self):
        for node in range(len(self.node_ids)):
            asterisk_voice_file_path = self.get_asterisk_voice_file_path(self.node_ids[node])
            self.copy_and_replace_file(self.voice_file_paths[node], self.node_ids[node], asterisk_voice_file_path)