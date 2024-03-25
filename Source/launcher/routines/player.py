import launcher.routines.web_server as web_server
import launcher.routines._logic as logic
import urllib.request
import util.versions
import urllib.parse
import urllib.error
import dataclasses
import util.const
import functools
import ctypes
import time
import ssl


@functools.cache
def get_none_ssl() -> ssl.SSLContext:
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    return ctx


@dataclasses.dataclass
class _arg_type(logic.bin_arg_type):
    rcc_host: str = 'localhost'
    rcc_port_num: int = 2005
    web_host: str | None = None
    web_port: logic.port = logic.port(
        port_num=80,
        is_ssl=False,
        is_ipv6=False,
    ),  # type: ignore
    user_code: str | None = None
    delay: float = 1

    def sanitise(self):
        super().sanitise()
        if self.rcc_host == 'localhost':
            self.rcc_host = '127.0.0.1'
        if self.web_host == 'localhost':
            self.web_host = '127.0.0.1'

    def get_base_url(self) -> str:
        return \
            f'http{"s" if self.web_port.is_ssl else ""}://' + \
            f'{self.web_host}:{self.web_port.port_num}'


class obj_type(logic.bin_entry):
    local_args: _arg_type
    DIR_NAME = 'Player'

    def retr_version(self) -> util.versions.rōblox:
        try:
            res = urllib.request.urlopen(
                f'{self.local_args.get_base_url()}/roblox_version',
                context=get_none_ssl(),
            )
        except urllib.error.URLError:
            raise urllib.error.URLError(
                'No server is currently running on ' +
                f'"{self.local_args.web_host}:{
                    self.local_args.web_port.port_num}".',
            )

        return util.versions.rōblox.from_name(str(res.read(), encoding='utf-8'))

    def save_app_setting(self) -> str:
        '''
        Modifies settings to point to correct host name.
        '''
        path = self.get_versioned_path('AppSettings.xml')
        with open(path, 'w') as f:
            f.write('\n'.join([
                """<?xml version="1.0" encoding="UTF-8"?>""",
                """<Settings>""",
                f"""\t<BaseUrl>{self.local_args.get_base_url()}</BaseUrl>""",
                """</Settings>""",
            ]))
        return path

    def enable_mutex(self) -> None:
        '''
        Enables multiple instances of Rōblox to run concurrently.
        '''
        ctypes.windll.kernel32.CreateMutexW(0, 1, "ROBLOX_singletonEvent")

    def save_ssl(self) -> None:
        if not self.local_args.web_port.is_ssl:
            return

        try:
            res = urllib.request.urlopen(
                f'{self.local_args.get_base_url()}/retrieve_certs',
                context=get_none_ssl(),
            )
        except urllib.error.URLError:
            raise urllib.error.URLError(
                'No server is currently running on ' +
                f'"{self.local_args.web_host}:{
                    self.local_args.web_port.port_num}".',
            )

        path = self.get_versioned_path('SSL', 'cacert.pem')
        with open(path, 'wb') as f:
            f.write(res.read())

    def initialise(self) -> None:
        self.save_app_setting()
        self.enable_mutex()
        self.save_ssl()

        time.sleep(self.local_args.delay)
        base_url = self.local_args.get_base_url()
        self.make_popen([
            self.get_versioned_path('RobloxPlayerBeta.exe'),
            '-a', f'{base_url}/login/negotiate.ashx',
            '-j', f'{base_url}/game/placelauncher.ashx?' +
            urllib.parse.urlencode({k: v for k, v in {
                'ip':
                    self.local_args.rcc_host,
                'port':
                    self.local_args.rcc_port_num,
                'user':
                    self.local_args.user_code,
            }.items() if v}),
            '-t', '1',
        ])


class arg_type(_arg_type):
    obj_type = obj_type
