'''
components

a set of quantum components

WARNING!!!:
    the dictionarys defined here as used for accelerate the building process for the circuit reusing
    computations mades before, DON'T MODIFY ITS!!!.
'''

from qiskit import QuantumCircuit
from tools import modular_inverse,modular_square_exponentiation
from quantum.runners import normalize
from datetime import datetime
import numpy as np

# this dictionarys is for reduce the time of all future computations
global adders
global modular_adders
global modular_multipliers
global reductors
global controlled_adders
global controlled_modular_adders

adders = {}
reductors = {}
modular_adders = {}
modular_multipliers = {}
controlled_adders = {}
controlled_modular_adders = {}

def constant_adder(a:int,qubits:int,as_gate:bool=False):
    '''
    return a circuit to compute the sum x + a
    
    a: constant for the operation
    qubits: number of qubits for the circuit
    '''
    global adders

    if (a,qubits,as_gate) in adders.keys():
        return adders[(a,qubits,as_gate)]
    
    if as_gate and (a,qubits,False) in adders.keys():
        gate = adders[(a,qubits,False)].to_gate()
        gate.name = f'add {a}'
        adders[(a,qubits,as_gate)] = gate
        return gate

    if qubits < a.bit_length():
        raise ValueError(f'{qubits} ar too small for represent {a}')

    # gets the binary representation of a
    a_repr = [int(b,2) for b in bin(a)[2:].zfill(qubits)]
    # revert the binary representation of a
    a_repr.reverse()
    qc = QuantumCircuit(qubits)
    # dictionary to store the total of shift's phase to apply by qubit
    radians_by_qubit = {i:0 for i in range(qubits)}
    # compute the total of shift's phase to apply by qubit
    for i in range(len(a_repr)):
        if a_repr[i] == 1:
            for j in range(i,qubits):
                radians_by_qubit[j] += np.pi / (1 << (j - i))
                pass
            pass
        pass
    # apply the QFT
    for i in range(qubits - 1,-1,-1):
        qc.h(i)
        for j in range(i - 1,-1,-1):
            qc.cp(np.pi / (1 << (i - j)),j,i)
            pass
        # apply the shift phase
        if radians_by_qubit[i] != 0:
            qc.p(radians_by_qubit[i],i)
            pass
        pass
    # apply the IQFT
    for i in range(qubits):
        qc.h(i)
        for j in range(i + 1,qubits):
            qc.cp(-1 * np.pi / (1 << (j - i)),i,j)
            pass
        pass
    if as_gate:
        gate = qc.to_gate()
        gate.name = f'add {a}'
        adders[(a,qubits,as_gate)] = gate
        return gate
    adders[(a,qubits,as_gate)] = qc
    qc.name = f'add {a}'
    return qc

def controlled_constant_adder(a:int,qubits:int):
    '''
    the controlled version for the constant adder

    NOTE:
        the first qubit is the control-qubit
    '''
    global controlled_adders

    if (a,qubits) in controlled_adders.keys():
        return controlled_adders[(a,qubits)]
    # gets the binary representation of a
    a_repr = [int(b,2) for b in bin(a)[2:].zfill(qubits)]
    # revert the binary representation of a
    a_repr.reverse()
    qc = QuantumCircuit(qubits + 1)
    # dictionary to store the total of shift's phase to apply by qubit
    radians_by_qubit = {i:0 for i in range(qubits)}
    # compute the total of shift's phase to apply by qubit
    for i in range(len(a_repr)):
        if a_repr[i] == 1:
            for j in range(i,qubits):
                radians_by_qubit[j] += np.pi / (1 << (j - i))
                pass
            pass
        pass
    # apply the QFT
    for i in range(qubits - 1,-1,-1):
        qc.h(i + 1)
        for j in range(i - 1,-1,-1):
            qc.cp(np.pi / (1 << (i - j)),j + 1,i + 1)
            pass
        # apply the shift phase
        if radians_by_qubit[i] != 0:
            qc.cp(radians_by_qubit[i],0,i + 1)
            pass
        pass
    # apply the IQFT
    for i in range(qubits):
        qc.h(i + 1)
        for j in range(i + 1,qubits):
            qc.cp(-1 * np.pi / (1 << (j - i)),i + 1,j + 1)
            pass
        pass
    qc.name = f'c_add {a}'
    controlled_adders[(a,qubits)] = qc
    return qc

