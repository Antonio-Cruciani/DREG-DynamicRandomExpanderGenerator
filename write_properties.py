import configparser
config = configparser.ConfigParser()
config['model'] ={
	"graph" : "ED",
	"nodes" :  [64,128,256,512,1024,2048,4096,8192,16384,32768],
	"degree" : [2,3,4],
	"tolerance" : [1.5,2,3],
	"edge_node_falling_probability" : [0.9,0.8,0.7,0.6,0.5,0.4,0.3,0.2,0.1,0.06,0.05,0.02,0.005,0.002,9e-05,9e-06,1e-07,0.0],
	"nodes_poisson_rate" : "None",
}

config['simultations'] = {
	"flooding_protocol" :  "True",
	"simultaions_number": 30,
	"only_spectral_properties": "False",
	"offline_simulation" : "False",
}
config['other_parameters'] = {
	"gpu_optimization" : "False",
	"epsilon" : 0.005,
	"max_iterations" : 100,
}

config['output_path']= {
	"outputPath" : "./Outputs/EdgeDynamics",

}

config['advanced'] = {
	"min_nodes" : "None",
	"max_nodes" : "None",
	"step_nodes" : "None",

	"min_degree" : "None",
	"max_degree" : "None",
	"step_degree" : "None",

	"min_tolerance" : "None",
	"max_tolerance" : "None",
	"step_tolerance" : "None",

	"min_edge_node_falling_probability" : "None",
	"max_edge_node_falling_probability" : "None",
	"step_edge_node_falling_probability" : "None",

	"min_nodes_poisson_rate" : "None",
	"max_nodes_poisson_rate" : "None",
	"step_nodes_poisson_rate" : "None",
}
fp = open(r'config.ini','w')
config.write(open(r'config.ini','w'))
#with open(r'config.ini','w') as configfile:
#	config.write(config)
