import glob
import os
import re
import subprocess
import tempfile
from urllib.parse import urlparse

import yt_dlp
from mcp.server.fastmcp import FastMCP
from mcp.types import Image, TextContent

mcp = FastMCP("instagram-reel-analyzer")

ALLOWED_HOSTS = {"instagram.com", "www.instagram.com", "m.instagram.com"}
MAX_BYTES = 100 * 1024 * 1024
MAX_SECONDS = 180


def validate_reel_url(url: str) -> None:
    parsed = urlparse(url)
    host = (parsed.hostname or "").lower()
    if parsed.scheme != "https" or host not in ALLOWED_HOSTS:
        raise ValueError("Use an HTTPS link from instagram.com.")
    if not re.match(r"^/(reel|p|tv)/[A-Za-z0-9_-]+/?$", parsed.path):
        raise ValueError("That does not look like a supported Instagram post or Reel URL.")


@mcp.tool()
def analyze_instagram_reel(url: str) -> list:
    """Return five sampled frames from a publicly accessible Instagram Reel for Claude to inspect.

    Works only when Instagram permits unauthenticated access. Does not access private
    accounts, bypass login, or use account cookies. Claude analyzes the returned images.
    """
    validate_reel_url(url)

    with tempfile.TemporaryDirectory(prefix="ig-reel-") as folder:
        options = {
            "outtmpl": os.path.join(folder, "reel.%(ext)s"),
            "format": "best[ext=mp4]/best",
            "noplaylist": True,
            "max_filesize": MAX_BYTES,
            "socket_timeout": 20,
            "retries": 1,
            "quiet": True,
            "no_warnings": True,
        }

        try:
            with yt_dlp.YoutubeDL(options) as downloader:
                info = downloader.extract_info(url, download=True)
                video_path = downloader.prepare_filename(info)
        except Exception as exc:
            raise RuntimeError(
                "Instagram did not provide a downloadable public video. "
                "The Reel may require login, be unavailable, or be blocked by Instagram."
            ) from exc

        duration = float(info.get("duration") or 0)
        if duration <= 0:
            raise RuntimeError("Could not determine the video's duration.")
        if duration > MAX_SECONDS:
            raise ValueError(f"Video exceeds the {MAX_SECONDS}-second limit.")

        if not os.path.exists(video_path):
            candidates = [
                path for path in glob.glob(os.path.join(folder, "reel.*"))
                if not path.endswith((".part", ".ytdl"))
            ]
            if not candidates:
                raise RuntimeError("Downloaded video file could not be found.")
            video_path = candidates[0]

        timestamps = [
            duration * fraction for fraction in (0.05, 0.25, 0.50, 0.75, 0.95)
        ]
        results = [
            TextContent(
                type="text",
                text=(
                    f"Title: {info.get('title') or 'Instagram Reel'}\\n"
                    f"Duration: {duration:.1f} seconds.\\n"
                    "The images below are sampled frames in chronological order. "
                    "Analyze only visible content; do not assume unseen motion or audio."
                ),
            )
        ]

        for index, timestamp in enumerate(timestamps):
            frame_path = os.path.join(folder, f"frame-{index}.jpg")
            subprocess.run(
                [
                    "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
                    "-ss", str(timestamp), "-i", video_path,
                    "-frames:v", "1", "-vf", "scale=960:-1",
                    "-q:v", "4", frame_path,
                ],
                check=True,
                timeout=30,
                capture_output=True,
            )
            with open(frame_path, "rb") as frame:
                results.append(Image(data=frame.read(), format="jpeg"))

        return results


if __name__ == "__main__":
    # Claude.ai requires a publicly reachable HTTP MCP endpoint, not local stdio.
    mcp.run(
        transport="streamable-http",
        host="0.0.0.0",
        port=int(os.environ.get("PORT", "10000")),
    )
