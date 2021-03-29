import click

from .config import Config
from .crawlers import Crawlers, begin_crawl
from .classifiers import Classifiers, begin_classification
from .load import (load_courses,
                   load_scores_from_results,
                   load_levels_from_results,
                   load_scores_from_model)

@click.group()
@click.option('--config', help='Location of config file')
@click.option('--env', help='Environment to fetch skills/load scores',
              required=True)
def run(config, env):
    """Process configuration options"""
    Config.load(config)
    Config.set_env(env)
    Crawlers.load(Config.plugin_directory)
    Classifiers.load(Config.plugin_directory)



@run.group(invoke_without_command=True)
@click.pass_context
def inspect(ctx):
    """Collect information on current status"""
    if ctx.invoked_subcommand is None:
        click.echo('list')
    else:
        click.echo('Running ' + ctx.invoked_subcommand)


from .list import (providers,crawls,organisations,models,skills,results)



@run.command()
@click.option('--organisation', help='Crawl providers for organisation')
@click.option('--provider', help='Crawl specific provider')
def crawl(organisation, provider):
    """Crawl providers for courses"""
    begin_crawl(organisation, provider)



@run.command()
@click.option('--crawl', help='Crawl used for courses')
@click.option('--organisation', help='Latest crawls for all providers used by organisation')
@click.option('--provider', help='Latest crawls for specific provider')
@click.option('--model', help='Model to use for scoring courses')
@click.option('--clean', default=False, help='Create a new analysis rather than resuming an existing analysis')
def classify(crawl, organisation, provider, model, clean):
    """Apply a model to predict the best courses for a set of skills"""
    begin_classification(organisation, model, provider, crawl, clean)


@run.command()
@click.option('--crawl', help='Crawl used for courses')
@click.option('--organisation',
              help='Latest crawls for all providers used by organisation')
@click.option('--provider', help='Latest crawls for specific provider')
@click.option('--clean', default=False, is_flag=True,
              help='Update existing courses')
@click.option('--courses', default=False, is_flag=True, help='Load courses')
@click.option('--model', help='Model to obtain scores')
@click.option('--results', help='Scoring results to load into DB')
@click.option('--levels', help='Level results to load into DB')
def load(crawl, organisation, provider, clean,
         courses, model, results, levels):
    """Load a set of results into the environment database"""
    if courses:
        load_courses(organisation, provider, crawl, clean)
    if results:
        load_scores_from_results(organisation, results)
    elif levels:
        load_levels_from_results(organisation, levels)
    elif model:
        load_scores_from_model(organisation, model)

@run.command()
@click.option("--organisation",
              help="Generate embeddings for all skills used by organisation")
def embed(organisation):
    """Generate and load embeddings for skill paths"""
    from .embedding import generate_skill_embeddings
    click.echo("Initialising USE to generate embeddings")
    generate_skill_embeddings(organisation)
