# kalib

## software

    docker pull stereolabs/kalibr
    FOLDER=/path/to/your/data/on/host
    xhost +local:root
    docker run -it -e "DISPLAY" -e "QT_X11_NO_MITSHM=1" -v "/tmp/.X11-unix:/tmp/.X11-unix:rw"  -v "$FOLDER:/data" stereolabs/kalibr
    source /kalibr_workspace/devel/setup.bash

## calibrate

    kalibr_bagcreater --folder bagsrc  --output-bag calib.bag
    kalibr_calibrate_cameras --target april_6x6.yaml --bag calib.bag --models pinhole-equi pinhole-equi pinhole-equi pinhole-equi --topics /cam1/image_raw /cam2/image_raw /cam3/image_raw /cam4/image_raw
    kalibr_bagextractor --image-topics /cam1/image_raw /cam2/image_raw /cam3/image_raw /cam4/image_raw --output-folder bagdst --bag calib.bag


# multical

## apriltags2_ethz

1. apt install libopencv-dev libeigen3-dev 
2. pip3 install .

## calibrate

1. multical calibrate --name cam1 --output_path . --image_path . --cameras cam1   --boards aprilgrid_6x6.yaml --fix_aspect --distortion_model standard --iter 5

2. multical calibrate --name calibration --output_path . --image_path . --iter 80 --boards aprilgrid_6x6.yaml   --master cam4

# References

1. https://medium.com/vacatronics/3-ways-to-calibrate-your-camera-using-opencv-and-python-395528a51615
2. https://github.com/BlackJocker1995/Apriltag_python
3. https://github.com/ethz-asl/kalibr/wiki/
4. https://github.com/ros-perception/image_pipeline/  "http://wiki.ros.org/camera_calibration"
5. https://github.com/AprilRobotics/apriltag_ros "http://wiki.ros.org/apriltag_ros"

# Other

1. 1/2.7" cmos: 5.27mm * 3.96mm
