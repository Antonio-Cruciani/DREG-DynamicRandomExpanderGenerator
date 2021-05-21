#!/usr/bin/python
from src.Algorithms.VertexDynamic import VertexDynamic
from src.Algorithms.EdgeDynamic import EdgeDynamic
import sys, getopt
import logging
logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)

d = 4
c = 3
#1e-07,9e-06,9e-05,0.002,0.005,0.02,0.05,
out = [0.9,0.8,0.7,0.6,0.5,0.4,0.3,0.1,0.05,0.02,0.005,0.002]
fixedN = [64,128,256,512,1024,2048,4096,8192]
inputs = []
outPath = '/media/antoniocruciani/SSD ASENNO/AltriVD'
for n in fixedN:
    for x in out:
        inputs.append([n * x,x])
for elem in inputs:

    ex = VertexDynamic([d], [c], [elem[0]], [elem[1]], outPath, flooding=False, regular_decay=0.5, model="Multiple", simNumber=10)
    ex.run()