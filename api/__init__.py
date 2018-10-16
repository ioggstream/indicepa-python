from .amministrazioni import *
from .aoo import *
from .uffici import *


def status():
    """
    Connect and disconnect from the LDAP Server. If it works, return 200.
    :return:
    """
    c = connect3(**current_app.config["server"])
    c.unbind()
    return problem(
        status=200,
        title="Success",
        detail="Application is working normally",
        ext={"result": "ok"},
    )
