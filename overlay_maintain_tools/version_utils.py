def cleanup_version(version: str) -> str:
    """Does some primitive cleanup of version string
    :type version: str, a version string from upstream
    :return version normalized to ebuild file name convention
    """
    return version[1:] if version.startswith("v") else version


def get_latest_version_from_github(target: str) -> str:
    # TODO: handle lack of version
    reply = requests.get(f"https://github.com/{target}/releases/latest")
    version_reply = reply.url.split("/")[-1]
    return cleanup_version(version_reply)
