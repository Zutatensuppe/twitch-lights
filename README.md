# twitch-lights

## Getting started

1. Install dependencies

    ```console
    poetry install
    ```

2. Find your light ip (you may need to adjust the broadcast address in `find_lights.py`)

    ```console
    poetry run poetry find_lights.py
    ```

3. Copy `config.example.py` to `config.py` and adjust as required

4. Run the script

    ```console
    poetry run poetry run.py
    ```
