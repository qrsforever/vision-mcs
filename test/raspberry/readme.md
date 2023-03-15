## Prepare

- sudo apt-get install -y python-smbus
- sudo apt-get install -y i2c-tools
- sudo raspi-config
- sudo i2cdetect -y 1


## Install

- sudo cp lcd1602.service /etc/systemd/system/lcd1602.service
- sudo systemctl enable lcd1602.service
- sudo reboot

## V4L2-Ctrl

- v4l2-ctl --list-ctrls
- v4l2-ctl --list-devices 
- v4l2-ctl --device /dev/video1 --list-ctrls

## References

- https://blog.csdn.net/weixin_40929065/article/details/126685611
- https://danoncoding.com/raspberrypi-ip-address-lcd-display-d31b496325fb
- https://github.com/Lqg97/RaspberryPi-Sensor-Experiment
- https://cloud.tencent.com/developer/inventory/1503/article/1707072
- https://forums.raspberrypi.com/viewtopic.php?t=142860 (同步问题）
