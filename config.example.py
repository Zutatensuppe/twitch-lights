from pywizlight import PilotBuilder

debug = True

lights = {
    "desk": {"ip": "192.168.1.69"},
    "kitchen": {"ip": "192.168.1.70"},
}

# the light that the script will use:
default_light = "desk"

# ------------------------------------------------------------------------------
# CREDENTIALS
#

# chat bot
twitch_username = "nc_para_"  # required
twitch_channel = "nc_para_"  # required
twitch_oauth_token = ""  # required

twitch_oauth_token_x = "" # required only for channel point rewards


# ------------------------------------------------------------------------------
# COMMANDS
#

# for wizlight functionality through chat:
rgb_command = "!rgb" # changes the color of the light, eg. !rgb 255 69 69
brightness_command = "!brightness" # changes the brigthness, eg. !brightness 200, !brigthness -10, !brigthness +10
scene_command = "!scene" # changes to another scene, eg. !scene party
speed_command = "!speed" # affects the speed of light changes in scenes, eg. !speed 200, !speed -10, !speed +10

# triggers on chat with the exact command given, eg. "!coldwhite"
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
        "builder": PilotBuilder(rgb=(255, 255, 255), brightness=255, speed=10),
    },
    "!coldwhite": {
        "builder": PilotBuilder(rgb=(255, 255, 255), brightness=255, cold_white=255),
    },
    "!scene police": {
        "loop": [
            { # red
                "duration": 0.5,
                "builder": PilotBuilder(rgb=(255, 0, 0), brightness=255),
            },
            { # blue
                "duration": 0.5,
                "builder": PilotBuilder(rgb=(0, 0, 255), brightness=255),
            },
        ],
        "duration": 3.0, # optional
    },
    "!off": {
        "off": True,
        "duration": 5.0, # optional
    },
}

# triggers on chat with the !scene keyword, eg. "!scene kirino"
named_scenes = {
    "kirino": PilotBuilder(rgb=(180, 80, 120), brightness=80, speed=10),
    "tvarynka": PilotBuilder(rgb=(0, 0, 255), brightness=100, speed=10),
    "baker-miller pink": PilotBuilder(rgb=(255, 145, 175), brightness=69, speed=10),
}

# channel points rewards must be named exactly like the names here, eg. "party"
named_rewards = {
    "blau": PilotBuilder(rgb=(0, 0, 255), brightness=255),
    "lila": PilotBuilder(rgb=(255, 0, 255), brightness=255),
    "rot": PilotBuilder(rgb=(255, 0, 0), brightness=255),
    "gruen": PilotBuilder(rgb=(0, 255, 0), brightness=255),
    "party": PilotBuilder(scene=4),
    "weiss": PilotBuilder(rgb=(255, 255, 255), brightness=255, cold_white=255),
}
