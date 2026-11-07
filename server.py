import glob
import os
import re
import subprocess
import tempfile
from urllib.parse import urlparse

import yt_dlp
from mcp.server.fastmcp import FastMCP, Image

mcp = FastMCP("instagram-reel-analyzer")

ALLOWED_HOSTS = {"instagram.com", "www.instagram.com", "m.instagram.com"}
MAX_BYTES = 100 * 1024 * 1024
MAX_SECONDS = 180
FRAME_COUNT = 5


def validate_reel_url(url: str) -> str:
    parsed = urlparse(url)
    host = (parsed.hostname or "").lower()
    if parsed.scheme != "https" or host not in ALLOWED_HOSTS:
        raise ValueError("Use an HTTPS link from instagram.com.")
    if not re.match(r"^/(reel|p|tv)/[A-Za-z0-9_-]+/?$", parsed.path):
        raise ValueError("That does not look like a supported Instagram post or Reel URL.")
    return url


@mcp.tool()
def analyze_instagram_reel(url: str) -> list:
    """Download a publicly accessible Instagram Reel and return five sample frames for visual analysis.

    Works only when Instagram permits unauthenticated access. It does not access private
    accounts, bypass login, or use account cookies. The caller (Claude) analyzes the
    returned images and can describe scenes, style, framing, and visible captions.
    """
    validate_reel_url(url)

    with tempfile.TemporaryDirectory(prefix="ig-reel-") as folder:
        output_template = os.path.join(folder, "reel.%(ext)s")
        options = {
            "outtmpl": output_template,
            "format": "best[ext=mp4]/best",
            "noplaylist": True,
            "max_filesize": MAX_BYTES,
            "socket_timeout": 20,
            "retries": 1,
            "quiet": True,
            "no_warnings": True,
            "skip_download": False,
        }

        try:
            with yt_dlp.YoutubeDL(options) as downloader:
                info = downloader.extract_info(url, download=True)
                video_path = downloader.prepare_filename(info)
        except Exception as exc:
            raise RuntimeError(
                "Instagram did not provide a downloadable public video. "
                "The Reel may require login, be unavailable, or be blocked by Instagram. "
                "Try a public Reel or upload the video directly to a trusted local workflow."
            ) from exc

        duration = float(info.get("duration") or 0)
        if duration <= 0:
            raise RuntimeError("Could not determine the video's duration.")
        if duration > MAX_SECONDS:
            raise ValueError(f"Video is longer than the {MAX_SECONDS}-second limit.")

        if not os.path.exists(video_path):
            candidates = [
                path for path in glob.glob(os.path.join(folder, "reel.*"))
                if not path.endswith((".part", ".ytdl"))
            ]
            if not candidates:
                raise RuntimeError("The downloaded video file could not be found.")
            video_path = candidates[0]

        timestamps = [
            duration * fraction
            for fraction in (0.05, 0.25, 0.50, 0.75, 0.95)
        ]
        content = [
            f"Video title: {info.get('title') or 'Instagram Reel'}",
            f"Duration: {duration:.1f} seconds.",
            "The following images are sampled frames in chronological order. "
            "Analyze only what is visible; do not assume unseen motion or audio."
        ]

        results = [{"type": "text", "text": "\n".join(content)}]

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
    mcp.run()
