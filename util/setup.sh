sudo pip3 install escpos guizero

sudo apt update
sudo apt install -y fonts-vlgothic

mkdir -p ~/.config/lxsession/LXDE-pi
cp autostart ~/.config/lxsession/LXDE-pi/autostart
sed -e "s/pi/$USER/g" casher.desktop | sudo tee ~/.local/share/applications/casher.desktop > /dev/null
sed -e "s/pi/$USER/g" 99-toshibatec.rules | sudo tee /etc/udev/rules.d/99-toshibatec.rules > /dev/null
