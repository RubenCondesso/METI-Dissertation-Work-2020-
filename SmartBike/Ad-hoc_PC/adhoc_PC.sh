
#!/bin/bash

sudo ip link set wlx503eaa4453ad down
sudo iwconfig wlx503eaa4453ad mode ad-hoc
sudo iwconfig wlx503eaa4453ad channel 1
sudo iwconfig wlx503eaa4453ad essid "SmartBike"
sudo ip link set wlx503eaa4453ad up
sudo ip addr add 10.0.0.200/24 dev wlx503eaa4453ad 