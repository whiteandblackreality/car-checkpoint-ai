import os
import shutil
import traceback
from pathlib import Path

from src.frames_getter.frames_getter import FramesGetterFFMPEG
from src.connector.connector import Connector
from src.rabbit.producer import Producer
from src import logger


if __name__ == '__main__':
    conn = Connector(path_to_rabbit_env=Path('configs', 'envs', '1.rabbit.env'))
    p = Producer(conn=conn)
    logger.info('Connect to RabbitMQ')

    fg = FramesGetterFFMPEG(fps=1,
                            path_to_audio_storage=Path('tmp_storages', 'tmp_audio_storage'),
                            path_to_frames_storage=Path('tmp_storages', 'tmp_frames_storage'),
                            selector_mode=False)
    logger.info('Create Frames Getter')

    storage_path = os.environ.get('PATH_TO_STORAGE')

    list_of_done_videos = []

    logger.info('Start work ...')
    while True:
        list_of_videos = os.listdir(Path(storage_path))
        for video in list_of_videos:
            if video not in list_of_done_videos:
                try:
                    frames, path_to_frames = fg.get_frames(Path(storage_path, video), verbose=False)
                    list_of_done_videos.append(video)
                    video_id = video.split('___')[0]

                    for frame in frames:
                        msg = {'base64_frame': frame,
                               'video_id': str(video_id)}
                        p.send_frame_message(msg=msg)

                    shutil.rmtree('/'.join(str(path_to_frames[0]).split('/')[:3]))

                    logger.info(f'Video {video} is done'
                                f' Count frames: {len(frames)}'
                                f' Count paths: {len(path_to_frames)}')

                except Exception as e:
                    logger.error(traceback.format_exc())
                    list_of_done_videos.append(video)

            os.remove(Path(storage_path, video))
