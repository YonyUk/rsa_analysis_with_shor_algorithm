'''
runners

basic backend for run quantum circuit
'''

from qiskit_aer import Aer
from qiskit import transpile
from tools import printtiming

@printtiming
def eval_circuit(circuit,shots=1000,backend=Aer.get_backend('qasm_simulator')):
    qc_t = transpile(circuit,backend)
    return backend.run(qc_t,shots=shots).result().get_counts()

@printtiming
def get_results(**results):
    return [(key,int(key,2),f'{results[key]} times') for key in results.keys()]

@printtiming
def normalize(circuit,backend=Aer.get_backend('qasm_simulator')):
    return transpile(circuit,backend)