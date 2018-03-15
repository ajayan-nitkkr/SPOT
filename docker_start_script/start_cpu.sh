docker load -i spot_v1_10-31-17.tar
sudo docker run -i -t --net=host -e DISPLAY -v /tmp/.X11-unix --device=/dev/video0 --name spot ajay/spot_v1.5
