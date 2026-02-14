from qiskit import QuantumCircuit, transpile, ClassicalRegister, QuantumRegister
from qiskit.visualization import plot_histogram
from qiskit import transpile
from numpy import sqrt
from qiskit.visualization import array_to_latex
from qiskit.quantum_info import Statevector, state_fidelity
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, depolarizing_error
from qiskit_ibm_runtime import QiskitRuntimeService
from qiskit_ibm_runtime import Sampler
bell_states=['phi+','phi-','psi+','psi-']

def bell_state(state, measure=False):

 q=QuantumRegister(2,'q')
 c=ClassicalRegister(2,'c')

 qc=QuantumCircuit(q,c)

 qc.h(q[0])

 qc.cx(q[0],q[1])

 match state:
    case 'phi-':
      qc.z(0)
    case 'psi+':
        qc.x(1)
    case 'psi-':
        qc.z(0)
        qc.x(1)
    case _:
        pass
 if measure:
    qc.measure(q,c)
 return qc

def connect():
    service=QiskitRuntimeService()
    QiskitRuntimeService.save_account(
    channel="ibm_quantum_platform",
    token="sDOFH-oRfXnj19eT-21rCJsgee41H_Hi8Y0hdM84ZXUA",
    overwrite=True
)
    backend=service.least_busy(simulator=False, min_num_qubits=5)
    print("connected to backend")
    for state in bell_states:
      ideal_qubit=bell_state(state,measure=True)
      transpiled=transpile(ideal_qubit, backend)
      sampler = Sampler(backend)
      job = sampler.run([transpiled], shots=5000)
      result = job.result()
      data = result[0].data
      counts =result[0].data.c.get_counts()
      total = sum(counts.values())
      fidelity_phi = (counts.get("00", 0) + counts.get("11", 0)) / total
      fidelity_psi = (counts.get("01", 0) + counts.get("10", 0)) / total
      fidelity=fidelity_phi+fidelity_psi
      print(fidelity)
    return




noise_model=NoiseModel()
error_1q=depolarizing_error(0.02,1)
error_2q=depolarizing_error(0.05,2)
noise_model.add_all_qubit_quantum_error(error_1q, ['h'])
noise_model.add_all_qubit_quantum_error(error_2q, ['cx'])

for state in bell_states:
    #ideal qubit to be used in fidelity calculation to measure how close the noisy state is to the ideal
    ideal_qubit=bell_state(state, measure=False)
    ideal_state=Statevector.from_instruction(ideal_qubit)
    noisy_qubit=bell_state(state, measure=False)
  noisy_qubit.save_density_matrix()

    noisy_sim=AerSimulator(method="density_matrix",noise_model=noise_model)
    compiled_noise=transpile(noisy_qubit,noisy_sim)
    result=noisy_sim.run(compiled_noise).result()
    rho=result.data(0)['density_matrix']
    fidelity=state_fidelity(ideal_state,rho)
    print(f"Fidelity with noise: {fidelity}")
    #run on ibm quantum hardware
connect()
      
