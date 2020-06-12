<img src="https://github.com/Antonio-Cruciani/dynamic-random-graph-generator/blob/master/img/Dynamic.png?v=3&s=200" title="Dynamic Random Graph" alt="DynamicRG" height=256 width=386>


# Dynamic Random Graph Generator

 This is a function package for people interested in studying graphs that evolves over time. Anyone with a basic understanding of Python can create their own dynamic graph.






## Table of Contents 



- [Description](#Description)
- [RAES Random Graph](#RAES)
- [Edge Dynamic Random Graph](#Edge-Dynamic)
- [Vertex Dynamic Random Graph](#Vertex-Dynamic)
- [Edge Markovian Random Graph](#Edge-Markovian)
- [Distributed Protocols](#Distributed-Protocols)
- [Heuristic Convergence ](#Heuristic-Convergence)
- [License](#License)




## Description
This package allows you to create random dynamic graphs inspired by P2P networks where each node at each time step chooses one or more neighbors uniformly at random (u.a.r.) and inspired by Radio Networks where each edge is a Birth-Death Markov Chain. We propose you four different dynamic random graphs:

### P2P  
- **RAES** ( Request a link, then Accept if Enough Space ) proposed by Becchetti et al. 
( https://arxiv.org/abs/1811.10316 ) that allow you to construct an Expander Graph in **O**(log n) rounds With High Probability.
- **Edge Dynamic** proposed by Antonio Cruciani ([Contribution guidelines for this project](./Thesis/AntonioCruciani_Master's_Degree_Thesis(ITA).pdf)) that is a natural extension of RAES where there exists the probability **p** that, at each time step, each edge of the graph can fall. This is an infinite stochastic process that allow you to construct a good dynamic Expander Graph. 
- **Vertex Dynamic** proposed by Antonio Cruciani that is a Dynamic Random Graph where at each time step there are new vertices that join the network and vertices that leave it. This is an infinite stochastic process that allow you to construct a good dynamic Expander Graph.
### Radio Networks 
- **Edge Markovian** You can read about it in https://dl.acm.org/doi/pdf/10.1145/1400751.1400781 in this model you have a fixed number of nodes and each edge is a Birth-Death Markov Chain.
## RAES
Dynamic Random Graph G(n,d,c) where:

-	 **n** is the number of vertices 
-  **d** is the minimum required degree in the graph
-  **c** is the tolerance (c*d = Max Degree in the graph)


RAES evolves over time with the following rules:

<img src="https://github.com/Antonio-Cruciani/dynamic-random-graph-generator/blob/master/img/RAES.png?v=3&s=200" title="RAES" alt="RAESRG" height=356 width=786>

```python 
from src.Graphs.Objects.MultipleEdge import DynamicGraph
# Initializing parameters
n = 30
d = 3 
c = 1.5 
p = 0
lamb = 1
beta = 0.01
G = DynamicGraph(n,d,c,lamb,beta,p,"Multiple")
# is regular return False if all vertices has d <= degree <= c*d, else return True
while(G.isregular()):
    # Phase 1
    G.add_phase()
    # Phase 2
    G.del_phase()  
```
Demo of the example,
       
- **blue nodes** : d <= degree <= c*d  
- **red nodes** :  degree < d or degree > c*d 
 <p align="center">
<img src="https://github.com/Antonio-Cruciani/dynamic-random-graph-generator/blob/master/img/RAES.gif?v=3&s=200" title="RAES" alt="RAESRG" height=256 width=486>
</p>

## Edge-Dynamic
Dynamic Random Graph G(n,d,c,p) where:

-	 **n** is the number of vertices 
-  **d** is the minimum required degree in the graph
-  **c** is the tolerance (c*d = Max Degree in the graph)
-  **p** is the falling proability of edges

Edge Dynamic evolves over time with the following rules:

<img src="https://github.com/Antonio-Cruciani/dynamic-random-graph-generator/blob/master/img/EdgeDynamic.png?v=3&s=200" title="RAES" alt="RAESRG" height=356 width=786>

```python 
from src.Graphs.Objects.MultipleEdge import DynamicGraph
# Initializing parameters
n = 30
d = 3 
c = 1.5 
p = 0.1
lamb = 1
beta = 0.01
G = DynamicGraph(n,d,c,lamb,beta,p,"Multiple")
t = 0
while(t<500):
    # Phase 1
    G.add_phase()
    # Phase 2
    G.del_phase() 
    # Phase 3
    G.random_fall()
    t+=1
```
Demo of the example,
       
- **blue nodes** : d <= degree <= c*d  
- **red nodes** :  degree < d or degree > c*d 
<p align="center">
<img src="https://github.com/Antonio-Cruciani/dynamic-random-graph-generator/blob/master/img/EdgeDynamic.gif?v=3&s=200" title="RAES" alt="RAESRG" height=256 width=486>
</p>

## Vertex-Dynamic
Dynamic Random Graph G(lambda,q,d,c) where:

-	 **lambda** is the intensity parameter of the Poisson Process
-  **q** is the exit proability of Vertices
-  **d** is the minimum required degree in the graph
-  **c** is the tolerance (c*d = Max Degree in the graph)

Vertex Dynamic evolves over time with the following rules:
<img src="https://github.com/Antonio-Cruciani/dynamic-random-graph-generator/blob/master/img/FullyDyn.png?v=3&s=200" title="Fdyn" alt="Fdyn" height=356 width=786>

```python 
from src.Graphs.Objects.MultipleEdge import DynamicGraph
# Initializing parameters
n = 0
d = 3 
c = 1.5 
p = 0
lamb = 1
beta = 0.01
G = DynamicGraph(n,d,c,lamb,beta,p,"Multiple")
t = 0
while(t<500):
    # Phase 1
    G.connect_to_network()
    # Phase 2
    G.add_phase()
    # Phase 3
    G.del_phase() 
    # Phase 4
    G.disconnect_from_network()
    t+=1
```
Demo of the example,
       
- **blue nodes** : d <= degree <= c*d  
- **red nodes** :  degree < d or degree > c*d 
<p align="center">
<img src="https://github.com/Antonio-Cruciani/dynamic-random-graph-generator/blob/master/img/VertexDynamic.gif?v=3&s=200" title="Vdyn" alt="Vdyn" height=256 width=486>
</p>

## Edge-Markovian
Dynamic Random Graph G(n,p,q,E0) where:

-	**n** is the number of vertices 
-  **p** is the birth-rate of the edges
-  **q** is the death-rate of the edges
-  **E0** is the set of the edges at time 0
 
The Edge Markovian Random Graph evolves over time with the following rule:

```python 
from src.Graphs.Objects.MultipleEdge import DynamicGraph
# Initializing parameters
n = 32
p = 0.5
q = 0.5
G = DynamicGraph(n,model = "EdgeMarkovian",starting_edge_list = [],edge_birth_rate = p,edge_death_rate= q)
t = 0
while(t<500): 
    G.edge_markovian()
    t+=1
```

Demo of the example,

<p align="center">
<img src="https://github.com/Antonio-Cruciani/dynamic-random-graph-generator/blob/master/img/EMG0505.gif?v=3&s=200" title="Vdyn" alt="Vdyn" height=256 width=486>
</p>



## Distributed-Protocols
It is possible to simulate the Flooding Procol on the Dynamic Graph. You just have to instantiate the Flooding object of the DynamicGraph:

```python 
G.set_flooding()
```
After this step you can choose the initiator u.a.r.:

```python 
G.flooding.set_initiator()
```
And for the update step you have to use:

```python 
G.flooding.update_flooding(G)
```  
Demo of the flooding on the Edge Dynamic,
       
- **black nodes** : Not informed  
- **yellow nodes** :  Informed 
<p align="center">
<img src="https://github.com/Antonio-Cruciani/dynamic-random-graph-generator/blob/master/img/floodEdjedyn.gif?v=3&s=200" title="flood" alt="flood" height=256 width=486>
</p>  
      
## Heuristic-Convergence
We propose an Heuristic to determine if the Edge Dynamic has converged.
Given the adjacency matrix **A** of the graph at a generic time step we define:   
<p align="center">
<img src="https://github.com/Antonio-Cruciani/dynamic-random-graph-generator/blob/master/img/TransitionMatrix.png?v=3&s=200" title="Tmatrix" alt="Tmat" height=27 width=50>
 </p>
 
Where **D** is the diagonal **degree matrix** of the graph. Given the spectrum of **P** (ordered in descending order) we define the **spectral gap** as the difference between the first and the second eigenvalues of **P**. We know that if the spectral gap of the transition matrix **P** is small (near to 0) we have that the graph is not a good Expander Graph. Thanks to this measure we can understand a key property of the graph at each time step and we can define a convergence criterion as follows: 
```if the spectral gap differs only by an epsilon for log n rounds we have that the graph is converged to a stationary configuration.```

To check this property we can define a queue (FIFO) of lenght log n and check if the last log n spectral gaps differs for an epsilon factor.

<p align="center">
<img src="https://github.com/Antonio-Cruciani/dynamic-random-graph-generator/blob/master/img/queue.png?v=3&s=200" title="queue" alt="queuem" height=256 width=486>
 </p>
 
```python 
from src.Graphs.Objects.MultipleEdge import DynamicGraph
from src.Graphs.Objects.Queue import Queue
from src.StastModules.SpectralAnalysis import get_spectral_gap_transition_matrix
# Initializing parameters
n = 64
d = 3 
c = 1.5 
p = 0.1
lamb = 1
beta = 0.01
epsilon = 0.05
spectral_queue = Queue(mt.log(n,2))
G = DynamicGraph(n,d,c,lamb,beta,p,"Multiple")
# G.get_converged() return True if the graph is converged, else return False
while(not(G.get_converged()):
    # Phase 1
    G.add_phase()
    # Phase 2
    G.del_phase() 
    # Phase 3
    G.random_fall()
    Isinvertible, spectralGap, lambdaNGap = get_spectral_gap_transition_matrix(G.get_G())
    spectral_queue.add_element_to_queue(spectralGap)
    if (spectral_queue.get_queue_lenght() == spectral_queue.get_max_lenght() and spectral_queue.get_converged() == False):
            spectral_differences = []
            s_q = spectral_queue.get_queue()
            for i in range(0, spectral_queue.get_queue_lenght() - 1):
                spectral_differences.append(abs(s_q[i] - s_q[i + 1]))
            terminate = True
            for j in spectral_differences:
                if (j > epsilon):
                    terminate = False
            if(terminate):
                spectral_queue.set_converged(terminate)
                G.set_converged(True)
```  
Demo of the heuristic on the Edge Dynamic,
       
- **black nodes** : Not Converged
- **yellow nodes** :  Converged 
<p align="center">
<img src="https://github.com/Antonio-Cruciani/dynamic-random-graph-generator/blob/master/img/spectralconv.gif?v=3&s=200" title="convercence" alt="convergence" height=256 width=486>
 </p>

## License
This is free software, if you want to use it please cite this work.
Users interested in improving and expanding the project are welcome.

Thanks to [Professor Francesco Pasquale](http://www.mat.uniroma2.it/~pasquale/) for supervising this work.
