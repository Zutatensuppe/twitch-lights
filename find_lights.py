import asyncio
from pywizlight import discovery


async def main_task():
    # Discover all bulbs in the network via broadcast datagram (UDP)
    # function takes the discovery object and returns a list with wizlight objects.
    bulbs = await discovery.discover_lights(broadcast_space="192.168.178.255")
    print(f"Found {len(bulbs)} lights.")
    # Print the IP address of the bulb on index 0
    for bulb in bulbs:
        print(f"Light IP address: {bulb.ip}")


if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        asyncio.run(main_task())
    except KeyboardInterrupt:
        pass