def constant_reductor(a:int,qubits:int,as_gate:bool=False):
    '''
    return a circuit to compute x - a

    a: constant to the operation
    qubits: number of qubits for the circuit

    this circuit can be used as a comparator, the result of comparision will be at the most significant qubit
    '''
    global reductors

    if (a,qubits,as_gate) in reductors.keys():
        return reductors[(a,qubits,as_gate)]
    
    if as_gate and (a,qubits,False) in reductors.keys():
        gate = reductors[(a,qubits,False)].to_gate()
        gate.name = f'sub {a}'
        reductors[(a,qubits,as_gate)] = gate
        return gate

    reductor = constant_adder(a,qubits + 1).inverse()
    if as_gate:
        result = reductor.to_gate()
        result.name = f'sub {a}'
        reductors[(a,qubits,as_gate)] = result
        return result
    reductors[(a,qubits,as_gate)] = reductor
    reductor.name = f'sub {a}'
    return reductor

def constant_modular_adder(a:int,N:int,as_gate:bool=False):
    '''
    return a circuit to compute x + a mod N

    a: constant
    qubits: number of qubits for this circuit

    NOTE: the circuit assumes that a is less than N, if not the case, them a % N is taken instead
    '''
    global modular_adders

    if (a,N,as_gate) in modular_adders.keys():
        return modular_adders[(a,N,as_gate)]
    
    if as_gate and (a,N,False) in modular_adders.keys():
        gate = modular_adders[(a,N,False)].to_gate()
        gate.name = f'add {a} mod {N}'
        modular_adders[(a,N,as_gate)] = gate
        return gate

    if a >= N:
        a %= N
        pass

    # compute the necessary qubits abd create the circuit
    qubits = N.bit_length()
    qc = QuantumCircuit(qubits + 2)
    # create the adder by a and the controlled version of the adder by N
    adder = constant_adder(a,qubits + 1,True)
    c_adder = constant_adder(N,qubits + 1,True).control(1)
    # create the reductor by N and by a
    reductor = constant_reductor(N,qubits,True)
    a_reductor = constant_reductor(a,qubits,True)
    # add the adder by a and the reductor by N
    qc.append(adder,range(qubits + 1))
    qc.append(reductor,range(qubits + 1))
    # control the last qubit to know if a + x < N
    qc.cx(qubits,qubits + 1)
    # add the controlled adder by N so if a + x < N, we add it again
    qc.append(c_adder,[qubits + 1] + list(range(qubits + 1)))
    # add the reductor by a to know if we have to restore the ancilla qubit
    qc.append(a_reductor,range(qubits + 1))
    # circuit to restore the last qubit if it's needed
    qc.x(qubits)
    qc.cx(qubits,qubits + 1)
    qc.x(qubits)
    # restore the result to the previously value to the reduction
    qc.append(adder,range(qubits + 1))

    if as_gate:
        result = qc.to_gate()
        result.name = f'add {a} mod {N}'
        modular_adders[(a,N,as_gate)] = result
        return result
    modular_adders[(a,N,as_gate)] = qc
    return qc

def constant_comparator(a:int,qubits:int,as_gate:bool=False,**kwargs):
    '''
    return the circuit to compute comparision bettwen a and x

    if keyword argument geq is passed as True, the operation is >=, else the operation is <

    a: constant
    qubits: number of qubits for the circuit
    '''
    
    qc = QuantumCircuit(qubits + 2)
    reductor = constant_reductor(a,qubits,True)
    adder = constant_adder(a,qubits + 1,True)

    qc.append(reductor,range(qubits + 1))
    qc.cx(qubits,qubits + 1)
    qc.append(adder,range(qubits + 1))

    operation = '<'

    if 'geq' in kwargs.keys() and kwargs['geq']:
        qc.x(qubits + 1)
        operation = '>='
        pass

    if as_gate:
        result = qc.to_gate()
        result.name = f'cmp {operation} {a}'
        return result
    
    return result

