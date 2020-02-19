#
# install script for RPiAdHocWifi
#


# make backups of existing files
if [ -e /etc/rc.local ]
then
    cp /etc/rc.local /etc/rc.local.adhoc_bak
fi


if [ -e /etc/dhcpcd.conf ]
then
    cp /etc/dhcpcd.conf /etc/dhcpcd.conf.adhoc_bak
fi


if [ -e /etc/network/interfaces ]
then
    cp /etc/network/interfaces /etc/network/interfaces.adhoc_bak
fi




# copy new files

#sudo cp rc.local /etc
sudo cp interfaces /etc/network/interfaces.d
sudo cp udhcpd.conf /etc
sudo cp dhcpcd.conf /etc

echo "Installation complete. Please reboot now for changes to take effect."
exit 0
