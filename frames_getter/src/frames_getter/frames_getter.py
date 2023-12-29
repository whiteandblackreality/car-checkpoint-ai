import os
import subprocess
import time
import base64
from pathlib import Path

import regex

from src import logger
from src.frames_getter.exceptions import *
from src.utils.frames_selector import FramesSelector


class FramesGetter:
    def __init__(self, fps,
                 path_to_frames_storage: Path = 'frames_storage',
                 path_to_audio_storage: Path = 'audio_storage',
                 selector_mode: bool = False,
                 path_to_selector_config: Path = Path('configs', 'selector.json')):
        self.fps = fps
        self.path_regex = regex.compile(r'(?<=\/)[^\/]*.mp4')
        self.path_to_frames_storage = path_to_frames_storage
        self.path_to_audio_storage = path_to_audio_storage
        self.selector_mode = selector_mode

        if self.selector_mode:
            self.fs = FramesSelector()
            self.fs.get_frames_selector(path_to_selector_config=path_to_selector_config)
            logger.info(f'Run application Frames-Getter with Frames Selector with params: {self.fs._params_code}')
        else:
            logger.info(f'Run application Frames-Getter')

    @staticmethod
    def validate_path(video_path):
        if not os.path.isfile(video_path):
            raise FramesGetterVideoPathError(f'Video is not found! Path: {video_path} is wrong!')

    @staticmethod
    def make_tmp_storage(storage_name):
        os.makedirs(storage_name, exist_ok=True)
        [os.remove(Path(storage_name, x)) for x in os.listdir(storage_name)]

    @staticmethod
    def check_output(storage_name, video_name, mode):
        if mode.lower() == 'audio':
            if not os.path.isfile(Path(storage_name, video_name.replace('.mp4', '.mp3'))):
                raise FramesGetterOutputError(f'No audio from video {video_name} in storage!')
        elif mode.lower() == 'frames':
            if not os.listdir(Path(storage_name, video_name.replace('.mp4', ''))):
                raise FramesGetterOutputError(f'No one frames from video {video_name} in output folder!')

    @staticmethod
    def encode_base64(path_to_file):
        with open(path_to_file, 'rb') as binary_file:
            binary_file_data = binary_file.read()
            base64_encoded_data = base64.b64encode(binary_file_data)
            base64_message = base64_encoded_data.decode('utf-8')
            return base64_message

    @staticmethod
    def decode_base64(filename, base64_string):
        base64_img_bytes = base64_string.encode('utf-8')
        with open(filename, 'wb') as file_to_save:
            decoded_image_data = base64.decodebytes(base64_img_bytes)
            file_to_save.write(decoded_image_data)


class FramesGetterFFMPEG(FramesGetter):
    def __init__(self, fps,
                 path_to_frames_storage: Path = 'frames_storage',
                 path_to_audio_storage: Path = 'audio_storage',
                 selector_mode: bool = True,
                 path_to_selector_config: Path = Path('configs', 'selector.json')):
        super().__init__(fps,
                         path_to_frames_storage,
                         path_to_audio_storage,
                         selector_mode,
                         path_to_selector_config)

    def get_frames(self, path_to_video,
                   verbose: bool = False):

        frames = []
        frames_paths = []

        self.validate_path(path_to_video)

        video_name = self.path_regex.search(string=str(path_to_video)).group(0)
        path_to_current_video_frames = Path(self.path_to_frames_storage, video_name.replace('.mp4', ''))

        self.make_tmp_storage(path_to_current_video_frames)

        # Video Cutting
        t0 = time.time()

        if self.selector_mode:
            self.fs(path_to_video=path_to_video,
                    output_frames_path=path_to_current_video_frames)
        else:
            subprocess.call(['ffmpeg',
                             '-i',
                             path_to_video,
                             '-vf',
                             f'fps={self.fps}',
                             f'{path_to_current_video_frames}/frame%d.png'])
        t1 = time.time() - t0

        self.check_output(self.path_to_frames_storage, video_name, 'frames')

        for frame in os.listdir(path_to_current_video_frames):
            frames.append(self.encode_base64(Path(path_to_current_video_frames, frame)))
            frames_paths.append(Path(path_to_current_video_frames, frame))

        if verbose:
            logger.info(
                f'--- Video {video_name} with {len(os.listdir(path_to_current_video_frames))} '
                f'saved frames is processed by {round(t1, 2)} seconds')

        return frames, frames_paths

    def get_audio(self, path_to_video,
                  verbose: bool = False):

        self.validate_path(path_to_video)

        video_name = self.path_regex.search(string=str(path_to_video)).group(0)
        audio_name = f'{video_name.replace(".mp4", ".mp3")}'

        os.makedirs(self.path_to_audio_storage, exist_ok=True)

        if audio_name in os.listdir(self.path_to_audio_storage):
            os.remove(Path(self.path_to_audio_storage, audio_name))

        t0 = time.time()
        subprocess.call(['ffmpeg',
                         '-i',
                         path_to_video,
                         '-b:a',
                         '192K',
                         '-vn',
                         f'{self.path_to_audio_storage}/{audio_name}'])
        t1 = time.time() - t0

        self.check_output(self.path_to_audio_storage, audio_name, 'audio')

        if verbose:
            logger.info(
                f'--- Video {video_name} with extracting audio is processed by {round(t1, 2)} seconds')

        audio_base64 = self.encode_base64(Path(self.path_to_audio_storage, audio_name))
        return audio_base64
