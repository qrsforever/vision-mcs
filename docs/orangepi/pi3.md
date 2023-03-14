## [armbian os](https://www.armbian.com/orangepi3-lts/)

### desktop

### server

1. login user: `root` login password: `1234` change to `123456`

2. armbian-config -> system -> hardware -> i2cx[\*]

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


## ubuntu os

[google drive](https://drive.google.com/drive/folders/1KzyzyByev-fpZat7yvgYz1omOqFFqt1k)


### desktop

### server

1. login user: `root` login password: `orangepi` change to `123456`

2. nand-sata-install (sdcard os to emmc)

3. set wifi dhcp and reboot

    auto wlan0
    iface wlan0 inet dhcp
    wpa-ssid hzcs211
    wpa-psk Mxjmxj211

4. lcd

   apt-get install python3-smbus


## issues

1. [armbian orange-pi-3-lts-no-wifi][1]

2. [Installing headers and building driver for RTL8188 WiFi dongle for orange pi pc][2]


[1]: https://forum.armbian.com/topic/23505-orange-pi-3-lts-no-wifi/ "not work to me"
[2]: https://forum.armbian.com/topic/17325-installing-headers-and-building-driver-for-rtl8188-wifi-dongle-for-orange-pi-pc-nmcli-dev-wifi-list-not-works/
