# lsgraph


**In August 2021 a new iteration of lsgraph was released with improved functionality. Existing users of lsgraph should use the [version1 branch](https://github.com/LearnerShape/lsgraph/tree/version1)** 

lsgraph was created with the aim of supporting reskilling and upskilling for both organisations and individuals, using machine learning and other data science methods. Over time, we plan to include in lsgraph a steadily increasing set of services for this purpose. 

The update of lsgraph is intended to separate the services provided by lsgraph from the frontend web application created for and run at [learnershape.com](https://www.learnershape.com/).

Functionality added includes:
* Skill creation and graph modification
* Learning resource management
* User management
* Group creation and management
* Resource collections
* "Online" application of machine learning models

Existing functionality will also be moved and improved:
* Learning resource recommendation
* Job recommendation
* Workforce planning
 

# Background

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

## First run

Using the terminal, navigate to the lsgraph directory and start all services:

`docker-compose up --build`

The lsgraph API is then available at http://localhost:5000/

## Interacting with the service

Notebooks for interacting with the service are available in the notebooks directory.

* [Setting up graphs, organisations, profiles, and users](https://github.com/LearnerShape/lsgraph/blob/main/notebooks/setup.ipynb)
* [Job recommendation](https://github.com/LearnerShape/lsgraph/blob/main/notebooks/job%20recommendation.ipynb)
* [Workforce planning](https://github.com/LearnerShape/lsgraph/blob/main/notebooks/workforce%20planning.ipynb)
* [Course recommendation](https://github.com/LearnerShape/lsgraph/blob/main/notebooks/course%20recommendation.ipynb)

These can be run using jupyter. In a terminal navigate to the notebooks directory and run:

`jupyter notebook`

This will open a web browser window with the notebooks available. If using jupyter for the first time this [tutorial](https://www.dataquest.io/blog/jupyter-notebook-tutorial/) may be useful.

# Contributing

For guidance on reporting issues, suggesting new features and contributing to project development, see the [contributing guidelines](https://github.com/LearnerShape/lsgraph/blob/main/CONTRIBUTING.md).

