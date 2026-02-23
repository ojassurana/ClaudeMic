# /mic-setup

Help the user set up ClaudeMic for voice-to-text input.

## Steps

1. Check if ClaudeMic is installed by running `claudemic status`.
2. If not installed, tell the user to run:
   ```bash
   cd <plugin-dir> && pip install -e .
   ```
3. Guide them through `claudemic setup` to configure their OpenAI API key.
4. Remind them to grant macOS permissions:
   - **Microphone** access for their terminal app
   - **Accessibility** access for their terminal app (keyboard simulation)
   - **Input Monitoring** access for their terminal app (hotkey detection)
5. Start the daemon with `claudemic start`.
6. Test by pressing **Cmd+Shift+M** and speaking a short phrase.

## Usage

- **Cmd+Shift+M** (single press): Toggle mic on/off. 5-minute auto-timeout.
- **Cmd+Shift+M** (double-tap): Perpetual mode — no auto-timeout.
- Run `claudemic stop` to stop the daemon.
- Run `claudemic status` to check if it's running.
