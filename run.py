import asyncio
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


last_light_state = {
    "rgb": None,
    "brightness": None,
    "scene": None,
}


async def _turn_on(
    builder: PilotBuilder,
    store: bool = True,
    light: Optional[str] = config.default_light,
):
    bulb = _light(light)
    if not bulb:
        return
    await bulb.turn_on(builder)
    if store:
        state = await bulb.updateState()
        last_light_state["rgb"] = state.get_rgb()
        last_light_state["brightness"] = state.get_brightness()
        last_light_state["scene"] = state.get_scene()


async def restore_state():
    if last_light_state["scene"]:
        scene_id = scenes.get_id_from_scene_name(last_light_state["scene"])
        await _turn_on(PilotBuilder(scene=scene_id), False)
    elif last_light_state["rgb"]:
        await _turn_on(PilotBuilder(rgb=last_light_state["rgb"]), False)
    if last_light_state["brightness"]:
        await _turn_on(PilotBuilder(brightness=last_light_state["brightness"]), False)


async def _handle_message(msg: str):
    lower_msg_full = msg.lower()
    if not lower_msg_full.startswith("!"):
        return

    if lower_msg_full in config.exact_commands:
        cmd = config.exact_commands[lower_msg_full]
        if cmd["duration"]:
            await _turn_on(cmd["builder"], False)
            loop = asyncio.get_event_loop()
            loop.call_later(cmd["duration"], loop.create_task, restore_state())
        else:
            await _turn_on(cmd["builder"])
        return

    # handle RGB commands
    cmd = config.rgb_command
    if cmd and lower_msg_full.startswith(f"{cmd} "):
        s = len(f"{cmd} ")
        (r, g, b) = lower_msg_full[s:].split(" ")
        r = int(r)
        g = int(g)
        b = int(b)
        if r >= 0 and r <= 255 and g >= 0 and g <= 255 and b >= 0 and b <= 255:
            await _turn_on(PilotBuilder(rgb=(r, g, b), speed=1))
        return

    # handle BRIGTHNESS commands
    cmd = config.brightness_command
    if cmd and lower_msg_full.startswith(f"{cmd} "):
        s = len(f"{cmd} ")
        brightness = lower_msg_full[s:]
        brightness = int(brightness)
        if brightness >= 0 and brightness <= 255:
            await _turn_on(PilotBuilder(brightness=brightness, speed=1))
        return

    # handle SCENE commands
    cmd = config.scene_command
    if cmd and lower_msg_full.startswith(f"{cmd} "):
        s = len(f"{cmd} ")
        scene = lower_msg_full[s:]
        if scene in config.named_scenes:
            await _turn_on(config.named_scenes[scene])
            return

        try:
            scene_id = scenes.get_id_from_scene_name(scene.capitalize())
            print(f"found scene_id {scene_id} for {scene.capitalize()}")
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
    log_debug("event_pubsub_channel_points: {event.reward.title}")
    if event.reward.title in config.named_rewards:
        await _turn_on(config.named_rewards[event.reward.title])


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
    # await _turn_on(config.named_rewards["weiss"])
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
