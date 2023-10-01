#!/bin/sh
sudo docker run --name postgres-db -p 5432:5432 -e POSTGRES_USER=user_demo -e POSTGRES_PASSWORD=password_123 -e POSTGRES_DB=demo_db -d postgres
