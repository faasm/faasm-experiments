from os.path import dirname, join, realpath

EXPERIMENTS_ROOT = dirname(dirname(dirname(realpath(__file__))))
EXPERIMENTS_THIRD_PARTY = join(EXPERIMENTS_ROOT, "third-party")
EXPERIMENTS_ANSIBLE_ROOT = join(EXPERIMENTS_ROOT, "ansible")
EXPERIMENTS_FUNC_DIR = join(EXPERIMENTS_ROOT, "func")

