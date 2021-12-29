sudo pip3 install escpos guizero

mkdir -p ~/.config/lxsession/LXDE-pi
cp autostart ~/.config/lxsession/LXDE-pi/autostart
cp casher.desktop ~/.local/share/applications/casher.desktop
sudo cp 99-toshibatec.rules /etc/udev/rules.d/99-toshibatec.rules
