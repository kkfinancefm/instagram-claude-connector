# Instagram Claude Connector

An experimental remote MCP server that lets Claude inspect sampled frames from publicly accessible Instagram Reels.

## What it does

- Accepts an Instagram Reel, post, or IGTV URL.
- Attempts to retrieve the public video with yt-dlp.
- Extracts five still frames with FFmpeg.
- Returns those frames to Claude so it can analyze visible scenes, composition, style, and on-screen text.

## Important limitations

- This is an early prototype, not a production service.
- It works only when Instagram allows unauthenticated access. Instagram may block downloads or require login, so some public links will fail.
- It does not access private accounts, bypass login, or use Instagram account cookies.
- It samples five still frames; it does not yet analyze full motion or audio.
- Keep usage respectful of Instagram's terms, copyright, and creators' rights.
- The hosted service may sleep or have resource limits on a free hosting plan.

## Deploy for Claude.ai

Claude.ai custom connectors require a server reachable over the public internet using a remote MCP transport. This project uses Streamable HTTP at the `/mcp` endpoint.

1. Sign in to Render and choose **New → Blueprint**.
2. Connect the GitHub repository `kkfinancefm/instagram-claude-connector`.
3. Render reads `render.yaml` and creates the web service. Review the plan and settings before deploying.
4. Wait for deployment to finish.
5. Copy the public service URL shown by Render and append `/mcp`. For example: `https://YOUR-SERVICE.onrender.com/mcp`.

Do not use the example URL literally. Use the exact hostname Render assigns to your service.

## Add it to Claude.ai

1. Open Claude and go to **Customize → Connectors**.
2. Choose **Add** / **Add custom connector**.
3. Name it `Instagram Reel Analyzer`.
4. Paste your deployed MCP URL ending in `/mcp`.
5. Continue with **No sign in** if Claude offers that option; this prototype has no user authentication.
6. Add the connector, then enable it for a conversation from the **+** menu → **Connectors**.

Claude's interface labels can vary by plan and account.

## Local development

Requirements: Python 3.10+, FFmpeg, and pip.

```bash
python -m venv .venv
```

Activate the environment:

**Windows PowerShell**
```powershell
.venv\\Scripts\\Activate.ps1
```

**macOS / Linux**
```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the HTTP server:

**Windows PowerShell**
```powershell
$env:PORT=10000
python server.py
```

**macOS / Linux**
```bash
PORT=10000 python server.py
```

The MCP endpoint is `http://localhost:10000/mcp`.

## Example prompt

"Use analyze_instagram_reel on this public Instagram Reel URL. Describe the opening hook, visible scene sequence, editing style, captions, and storytelling structure. Separate observations from guesses."

## Development status

Prototype. No production reliability, adoption, or download statistics are claimed.

## License

No license has been added yet. All rights remain with their respective owners until a license is selected.
