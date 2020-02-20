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

sudo stop network-manager; fi #top network-manager

#Restore interface config and removing backup
sudo cp /etc/network/interfaces.backup /etc/network/interfaces || error_exit "$LINENO: I couldn't restore the backup."
sudo rm /etc/network/interfaces.backup || error_exit "$LINENO: I couldn't delete the backup."
sudo iwconfig wlx503eaa4453ad mode Managed

sudo ifdown wlx503eaa4453ad #Turn off the interface of the network adaptor (of laptop)
sudo ifup wlx503eaa4453ad # Tunr on the wireless interface of the network adaptor (of laptop)

sudo start network-manager; fi #Restart network-manager
sudo iwlist wlx503eaa4453ad scan # Scan the networks available (this is needed with some networks adapters)
sudo iwconfig # Show actual interfaces settings
echo "All settings restored" && exit 0