import time

import py
import pyx

# compile
# python setup.py build_ext --inplace

number = 100

start = time.time()
py.test(number)
end = time.time()

py_time = end - start
print(f"Python time = {py_time}")

start = time.time()
pyx.test(number)
end = time.time()

cy_time = end - start
print(f"Cython time = {cy_time}")

print(f"Speedup = {py_time / cy_time}")
