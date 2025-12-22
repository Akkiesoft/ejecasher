sudo apt update
sudo apt install -y python3-venv fonts-vlgothic

cd ..
CURRENT_DIR=`pwd`
echo $CURRENT_DIR
python3 -m venv venv
venv/bin/pip install escpos guizero

cd util

sed -e "s|CURRENT_DIR|$CURRENT_DIR|g" casher.desktop | tee ~/.local/share/applications/casher.desktop > /dev/null

sed -e "s/pi/$USER/g" 99-toshibatec.rules | sudo tee /etc/udev/rules.d/99-toshibatec.rules > /dev/null
