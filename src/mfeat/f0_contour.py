

def get_f0_contour(path, sr=None, in_midi=False):
	"""
	Compute F0 contour using autocorrelation method from Praat.

	Parameters
	----------
	y: ndarray
		- Audio signal.
	sr: int
		- Sampling rate of the audio signal.
	in_midi: bool
		- Want the fundamental frequency in midi notation (Rounded to the nearest)
	Returns
	-------
	ndarray
		F0 contour array in (Hz or midi as per the in_midi parameter)
	ndarray
		Timestamp (sec).
	"""
	import parselmouth, librosa
	import os
	os.environ["MODUSA_NO_AUDIO"] = "1"
	import modusa as ms
	import numpy as np
	
	# Load the audio signal
	y, sr, title = ms.load(path, sr=None) # Loads in mono
	
	time_step = 0.01
	
	snd = parselmouth.Sound(values=y, sampling_frequency=sr)
	pitch_obj = snd.to_pitch_ac(
		time_step=time_step,
		pitch_floor=50.0, 
		max_number_of_candidates=15, 
		very_accurate=True, 
		silence_threshold=0.1,
		voicing_threshold=0.25,
		octave_cost=0.1, 
		octave_jump_cost=0.8, 
		voiced_unvoiced_cost=0.3, 
		pitch_ceiling=600
	)
	f0 = pitch_obj.selected_array['frequency']
	f0_t = pitch_obj.ts()
	f0_t = np.round(f0_t, 2)
	
	if in_midi is True:
		voiced_region = f0 > 10 # Voiced regions
		f0[voiced_region] = np.round(librosa.hz_to_midi(f0[voiced_region]))
		f0 = f0.astype(int)
		
	return f0, f0_t, title
