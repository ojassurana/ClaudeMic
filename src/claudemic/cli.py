"""Click CLI: setup, start, stop, status."""

import logging
import sys

import click

from .config import get_api_key, set_api_key
from .daemon import is_running, start_daemon, stop_daemon


@click.group()
def main():
    """ClaudeMic - Voice-to-text input for Claude Code."""
    pass


@main.command()
def setup():
    """Configure ClaudeMic (API key and permissions)."""
    click.echo("=== ClaudeMic Setup ===\n")

    # Check for existing key
    existing = get_api_key()
    if existing:
        masked = existing[:8] + "..." + existing[-4:]
        click.echo(f"Current API key: {masked}")
        if not click.confirm("Replace it?", default=False):
            click.echo("Keeping existing key.")
        else:
            _prompt_api_key()
    else:
        _prompt_api_key()

    click.echo("\n--- macOS Permissions ---")
    click.echo("ClaudeMic needs these permissions (System Settings > Privacy & Security):")
    click.echo("  1. Microphone: Allow your terminal app (Terminal / iTerm / etc.)")
    click.echo("  2. Accessibility: Allow your terminal app (for keyboard simulation)")
    click.echo("  3. Input Monitoring: Allow your terminal app (for hotkey detection)")
    click.echo("\nSetup complete! Run 'claudemic start' to begin.")


@main.command()
def start():
    """Start the ClaudeMic background daemon."""
    api_key = get_api_key()
    if not api_key:
        click.echo("Error: No API key configured. Run 'claudemic setup' first.", err=True)
        sys.exit(1)

    if start_daemon():
        click.echo("ClaudeMic daemon started. Press Cmd+Shift+M to toggle mic.")
    else:
        click.echo("ClaudeMic daemon is already running.")


@main.command()
@click.option("--quiet", is_flag=True, help="Suppress output.")
def stop(quiet):
    """Stop the ClaudeMic background daemon."""
    if stop_daemon():
        if not quiet:
            click.echo("ClaudeMic daemon stopped.")
    else:
        if not quiet:
            click.echo("ClaudeMic daemon is not running.")


@main.command()
def status():
    """Check if the ClaudeMic daemon is running."""
    if is_running():
        click.echo("ClaudeMic daemon is running.")
    else:
        click.echo("ClaudeMic daemon is not running.")


@main.command(name="_run", hidden=True)
def run_core():
    """Internal: run the core loop (called by daemon)."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    from .core import Core

    Core().run()


def _prompt_api_key():
    """Prompt user for OpenAI API key and save it."""
    key = click.prompt("Enter your OpenAI API key", hide_input=True)
    key = key.strip()
    if not key.startswith("sk-"):
        click.echo("Warning: Key doesn't start with 'sk-'. Saving anyway.")
    set_api_key(key)
    click.echo("API key saved to ~/.claudemic/config.json")


if __name__ == "__main__":
    main()
