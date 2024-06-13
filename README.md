# Pi Tools - Audio Ambience
Loops any number of audio files simultaneously on a raspberry pi.


## Remote Setup

```sh
#Optional, update your pi
sudo apt update
sudo apt upgrade
sudo apt autoremove

# cd to the desired path, then...
git clone git@github.com:Erik-Schlegel/pitools_audioambience.git

#Install
sudo ./install
```

## Run
`./run -c ./rain_fireplace/rf.config`


## Bluetooth Stuff

#### Bluetooth Status
`sudo stystemctl status bluetooth`

#### Bluetooth cli
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

