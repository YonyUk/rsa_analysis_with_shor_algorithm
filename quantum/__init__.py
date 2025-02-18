'''
quantum

a set of quantum implementations

WARNING!!!:
    the dictionarys defined here as used for accelerate the building process for the circuit reusing
    computations mades before, DON'T MODIFY ITS!!!.
'''

from .runners import eval_circuit,get_results
from .components import *
from qiskit.visualization import plot_histogram