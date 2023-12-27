import subprocess
from pathlib import Path
import re

import numpy as np
import json
import cv2

from src import logger
from src.utils.exceptions import InvalidFrameSelectorCVArgument, InvalidFrameSelectorFFMPEGArgument


class FrameSelectorCV:

    def __init__(self, blur_method=None, blur_threshold=None):
        self.blur_threshold = blur_threshold
        self.blur_method = blur_method
        if self.blur_method == 'tenengrad':
            self.blur_metric = self.tenengrad
        elif self.blur_method == 'laplacian':
            self.blur_metric = self.variance_of_laplacian
        elif self.blur_method == 'laplacian_energy':
            self.blur_metric = self.energy_of_laplacian
        elif self.blur_method == 'modified_laplacian':
            self.blur_metric = self.modified_laplacian
        elif self.blur_method is not None:
            raise InvalidFrameSelectorCVArgument(
                """Parameter 'blur_method' value must be one of 
                {"tenengrad", "laplacian_energy", "modified_laplacian"}""")

    @staticmethod
    def variance_of_laplacian(img):
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        return cv2.Laplacian(img, cv2.CV_64F).var()

    @staticmethod
    def modified_laplacian(img):
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        kernelx = np.array([[0, 0, 0], [-1, 2, -1], [0, 0, 0]])
        lx = cv2.filter2D(img, cv2.CV_32F, np.array(kernelx))
        kernely = np.array([[0, -1, 0], [0, 2, 0], [0, -1, 0]])
        ly = cv2.filter2D(img, cv2.CV_32F, np.array(kernely))
        return (np.abs(lx) + np.abs(ly)).mean()

    @staticmethod
    def energy_of_laplacian(img):
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        lap = cv2.Laplacian(img, cv2.CV_32F)
        return np.square(lap).mean()

    @staticmethod
    def tenengrad(img):
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        sx = cv2.Sobel(img, cv2.CV_32F, 1, 0, ksize=5)
        sy = cv2.Sobel(img, cv2.CV_32F, 0, 1, ksize=5)
        return cv2.magnitude(sx, sy).mean()

    def __call__(self, output_frames_path):
        img_paths = list(Path(output_frames_path).glob('*'))
        for img_path in img_paths:
            img = cv2.imread(str(img_path))
            if self.blur_method is not None:
                blur_value = self.blur_metric(img)
                if blur_value <= self.blur_threshold:
                    img_path.unlink()


class FrameSelectorFFMPEG:
    def __init__(self,
                 diff_threshold=0.0,
                 fps=None,
                 iframes_only=False,
                 mpdecimate=False,
                 mpdecimate_args=None,
                 blackdetect=False,
                 thumbnail=False):

        if mpdecimate_args is None:
            mpdecimate_args = {"hi": 768,
                               "lo": 320,
                               "frac": 0.33}

        self.codec_options = []
        if iframes_only:
            self.codec_options.extend(['-skip_frame', 'nokey'])
        self.filter_params = []
        self.blackdetect = blackdetect

        if thumbnail:
            self.filter_params.append('thumbnail')

        if mpdecimate:
            mpdecimate_args_dtype = type(mpdecimate_args)
            if mpdecimate_args_dtype != dict:
                raise InvalidFrameSelectorFFMPEGArgument(
                    """Argument mpdecimate_args value must be dict of format 
                    {'hi': int, 'lo': int, 'frac': int}, not """
                    + str(mpdecimate_args_dtype))
            self.filter_params.append('mpdecimate=hi={}:lo={}:frac={}'.format(
                mpdecimate_args['hi'],
                mpdecimate_args['lo'],
                mpdecimate_args['frac']
            ))

        if fps:
            self.filter_params.append(f"fps={fps}")

        if diff_threshold:
            self.filter_params.append(f"select='gt(scene,{diff_threshold})'")

        if len(self.filter_params) > 0:
            self.filter_options = ['-vf', ','.join(self.filter_params)]
        else:
            self.filter_options = []

    @staticmethod
    def get_blackdetect(path_to_video):
        ffprobe_cmd = [
            "ffprobe",
            "-f",
            "lavfi",
            "-i",
            f"movie={path_to_video},blackdetect=pic_th=0.75:pix_th=0.2[out0]",
            "-show_entries",
            "tags=lavfi.black_start,lavfi.black_end",
            "-of",
            "default=nw=1",
            "-v",
            "quiet",
        ]
        lines = subprocess.check_output(ffprobe_cmd).decode("utf-8")
        logger.info(lines)
        times = list(dict.fromkeys(re.findall(r"(?<==)\d+(?:\.\d+)?", lines)))
        logger.info(times)
        last_idx = lines.rfind('=')
        seek_options = []
        last_black_end = None
        if len(times) != 0:
            if times[0] == "0":
                seek_options.extend(['-ss', times[1]])
            times = times[1:]
            last_black_type = lines[last_idx - 5: last_idx]
            logger.info(last_black_type)
            if last_black_type == 'start':
                seek_options.extend(['-to', times[-1]])
            else:
                last_black_end = times[-1]
                times = times[:-1]
            logger.info(times)
        logger.info(len(times))
        timepairs = [(times[i], times[i + 1]) for i in range(0, len(times), 2)]
        logger.info(f'Detected {len(timepairs)} black intervals')
        return timepairs, seek_options, last_black_end

    @staticmethod
    def construct_ffmpeg_trim_cmd(timepairs, last_black_end):
        intervals = []
        for start, end in timepairs:
            intervals.append("between(t,{},{})".format(start, end))
        if last_black_end is not None:
            intervals.append(f"gte(t, {last_black_end})")
        return "select='" + "+".join(intervals) + "'"

    def __call__(self, path_to_video, output_frames_path, seek_options=None, end=None):
        if seek_options is None:
            seek_options = ['-ss', '0']

        if self.blackdetect:
            timepairs, seek_options, last_black_end = self.get_blackdetect(path_to_video)
            ignore_blackframes_cmd = self.construct_ffmpeg_trim_cmd(timepairs, last_black_end)
            self.filter_params.insert(0, ignore_blackframes_cmd)
            self.filter_options = ['-vf', ','.join(self.filter_params)]

            if end is not None:
                seek_options.extend(['-to', end])

        command = ['ffmpeg',
                   '-an',
                   *seek_options,
                   *self.codec_options,
                   '-i', str(path_to_video),
                   *self.filter_options,
                   '-vsync', 'vfr',
                   f'{output_frames_path}/frame%d.png']
        subprocess.check_call(command)


