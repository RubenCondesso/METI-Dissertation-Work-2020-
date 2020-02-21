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


# Wireless interface to configure (check the wireless interface with iwconfig)

IFACE="wlan0" # this is the one for the Raspberry Pi



# Creates a backup of /etc/network/interfaces
if [ -e /etc/network/interfaces.backup ]; then	# if there is alredy a backup, the device should be alredy in Ad-Hoc mode
	echo "Backup alredy exist. Ad-Hoc probably on, trying to turn it off and then continuing" # Just in case, it's turn off and try again (so the network ca be 'restart' easily)
	$DIR/uninstall_PI.sh
else
	echo "Backup /etc/network/interfaces as interfaces.backup" # Make a backup of this file
	sudo cp /etc/network/interfaces /etc/network/interfaces.backup || error_exit "$LINENO: Error creating interfaces backup"
fi

sudo ifconfig $IFACE down # Turn off interface

sudo cp $DIR/interfaces_adhocPI /etc/network/interfaces || error_exit "$LINENO: Error copying  .adhocPI to /etc/network"


sudo ifconfig $IFACE down && sudo ifconfig $IFACE up # Restarting wireless interface to apply the changes made
sudo ifconfig $IFACE down && sudo ifconfig $IFACE up # Twice for actually get it working
echo "Restarting inteface $IFACE. Wait about 25s" # Waiting for the interface establishment
sleep 25

sudo iwlist $IFACE scan # Scan networks with interface $IFACE 

sudo iwconfig # Show actual interfaces settings to check the configurations made
echo "The Ad-Hoc SmartBike newtork is ready" && exit 0