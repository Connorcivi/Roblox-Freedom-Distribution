import subprocess
import urllib3


def download_item(url: str) -> bytes | None:
    try:
        http = urllib3.PoolManager(headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36,gzip(gfe),gzip(gfe)'})
        response = http.request('GET', url)
        if response.status != 200:
            return None
        return response.data
    except urllib3.exceptions.HTTPError as e:
        return None


def download_rōblox_asset(asset_id: int) -> bytes | None:
    for key in {'id'}:
        result = download_item(
            'https://assetdelivery.roblox.com/v1/asset/?%s=%s' %
            (key, asset_id)
        )
        if result is not None:
            return result


def process_command_line(cmd_line: str) -> bytes:
    popen = subprocess.Popen(
        args=cmd_line,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        shell=True,
    )
    (stdout, _) = popen.communicate()
    return stdout
