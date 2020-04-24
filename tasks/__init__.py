from invoke import Collection

from . import bench_capacity
from . import bench_mem
from . import bench_time
from . import bench_tpt
from . import data
from . import experiments
from . import genomics

# Include all Faasm tasks
from faasmcli.tasks import ns

# Tasks from this repo
ns.add_collection(bench_capacity)
ns.add_collection(bench_mem)
ns.add_collection(bench_time)
ns.add_collection(bench_tpt)
ns.add_collection(data)
ns.add_collection(experiments)
ns.add_collection(genomics)
