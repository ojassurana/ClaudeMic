# ClaudeMic

Voice-to-text plugin for [Claude Code](https://docs.anthropic.com/en/docs/claude-code). Speak into your microphone and get transcribed text back in Claude using OpenAI Whisper.

## Requirements

- macOS or Linux
- Python 3.10+
- An [OpenAI API key](https://platform.openai.com/api-keys) (for Whisper transcription)
- Microphone access granted to your terminal app

## Install

```bash
git clone https://github.com/ojassurana/ClaudeMic.git
```

That's it. Dependencies are installed automatically on first launch.

## Usage

Start Claude Code with the plugin:

```bash
claude --plugin-dir /path/to/ClaudeMic
```

### First-time setup

Tell Claude your OpenAI API key:

> "Set up my mic with API key sk-..."

Or set `OPENAI_API_KEY` as an environment variable to skip this step.

### Voice input

Say any of the following to Claude:

- "/listen"
- "listen to me"
- "use my mic"
- "dictate"

Claude will activate your microphone, record until you stop speaking, transcribe the audio, and use the text directly.

### Check status

> "check mic status"

Reports whether your API key is configured and an audio input device is available.

## Tools

The plugin exposes three MCP tools:

| Tool | Description |
|------|-------------|
| `listen` | Records a single utterance from the mic and returns transcribed text. Optional `timeout` parameter (default 60s). |
| `setup` | Saves an OpenAI API key to `~/.claudemic/config.json`. |
| `status` | Checks API key configuration and audio input device availability. |

## macOS permissions

Your terminal app (Terminal, iTerm, Warp, etc.) needs **Microphone** access:

**System Settings > Privacy & Security > Microphone** — enable your terminal app.

## How it works

ClaudeMic runs as an MCP server over stdio. Claude Code manages the server lifecycle automatically — no background daemons or hotkeys involved.

1. Claude Code starts the MCP server via `scripts/run-server.sh`
2. On first run, the script creates a `.venv` and installs dependencies
3. When you ask Claude to listen, it calls the `listen` tool
4. The tool captures audio from your mic using `sounddevice`
5. Voice activity detection (VAD) detects when you stop speaking
6. The audio is sent to OpenAI Whisper for transcription
7. Transcribed text is returned directly to Claude

## Troubleshooting

**"python3 not found"** — Install Python 3.10+ and ensure `python3` is on your PATH.

**"No speech detected within timeout"** — Check that your mic is working and your terminal has microphone permission. Try increasing the timeout: the `listen` tool accepts a `timeout` parameter.

**"API key not configured"** — Tell Claude "set up my mic with API key sk-..." or export `OPENAI_API_KEY`.

**Rebuild the venv** — If dependencies get corrupted, delete `.venv` and relaunch:
```bash
rm -rf /path/to/ClaudeMic/.venv
claude --plugin-dir /path/to/ClaudeMic
```
