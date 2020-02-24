<img src="https://github.com/Antonio-Cruciani/dynamic-random-graph-generator/blob/master/img/Dynamic.png?v=3&s=200" title="Dynamic Random Graph" alt="DynamicRG" height=256 width=386>


# Dynamic Random Graph Generator

 This is a function package for people interested in studying graphs that evolves over time. Anyone with a basic understanding of Python can create their own dynamic graph.






## Table of Contents 



- [Installation](#installation)
- [Description](#Description)
- [RAES Random Graph](#RAES)
- [Edge Dynamic Random Graph](#Edge-Dynamic)
- [Vertex Dynamic Random Graph](#Vertex-Dynamic)
- [Distributed Protocols](#Distributed-Protocols)
- [Heuristic Convergence ](#Heuristic-Convergence)
- [License](#license)




## Description
This package allows you to create random dynamic graphs where each node at each time step chooses one or more neighbors uniformly at random (u.a.r.). We propose you three different dynamic random graphs:
- **RAES** ( Request a link, then Accept if Enough Space ) proposed by Becchetti et al. 
( https://arxiv.org/abs/1811.10316 ) that allow you to construct an Expander Graph in **O**(log n) rounds With High Probability.
- **Edge Dynamic** proposed by Antonio Cruciani that is a natural extension of RAES where there exists the probability **p** that, at each time step, an edge of the graph can fall. This is an infinite stochastic process that allow you to construct a good dynamic Expander Graph. 
- **Vertx Dynamic** proposed by Antonio Cruciani that is a Dynamic Random Graph where at each time step there are new vertices that join the network and vertices that leave it. This is an infinite stochastic process that allow you to construct a good dynamic Expander Graph.


## RAES
Dynamic Random Graph G(n,d,c) where:

-	 **n** is the number of vertices 
-  **d** is the minimum required degree in the graph
-  **c** is the tolerance (c*d = Max Degree in the graph)


RAES evolves over time with the following rules:

<img src="https://github.com/Antonio-Cruciani/dynamic-random-graph-generator/blob/master/img/RAES.png?v=3&s=200" title="RAES" alt="RAESRG" height=356 width=786>

```python 
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
 
<img src="https://github.com/Antonio-Cruciani/dynamic-random-graph-generator/blob/master/img/RAES.gif?v=3&s=200" title="RAES" alt="RAESRG" height=256 width=486>


## Edge-Dynamic
Dynamic Random Graph G(n,d,c,p) where:

-	 **n** is the number of vertices 
-  **d** is the minimum required degree in the graph
-  **c** is the tolerance (c*d = Max Degree in the graph)
-  **p** is the falling proability of edges

Edge Dynamic evolves over time with the following rules:

<img src="https://github.com/Antonio-Cruciani/dynamic-random-graph-generator/blob/master/img/EdgeDynamic.png?v=3&s=200" title="RAES" alt="RAESRG" height=356 width=786>

```python 
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

<img src="https://github.com/Antonio-Cruciani/dynamic-random-graph-generator/blob/master/img/EdgeDynamic.gif?v=3&s=200" title="RAES" alt="RAESRG" height=256 width=486>


## Vertex-Dynamic
Dynamic Random Graph G(lambda,q,d,c) where:

-	 **lambda** is the intensity parameter of the Poisson Process
-  **q** is the exit proability of Vertices
-  **d** is the minimum required degree in the graph
-  **c** is the tolerance (c*d = Max Degree in the graph)

Vertex Dynamic evolves over time with the following rules:
<img src="https://github.com/Antonio-Cruciani/dynamic-random-graph-generator/blob/master/img/FullyDyn.png?v=3&s=200" title="Fdyn" alt="Fdyn" height=356 width=786>

```python 
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

<img src="https://github.com/Antonio-Cruciani/dynamic-random-graph-generator/blob/master/img/VertexDynamic.gif?v=3&s=200" title="Vdyn" alt="Vdyn" height=256 width=486>

## Distributed-Protocols
It is possible to simulate the Flooding Procol on the Dynamic Graph. You just have to instantiate the Flooding object of the DynamicGraph:
```python 
Graph.set_flooding()
```
After this step you can choose the initiator u.a.r.:
```python 
Graph.flooding.set_initiator()
```
And for the update step you have to use:
```python 
Graph.flooding.update_flooding(Graph)
```        
            
