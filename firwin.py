#!/usr/bin/python3

import commpy
from scipy import signal
import numpy as np
import matplotlib.pyplot as plt

def fft(sig, N, Fs, threshold=0.0001):
    fft = np.fft.fft(sig, N)
    freq = np.fft.fftfreq(N, d=1/Fs)

    fft = fft[:N//2]
    freq = freq[:N//2]

    magnitude = abs(fft)
    # In power dB
    power_db = 20 * np.log10(magnitude)

    fft_indices = np.argwhere(magnitude > threshold).flatten()
    all_indices = False
    if len(fft_indices) == 0:
        all_indices = True
        fft_indices = np.argwhere(magnitude).flatten()

    if not all_indices:
        min_freq = np.min(freq[fft_indices])
        max_freq = np.max(freq[fft_indices])
        d = (abs(max_freq) - abs(min_freq))
        min_freq -= d
        max_freq += d
        min_idx = (np.abs(freq - min_freq)).argmin()
        max_idx = (np.abs(freq - max_freq)).argmin()
        fft_indices = np.arange(min_idx, max_idx)

    return fft_indices, freq, magnitude, power_db



Fs = 160
N = Fs

bandpass = signal.firwin(numtaps=71, cutoff=[35, 45], scale=True, pass_zero=False, fs=Fs)

n = len(bandpass)
f = 40
w = 2*np.pi*f/Fs
zeta = np.array([np.exp(-1j*w*k) for k in np.arange(0, n)])
zeta *= bandpass
print("Bandpass G %.3f for %.3f Hz" % (np.abs(np.sum(zeta)), f))

impulse = np.zeros(N)
impulse[0] = 1

#XXX
impulse = np.cos(2*np.pi*40*np.linspace(0, 1, N, endpoint=False))

impulse_response = np.convolve(impulse, bandpass)
#impulse_response = signal.lfilter(bandpass, 1, impulse)


bp_fft_indices, bp_freq, bp_magnitude, bp_power_db = fft(bandpass, N, Fs)
ir_fft_indices, ir_freq, ir_magnitude, ir_power_db = fft(impulse_response, N, Fs)

fig, ax = plt.subplots(4,1)

ax[0].plot(bandpass)
ax[1].plot(impulse_response[:len(bandpass)])
#ax[1].plot(impulse_response[:len(bandpass)])

ax[2].plot(bp_freq[bp_fft_indices], bp_magnitude[bp_fft_indices])
ax[3].plot(ir_freq[ir_fft_indices], ir_magnitude[ir_fft_indices])

plt.show()
