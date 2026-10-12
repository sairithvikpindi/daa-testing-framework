import streamlit as st, pandas as pd, matplotlib.pyplot as plt, random, math, time, tracemalloc
from algorithms.mst import prim_mst, kruskal_mst
from algorithms.knapsack import fractional_knapsack, zero_one_knapsack
from algorithms.dynamic_programming import floyd_warshall, matrix_chain_multiplication
from algorithms.backtracking import n_queens, hamiltonian_cycle, tsp_branch_bound
from algorithms.advanced_structures import run_structure_test
from algorithms.complexity import classification_table
from testing.generators import generate_graph, generate_items

st.set_page_config(page_title="DAA Stress Lab", page_icon="🧪", layout="wide")
st.title("DAA Algorithm Vulnerability & Stress-Testing Framework")
st.caption("Test input families, measure runtime and traced memory, and interpret observed risk alongside theoretical complexity.")
seed=st.sidebar.number_input("Random seed",0,999999,42)
trials=st.sidebar.slider("Benchmark repetitions",1,5,3)
category=st.sidebar.selectbox("Assignment category",["Advanced Data Structures","MST Algorithms","Knapsack","Dynamic Programming","Backtracking / Branch & Bound","Complexity Classification"])

def measure(name, fn, args, n, family, complexity):
    times=[];mem=[];result=None
    for _ in range(trials):
        tracemalloc.start();start=time.perf_counter()
        result=fn(*args);times.append(time.perf_counter()-start)
        _,peak=tracemalloc.get_traced_memory();tracemalloc.stop();mem.append(peak/1024)
    avg=sum(times)/len(times);peak=max(mem)
    risk="High" if avg>3 or peak>262144 else "Moderate" if avg>.5 or peak>65536 else "Low"
    return {"Algorithm":name,"Input size":n,"Input family":family,"Average time (s)":round(avg,6),"Peak traced memory (KiB)":round(peak,2),"Operations/states":getattr(fn,"last_operations",getattr(fn,"last_states",0)),"Theoretical complexity":complexity,"Risk":risk,"Result":str(result)[:180]}

if category=="MST Algorithms":
    n=st.slider("Vertices",10,250,50,10);density=st.selectbox("Graph",["sparse","medium","dense"])
    if st.button("Run tests",type="primary"):
        g=generate_graph(n,density,int(seed));rows=[measure("Prim",prim_mst,(g,),n,density,"O((V+E) log V)"),measure("Kruskal",kruskal_mst,(g,),n,density,"O(E log E)")]
        a,b=prim_mst(g),kruskal_mst(g);st.success("Correctness check passed" if a[0]==b[0] else "MST weights differ")
        rows[0]["MST weight"]=a[0];rows[1]["MST weight"]=b[0];st.session_state["results"]=rows
elif category=="Knapsack":
    n=st.slider("Items",5,35,15,5);cap=st.slider("Capacity",10,300,60,10)
    if st.button("Run tests",type="primary"):
        data=generate_items(n,int(seed));rows=[measure("Fractional Knapsack",fractional_knapsack,(data,cap),n,f"capacity={cap}","O(n log n)"),measure("0/1 Knapsack DP",zero_one_knapsack,(data,cap),n,f"capacity={cap}","O(nW) time, O(W) space")]
        rows[0]["Objective value"]=fractional_knapsack(data,cap)[0];rows[1]["Objective value"]=zero_one_knapsack(data,cap)[0];st.session_state["results"]=rows
        st.info("Fractional permits partial items; 0/1 requires whole items.")
elif category=="Dynamic Programming":
    choice=st.radio("Algorithm",["Floyd–Warshall","Matrix Chain Multiplication"],horizontal=True)
    if choice=="Floyd–Warshall":
        n=st.slider("Vertices",5,100,25,5)
        if st.button("Run test",type="primary"):
            r=random.Random(int(seed));g=[[0 if i==j else (r.randint(1,30) if r.random()<.35 else math.inf) for j in range(n)] for i in range(n)]
            st.session_state["results"]=[measure(choice,floyd_warshall,(g,),n,"weighted directed graph","O(V³) time, O(V²) space")]
    else:
        n=st.slider("Matrices",3,40,12)
        if st.button("Run test",type="primary"):
            r=random.Random(int(seed));dims=[r.randint(5,80) for _ in range(n+1)]
            row=measure(choice,matrix_chain_multiplication,(dims,),n,"random dimensions","O(n³) time, O(n²) space")
            row["Minimum scalar multiplications"]=matrix_chain_multiplication(dims)[0];st.session_state["results"]=[row]
elif category=="Backtracking / Branch & Bound":
    choice=st.radio("Problem",["N-Queen","Hamiltonian Cycle","TSP Branch & Bound"],horizontal=True);n=st.slider("Board/graph size",4,11,8)
    if st.button("Run test",type="primary"):
        if choice=="N-Queen":fn,args,comp=n_queens,(n,),"Exponential worst case"
        elif choice=="Hamiltonian Cycle":
            g=generate_graph(n,"sparse",int(seed));adj=[[False]*n for _ in range(n)]
            for u,ns in enumerate(g):
                for v,w in ns:adj[u][v]=True
            fn,args,comp=hamiltonian_cycle,(adj,),"O(V!) worst case"
        else:
            r=random.Random(int(seed));cost=[[0 if i==j else r.randint(1,100) for j in range(n)] for i in range(n)]
            fn,args,comp=tsp_branch_bound,(cost,),"O(n!) worst case; pruning is instance-dependent"
        row=measure(choice,fn,args,n,"generated instance",comp);row["States generated"]=getattr(fn,"last_states",0);row["States pruned"]=getattr(fn,"last_pruned",0);st.session_state["results"]=[row]
elif category=="Advanced Data Structures":
    st.warning("Four structures are included: Binomial Heap, Fibonacci Heap, B-Tree and Red-Black Tree. Operations shown are insert/extract or insert/search, depending on structure.")
    kind=st.selectbox("Structure",["Binomial Heap","Fibonacci Heap","B-Tree","Red-Black Tree"]);n=st.slider("Keys",20,1000,200,20);pattern=st.selectbox("Input family",["random","ascending","descending","duplicates"])
    if st.button("Run test",type="primary"):st.session_state["results"]=[run_structure_test(kind,n,pattern,int(seed))]
else:
    st.subheader("Complexity classification")
    st.dataframe(pd.DataFrame(classification_table()),use_container_width=True,hide_index=True)
    st.markdown("**Decision** asks yes/no; **optimization** seeks the best feasible answer. **NP-complete** problems are both in NP and NP-hard. **NP-hard** problems are at least as hard as every problem in NP under the relevant reductions.")
if st.session_state.get("results"):
    df=pd.DataFrame(st.session_state["results"]);st.subheader("Latest results");st.dataframe(df,use_container_width=True,hide_index=True)
    st.download_button("Download CSV",df.to_csv(index=False).encode(),"daa_results.csv","text/csv")
    if "Average time (s)" in df:
        for col,label in [("Average time (s)","Runtime"),("Peak traced memory (KiB)","Peak traced memory")]:
            fig,ax=plt.subplots();ax.bar(df.iloc[:,0],df[col]);ax.set_ylabel(label);ax.tick_params(axis="x",rotation=20);st.pyplot(fig);plt.close(fig)
st.caption("Risk thresholds are prototype heuristics. tracemalloc measures traced Python allocations, not total OS memory.")
