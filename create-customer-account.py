# Copyright (C) 2021  Learnershape and contributors

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.



import click
from sqlalchemy.exc import IntegrityError
from test.conftest import create_customer

@click.command()
@click.argument("name")
@click.argument("email")
def customer_account(name, email):
    """Create a customer account"""
    try:
        customer_id, access_id, access_secret = create_customer(name, email)
        click.echo(f"Customer ID: {customer_id}")
        click.echo(f"API Key: {access_id}")
        click.echo(f"Access Token: {access_secret}")
    except IntegrityError as err:
        click.echo("Duplicate key error")
        click.echo(err.orig)


if __name__ == "__main__":
    customer_account()