class Singleton(object):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not isinstance(cls._instance, cls):
            cls._instance = object.__new__(cls, *args, **kwargs)
        return cls._instance


class FramesSelector(Singleton):
    def __init__(self):
        self.config = None
        self.ffmpeg_selector = None
        self.cv2_selector = None
        self._params_code = None

    def get_frames_selector(self,
                            path_to_selector_config: Path = Path('configs', 'selector.json')):
        self.config = self.load_selector_config(path_to_selector_config)

        if self.config['selector_ffmpeg_is_used']:
            self.ffmpeg_selector = FrameSelectorFFMPEG(diff_threshold=self.config['selector_ffmpeg']['diff_threshold'],
                                                       fps=self.config['selector_ffmpeg']['fps'],
                                                       iframes_only=self.config['selector_ffmpeg']['iframes_only'],
                                                       mpdecimate=self.config['selector_ffmpeg']['mpdecimate'],
                                                       mpdecimate_args=self.config['selector_ffmpeg']['mpdecimate_args'],
                                                       blackdetect=self.config['selector_ffmpeg']['blackdetect'],
                                                       thumbnail=self.config['selector_ffmpeg']['thumbnail'])
        else:
            logger.warning('FFMPEG selector is configured but is not active. Check selector config!')

        if self.config['selector_cv2_is_used']:
            self.cv2_selector = FrameSelectorCV(blur_method=self.config['selector_cv2']['blur_method'],
                                                blur_threshold=self.config['selector_cv2']['blur_threshold'])
        else:
            logger.warning('CV2 selector is configured but is not active. Check selector config!')

        if self.config['selector_ffmpeg_is_used'] and self.config['selector_cv2_is_used']:
            self._params_code = (f"ffmpeg_"
                                 f"{self.config['selector_ffmpeg']['diff_threshold']}_"
                                 f"{self.config['selector_ffmpeg']['fps']}"
                                 f"{'_iframes_only' if self.config['selector_ffmpeg']['iframes_only'] else ''}"
                                 f"{'_mpdecimate' if self.config['selector_ffmpeg']['mpdecimate'] else ''}"
                                 f"{'_blackdetect' if self.config['selector_ffmpeg']['blackdetect'] else ''}"
                                 f"{'_thumbnail' if self.config['selector_ffmpeg']['thumbnail'] else ''}"
                                 f"_cv2_{self.config['selector_cv2']['blur_method']}")
        elif self.config['selector_ffmpeg_is_used'] and not self.config['selector_cv2_is_used']:
            self._params_code = (f"ffmpeg_"
                                 f"{self.config['selector_ffmpeg']['diff_threshold']}_"
                                 f"{self.config['selector_ffmpeg']['fps']}"
                                 f"{'_iframes_only' if self.config['selector_ffmpeg']['iframes_only'] else ''}"
                                 f"{'_mpdecimate' if self.config['selector_ffmpeg']['mpdecimate'] else ''}"
                                 f"{'_blackdetect' if self.config['selector_ffmpeg']['blackdetect'] else ''}"
                                 f"{'_thumbnail' if self.config['selector_ffmpeg']['thumbnail'] else ''}"
                                 f"_cv2_NONE")
        elif not self.config['selector_ffmpeg_is_used'] and self.config['selector_cv2_is_used']:
            self._params_code = (f"ffmpeg_NONE"
                                 f"_cv2_{self.config['selector_cv2']['blur_method']}")

    @staticmethod
    def load_selector_config(path_to_selector_config):
        with open(path_to_selector_config, 'r') as config_file:
            return json.load(config_file)

    def __call__(self, path_to_video, output_frames_path):

        if self.config['selector_ffmpeg_is_used']:
            self.ffmpeg_selector(path_to_video=path_to_video,
                                 output_frames_path=output_frames_path)

        if self.config['selector_cv2_is_used']:
            self.cv2_selector(output_frames_path=output_frames_path)
