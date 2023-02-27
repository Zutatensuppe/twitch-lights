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


#### CUSTOM SCENE
##########################################

custom_scene = { "actions": [], "idx": -1 }
async def _next():
    global custom_scene
    if len(custom_scene["actions"]) == 0:
        return
    
    custom_scene["idx"]+=1
    if custom_scene["idx"] > (len(custom_scene["actions"]) -1):
        custom_scene["idx"] = 0
    cmd = custom_scene["actions"][custom_scene["idx"]]

    await _turn_on(cmd['builder'], False)
    loop = asyncio.get_event_loop()
    loop.call_later(cmd["duration"], loop.create_task, _next())


async def _start_custom_scene(custom_scene_settings):
    custom_scene["actions"] = custom_scene_settings["loop"]
    custom_scene["idx"] = -1
    await _store_current_state()
    await _next()
    if "duration" in custom_scene_settings:
        loop = asyncio.get_event_loop()
        loop.call_later(custom_scene_settings["duration"], loop.create_task, _stop_custom_scene_and_restore_state())


async def _stop_custom_scene_and_restore_state():
    _stop_custom_scene()
    await restore_state()


def _stop_custom_scene():
    custom_scene["actions"] = []
    custom_scene["idx"] = -1


#### LIGHT
##########################################


def _light(light: str):
    if not light in config.lights:
        return None
    return wizlight(
        ip=config.lights[light].get("ip"),
        port=config.lights[light].get("port", 38899),
    )


last_light_state = {
    "rgb": None,
    "brightness": None,
    "scene": None,
    "cold_whitecold_white": None,
}


async def _current_brightness(light: Optional[str] = config.default_light):
    bulb = _light(light)
    if not bulb:
        return None
    state = await bulb.updateState()
    return state.get_brightness()


async def _current_speed(light: Optional[str] = config.default_light):
    bulb = _light(light)
    if not bulb:
        return None
    state = await bulb.updateState()
    return state.get_speed()


async def _set_effect_speed(
    speed: int,
    light: Optional[str] = config.default_light,
):
    bulb = _light(light)
    if not bulb:
        return
    await bulb.set_speed(speed)


async def _store_current_state(
    light: Optional[str] = config.default_light,
):
    bulb = _light(light)
    if not bulb:
        return
    log_debug("storing current light state")
    state = await bulb.updateState()
    last_light_state["rgb"] = state.get_rgb()
    last_light_state["brightness"] = state.get_brightness()
    last_light_state["scene"] = state.get_scene()
    last_light_state["cold_white"] = state.get_cold_white()
    # todo: store/restore custom_scene


async def _turn_off(
    light: Optional[str] = config.default_light,
):
    bulb = _light(light)
    if not bulb:
        return
    await bulb.turn_off()


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
        await _store_current_state(light)


async def restore_state():
    restored = []
    if last_light_state["scene"]:
        scene_id = scenes.get_id_from_scene_name(last_light_state["scene"])
        await _turn_on(PilotBuilder(scene=scene_id), False)
        restored.append('scene')
    elif last_light_state["rgb"]:
        await _turn_on(PilotBuilder(rgb=last_light_state["rgb"]), False)
        restored.append('rgb')

    if last_light_state["brightness"]:
        await _turn_on(PilotBuilder(brightness=last_light_state["brightness"]), False)
        restored.append('brightness')
    if last_light_state["cold_white"]:
        await _turn_on(PilotBuilder(cold_white=last_light_state["cold_white"]), False)
        restored.append('cold_white')
    log_debug(f"restored light state: {', '.join(restored)}")


async def _handle_message(msg: str):
    global custom_scene
    lower_msg_full = msg.lower()
    if not lower_msg_full.startswith("!"):
        return

    if lower_msg_full in config.exact_commands:
        cmd = config.exact_commands[lower_msg_full]
        if "off" in cmd:
            await _turn_off()
            if "duration" in cmd:
                _stop_custom_scene()
                await _store_current_state()
                loop = asyncio.get_event_loop()
                loop.call_later(cmd["duration"], loop.create_task, restore_state())
        elif "loop" in cmd:
            await _start_custom_scene(cmd)
        elif "duration" in cmd:
            _stop_custom_scene()
            await _store_current_state()
            await _turn_on(cmd["builder"], False)
            loop = asyncio.get_event_loop()
            loop.call_later(cmd["duration"], loop.create_task, restore_state())
        else:
            _stop_custom_scene()
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
            _stop_custom_scene()
            log_debug(f"Changing light rgb to: {r} {g} {b}")
            await _turn_on(PilotBuilder(rgb=(r, g, b), speed=10))
        return

    # handle SPEED commands
    cmd = config.speed_command
    if cmd and lower_msg_full.startswith(f"{cmd} "):
        speed_current = await _current_speed()
        if not speed_current:
            log_debug("unable to determine current speed.. cant change speed")
            return
    
        s = len(f"{cmd} ")
        speed = lower_msg_full[s:]
        if speed.startswith('-') or speed.startswith('+'):
            speed_new = speed_current + int(speed)
        else:
            speed_new = int(speed)

        speed_new = min(200, max(20, speed_new))
        _stop_custom_scene()
        log_debug(f"Changing effect speed: {speed_current} -> {speed_new}")
        await _set_effect_speed(speed_new)
        return
    
    # handle BRIGTHNESS commands
    cmd = config.brightness_command
    if cmd and lower_msg_full.startswith(f"{cmd} "):
        brightness_current = await _current_brightness()
        if not brightness_current:
            log_debug("unable to determine current brightness.. cant change brightness")
            return

        s = len(f"{cmd} ")
        brightness = lower_msg_full[s:]
        if brightness.startswith('-') or brightness.startswith('+'):
            brightness_new = brightness_current + int(brightness)
        else:
            brightness_new = int(brightness)

        brightness_new = min(255, max(0, brightness_new))
        log_debug(f"Changing brightness: {brightness_current} -> {brightness_new}")
        _stop_custom_scene()
        await _turn_on(PilotBuilder(brightness=brightness_new, speed=10))
        return

    # handle SCENE commands
    cmd = config.scene_command
    if cmd and lower_msg_full.startswith(f"{cmd} "):
        s = len(f"{cmd} ")
        scene = lower_msg_full[s:]
        if scene in config.named_scenes:
            _stop_custom_scene()
            await _turn_on(config.named_scenes[scene])
            return

        try:
            scene_id = scenes.get_id_from_scene_name(scene.capitalize())
            log_debug(f"Changing to scene: {scene.capitalize()} ({scene_id})")
            _stop_custom_scene()
            await _turn_on(PilotBuilder(scene=scene_id))
        except:
            # not found scene
            pass


#### PUBSUB + BOT
######################################################################

my_token = config.twitch_oauth_token
users_oauth_token = config.twitch_oauth_token_x

client = commands.Bot(
    token=config.twitch_oauth_token,
    client_id="",
    nick=config.twitch_username,
    prefix="!IGNOREME",
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
