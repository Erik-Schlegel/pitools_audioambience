# Developer Notes

## Fixes
- Raspberry Pi 4 puts wireless interface in low power mode after interactivity.
   ```sh
   sudo nano /etc/network/interfaces
   # add this line
   wireless-power off
   ```
