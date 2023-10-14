echo "Starting benchmarks ..."
python3 initialize_benchmarks.py

echo "bm: CPython"
python3 benchmark_code.py

echo "bm: CPython + Cython"
python3 benchmark_code.py

echo "bm: PyPy"
python3 benchmark_code.py

echo "bm: PyPy + Cython"
python3 benchmark_code.py

echo "bm: Pyston"
python3 benchmark_code.py

echo "bm: nogil"
python3 benchmark_code.py

echo "bm: Cinder"
python3 benchmark_code.py

echo "bm: Codon"
python3 benchmark_code.py

echo "Gathering benchmarks ..."
python3 gather_benchmarks.py
