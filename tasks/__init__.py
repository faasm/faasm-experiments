from invoke import Collection

from . import data
from . import experiments
from . import genomics

# Include all Faasm tasks
from faasmcli.tasks import ns

# Tasks from this repo
ns.add_collection(data)
ns.add_collection(experiments)
ns.add_collection(genomics)
