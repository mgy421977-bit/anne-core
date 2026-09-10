"""Command-line interface for ANNE Core."""

from __future__ import annotations

import sys

import click

from anne_core.core import ANNECore
from anne_core.memory.sqlite import CognitiveMemory


def _print_log(log: list[str]) -> None:
    for line in log:
        click.echo(line)


@click.group()
@click.version_option(version="0.1.0", prog_name="anne-core")
def main() -> None:
    """ANNE Core — Open Cognitive Architecture CLI."""


@main.command()
@click.argument("question")
@click.option("--force-new", is_flag=True, help="Ignore memory and force a fresh exploration.")
@click.option("--db", default=None, help="Path to SQLite memory database.")
def ask(question: str, force_new: bool, db: str | None) -> None:
    """Run the cognitive loop for a question."""
    memory = CognitiveMemory(db_path=db) if db else CognitiveMemory()
    core = ANNECore(memory=memory)
    result = core.ask(question, force_new=force_new)
    _print_log(result.log)
    click.echo("")
    click.echo(result.response)


@main.command()
@click.option("--db", default=None, help="Path to SQLite memory database.")
def memory(db: str | None) -> None:
    """Show stored cognitive structures."""
    mem = CognitiveMemory(db_path=db) if db else CognitiveMemory()
    core = ANNECore(memory=mem)
    click.echo(core.memory_summary())


@main.command()
@click.option("--db", default=None, help="Path to temporary demo database.")
def demo(db: str | None) -> None:
    """Run the memory-reuse demonstration.

    Executes the same (or closely related) question twice and prints the
    distinct first-run vs second-run behaviour.
    """
    import tempfile
    import os

    # Use an isolated DB so the demo is reproducible and does not pollute
    # the user's main memory file.
    if db is None:
        fd, db = tempfile.mkstemp(suffix=".db", prefix="anne_demo_")
        os.close(fd)

    click.echo("=" * 60)
    click.echo("ANNE CORE — MEMORY REUSE DEMO")
    click.echo("=" * 60)
    click.echo(f"Using temporary memory: {db}")
    click.echo("")

    memory = CognitiveMemory(db_path=db)
    # Ensure clean slate
    memory.clear()
    core = ANNECore(memory=memory)

    question = "What are the main causes of urban heat islands?"

    # ---------- FIRST RUN ----------
    click.echo("-" * 60)
    click.echo("FIRST RUN")
    click.echo("-" * 60)
    result1 = core.ask(question)
    _print_log(result1.log)
    click.echo("")
    click.echo(result1.response)
    click.echo("")

    # ---------- SECOND RUN (same question) ----------
    click.echo("-" * 60)
    click.echo("SECOND RUN (same / related question)")
    click.echo("-" * 60)
    result2 = core.ask(question)
    _print_log(result2.log)
    click.echo("")
    click.echo(result2.response)
    click.echo("")

    click.echo("=" * 60)
    click.echo("DEMO SUMMARY")
    click.echo("=" * 60)
    click.echo(f"First run reused memory : {result1.reused}")
    click.echo(f"Second run reused memory: {result2.reused}")
    click.echo(f"Structures in memory    : {memory.count()}")
    click.echo("")
    if not result1.reused and result2.reused:
        click.echo("✓ Memory reuse behaviour demonstrated successfully.")
    else:
        click.echo("⚠ Unexpected reuse pattern — inspect logs above.")

    # Clean up temp DB if we created it
    if db and db.startswith(tempfile.gettempdir()):
        try:
            os.unlink(db)
        except OSError:
            pass


@main.command()
@click.option("--db", default=None, help="Path to SQLite memory database.")
def clear_memory(db: str | None) -> None:
    """Clear all cognitive structures (destructive)."""
    mem = CognitiveMemory(db_path=db) if db else CognitiveMemory()
    if click.confirm("Really erase all cognitive memory?"):
        mem.clear()
        click.echo("Memory cleared.")


if __name__ == "__main__":
    main()