def modular(N:int,qubits:int):
    '''
    return the circuit that compute x mod N

    N: constant module
    qubits: number of qubits for the circuit
    '''
    n = N.bit_length()

    if qubits < n:
        raise ValueError(f'more than {qubits} qubits it\'s necessary to represent {N}')
    
    qc = QuantumCircuit(qubits + 2)
    n_reductor = constant_reductor(N,n,True)
    c_n_adder = constant_adder(N,n + 1,True).control(1)
    n_1_reductor = constant_reductor(N,n + 1,True)
    c_n_1_adder = constant_adder(N,n + 2,True).control(1)
    op_times = qubits - n + 1

    for i in range(op_times):
        if i == 0:
            input_qubits = list(range(qubits - n - i,qubits - i))
            qc.append(n_reductor,input_qubits + [qubits])
            qc.cx(qubits,qubits + 1)
            qc.append(c_n_adder,[qubits + 1] + input_qubits + [qubits])
            qc.reset(qubits + 1)
            pass
        else:
            input_qubits = list(range(qubits - n - i,qubits - i + 1))
            qc.append(n_1_reductor,input_qubits + [qubits + 1 - i])
            qc.cx(qubits + 1 - i,qubits + 1)
            qc.append(c_n_1_adder,[qubits + 1] + input_qubits + [qubits + 1 - i])
            qc.reset(qubits + 1)
            pass
        pass

    return qc

def constant_modular_multiplier(a:int,N:int,qubits:int):
    '''
    return the circuit to compute a*x mod N

    a: the constant
    N: the constant module
    qubits: maximun number of qubits for the input

    NOTE:
        This component includes a control-qubit at 0-position for accelerate the building
        of the f(x) = a^x mod N circuit. If the control-qubit is activate, them this circuit
        performs the operation a*x mod N, else does nothing
    '''
    global modular_multipliers

    if (a,N,qubits) in modular_multipliers.keys():
        return modular_multipliers[(a,N,qubits)]

    num_qubits = N.bit_length()

    qc = QuantumCircuit(num_qubits + qubits + 3)
    for i in range(1,qubits + 1):
        adder = constant_modular_adder((a*1<<(i - 1)) % N,N).control(2)
        adder.name = f'add {a*1<<(i - 1)} mod N'
        qc.append(adder,[0,i] + list(range(qubits + 1,qubits + num_qubits + 3)))
        pass

    modular_multipliers[(a,N,qubits)] = qc
    qc.name = f'mul {a} mod {N}'
    return qc

def constant_modular_exponentiation(a:int,N:int,qubits:int):
    '''
    return the circuit to compute a^x mod N

    a: constant
    N: constant module
    qubits: number of qubits for the input
    '''

    qc = QuantumCircuit(qubits + N.bit_length()*2 + 2)
    qc.x(qubits)
    for i in range(qubits):
        value = modular_square_exponentiation(a,1 << i, N)
        mod_mul = constant_modular_multiplier(value,N,N.bit_length())
        inv_value = modular_inverse(value,N)
        inv_mod_mul = constant_modular_multiplier(inv_value,N,N.bit_length()).inverse()
        inv_mod_mul.name = f'mul {inv_value} mod {N} inverted'
        qc.append(mod_mul,[i] + list(range(qubits,qubits + mod_mul.num_qubits - 1)))
        for j in range(qubits,qubits + N.bit_length()):
            qc.cswap(i,j,j + N.bit_length())
            pass
        qc.append(inv_mod_mul,[i] + list(range(qubits,qubits + inv_mod_mul.num_qubits - 1)))
        pass

    return qc