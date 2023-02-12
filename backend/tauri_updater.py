from functools import lru_cache, wraps
import time
from flask import Blueprint
import requests


def time_cache(max_age, maxsize=None, typed=False):
    """Least-recently-used cache decorator with time-based cache invalidation.
    Args:
        max_age: Time to live for cached results (in seconds).
        maxsize: Maximum cache size (see `functools.lru_cache`).
        typed: Cache on distinct input types (see `functools.lru_cache`).
    """

    def _decorator(fn):
        @lru_cache(maxsize=maxsize, typed=typed)
        def _new(*args, __time_salt, **kwargs):
            return fn(*args, **kwargs)

        @wraps(fn)
        def _wrapped(*args, **kwargs):
            return _new(*args, **kwargs, __time_salt=int(time.time() / max_age))

        return _wrapped

    return _decorator


tauri_releases_bp = Blueprint("tauri_releases", __name__, url_prefix="/tauri-releases")

SOFTWARE_PLUS_DESKTOP_REPO = "abdennour-touat/software-plus"

PLATFORMS = [  # platform, extension
    # (('linux-x86_64',), 'amd64.AppImage.tar.gz'),
    # (('darwin-x86_64', 'darwin-aarch64'), 'app.tar.gz'),
    (("windows-x86_64",), "x64_en-US.msi.zip"),
]

# https://github.com/abdennour-touat/software-plus/releases/download/app-v0.1.3/software-plus_0.1.3_x64_en-US.msi.zip
@time_cache(60 * 5)  # every 5 minutes
def get_latest_gh_release(repo) -> dict:

    github_latest_release_url = f"https://api.github.com/repos/{repo}/releases/latest"
    print(github_latest_release_url)
    try:
        release = requests.get(github_latest_release_url).json()
    except requests.RequestException:
        return {}
    release_response = {
        "version": release["tag_name"],
        "notes": release["body"]
        .removesuffix("See the assets to download this version and install.")
        .rstrip("\r\n "),
        "pub_date": release["published_at"],
        "platforms": {},
    }
    print(release_response)
    for asset in release.get("assets", []):
        for for_platforms, extension in PLATFORMS:
            if asset["name"].endswith(extension):
                for platform in for_platforms:
                    release_response["platforms"][platform] = {
                        **release_response["platforms"].get(platform, {}),
                        "url": asset["browser_download_url"],
                    }
            elif asset["name"].endswith(f"{extension}.sig"):
                try:
                    sig = requests.get(asset["browser_download_url"]).text
                except requests.RequestException:
                    sig = ""
                for platform in for_platforms:
                    release_response["platforms"][platform] = {
                        **release_response["platforms"].get(platform, {}),
                        "signature": sig,
                    }
    return release_response


@tauri_releases_bp.route("/software-plus/<platform>/<current_version>")
def software_plus_api(platform, current_version):
    latest_release = get_latest_gh_release(SOFTWARE_PLUS_DESKTOP_REPO)
    if not latest_release:
        # GH API request failed in get_latest_release for GKD
        # TODO: Push Discord or Element notification (max once) if request failed
        return "", 204
    try:
        # version checks
        latest_version = latest_release["version"]
        latest_maj, latest_min, latest_patch = latest_version.lstrip("v").split(".")
        cur_maj, cur_min, cur_patch = current_version.lstrip("v").split(".")
        if (
            cur_maj == latest_maj
            and cur_min == latest_min
            and cur_patch == latest_patch
        ):
            raise ValueError
        # NOTE: here you may want to check the current_version or platform (see README.md)
    except ValueError:
        return "", 204
    return latest_release


@tauri_releases_bp.route("/software-plus/")
def software_plus_page():
    # TODO: Download Links Page
    return "", 404
