from typing import Optional
import config

import signal
import sys

from pywizlight import scenes, PilotBuilder, wizlight
from twitchio.ext import commands, pubsub

#### HELPERS
##########################################


def log_debug(msg):
    if config.debug:
        print(msg)


def sig_handler(signum, frame) -> None:
    sys.exit(1)


#### LIGHT
##########################################


def _light(light: str):
    if not light in config.lights:
        return None
    return wizlight(
        ip=config.lights[light].get("ip"),
        connect_on_init=True,
        port=config.lights[light].get("port", 38899),
    )


async def _turn_on(builder: PilotBuilder, light: Optional[str] = config.default_light):
    bulb = _light(light)
    if not bulb:
        return
    await bulb.turn_on(builder)


async def _handle_message(msg: str):
    lower_msg_full = msg.lower()
    if not lower_msg_full.startswith("!"):
        return

    if lower_msg_full.startswith("!sr bad"):
        lower_msg_full = "!rgb 255 0 0"
    elif lower_msg_full.startswith("!sr good"):
        lower_msg_full = "!rgb 0 255 0"

    lower_msg = lower_msg_full[1:]
    if lower_msg in config.named_colors:
        await _turn_on(
            PilotBuilder(
                rgb=config.named_colors[lower_msg]["rgb"],
                brightness=config.named_colors[lower_msg]["brightness"],
            )
        )
    elif lower_msg.startswith("rgb "):
        (r, g, b) = lower_msg[4:].split(" ")
        r = int(r)
        g = int(g)
        b = int(b)
        if r >= 0 and r <= 255 and g >= 0 and g <= 255 and b >= 0 and b <= 255:
            await _turn_on(PilotBuilder(rgb=(r, g, b)))
    elif lower_msg.startswith("brightness "):
        brightness = lower_msg[11:]
        brightness = int(brightness)
        if brightness >= 0 and brightness <= 255:
            await _turn_on(PilotBuilder(brightness=brightness))
    elif lower_msg.startswith("scene "):
        scene = lower_msg[6:]
        if scene in config.named_scenes:
            await _turn_on(
                PilotBuilder(
                    rgb=config.named_scenes[scene]["rgb"],
                    brightness=config.named_scenes[scene]["brightness"],
                )
            )
            return

        try:
            scene_id = scenes.get_id_from_scene_name(scene.capitalize())
            await _turn_on(PilotBuilder(scene=scene_id))
        except:
            # not found scene
            pass


#### PUBSUB + BOT
######################################################################

my_token = config.twitch_oauth_token
users_oauth_token = config.twitch_oauth_token_x
users_channel_id = config.twitch_channel_id

client = commands.Bot(
    token=config.twitch_oauth_token,
    client_id="",
    nick=config.twitch_username,
    prefix="!",
    initial_channels=[config.twitch_channel],
)
client.pubsub = pubsub.PubSubPool(client)


@client.event()
async def event_pubsub_bits(event: pubsub.PubSubBitsMessage):
    "Called every time there is a bit donation."
    log_debug("event_pubsub_bits")
    log_debug(event.bits_used)


@client.event()
async def event_pubsub_channel_points(event: pubsub.PubSubChannelPointsMessage):
    "Called every time there is a channel point redemption."
    log_debug("event_pubsub_channel_points")
    log_debug(event.reward.title)


@client.event()
async def event_ready():
    "Called once when the bot goes online."
    log_debug("Bot connected!")


@client.event()
async def event_message(ctx):
    "Runs every time a message is sent in chat."
    log_debug(f"received message: {ctx.content}")
    await _handle_message(ctx.content)


async def main_task():
    topics = [
        pubsub.channel_points(users_oauth_token)[config.twitch_channel_id],
        pubsub.bits(users_oauth_token)[config.twitch_channel_id],
    ]
    await client.pubsub.subscribe_topics(topics)
    await client.connect()


def main():
    """
    A blocking function that starts the asyncio event loop,
    connects to the twitch IRC server, and cleans up when done.
    """
    signal.signal(signal.SIGTERM, sig_handler)
    try:
        client.loop.create_task(main_task())
        client.loop.run_forever()
    except KeyboardInterrupt:
        pass
    except Exception as e:
        log_debug(e)
        input()  # stop for error!!
    finally:
        client.loop.run_until_complete(client.close())
        client.loop.close()
        signal.signal(signal.SIGTERM, signal.SIG_IGN)
        signal.signal(signal.SIGINT, signal.SIG_IGN)
        signal.signal(signal.SIGTERM, signal.SIG_DFL)
        signal.signal(signal.SIGINT, signal.SIG_DFL)


if __name__ == "__main__":
    sys.exit(main())
