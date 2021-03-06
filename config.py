import os
from pywizlight import PilotBuilder

# use `wizlight discover` to find out what lamps there
# are
#
#   wizlight discover --b BROADCAST_ADDRESS
#
# most likely the bulbs are in the same network than you are, so replace
# BROADCAST_ADDRESS with your ip and change the last number to 255,
# eg. if your own ip is 192.168.13.239 you would use
#
#   wizlight discover --b 192.168.13.255
#
lights = {
    "desk": {"ip": "192.168.1.13"},
    "kitchen": {"ip": "192.168.1.14"},
}
default_light = "kitchen"

exact_commands = {
    "!blue": {
        "duration": 3.0,
        "builder": PilotBuilder(rgb=(255, 0, 0), brightness=200),
    },
    "!red": {
        "duration": 3.0,
        "builder": PilotBuilder(rgb=(255, 0, 0), brightness=255),
    },
    "!white": {
        "duration": 0,
        "builder": PilotBuilder(rgb=(255, 255, 255), brightness=255, speed=1),
    },
}


rgb_command = "!rgb"
brightness_command = "!brightness"
scene_command = "!scene"

named_scenes = {
    "kirino": PilotBuilder(rgb=(180, 80, 120), brightness=80, speed=1),
    "tvarynka": PilotBuilder(rgb=(0, 0, 255), brightness=100, speed=1),
    "baker-miller pink": PilotBuilder(rgb=(255, 145, 175), brightness=69, speed=1),
}

named_rewards = {
    "blau": PilotBuilder(rgb=(0, 0, 255), brightness=255),
    "lila": PilotBuilder(rgb=(255, 0, 255), brightness=255),
    "rot": PilotBuilder(rgb=(255, 0, 0), brightness=255),
    "gruen": PilotBuilder(rgb=(0, 255, 0), brightness=255),
    "party": PilotBuilder(scene=4),
    "weiss": PilotBuilder(rgb=(255, 255, 255), brightness=255, cold_white=255),
}

# chat bot
twitch_username = "nc_para_"  #
twitch_channel = "nc_para_"  #
twitch_oauth_token = os.environ["TWITCH_OAUTH_TOKEN"] or ""  #

# required for channel points + bits
twitch_channel_id = 26851026
twitch_oauth_token_x = os.environ["TWITCH_OAUTH_TOKEN_X"] or ""


debug = True
