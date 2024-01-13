import os

os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"  # see issue #152
os.environ["CUDA_VISIBLE_DEVICES"] = "1"

import logging
import time
import json
import base64
import io

import torch
import requests
import click
import pika
from PIL import Image
from torchvision import transforms


from pymilvus import connections, Collection

from src.logger import logger
from models.vehicle_recognition.models.arc_face import CarsModel, ArcFace
from models_adapter import ALPR_MODEL, CARS_MODEL

connections.connect(
    alias="default",
    user='username',
    password='password',
    host='localhost',
    port='19530'
)

collection = Collection(name="Cars_crop_3")
collection.load()

search_params = {
    "metric_type": "COSINE",
    "offset": 0,
    "ignore_growing": False,
    "params": {"nprobe": 1024}
}


class PikaConnection:

    def __init__(self, url: str, input_queue: str):
        self.correlation_id = None
        self.start_time = None
        self.end_time = None
        self.url = url
        self.url_app = "http://localhost:8679/v1/frames"
        self.header = {'accept': "application/json"}
        self.input_queue = input_queue
        self.url_pika = pika.URLParameters(url)
        self.parameters = pika.ConnectionParameters(heartbeat=600,
                                                    blocked_connection_timeout=300,
                                                    host=self.url_pika.host,
                                                    port=self.url_pika.port,
                                                    virtual_host="/",
                                                    credentials=self.url_pika.credentials)

    def on_message(self, chan, method_frame, properties, body):

        self.start_time = time.time()
        self.correlation_id = properties.correlation_id
        input_message = json.loads(body)
        decode_message = Image.open(io.BytesIO(base64.b64decode(input_message["base64_frame"])))
        with torch.no_grad():
            alpr = ALPR_MODEL.predict_image(decode_message)

        if alpr[0] is not None:
            plate_crop_resize = transforms.Compose([transforms.ToTensor(),
                                                    transforms.Resize((512, 512), antialias=True)])(alpr[0]).to("cuda")
            print(plate_crop_resize.shape)
            plate_crop_resize = plate_crop_resize.permute(1, 2, 0).unsqueeze(0)

            with torch.no_grad():
                emb = CARS_MODEL(plate_crop_resize).reshape(-1)
            result = collection.search(
                data=[emb],
                anns_field="embedding",
                param=search_params,
                limit=1,
                expr=None,
                output_fields=["label"]
            )

            self.end_time = time.time()

            response = requests.post(url=self.url_app,
                                     headers=self.header,
                                     json={"base64_frame": input_message["base64_frame"],
                                           "video_id": input_message["video_id"],
                                           "car_number": str(alpr[1]),
                                           "car_model": result[0][0].entity.get("label")})

            logger.debug(
                f"""
                ALPR: {alpr[1]},
                Model: {result[0][0].entity.get("label")},
                Status code: {response.status_code} 
                """)

        chan.basic_ack(delivery_tag=method_frame.delivery_tag)

    def consume(self):
        connection = pika.BlockingConnection(self.parameters)
        channel = connection.channel()
        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(queue=self.input_queue,
                              on_message_callback=self.on_message)
        try:
            channel.start_consuming()
        except KeyboardInterrupt:
            channel.stop_consuming()

        connection.close()

    def __call__(self):
        self.consume()


@click.command()
@click.option('--url')
@click.option('--queue')
def start_consuming(url, queue):
    consumer = PikaConnection(url=url, input_queue=queue)
    consumer()


if __name__ == "__main__":
    start_consuming()
