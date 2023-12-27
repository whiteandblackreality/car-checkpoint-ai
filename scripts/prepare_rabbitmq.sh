CRID=$(cat crid)
echo $CRID
sudo docker exec $CRID rabbitmqctl add_user user_demo password_123
sudo docker exec $CRID rabbitmqctl set_user_tags user_demo administrator
sudo docker exec $CRID rabbitmqctl set_permissions -p / user_demo ".*" ".*" ".*"
echo "User is created"
curl -i -u user_demo:password_123 -H "content-type:application/json" -XPUT -d'{"durable":true}' http://10.144.193.12:15672/api/queues/%2F/frames.getter.output
echo "Queue is created"