#!/bin/sh
sudo rm crid
sudo docker run -d --rm -p 5672:5672 -p 15672:15672 rabbitmq:3.10.7-management >> crid # quest:quest
echo "RabbitMQ is worked"