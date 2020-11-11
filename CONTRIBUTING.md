Thank you for considering contributing to lsgraph. Whether you are using the project, reporting bugs, requesting features, or submitting code your involvement helps build lsgraph. 


# Support questions

If you have questions about lsgraph the best point of contact is jonathan@learnershape.com.


# Getting involved

We welcome bug reports, feature requests, and code contributions.


# Reporting issues

Please report bugs on our issues page. The more information you can provide the faster a fix can be created. The following information helps:

- Describe what you expected to happen
- A simple test case that triggers the bug. This is also known as a minimal reproducible example.
- Describe what actually happened. If you can include tracebacks or logs these are very useful.
- List the code commit you are using together with the versions of any relevant software.


## Security issues

If you think a bug may have security implications please report it privately to jonathan@learnershape.com. Your report will be acknowledged and a plan established to address the issue. By having a fix available before a security issue is announced the public impact is hopefully reduced.

At Learnershape we are running lsgraph on a private subnet preventing direct access. This provides additional security benefits, but we are also committed to keeping lsgraph as secure as possible when running in a less secure environment.


# Contributing

## guidelines

lsgraph is a young project under active development. There is a lot to do and we would love to receive contributions from you.

If you want to contribute but do not know what to work on take a look at the open issues [*do we need a link?*] or contact jonathan@learnershape.com.

If you already have a new feature in mind the best place to start is creating a new feature request on our issues page. This avoids duplicated effort and ensures we will be able to merge your contribution into lsgraph when completed.

## license

This project is licensed under the GNU LGPL v3 license and by contributing you would be releasing your code under this license. The full text of this license can be found in the LICENSE.md file.

When creating a new source file it must begin with a license header:



    Copyright (C) 2019-2020  Learnershape and contributors

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Lesser General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Lesser General Public License for more details.

    You should have received a copy of the GNU Lesser General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.


## code style

Code written with a consistent code style is easier to read. Generally, we follow the PEP8 code style. If you see any code that appears to violate this style guide, please fix it and send a pull request.

Automated code linters and formatters can be useful. Black is a popular option.

## setting up development environment

lsgraph is a flask-based web application with a separate command line interface. A docker-compose file is available for rapidly starting an instance together with a supporting database instance.

## running tests

lsgraph was spun out from an internal project at LearnerShape. The internal test suite was tightly coupled to internal systems resulting in a greatly reduced public test suite. Additional tests and changes to facilitate testing are being made and contributions would also be welcome.

The test suite can be run with 

`pytest`

Areas of the codebase that do not have thorough tests can be found by generating a coverage report. The coverage package must be installed.

`pytest --cov= --cov-report=html`


# Code of conduct

We hope to build a welcoming and friendly community around this project. Everyone is invited to participate. Unethical and unprofessional behaviour will not be tolerated. We have adopted the Contributor Covenant to support this aim. Any issues can be reported to jonathan@learnershape.com or maury@learnershape.com.




