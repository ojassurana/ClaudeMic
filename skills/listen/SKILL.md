# /listen

Voice-to-text input using the microphone.

When the user wants to speak instead of type — e.g., "listen to me", "use my mic", "dictate", "voice input", or "/listen" — use the `mcp__claudemic__listen` tool to capture and transcribe their speech.

## Usage

1. Call the `mcp__claudemic__listen` tool. It will record audio from the user's microphone and return transcribed text.
2. Present the transcribed text to the user, or use it as input for whatever they requested.

## Setup

If the listen tool returns an API key error, guide the user through setup:

1. Call `mcp__claudemic__setup` with their OpenAI API key.
2. Remind them to grant **Microphone** access to their terminal app in System Settings > Privacy & Security.

## Checking status

Use `mcp__claudemic__status` to check if the API key is configured and an audio input device is available.
