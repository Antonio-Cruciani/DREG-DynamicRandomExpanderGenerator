

# Dynamic Random (Expander) Graph Generator

 This is a function package for people interested in studying graphs that evolve over time. Anyone with a basic understanding of Python can create their own dynamic graph.






## Table of Contents 


- [General info](#General-info)
- [Description](#Description)
- [How to define and execute a model](#How-to-define-and-execute-a-model)
- [License](#License)


## General info
This python package is a dynamic random graphs generator. It allows defining bounded degree dynamic undirected networks i.e., evolving graphs in which each node has bounded degree.

### What is a Dynamic Random Graph?
A dynamic graph is a sequence of graphs <img src="https://bit.ly/35x8Ux6" align="center" border="0" alt="\mathcal{G} =\{G_t = (V_t, E_t) \,:\, t \in \mathbb{N}\}" width="219" height="18" />
where the sets of nodes and edges
can change at any discrete round. If they can change randomly we call the
corresponding random process a dynamic random graph.

### Why Dynamic Random Graphs?
Dynamic random graphs analysis allows us to define more accurate models that represent real phenomena.

## Description
In these models each node individually execute a distributed protocol in order to maintain a bounded number of connections.
It is possible to define " external events " that causes the edge or node disappearance at each time instant.


### P2P  
- **RAES** ( Request a link, then Accept if Enough Space ) proposed by Becchetti et al. 
( [More details](https://arxiv.org/abs/1811.10316) ) that allows you to define an Expander Graph in **O**(log n) rounds With High Probability.
- **Edge Dynamic (ERAES)** proposed by Antonio Cruciani and Francesco Pasquale that is a natural extension of RAES where there exists the probability **p** that, at each time step, each edge of the graph can fall. This is an infinite stochastic process that allow you to construct a good dynamic Expander Graph. 
- **Vertex Dynamic (VRAES)** proposed by Antonio Cruciani and Francesco Pasquale that is a Dynamic Random Graph where at each time step there are new vertices that join the network and vertices that leave it. This is an infinite stochastic process that allow you to construct a good dynamic Expander Graph.
- **Mixed Dynamic (EVRAES)**  proposed by Antonio Cruciani and Francesco Pasquale. This is a Dynamic Graph model in which nodes and edges appear and disappear. Nodes follow the same rules of VRAES and the edge disappearance phenomenon follows the ERAES scheme.

## How to define and execute a model
Given the **config.ini** file you can set up the the experiments for ERAES and VRAES. 

To simulate the EVRAES you can run ```python mixedDynamic.py```. Such simulation is multiprocessing and exploits all your cores. If you want to change the parameters you need to edit the ```mixedDynamic.py``` file.

### Defining ERAES/VRAES
Modify the **.ini** file under the section: **[model]**

* **graph** use **ED** to define an Edge Dyanamics or **VD** to define a Vertex Dynamic model

* **nodes** is the number of nodes of the dynamic random graph. Must be a list of nodes, if more than one integer is in such list the tool will simulate sequentially the model with all the nodes in such list.

* **degree** is the "target\min" degree that each node must have. Must be a list of integers, if more than one integer is in such list the tool will simulate sequentially the model with all the degrees in such list. 

* **tolerance** is the max degree that each node can have. Can be a list of integers or floats, if more than one value is in such list the tool will simulate sequentially the model with all the tolerances in such list.

* **edge_node_falling_probability** is the edge-disappearance probability at each round in case of the Edge Dynamics or the node-exiting probability in case of the Vertex Dynamics. Is a list of floats, must be between 0 and 1, if more than one value is in such list the tool will simulate sequentially the model with all the probabilities in such list.

* **nodes_poisson_rate** is the node-joining rate of the Poisson Process of the Vertex Dynamics. If it is equal to **None** the tool will use as rates the product of the number of nodes **n** and the exiting probabilities **q**. Is a list of floats, if more than one value is in such list the tool will simulate sequentially the model with all the probabilities in such list.

### Simulations parametes
Modify the **.ini** file under the section: **[simulations]**

* **flooding_protocol** If **True** the protocol will simulate the Flooding process.

* **simultaions_number**  Number of simulation that you want to perform for each fixed model. Must be an integer

* **only_spectral_properties** If **True** simulate the model saving only the Spectral Gaps at each round.

* **offline_simulation** If **True** saves as a file the adjacency list of the Dynamic Graph before and after the execution of the distributed protocol. **WARNING:** It performs a high amount of file writings on the disk.

### Other parameters
Modify the **.ini** file under the section: **[other_parameters]**

* **epsilon** Float value for the epsilon used by the convergence heuristic in the Edge Dynamic model. **NOTE:** the Edge Dynamic automatically estimate the epsilon value.

* **max_iterations** Int value for the maximum number of iteration of the models after their convergence (if you are not simulating the Offline version) or number of steps to perform (if you are simulating the Offline version).

### Output path
Modify the **.ini** file under the section: **[output_path]**

* **output_path** Output path of the simulations, for EVRAES is ./tmp

### Advanced parameters
Modify the **.ini** file under the section: **[advanced]**. Commands for simulating the model on a range of values, every command follows the pattern **< min_param , max_param, step_param >** where:
* **min_param** is the minimum value
* **max_param** is the maximum value 
* **step_param** is the constant increment from **min_param** to **max_param** 

For example, for:
  * min_nodes = 10
  * max_nodes = 100
  * step_nodes = 20

the tool will simulate the model with the following number of nodes:  [10,30,50,70,90]
    
### Running the model
For executing the model use the command:

                                Python main.py

## Reproducing the experiments in the paper
In order to reproduce the experiments in the paper substitute the **config.ini** file with the ones in the appropriate folders **configurations/EdgeDynamics** or  **configurations/VertexDynamics**.
* **Spectral properties** : model_spectral_conf.ini
  
* **Flooding simulation** : model_flooding_simulation.ini

## License
This is free software, if you want to use it please cite this work.
Users interested in improving and expanding the project are welcome.

Thanks to [Professor Francesco Pasquale](http://www.mat.uniroma2.it/~pasquale/) for supervising this work.
