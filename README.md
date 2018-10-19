# indicepa-python
A simple, convergent API for indicePA.

This application is based on `OpenAPI` specs in `openapi.yaml` and
on the connexion framework managing requests using the openapi.yaml 
as a dispatch table.

## Running

In three steps:

    1. Insert in `config.yaml`:
       - your LDAP iPA credentials
       - (optional) the public url of your server if it's not localhost
    2. Run

         docker-compose up simple


Dependencies can be found in [Dockerfile](Dockerfile) and [requirements.txt](requirements.txt)

## Using

The API provides the following URLs:

  - https://$SERVERIP:8443/ipa/v0/ui/			# The Web User Interface
  - https://$SERVERIP:8443/ipa/v0/openapi.json		# OpenAPI specs in json

## Testing

You can test locally via tox and python 3.7, with

        tox

Or via Docker

        docker-compose up test
