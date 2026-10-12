DAA Algorithm Vulnerability & Stress-Testing Framework

INSTALL / RUN (VS Code on Windows)
1. Extract this ZIP.
2. VS Code > File > Open Folder > select the extracted DAA_Stress_Testing_Framework_Package folder.
3. Terminal > New Terminal.
4. Run: python -m pip install -r requirements.txt
5. Run: python -m streamlit run app.py

The dashboard has all six assignment categories:
1. Advanced data structures
2. Prim and Kruskal MST
3. Fractional and 0/1 Knapsack
4. Floyd-Warshall and Matrix Chain Multiplication
5. N-Queen, Hamiltonian Cycle and TSP Branch & Bound
6. Decision/optimization and NP-hard/NP-complete classification

Notes: risk thresholds are heuristics, not universal guarantees. tracemalloc is traced Python memory, not total OS memory. The Fibonacci Heap option currently uses a heapq-backed baseline, not the textbook Fibonacci Heap; implement a full Fibonacci Heap before claiming that requirement is fully met. Validate outputs and discuss theoretical complexity in your report.
