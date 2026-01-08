import streamlit as st
import numpy as np
import scipy.signal
import soundfile as sf

# --- CONFIGURATION ---
st.set_page_config(page_title="SOT Engine Doctor", page_icon="🩺", layout="centered")

# --- CSS FOR MOBILE FEEL ---
st.markdown("""
    <style>
    .stApp { background-color: #000000; color: #ffffff; }
    div.stButton > button {
        width: 100%; height: 70px; font-size: 22px; font-weight: bold;
        background-color: #FF4B4B; color: white; border-radius: 12px; border: none;
    }
    .result-box {
        padding: 20px; border-radius: 10px; text-align: center; margin-bottom: 20px;
    }
    .safe { background-color: #06402B; border: 2px solid #00CC96; }
    .danger { background-color: #590000; border: 2px solid #FF2B2B; }
    h1 { text-align: center; }
    </style>
""", unsafe_allow_html=True)

st.title("🩺 SOT Engine Doctor")
st.write("Universal Physics Diagnostic Tool")

# --- THE PHYSICS BRAIN (SOT TURBULENCE) ---
def calculate_turbulence(audio_data, rate):
    # 1. Slice audio into micro-chunks to check rhythm
    chunk_size = int(len(audio_data) / 20) # 20 slices
    if chunk_size == 0: return 0, 0
    
    chunks = [audio_data[i:i + chunk_size] for i in range(0, len(audio_data), chunk_size)]
    lle_scores = []
    
    for chunk in chunks:
        if len(chunk) < 50: continue
        # Hilbert Envelope (Energy Shape)
        envelope = np.abs(scipy.signal.hilbert(chunk))
        # Log-Divergence (Instant Chaos)
        lle = np.std(np.log(envelope + 1e-9))
        lle_scores.append(lle)
    
    # METRICS
    # If the engine is healthy, the "Chaos Score" should be constant (Low Variance).
    # If broken, it skips beats (High Variance).
    turbulence_variance = np.std(lle_scores)
    avg_intensity = np.mean(lle_scores)
    
    return turbulence_variance, avg_intensity

# --- THE UI ---
st.info("👇 Tap 'Record' and hold close to the engine (5s).")

# The Native Mobile Recorder
audio_file = st.audio_input("Record Engine Sound")

if audio_file is not None:
    with st.spinner("⚛️ Analyzing Micro-Vibrations..."):
        # Load Audio
        data, rate = sf.read(audio_file)
        if len(data.shape) > 1: data = data.mean(axis=1) # Stereo to Mono
        
        # Run SOT Physics
        turbulence, intensity = calculate_turbulence(data, rate)
        
        st.divider()
        
        # DIAGNOSIS
        # Thresholds: > 0.15 is usually a skipped beat or loose part
        if turbulence > 0.15:
            st.markdown(f"""
                <div class="result-box danger">
                    <h2>🚨 CRITICAL FAULT</h2>
                    <p>Turbulence Score: {turbulence:.3f}</p>
                    <p>Diagnosis: Rhythm Instability Detected (Loose Part/Misfire)</p>
                </div>
            """, unsafe_allow_html=True)
        elif turbulence > 0.08:
            st.markdown(f"""
                <div class="result-box danger" style="background-color: #5e4b00; border-color: #ffcc00;">
                    <h2>⚠️ WARNING SIGNS</h2>
                    <p>Turbulence Score: {turbulence:.3f}</p>
                    <p>Diagnosis: High Wear / Rough Idle</p>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
                <div class="result-box safe">
                    <h2>✅ HEALTHY ENGINE</h2>
                    <p>Turbulence Score: {turbulence:.3f}</p>
                    <p>Diagnosis: Laminar Flow (Perfect Rhythm)</p>
                </div>
            """, unsafe_allow_html=True)

        st.caption("Physics Visualization (Waveform)")
        st.line_chart(data[::50])
