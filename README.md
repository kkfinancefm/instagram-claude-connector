# Instagram Claude Connector

An experimental local MCP server that lets Claude inspect sampled frames from publicly accessible Instagram Reels.

## What it does

- Accepts an Instagram Reel, post, or IGTV URL.
- Attempts to retrieve the public video with yt-dlp.
- Extracts five frames with FFmpeg.
- Returns those frames to Claude so Claude can analyze visible scenes, composition, style, and on-screen text.

## Important limitations

- This is an early prototype, not a hosted service.
- It works only when Instagram allows unauthenticated access to the video. Instagram may block downloads or require login, so some public links will fail.
- It does not access private accounts, bypass login, or use Instagram account cookies.
- It samples still frames; it does not yet analyze the full motion or audio track.
- Keep usage respectful of Instagram's terms, copyright, and the rights of creators.

## Requirements

- Python 3.10+
- FFmpeg installed and available on your PATH
- Claude Desktop with local MCP server support

## Install

Clone this repository, then run:

```bash
python -m venv .venv
```

Activate the environment:

**Windows PowerShell**
```powershell
.venv\Scripts\Activate.ps1
```

**macOS / Linux**
```bash
source .venv/bin/activate
```

Install Python dependencies:

```bash
pip install -r requirements.txt
```

Install FFmpeg separately and verify that `ffmpeg -version` works in your terminal.

## Connect to Claude Desktop

Add a server entry to Claude Desktop's MCP configuration. Replace the path below with the absolute path to this repository on your computer.

**Windows example**
```json
{
  "mcpServers": {
    "instagram-reel-analyzer": {
      "command": "C:\\absolute\\path\\to\\instagram-claude-connector\\.venv\\Scripts\\python.exe",
      "args": [
        "C:\\absolute\\path\\to\\instagram-claude-connector\\server.py"
      ]
    }
  }
}
```

**macOS / Linux example**
```json
{
  "mcpServers": {
    "instagram-reel-analyzer": {
      "command": "/absolute/path/to/instagram-claude-connector/.venv/bin/python",
      "args": [
        "/absolute/path/to/instagram-claude-connector/server.py"
      ]
    }
  }
}
```

Restart Claude Desktop. You should then see the `analyze_instagram_reel` tool available.

## Example prompt

"Use analyze_instagram_reel on this public Instagram Reel URL. Describe the opening hook, visual sequence, editing style, visible captions, and storytelling structure. Separate observations from guesses."

## Development status

Prototype. No download statistics or production reliability claims are made yet.

## License

No license has been added yet. All rights remain with their respective owners until a license is selected.
