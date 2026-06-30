from __future__ import annotations

import click


@click.group()
def cli() -> None:
    """AVIN command line interface."""


@cli.group()
def data() -> None:
    """Market data commands."""


@data.command("update")
def data_update() -> None:
    """Update local market data."""
    click.echo("avin data update: not implemented yet")


def main() -> None:
    cli()
