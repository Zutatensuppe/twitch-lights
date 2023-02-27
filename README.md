# twitch-lights

## Getting started

1. Install dependencies

    ```console
    poetry install
    ```

2. Find your light ip using `wizlight discover`

    ```console
    poetry run wizlight discover --b BROADCAST_ADDRESS
    ```

    Most likely the bulbs are in the same network than you are, so replace
    `BROADCAST_ADDRESS` with your ip and change the last number to 255,
    eg. if your own ip is 192.168.13.239 you would use:

    ```console
    poetry run wizlight discover --b 192.168.13.255
    ```

3. Copy `config.example.py` to `config.py` and adjust as required

4. Run the script

    ```console
    poetry run poetry run.py
    ```
