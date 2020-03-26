#!/bin/sh
#
# uninstall_AP.sh - Script for the Raspberry Pi Zero
#
# 04 March 2020 - 1.0 
# 
# Author: Ruben Condesso - 81969 - 2nd Semester (2020)
#
# 
# SmartBike System - Master Thesis in Telecommunications and Computer Engineering
#
# 
# Script that uninstall the configurations made to setup an access point in Raspberry Pi Zero
# 
#

clear

echo "===================================================================="
echo "========== Uninstall the Raspberry Pi Zero Access Point ============"
echo "===================================================================="


################################################################################# Uninstall Configuration ####################################################################################

# Restore the /etc/udhcpd.conf backup
sudo mv /etc/udhcpd.conf.backup /etc/udhcpd.conf || error_exit "$LINENO: I couldn't restore the /etc/udhcpd.conf backup."

# Restore the /etc/default/udhcpd backup
sudo mv /etc/default/udhcpd.backup /etc/default/udhcpd || error_exit "$LINENO: I couldn't restore the /etc/default/udhcpd backup."

# Restore the /etc/dhcpcd.conf backup
sudo mv /etc/dhcpcd.conf.backup /etc/dhcpcd.conf || error_exit "$LINENO: I couldn't restore the /etc/dhcpcd.conf backup."

# Restore the /etc/dnsmasq.conf backup
sudo mv /etc/dnsmasq.conf.backup /etc/dnsmasq.conf || error_exit "$LINENO: I couldn't restore the /etc/dnsmasq.conf backup."

# Restore the /etc/hostapd/hostapd.conf backup
sudo mv /etc/hostapd/hostapd.conf.backup /etc/hostapd/hostapd.conf || error_exit "$LINENO: I couldn't restore the /etc/hostapd/hostapd.conf backup."

# Restore the /etc/default/hostapd backup
sudo mv /etc/default/hostapd.backup /etc/default/hostapd || error_exit "$LINENO: I couldn't restore the /etc/default/hostapd backup."

# Restore the /etc/sysctl.conf backup
sudo mv /etc/sysctl.conf.backup /etc/sysctl.conf || error_exit "$LINENO: I couldn't restore the /etc/sysctl.conf backup."

# Restore the /etc/iptables.ipv4.nat backup
sudo mv /etc/iptables.ipv4.nat.backup /etc/iptables.ipv4.nat || error_exit "$LINENO: I couldn't restore the /etc/iptables.ipv4.nat.backup backup."

# Restore the /etc/wpa_supplicant/wpa_supplicant.conf backup
sudo mv /etc/wpa_supplicant/wpa_supplicant.conf.backup /etc/wpa_supplicant/wpa_supplicant.conf || error_exit "$LINENO: I couldn't restore the /etc/wpa_supplicant/wpa_supplicant.conf backup."

echo "Uninstall Configuration is finished! Please reboot your Raspberry Pi Zero to apply the changes made."



