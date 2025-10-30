import os
import streamlit as st

# Must be set before any modusa import
os.environ["MODUSA_NO_AUDIO"] = "1"

# Try safe import of modusa
ms = None
try:
    import modusa as _modusa
    ms = _modusa
except Exception as e:
    st.warning("Audio functions are disabled in this deployment environment.")
    ms = None

from loudness import get_loudness_contour

import os
import tempfile
import numpy as np

import sys
from pathlib import Path
modules_dir = Path(__file__).resolve().parents[1]/"src"/"mfeat"
sys.path.append(str(modules_dir))

from loudness import get_loudness_contour
from high_cut_off import get_high_cutoff_freq
from tempo import get_tempo
from rhythmicity import get_rhythmicity
from f0_contour import get_f0_contour


# Create a streamlit webapp to allow users to upload an audio file (music) and plot all the 4 features
# Loudness, High Cutoff, Tempo, Rhythmicity

# Add a title
st.title("MFeat")
st.subheader("Musical Features Extractor")

# Create upload widget with streamlit
uploaded_audio = st.file_uploader(
	label="🎵 Upload your music file",

	accept_multiple_files=False,
	type=["mp3", "wav"],
	help="Upload your music file in .mp3 or .wav format"
)

# Load the audio content from st uploaded file object
if uploaded_audio is not None:
	with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
		# Load the audio at 48000
		tmp.write(uploaded_audio.read())
		tmp_path = tmp.name
		
		y, sr, _ = ms.load(tmp_path, sr=48000)
		title = uploaded_audio.name
	
		st.write(f"{title}")
		st.audio(uploaded_audio)
	
		# Compute loudness
		st.subheader("Loudness Contour")
		local_loudness, local_loudness_t, _ = get_loudness_contour(tmp_path)
		fig = ms.fig("s")
		fig.add_signal(
			local_loudness, local_loudness_t,
			ylabel="Loudness (dB)",
			label="Loudness contour"
		)
		fig.add_xlabel("Time (sec)")
		fig.add_title(title)
		st.pyplot(fig._fig)
		
		# Compute high cutoff
		st.subheader("High Cutoff Frequency")
		local_cutoff, local_cutoff_t, agg_cutoff, _, S = get_high_cutoff_freq(tmp_path)
		fig = ms.fig("m")
		fig.add_matrix(
			S[0], S[1], S[2],
			ylabel="Frequency (Hz)",
			label="Spectrogram",
			o="lower",
			c="gray_r"
		)
		fig.add_signal(
			local_cutoff, local_cutoff_t,
			label="High Cutoff",
			ax=1,
			c="r"
		)
		fig.add_xlabel("Time (sec)")
		fig.add_title(title)
		fig.add_legend()
		st.write(f"Overall cutoff frequency: {agg_cutoff} Hz")
		st.pyplot(fig._fig)
		
		
		# Compute F0 contour
		st.subheader("Pitch Tracking")
		f0, f0_t, _ = get_f0_contour(tmp_path)
		f0_midi, f0_midi_t, _ = get_f0_contour(tmp_path, in_midi=True)
		fig = ms.fig("ss")
		fig.add_signal(
			f0, f0_t,
			ylabel="Pitch (Hz)",
			label="Pitch (Hz)"
		)
		fig.add_signal(
			f0_midi, f0_midi_t,
			ylabel="Pitch (MIDI)",
			label="Pitch (MIDI)"
		)
		fig.add_xlabel("Time (sec)")
		fig.add_title(title)
		fig.add_legend()
		st.pyplot(fig._fig)
		
		st.subheader("Pitch Tracking (ZOOMED IN)")
		fig = ms.fig("ss", xlim=(0, 30))
		fig.add_signal(
			f0, f0_t,
			ylabel="Pitch (Hz)",
			label="Pitch (Hz)"
		)
		fig.add_signal(
			f0_midi, f0_midi_t,
			ylabel="Pitch (MIDI)",
			label="Pitch (MIDI)"
		)
		fig.add_xlabel("Time (sec)")
		fig.add_title(title)
		fig.add_legend()
		st.pyplot(fig._fig)
		
		# Pitch Distribution
		st.subheader("Pitch Distribution")
		f0, f0_t, _ = get_f0_contour(tmp_path)
		f0_midi, f0_midi_t, _ = get_f0_contour(tmp_path, in_midi=True)
		fig = ms.hill_plot(
			f0[f0>0],
			labels=title[:10]+ "...",
			xlabel="Pitch (Hz)"
		)
		
		st.pyplot(fig)
		
		fig = ms.hill_plot(
			f0_midi[f0>0],
			labels=title[:10] + "...",
			xlabel="Pitch (MIDI)"
		)
		st.pyplot(fig)
		
		
		
		# Compute tempo
		st.subheader("Tempo")
		local_tempo, local_tempo_t, agg_tempo, confidence = get_tempo(tmp_path)
		fig = ms.fig("s")
		fig.add_signal(
			local_tempo, local_tempo_t,
			ylabel="Tempo (BPM)",
			label="Tempo"
		)
		fig.add_xlabel("Time (sec)")
		fig.add_title(title)
		fig.add_legend()
		st.write(f"Global Tempo: {agg_tempo} BPM")
		st.pyplot(fig._fig)
		
		
		# Compute rhythmicity
		st.subheader("Rhythmicity")
		local_rhythmicity, local_rhythmicity_t, _ = get_rhythmicity(tmp_path)
		fig = ms.fig("s")
		fig.add_signal(
			local_rhythmicity, local_rhythmicity_t,
			ylabel="Strength",
			label="Rhythmicity"
		)
		fig.add_xlabel("Time (sec)")
		fig.add_title(title)
		fig.add_legend()
		st.pyplot(fig._fig)
	
	os.remove(tmp_path)
