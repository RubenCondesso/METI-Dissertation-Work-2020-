#!/bin/bash

# Turn off the Ad-Hoc network and restore the previous wlan configuration


#############################	Error handling	##############

#DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )" # Directory where this script is

PROGNAME=$(basename $0) # A slicker error handling routine by William Shotts (www.linuxcommand.org)
error_exit() {
	echo "${PROGNAME}: ${1:-"Unknown Error"}" 1>&2
	exit 1
}

	

#############################	Start of script	##############################


PI=false #Check if the device that is running is a Raspberry Pi

grep 'BCM2708' /proc/cpuinfo && PI=true	# BCM27XX is the name of rpi's processor, if grep is succesful we are in a rpi
grep 'BCM2709' /proc/cpuinfo && PI=true # You could use this to identify differents rpis with caution, same versions of rpi share the same family chip
grep 'BCM2710' /proc/cpuinfo && PI=true # https://raspberrypi.stackexchange.com/questions/840/why-is-the-cpu-sometimes-referred-to-as-bcm2708-sometimes-bcm2835


if [ "$PI" = false ]; then sudo stop network-manager; fi #In case of being a regular laptop, stop network-manager

#Restore interface config and removing backup
sudo cp /etc/network/interfaces.backup /etc/network/interfaces || error_exit "$LINENO: I couldn't restore the backup."
sudo rm /etc/network/interfaces.backup || error_exit "$LINENO: I couldn't delete the backup."
sudo iwconfig wlp2s0 mode Managed

sudo ifdown wlx503eaa4453ad #Turn off the interface of the network adaptor (of laptop)
sudo ifup wlx503eaa4453ad # Tunr on the wireless interface of the network adaptor (of laptop)

if [ "$PI" = false ]; then sudo start network-manager; fi #In case of being a regular laptop, restart network-manager
sudo iwlist wlx503eaa4453ad scan # Scan the networks available (this is needed with some networks adapters)
sudo iwconfig # Show actual interfaces settings
echo "All settings restored" && exit 0