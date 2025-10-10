"""CLI (placeholder)."""
import click
@click.group()
def main():
    pass

@main.command()
def status():
    click.echo("OneFlow.AI OK")
