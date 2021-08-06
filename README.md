# Podman Discord Bot

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

[![CircleCI](https://circleci.com/gh/infiniteregrets/podman-bot.svg?style=svg)](https://circleci.com/gh/infiniteregrets/podman-bot)

This is a cute little discord bot made for referring the Podman Docs and fetching information from the Docker Hub API. 
More features coming soon!

## Installing

**IMPORTANT:** Rename the `example_config.py` file to `config.py`, add your bot token there and choose a relevant prefix.

### Running in a container

`docker build -t <TAG> .`

`docker run <TAG>` or `docker run -it <TAG>`

One can also use docker compose but I have not added the relevant files for that.

### Running locally

*Make sure your system has **chromium driver** installed.*

`pipenv install`

`pipenv run python3 index.py`

Sometimes, some weird error might occur regarding your dependencies then you might wanna try running ` pipenv lock --pre --clear `.

## Contributing

Have something cool in mind? Just make sure to format with `black` and lint your code before opening a PR.
