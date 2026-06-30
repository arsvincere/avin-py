# ────────────────────────────────────────────────────────────────────────────
#  AVIN
#  Understand the market before trading it.
#
#  https://avin.info
# ────────────────────────────────────────────────────────────────────────────

from __future__ import annotations

import click


@click.group()
def cli() -> None:
    """AVIN command line interface."""


@cli.group()
def data() -> None:
    """Market data commands."""


@data.command("sync")
@click.argument("code", required=False)
@click.argument("market_data", required=False)
def data_sync(
    code: str | None,
    market_data: str | None,
) -> None:
    """Sync local market data with data.toml."""
    if (code is None) != (market_data is None):
        raise click.UsageError(
            "Use either 'avin data sync' or "
            "'avin data sync <code> <market_data>'."
        )

    click.echo("avin data sync: not implemented yet")


def main() -> None:
    cli()
