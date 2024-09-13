# Validation service

Validation service based on the [mu-python-template](https://github.com/mu-semtech/mu-python-template) template for microservices written in Python. 

Please see there for general instructions on building and running the service.

## Configuration

The Dockerfile needs to set the environment parameters OPENAI_KEY and OPENAI_ORGANIZATION with a valid OpenAI account key and organization ID.

## Usage

The service takes two arguments. The *id* argument expects the ID of a decision to make something a monument (e.g. [14850](https://besluiten.onroerenderfgoed.be/besluiten/14850)), while the *text* argument expects a description of the works planned in Dutch (e.g. "Ik ben van plan om een trap te verplaatsen. Mag dat?").

The service returns an answer to the question from the OpenAI service after analyzing the submitted documents and the question.


