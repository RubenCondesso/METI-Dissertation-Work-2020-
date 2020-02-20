#!/bin/bash

# Setup an Wireless Ad-Hoc network in a Raspberry Pi or regular laptop
# If Ad-Hoc is alredy active, this script will restart interfaces (backups are created) and setup it again


#############################	Error handling	##############

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )" # Directory where this script is

PROGNAME=$(basename $0) # A slicker error handling routine
error_exit() {
	echo "${PROGNAME}: ${1:-"Unknown Error"}" 1>&2
	exit 1
}
	
#############################	Start of script  ##############################



PI=false # Check if this device (that is running) is a Raspberry Pi

grep 'BCM2708' /proc/cpuinfo && PI=true	# BCM27XX is the name of rpi's processor, if grep is succesful we are in a rpi
grep 'BCM2709' /proc/cpuinfo && PI=true # This can be used to identify differents rpis with caution, same versions of rpi share the same family chip
grep 'BCM2710' /proc/cpuinfo && PI=true # https://raspberrypi.stackexchange.com/questions/840/why-is-the-cpu-sometimes-referred-to-as-bcm2708-sometimes-bcm2835



# Wireless interface to configure (check the wireless interface with iwconfig)

IFACE="wlan0" # this is the one for the Raspberry Pi



# Creates a backup of /etc/network/interfaces
if [ -e /etc/network/interfaces.backup ]; then	# if there is alredy a backup, the device should be alredy in Ad-Hoc mode
	echo "Backup alredy exist. Ad-Hoc probably on, trying to turn it off and then continuing" # Just in case, it's turn off and try again (so the network ca be 'restart' easily)
	.$DIR/ahoff.sh
else
	echo "Backup /etc/network/interfaces as interfaces.backup" # Make a backup of this file
	sudo cp /etc/network/interfaces /etc/network/interfaces.backup || error_exit "$LINENO: Error creating interfaces backup"
fi

sudo ifdown $IFACE # Turn off interfaces

echo " Setting /etc/network/interfaces properly" # Change interfaces for interfaces.adhoc
if [ "$PI" = true ]; then 
	sudo cp $DIR/interfaces_adhocPI /etc/network/interfaces || error_exit "$LINENO: Error copying  .adhocPI to /etc/network"
else
	sudo stop network-manager
	sudo cp $DIR/interfaces.adhocPC /etc/network/interfaces || error_exit "$LINENO: Error copying  .adhocPC to /etc/network"
fi



sudo ifdown $IFACE && sudo ifup $IFACE # Restarting wireless interface to apply the changes made
sudo ifdown $IFACE && sudo ifup $IFACE # Twice for actually get it working
echo "Restarting inteface $IFACE. Wait about 25s" # Waiting for the interface establishment
sleep 25
if [ "$PI" = false ]; then sudo start network-manager; fi # In case we are not in a Raspberry Pi, restart network-manager 
sudo iwlist $IFACE scan # Scan networks with interface $IFACE 

sudo iwconfig # Show actual interfaces settings to check the configurations made
echo "The Ad-Hoc SmartBike newtork is ready" && exit 0