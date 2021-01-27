from quantities import mV, ms, s, V
from neo import AnalogSignal
import numpy as np
import quantities as pq
import numpy
voltage_units = mV
import copy
from elephant.spike_train_generation import threshold_detection
from sciunit.models.backends import Backend
from numba import jit
import cython
from sciunit.models import RunnableModel

@jit(nopython=True)
def get_vm_four(C=89.7960714285714,
		 a=0.01, b=15, c=-60, d=10, k=1.6,
		 vPeak=(86.364525297619-65.2261863636364),
		  vr=-65.2261863636364, vt=-50,I=[]):
	tau = dt = 0.25
	N = len(I)

	v = vr*np.ones(N)
	u = np.zeros(N)
	v[0] = vr
	for i in range(N):
		# forward Euler method
		v[i+1] = v[i] + tau * (k * (v[i] - vr) * (v[i] - vt) - u[i] + I[i]) / C
		u[i+1] = u[i]+tau*a*(b*(v[i]-vr)-u[i]); # Calculate recovery variable
		if v[i+1] > (vPeak - 0.1*u[i+1]):
			v[i] = vPeak - 0.1*u[i+1]
			v[i+1] = c + 0.04*u[i+1]; # Reset voltage
			if (u[i]+d)<670:
				u[i+1] = u[i+1]+d; # Reset recovery variable
			else:
				u[i+1] = 670;

	return v

@jit(nopython=True)
def get_vm_five(C=89.7960714285714,
		 a=0.01, b=15, c=-60, d=10, k=1.6,
		 vPeak=(86.364525297619-65.2261863636364),
		  vr=-65.2261863636364, vt=-50,I=[]):
	N = len(I)

	tau= dt = 0.25; #dt
	v = vr*np.ones(N)
	u = np.zeros(N)
	v[0] = vr
	for i in range(N):
		# forward Euler method
		v[i+1] = v[i] + tau * (k * (v[i] - vr) * (v[i] - vt) - u[i] + I[i]) / C

		if v[i+1] < d:
			u[i+1] = u[i] + tau*a*(0-u[i])
		else:
			u[i+1] = u[i] + tau*a*((0.025*(v[i]-d)**3)-u[i])


		if v[i+1]>=vPeak:
			v[i]=vPeak;
			v[i+1]=c;

	return v



@jit(nopython=True)
def get_vm_six(C=89.7960714285714,
		 a=0.01, b=15, c=-60, d=10, k=1.6,
		 vPeak=(86.364525297619-65.2261863636364),
		  vr=-65.2261863636364, vt=-50,I=[]):
	tau= dt = 0.25; #dt
	N = len(I)

	v = vr*np.ones(N)
	u = np.zeros(N)
	v[0] = vr
	for i in range(N):
	   # forward Euler method
		v[i+1] = v[i] + tau * (k * (v[i] - vr) * (v[i] - vt) - u[i] + I[i]) / C


		if v[i+1] > -65:
			b=0;
		else:
			b=15;
		u[i+1]=u[i]+tau*a*(b*(v[i]-vr)-u[i]);

		if v[i+1] > (vPeak + 0.1*u[i+1]):
			v[i]= vPeak + 0.1*u[i+1];
			v[i+1] = c-0.1*u[i+1]; # Reset voltage
			u[i+1]=u[i+1]+d;

	return v

@jit(nopython=True)
def get_vm_seven(C=89.7960714285714,
		 a=0.01, b=15, c=-60, d=10, k=1.6,
		 vPeak=(86.364525297619-65.2261863636364),
		  vr=-65.2261863636364, vt=-50,I=[]):
	tau= dt = 0.25; #dt
	N = len(I)
	v = vr*np.ones(N)
	u = np.zeros(N)
	v[0] = vr
	for i in range(N):

		# forward Euler method
		v[i+1] = v[i] + tau * (k * (v[i] - vr) * (v[i] - vt) - u[i] + I[i]) / C


		if v[i+1] > -65:
			b=2;
		else:
			b=10;

		u[i+1]=u[i]+tau*a*(b*(v[i]-vr)-u[i]);
		if v[i+1]>=vPeak:
			v[i]=vPeak;
			v[i+1]=c;
			u[i+1]=u[i+1]+d;  # reset u, except for FS cells


	return v


@jit(nopython=True)
def get_vm_one_two_three(C=89.7960714285714,
		 a=0.01, b=15, c=-60, d=10, k=1.6,
		 vPeak=(86.364525297619-65.2261863636364),
		  vr=-65.2261863636364, vt=-50,I=[]):
	tau= dt = 0.25; #dt
	N = len(I)
	v = vr*np.ones(N)
	u = np.zeros(N)
	v[0] = vr
	for i in range(N-1):
		# forward Euler method
		v[i+1] = v[i] + tau * (k * (v[i] - vr) * (v[i] - vt) - u[i] + I[i]) / C
		u[i+1] = u[i]+tau*a*(b*(v[i]-vr)-u[i]); # Calculate recovery variable

		if v[i+1]>=vPeak:
			v[i]=vPeak
			v[i+1]=c
			u[i+1]=u[i+1]+d  # reset u, except for FS cells
	return v

