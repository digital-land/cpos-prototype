import csv
import click
import requests

from flask.cli import with_appcontext
from contextlib import closing


@click.command()
@with_appcontext
def load():
    cpo_data_url = 'https://raw.githubusercontent.com/digital-land/...'
    print("Fetching data.....")

