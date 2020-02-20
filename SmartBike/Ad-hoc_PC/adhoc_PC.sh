#!/bin/bash

# Setup an wireless Ad-Hoc network in a rpi or regular pc
# Used with adhoff.sh is a easy way for tongle the Ad-Hoc
# If Ad-Hoc is alredy active this script will restart interfaces and setup it again


#############################	Useful things and error handling	##############

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )" # Directory where this script is (Commentable in case it is not neccesary)

PROGNAME=$(basename $0) # A slicker error handling routine
error_exit() {
	echo "${PROGNAME}: ${1:-"Unknown Error"}" 1>&2
	exit 1
}
	
#############################	The script starts here	##############################

PI=false #Check if this is running in a rpi
grep 'BCM2708' /proc/cpuinfo && PI=true	# BCM27XX is the name of rpi's processor, if grep is succesful we are in a rpi
grep 'BCM2709' /proc/cpuinfo && PI=true # This can be used to identify differents rpis with caution, same versions of rpi share the same family chip
grep 'BCM2710' /proc/cpuinfo && PI=true # https://raspberrypi.stackexchange.com/questions/840/why-is-the-cpu-sometimes-referred-to-as-bcm2708-sometimes-bcm2835

# Wireless interface to configure. Check the wireless interface with iwconfig
#IFACE="wlan0" # this is the one for my rpi

IFACE="wlx503eaa4453ad" # this is the one for my network adaptor in my PC


# We need to change things on /etc/network/interfaces so lets backup it
if [ -e /etc/network/interfaces.backup ]; then	# Ooops if there is alredy a backup we should be alredy in Ad-Hoc mode
	echo "Backup alredy exist. Ad-Hoc probably on, trying to turn it off and then continuing" # Just in case, we turn it off and try again (so we can 'restart' the network easily)
	.$DIR/ahoff.sh
else
	echo "Backup /etc/network/interfaces as interfaces.backup" # Make backup
	sudo cp /etc/network/interfaces /etc/network/interfaces.backup || error_exit "$LINENO: Error creating backup"
fi

sudo ifdown $IFACE # Turn off interfaces

echo " Setting /etc/network/interfaces properly" # Change interfaces for interfaces.adhoc
if [ "$PI" = true ]; then 
	sudo cp $DIR/interfaces_adhocPI /etc/network/interfaces || error_exit "$LINENO: Error copying  .adhocPI to /etc/network"
else
	sudo stop network-manager		# If we are in a pc that uses GNOME or KDE (I wrote this comment 2 years ago so Im not sure what gnome or kde has to do with network-manager but ok)
	sudo cp $DIR/interfaces.adhocPC /etc/network/interfaces || error_exit "$LINENO: Error copying  .adhocPC to /etc/network"
fi

sudo ifdown $IFACE && sudo ifup $IFACE # Restarting wireless interface to apply changes
sudo ifdown $IFACE && sudo ifup $IFACE # Twice for actually get it working(idk why I need to do this in my rpi)
echo "Restarting inteface $IFACE. This gonna take me 20s" # Waiting for the interface establishment
sleep 20
if [ "$PI" = false ]; then sudo start network-manager; fi # In case we are not in a rpi, restart network-manager 
sudo iwlist $IFACE scan # Scan networks with interface $IFACE (Somes drivers need this to trigger IBSS)

sudo iwconfig # Show actual interfaces settings
echo "Ad-Hoc SmartBike newtork is ready." && exit 0