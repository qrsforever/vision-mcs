## [armbian os](https://www.armbian.com/orangepi3-lts/)

### desktop

### server

1. login user: `root` login password: `1234` change to `123456`

2. armbian-config

   system -> hardware -> [\*]i2c0
   system -> firmware -> update

3. china source `/etc/apt/sources.list`

    deb http://mirrors.aliyun.com/ubuntu-ports/ jammy main restricted universe multiverse
    deb http://mirrors.aliyun.com/ubuntu-ports/ jammy-security main restricted universe multiverse
    deb http://mirrors.aliyun.com/ubuntu-ports/ jammy-updates main restricted universe multiverse
    deb http://mirrors.aliyun.com/ubuntu-ports/ jammy-backports main restricted universe multiverse

4. `apt install -y`

    - git python3-dev python3-pip python3-smbus

5. `pip install`

    - O

6. `git clone https://github.com/orangepi-xunlong/wiringOP; ./build; gpio readall`

7. install gstream

    apt-get install -y gstreamer1.0-tools gstreamer1.0-alsa \
         gstreamer1.0-plugins-base gstreamer1.0-plugins-good \
         gstreamer1.0-plugins-bad gstreamer1.0-plugins-ugly \
         gstreamer1.0-libav

    test:
       gst-launch-1.0 v4l2src device=/dev/video1 io-mode=4 ! queue ! videoconvert ! x264enc bframes=0 speed-preset=veryfast key-int-max=30 ! flvmux streamable=true ! queue ! rtmpsink location=rtmp://srs.hzcsdata.com/live/orangepi3?vhost=seg.30s

8. wifi

    nmcli dev wifi rescan
    nmcli dev status
    nmcli dev wifi list


## ubuntu os

[google drive](https://drive.google.com/drive/folders/1KzyzyByev-fpZat7yvgYz1omOqFFqt1k)
[image download](http://www.orangepi.cn/html/hardWare/computerAndMicrocontrollers/service-and-support/Orange-Pi-3-LTS.html)


### desktop

### server

1. login user: `root` login password: `orangepi` change to `123456`

2. nand-sata-install (sdcard os to emmc)

3. set wifi dhcp and reboot

    auto wlan0
    iface wlan0 inet dhcp
    wpa-ssid hzcsdata
    wpa-psk Hzcsai@123

~~4. lcd~~

   apt-get install python3-smbus

~~5. systemctl service~~

   cp xxx.service /etc/systemd/system/
   systemctl enable xxx.service
   systemctl restart xxx.service

6. install apt / pip

```
    apt install python3-dev python3-pip libx264-dev libjpeg-dev

    apt install -y gstreamer1.0-tools gstreamer1.0-alsa \
         gstreamer1.0-plugins-base gstreamer1.0-plugins-good \
         gstreamer1.0-plugins-bad gstreamer1.0-plugins-ugly \
         gstreamer1.0-libav

    apt install python3-gst-1.0
```

## issues

1. [armbian orange-pi-3-lts-no-wifi][1]
2. [Installing headers and building driver for RTL8188 WiFi dongle for orange pi pc][2]
3. [A start job is running for Raise network interface（5min 13s ）问题解决方法][3]
    /etc/systemd/system/network-online.target.wants/networking.service
    TimeoutStartSec=5min --> TimeoutStartSec=2sec

[1]: https://forum.armbian.com/topic/23505-orange-pi-3-lts-no-wifi/ "not work to me"
[2]: https://forum.armbian.com/topic/17325-installing-headers-and-building-driver-for-rtl8188-wifi-dongle-for-orange-pi-pc-nmcli-dev-wifi-list-not-works/
[3]: https://www.cnblogs.com/pipci/p/8537274.html
