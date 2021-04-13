# lsgraph

lsgraph was created with the aim of supporting reskilling and upskilling for both organisations and individuals, using machine learning and other data science methods. Over time, we plan to include in lsgraph a steadily increasing set of services for this purpose. 

lsgraph currently provides services to:
* collect course details
* associate learning resources with skills
* recommend learning resources for a learner based on target skills
* recommend suitable job profiles based on current skills
* suggest reskilling options for target jobs across a workforce. 

This project was released by [LearnerShape](https://www.learnershape.com), which uses these services to provide reskilling and upskilling services through a user-facing website.

lsgraph is interacted with programmatically. This is ideal for research or building functionality into a larger project.

Our approach is centred around 'skills', which is a broad term used to cover the full range of personal abilities (e.g. knowledge, competences and aptitudes). Skills are organised into a 'skills graph', which is a hierarchical directed acyclic graph associating skills in a framework. Multiple, independent 'skills graphs' can be hosted by lsgraph to support the needs of multiple organisations. As an example, the public graph used at Learnershape (and included with lsgraph) contains the top-level skill 'software engineering' that links to the skill 'languages' that links to the skill 'Python'.

Skills in a skills graph can be associated with individual learners or job profiles, and connected to learning resources including courses, videos, articles, etc. Individuals can create a profile for themselves that lists all of their skills and provides a level for each (current level options are beginner, intermediate, advanced, and expert). Profiles can also be created for specific jobs. These profiles can then be compared enabling job recommendation (a one-to-many comparison) and workforce planning (a many-to-many comparison)

Courses can be marked as teaching a particular skill. This is an area of active development. These links can be made with a variety of machine learning models and optionally manually reviewed.

In production lsgraph is run as a web service with requests and responses exchanged as JSON formatted objects. A Dockerfile and docker-compose file have been provided to start a working instance of lsgraph. Any questions should be sent to jonathan@learnershape.com

# Installing


## Download and install software

For convenience, a docker-compose file is included for running the service. This is all that is required but git and jupyter are also recommended.

First, install Docker and docker-compose:
* [Docker](https://docs.docker.com/get-docker/)
* [docker-compose](https://docs.docker.com/compose/install/)

lsgraph can be downloaded as a zip archive. However, using git it is easier to get updates. [Install git](https://git-scm.com/downloads), open a terminal, navigate to where you want to store lsgraph, and then run:

`git clone git@github.com:LearnerShape/lsgraph.git`

If you are unfamiliar with using a terminal or command line these guides for [Linux (and Mac)](https://ubuntu.com/tutorials/command-line-for-beginners#1-overview) and [Windows](https://www.computerhope.com/issues/chusedos.htm) will hopefully be useful.

Notebooks are available demonstrating the lsgraph functionality. These require jupyter to run. If you have Python installed running `pip install jupyter` should be sufficient. If you do not have a version of Python installed, the [Ananconda distribution](https://www.anaconda.com/products/individual) is recommended.

## Before first running

Using the terminal, navigate to the lsgraph directory and start the database:

`docker-compose up lsdatabase`

While the database is running this will print any logs. Start a new terminal, navigate to the lsgraph directory again and set up the initial database:

`docker exec -i lsgraph_lsdatabase_1 psql -U postgres postgres < schema.sql`

If you are using PowerShell on Windows the above command will cause an error. Piping `<` is not supported in the same way. This can be resolved by first moving the schema.sql file into the running container, and then initializing the database.
Move schema.sql:
`docker cp schema.sql lsgraph_lsdatabase_1:schema.sql`
Connect to container:
`docker exec -it lsgraph_lsdatabase_1 /bin/bash`
Initialize database:
`psql -U postgres postgres < schema.sql`
Then exit the container with Ctrl-D.

## First run

In the terminal running the database press Ctrl-C to stop it. Then, run both the database and lsgraph web application with:

`docker-compose up --build`

The service is then available at http://localhost:5000/

## Interacting with the service

Notebooks for interacting with the service are available in the notebooks directory.

* [Setting up graphs, organisations, profiles, and users](https://github.com/LearnerShape/lsgraph/blob/main/notebooks/setup.ipynb)
* [Job recommendation](https://github.com/LearnerShape/lsgraph/blob/main/notebooks/job%20recommendation.ipynb)
* [Workforce planning](https://github.com/LearnerShape/lsgraph/blob/main/notebooks/workforce%20planning.ipynb)
* [Course recommendation](https://github.com/LearnerShape/lsgraph/blob/main/notebooks/course%20recommendation.ipynb)

These can be run using jupyter. In a terminal navigate to the notebooks directory and run:

`jupyter notebook`

This will open a web browser window with the notebooks available. If using jupyter for the first time this [tutorial](https://www.dataquest.io/blog/jupyter-notebook-tutorial/) may be useful.

## Loading courses and scoring

Courses are collected from providers and scored against skills using a command line interface.

A sample configuration file is included at cli/config.json for the test organisation created in the notebooks above. A crawler for [Pluralsight](https://www.pluralsight.com/) is also included.

The program is structured to facilitate easily creating crawlers for other services. Common functionality is encapsulated into generic crawler classes. When creating a new crawler they inherit from the generic classes. See `cli/plugins/crawlers/pluralsight.py` for an example.

To crawl all providers for the test organisation created in the notebooks:

`python ls.py --config=cli/config.json --env=testing crawl --organisation Test`

The above command can be run from the host or the docker container. The following commands connect to the database and if using the testing environment must be run from within the docker container. Instead, the testing-host environment is used enabling the commands to be run from the host.

The courses can be scored against the skill graph:

`python ls.py --config=cli/config.json --env=testing-host classify --organisation Test --model=simple`

As with crawlers, new models can also be easily created. The simple model used above can be seen at `cli/plugins/models/simple.py`.

Next, courses and scores can be loaded into the database:

`python ls.py --config=cli/config.json --env=testing-host load --organisation=Test --courses --model=simple`

A vector representation for each skill is used during job recommendation. The packages required must first be installed by running:

`pip install -r requirements-model.txt`

The vector embeddings can then be generated with:

`python ls.py --config=cli/config.json --env=testing-host embed --organisation=Test`


# Contributing

For guidance on reporting issues, suggesting new features and contributing to project development, see the [contributing guidelines](https://github.com/LearnerShape/lsgraph/blob/main/CONTRIBUTING.md).

