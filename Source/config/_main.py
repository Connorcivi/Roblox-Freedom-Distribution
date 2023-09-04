
from config._logic import allocateable as 𝕏
import config._logic
import util.versions
import util.resource
import functools
import typing
import enum


class chat_style(enum.Enum):
    CLASSIC_CHAT = "Classic"
    BUBBLE_CHAT = "Bubble"
    CLASSIC_AND_BUBBLE_CHAT = "ClassicAndBubble"


class obj_type(config._logic._configtype):
    '''
    Configuration specification, according by default to "GameConfig.toml".
    '''
    class server_assignment(𝕏):
        class players(𝕏):
            maximum: int
            preferred: int

        class instances(𝕏):
            count: int

    class game_setup(𝕏):
        place_path: config._logic.path
        icon_path: config._logic.path
        roblox_version: util.versions.rōblox

        class creator(𝕏):
            name: str
        name: str
        description: str

    class server_core(𝕏):
        chat_style: chat_style
        retrieve_default_user_code: typing.Callable[[float], str]
        retrieve_username: typing.Callable[[str], str]
        retrieve_user_id: typing.Callable[[str], int]
        retrieve_account_age: typing.Callable[[str], int]
        filter_text: typing.Callable[[str, str], str]


@functools.cache
def get_config(path: str = util.resource.DEFAULT_CONFIG_PATH) -> obj_type:
    return obj_type(path)
