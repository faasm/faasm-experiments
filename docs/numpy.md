# Numpy without BLAS

To benchmark a native Numpy without BLAS we need to run a custom build. 

To do this we can run:

```bash
./bin/build_unoptimized_numpy.sh
```

You can check the results with:

```python
import numpy as np

# This should show all as NOT_AVAILABLE
np.__config__.show()

# This should take several seconds and only use one thread
a = np.random.rand(2048, 2048)
b = np.random.rand(2048, 2048)
c = np.dot(a, b)
```

You can then try running the same thing with a default installation. There
should be some info under `lapack_opt_info` and `blas_opt_info`, then the matrix
multiplication will take under a second.

