#Install System-Level Dependencies
sudo apt install python3 python3-pip python3-venv ffmpeg libportaudio2 libportaudiocpp0 portaudio19-dev tmux

python3 -m venv venv
source ./venv/bin/activate

#Install Python-Level Dependencies
pip install -r requirements.txt
