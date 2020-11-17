import click

from . import inspect
from .config import Config
from .crawlers import Crawlers


@inspect.command()
def providers():
    for i in Crawlers.crawlers:
        click.echo(i)


@inspect.command()
def crawls():
    for i,j in Crawlers.crawlers.items():
        c = j(Config.active['results_dir'])
        click.echo("{0}: {1}".format(i, len(c.list())))


@inspect.command()
def organisations():
    click.echo('c2')


@inspect.command()
def models():
    click.echo('c2')


@inspect.command()
def skills():
    click.echo('c2')


@inspect.command()
def results():
    click.echo('c2')

