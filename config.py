import os

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
lights = {"desk": {"ip": "192.168.178.42"}}
default_light = "desk"

named_colors = {
    "red": {"rgb": (255, 0, 0), "brightness": 255},
    "green": {"rgb": (0, 255, 0), "brightness": 255},
    "blue": {"rgb": (0, 0, 255), "brightness": 255},
    "white": {"rgb": (255, 255, 255), "brightness": 255},
    "orange": {"rgb": (255, 165, 0), "brightness": 255},
    "yellow": {"rgb": (255, 255, 0), "brightness": 255},
    "pink": {"rgb": (125, 0, 0), "brightness": 255},
}

named_scenes = {
    "kirino": {"rgb": (180, 80, 120), "brightness": 80},
    "baker-miller pink": {"rgb": (255, 145, 175), "brightness": 69},
}

# chat bot
twitch_username = "nc_para_"  #
twitch_channel = "nc_para_"  #
twitch_oauth_token = os.environ["TWITCH_OAUTH_TOKEN"] or ""  #

# required for channel points + bits
twitch_channel_id = 26851026
twitch_oauth_token_x = os.environ["TWITCH_OAUTH_TOKEN_X"] or ""


debug = True
