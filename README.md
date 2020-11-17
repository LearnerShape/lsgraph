# lsgraph

lsgraph was created with the aim of supporting reskilling and upskilling for both organisations and individuals, using machine learning and other data science methods. Over time, we plan to include in lsgraph a steadily increasing set of services for this purpose. 

lsgraph currently provides services to:
* collect course details
* associate learning resources with skills
* recommend learning resources for a learner based on target skills
* recommend suitable job profiles based on current skills
* suggest reskilling options for target jobs across a workforce. 

This project was released by [LearnerShape](https://www.learnershape.com), which uses these services to provide reskilling and upskilling services through a user-facing website.

Our approach is centred around 'skills', which is a broad term used to cover the full range of personal abilities (e.g. knowledge, competences and aptitudes). Skills are organised into a 'skills graph', which is a hierarchical directed acyclic graph associating skills in a framework. Multiple, independent 'skills graphs' can be hosted by lsgraph to support the needs of multiple organisations. As an example, the public graph used at Learnershape (and included with lsgraph) contains the top-level skill 'software engineering' that links to the skill 'languages' that links to the skill 'Python'.

Skills in a skills graph can be associated with individual learners or job profiles, and connected to learning resources including courses, videos, articles, etc. Individuals can create a profile for themselves that lists all of their skills and provides a level for each (current level options are beginner, intermediate, advanced, and expert). Profiles can also be created for specific jobs. These profiles can then be compared enabling job recommendation (a one-to-many comparison) and workforce planning (a many-to-many comparison)

Courses can be marked as teaching a particular skill. This is an area of active development. These links can be made with a variety of machine learning models and optionally manually reviewed.

In production lsgraph is run as a web service with requests and responses exchanged as JSON formatted objects. A Dockerfile and docker-compose file have been provided to start a working instance of lsgraph

# Installing

For convenience, a docker-compose file is included for running the service.

First, install Docker and docker-compose:
* [Docker](https://docs.docker.com/get-docker/)
* [docker-compose](https://docs.docker.com/compose/install/)

Start the database and lsgraph service:

`docker-compose up --build`

Set up initial database:

`docker exec -i lsgraph_lsdatabase_1 psql -U postgres postgres < schema.sql`

The service is then available at http://localhost:5000/

## Interacting with the service

Notebooks for interacting with the service are available in the notebooks directory.

* [Setting up graphs, organisations, profiles, and users](https://github.com/LearnerShape/lsgraph/blob/main/notebooks/setup.ipynb)
* [Job recommendation](https://github.com/LearnerShape/lsgraph/blob/main/notebooks/job%20recommendation.ipynb)
* [Workforce planning](https://github.com/LearnerShape/lsgraph/blob/main/notebooks/workforce%20planning.ipynb)
* [Course recommendation](https://github.com/LearnerShape/lsgraph/blob/main/notebooks/course%20recommendation.ipynb)

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

Finally, courses and scores can be loaded into the database:

`python ls.py --config=cli/config.json --env=testing-host load --organisation=Test --courses --model=simple`


# Contributing

For guidance on reporting issues, suggesting new features and contributing to project development, see the [contributing guidelines](https://github.com/LearnerShape/lsgraph/blob/main/CONTRIBUTING.md).

