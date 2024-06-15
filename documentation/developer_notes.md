# Developer Notes

## Fixes
- Raspberry Pi 4 puts wireless interface in low power mode after interactivity.
   ```sh

   # Turn off power saving feature on the wireless adapter
   sudo nano /etc/network/interfaces
   # add this line
   wireless-power off

   # Set up a cron job to ping the router ever minute to keep the connection alive
   crontab -e
   * * * * * ping -c 1 192.168.1.1 > /dev/null 2>&1

   # now, power cycle
   ```