@jit(nopython=True)
def get_2003_vm(I,times,a=0.01, b=15, c=-60, d=10,vr = -70):
	u=b*vr
	V = vr
	tau = dt = 0.25
	N = len(I)
	vv = np.zeros(N)
	UU = np.zeros(N)

	for i in range(N):
		V = V + tau*(0.04*V**2+5*V+140-u+I[i]);
		u = u + tau*a*(b*V-u);
		if V > 30:
			vv[i] = 30;
			V = c;
			u = u + d;
		else:
			vv[i]=V;
		UU[i]=u;
	return vv


class JIT_IZHIBackend(Backend,RunnableModel):

	name = 'IZHI'
	def __init__(self, attrs=None):
		self.vM = None
		self._attrs = None
		self.temp_attrs = None
		if type(attrs) is not type(None):
			self._attrs = attrs
		self.default_attrs = {'C':89.7960714285714,
			'a':0.01, 'b':15, 'c':-60, 'd':10, 'k':1.6,
			'vPeak':(86.364525297619-65.2261863636364),
			'vr':-65.2261863636364, 'vt':-50, 'celltype':3}

		if self._attrs is None:
			self._attrs = self.default_attrs

		super().__init__(name='IZHI')
		super().init_backend(attrs=self._attrs,name='IZHI')
		self.spikes = 0


	def set_stop_time(self, stop_time = 650*pq.ms):
		"""Sets the simulation duration
		stopTimeMs: duration in milliseconds
		"""
		self.tstop = float(stop_time.rescale(pq.ms))


	def get_membrane_potential(self):
		"""Must return a neo.core.AnalogSignal.
		"""
		if type(self.vM) is not type(None):
			return self.vM


		if type(self.vM) is type(None):

			everything = copy.copy(self.attrs)
			if hasattr(self,'Iext'):
				everything.update({'Iext':self.Iext})

			if 'current_inj' in everything.keys():
				everything.pop('current_inj',None)
			everything = copy.copy(self.attrs)

			self.attrs['celltype'] = int(round(self.attrs['celltype']))
			assert type(self.attrs['celltype']) is type(int())
			if self.attrs['celltype'] <= 3:
				everything.pop('celltype',None)
				v = get_vm_one_two_three(**everything)
			else:
				if self.attrs['celltype'] == 4:
					v = get_vm_four(**everything)
				if self.attrs['celltype'] == 5:
					v = get_vm_five(**everything)
				if self.attrs['celltype'] == 6:
					v = get_vm_six(**everything)
				if self.attrs['celltype'] == 7:



					v = get_vm_seven(**everything)

			self.vM = AnalogSignal(v,
								units=pq.mV,
								sampling_period=0.25*pq.ms)



		return self.vM

	@cython.boundscheck(False)
	@cython.wraparound(False)
	def inject_square_current(self, amplitude=100*pq.pA, delay=10*pq.ms, duration=500*pq.ms,padding=0*pq.ms):
		"""
		Inputs: current : a dictionary with exactly three items, whose keys are: 'amplitude', 'delay', 'duration'
		Example: current = {'amplitude':float*pq.pA, 'delay':float*pq.ms, 'duration':float*pq.ms}}
		where \'pq\' is a physical unit representation, implemented by casting float values to the quanitities \'type\'.
		Description: A parameterized means of applying current injection into defined
		Currently only single section neuronal models are supported, the neurite section is understood to be simply the soma.

		"""

		attrs = self.attrs
		if attrs is None:
			attrs = self.model.default_attrs

		self.attrs = attrs
		'''
		square = True

		if isinstance(amplitude,type(dict())):
			c = amplitude
			amplitude = float(c['amplitude'])
			duration = float(c['duration'])
			delay = float(c['delay'])
			if 'padding' in c.keys():
				padding = float(c['padding'])
		'''
		amplitude = float(amplitude)
		duration = float(duration)
		delay = float(delay)
		padding = float(padding)
		tMax = delay + duration + padding

		tMax = self.tstop = float(tMax)
		N = int(tMax/0.25)
		Iext = np.zeros(N)
		delay_ind = int((delay/tMax)*N)
		duration_ind = int((duration/tMax)*N)

		Iext[0:delay_ind-1] = 0.0
		Iext[delay_ind:delay_ind+duration_ind-1] = amplitude
		Iext[delay_ind+duration_ind::] = 0.0
		self.Iext = None
		self.Iext = Iext
		self.attrs['I'] = Iext
		everything = copy.copy(self.attrs)
		everything.pop('celltype',None)
		everything['I'] = Iext
		if 'current_inj' in everything.keys():
			everything.pop('current_inj',None)
		self.attrs['celltype'] = round(self.attrs['celltype'])

		if np.bool_(self.attrs['celltype'] <= 3):
			v = get_vm_one_two_three(**everything)
		else:

			if np.bool_(self.attrs['celltype'] == 4):
				v = get_vm_four(**everything)
			if np.bool_(self.attrs['celltype'] == 5):
				v = get_vm_five(**everything)
			if np.bool_(self.attrs['celltype'] == 6):
				v = get_vm_six(**everything)
			if np.bool_(self.attrs['celltype'] == 7):
				v = get_vm_seven(**everything)



		self.vM = AnalogSignal(v,
							units=pq.mV,
							sampling_period=0.25*pq.ms)
							#sampling_rate=(1.0/(0.00025))*pq.Hz)

		self.attrs.pop('I',None)
		if float(self.vM.times[-1])!=float(delay)+float(duration)+float(padding):
			extra_part = float(self.vM.times[-1]) - (float(delay)+float(duration)+float(padding))
			#print(extra_part)
		return self.vM

	@property
	def attrs(self):
		return self._attrs

	@attrs.setter
	def attrs(self,attrs):
		if attrs is not None:
			self.default_attrs.update(attrs)
		else:
			self._attrs = self.default_attrs

		if hasattr(self,'model'):
			if not hasattr(self.model,'attrs'):
				self.model.attrs = {}
				self.model.attrs.update(attrs)



	def wrap_known_i(self,i,times):
		everything = self.attrs
		if 'current_inj' in everything.keys():
			everything.pop('current_inj',None)
		if 'celltype' in everything.keys():
			everything.pop('celltype',None)
		two_thousand_and_three=False
		if two_thousand_and_three:
			v = AnalogSignal(get_2003_vm(i,times,**reduced),units=pq.mV,sampling_period=0.25*pq.ms)
		else:
			v = AnalogSignal(get_vm_known_i(i,times,**everything),units=pq.mV,sampling_period=(times[1]-times[0])*pq.ms)
		thresh = threshold_detection(v,0*pq.mV)
		return v


	def get_spike_count(self):
		thresh = threshold_detection(self.vM,0*pq.mV)
		self.spikes = len(thresh)
		return len(thresh)

	@cython.boundscheck(False)
	@cython.wraparound(False)
	def inject_direct_current(self, I):
		"""
		Inputs: current : a dictionary with exactly three items, whose keys are: 'amplitude', 'delay', 'duration'
		Example: current = {'amplitude':float*pq.pA, 'delay':float*pq.ms, 'duration':float*pq.ms}}
		where \'pq\' is a physical unit representation, implemented by casting float values to the quanitities \'type\'.
		Description: A parameterized means of applying current injection into defined
		Currently only single section neuronal models are supported, the neurite section is understood to be simply the soma.

		"""

		attrs = self.attrs
		if attrs is None:
			attrs = self.default_attrs

		self.attrs = attrs
		self.attrs['I'] = np.array(I)

		self.attrs['celltype'] = int(round(self.attrs['celltype']))
		everything = copy.copy(self.attrs)

		if 'current_inj' in everything.keys():
			everything.pop('current_inj',None)

		if np.bool_(self.attrs['celltype'] <= 3):
			everything.pop('celltype',None)
			v = get_vm_one_two_three(**everything)
		else:


			if np.bool_(self.attrs['celltype'] == 4):
				everything.pop('celltype',None)
				v = get_vm_four(**everything)
			if np.bool_(self.attrs['celltype'] == 5):
				everything.pop('celltype',None)
				v = get_vm_five(**everything)
			if np.bool_(self.attrs['celltype'] == 6):
				everything.pop('celltype',None)
				if 'I' in self.attrs.keys():
					everything.pop('I',None)
				v = get_vm_six(self.attrs['I'],**everything)
			if np.bool_(self.attrs['celltype'] == 7):
				everything.pop('celltype',None)
				v = get_vm_seven(**everything)

		if 'I' in self.attrs.keys():
			self.attrs.pop('I',None)

		self.vM = AnalogSignal(v,
							units=pq.mV,
							sampling_period=0.25*pq.ms)

		return self.vM

	def inject_ramp_current(self, t_stop, gradient=0.000015,
							onset=30.0, baseline=0.0, t_start=0.0):
		times, amps = self.ramp(gradient, onset, t_stop, baseline=0.0, t_start=0.0)
		everything.update({'ramp':amps})
		everything.update({'start':onset})
		everything.update({'stop':t_stop})

		if 'current_inj' in everything.keys():
			everything.pop('current_inj',None)

		self.attrs['celltype'] = round(self.attrs['celltype'])
		if np.bool_(self.attrs['celltype'] <= 3):
			everything.pop('celltype',None)
			v = get_vm_one_two_three(**everything)
		else:



			if np.bool_(self.attrs['celltype'] == 4):
				v = get_vm_four(**everything)
			if np.bool_(self.attrs['celltype'] == 5):
				v = get_vm_five(**everything)
			if np.bool_(self.attrs['celltype'] == 6):
				v = get_vm_six(**everything)
			if np.bool_(self.attrs['celltype'] == 7):
				v = get_vm_seven(**everything)
		self.vM = AnalogSignal(v,
							units=pq.mV,
							sampling_period=0.25*pq.ms)

		return self.vM
	def _backend_run(self):
		results = {}
		results['vm'] = self.vM.magnitude
		results['t'] = self.vM.times
		results['run_number'] = results.get('run_number',0) + 1
		return results
