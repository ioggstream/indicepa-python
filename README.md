# indicepa-python
A simple, convergent API for indicePA.

This application is based on `OpenAPI` specs in `openapi.yaml` and
on the connexion framework managing requests using the openapi.yaml 
as a dispatch table.

## Running

Just run

         docker-compose up simple

Dependencies can be found in [Dockerfile](Dockerfile) and [requirements.txt](requirements.txt)

## Testing

You can test locally via tox and python 3.7, with

        tox

Or via Docker

        docker-compose up test
