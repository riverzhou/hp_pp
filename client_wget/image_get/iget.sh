#!/bin/sh

wget --no-check-certificate -U "Mozilla/3.0 (compatible; Indy Library)" -i login.request -O login.ack

sleep 1

i=0

while true
do
	i=$(($i + 1))
	echo $i
	wget --no-check-certificate -U "Mozilla/3.0 (compatible; Indy Library)" -i image.request -O ack/image_$i.ack
	sleep 1
done




