# Pi Tools - Audio Ambience
Loops any number of audio files simultaneously on a raspberry pi.

## Remote Setup

```sh
#Optional, update your pi
sudo apt update
sudo apt upgrade
sudo apt autoremove

# cd to the desired path, then...
git clone https://github.com/Erik-Schlegel/pitools_audioambience.git

#Install
sudo ./install.sh
```

## Run

```sh
#ssh into the playing device

# Does tmux session already exist?
tmux ls

#if not, create new session
tmux new -s audio
cd pitools_audioambience

#if already playing, and need to reconnect
tmux attach -t <session_name>

./run -p <name_of_audio_stage>
```


## Bluetooth Stuff
```sh
# enter bluetooth interactive command
bluetoothctl
power on

# setup for pairing
agent on
default-agent
scan on
# wait for device to show e.g. Raycons -- 98:47:44:33:97:DF
pair <_mac_address_>
trust <_mac_address_> #allow auto-reconnect in future
connect <_mac_address_>

# stop bluetooth command line
scan off
quit
```

