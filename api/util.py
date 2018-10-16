from flask import request
from connexion import problem


def assert_one_entry(count):
    if count == 0:
        return problem(
            status=404,
            title="Not Found",
            instance=request.url,
            detail="Entry not found",
        )
    if count > 1:
        return problem(
            status=404,
            title="Not Found",
            instance=request.url,
            detail="More than one entry",
        )
