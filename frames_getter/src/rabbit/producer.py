import json

import amqp


class Producer:
    def __init__(self, conn):
        self.correlation_id = 0
        self.properties_dump = {'priority': 20,
                                'reply_to': ''}

        self.conn = conn

    def send_frame_message(self, msg):
        _properties_dump = self.properties_dump
        _properties_dump['correlation_id'] = str(self.correlation_id)

        msg = amqp.basic_message.Message(body=json.dumps(msg), **_properties_dump)

        self.conn.rabbit_channel.basic_publish(msg, exchange='', routing_key=self.conn.rabbit_output_frame_queue)
        self.correlation_id += 1
