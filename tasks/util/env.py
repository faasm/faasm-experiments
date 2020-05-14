from os.path import dirname, join, realpath

EXPERIMENTS_ROOT = dirname(dirname(dirname(realpath(__file__))))
EXPERIMENTS_ANSIBLE_ROOT = join(EXPERIMENTS_ROOT, "ansible")
