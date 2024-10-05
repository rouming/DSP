#!/usr/bin/python3

import commpy
from scipy import signal
import numpy as np
import matplotlib.pyplot as plt

def zoom_fft(fft, N, Fs, threshold=0.5):
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
        d = (max_freq - min_freq) * 2
        min_freq -= d
        max_freq += d
        min_idx = (np.abs(freq - min_freq)).argmin()
        max_idx = (np.abs(freq - max_freq)).argmin()
        fft_indices = np.arange(min_idx, max_idx)

    return fft_indices, freq, magnitude, power_db



Fs = 512
N = Fs
G = 1

bandpass = signal.firwin(numtaps=255, cutoff=[35, 45], scale=True, pass_zero=False, fs=Fs)
bandpass *= G

n = len(bandpass)
f = 40
w = 2*np.pi*f/Fs
zeta = np.array([np.exp(-1j*w*k) for k in np.arange(0, n)])
zeta *= bandpass
print("Bandpass G %.3f for %.3f Hz" % (np.abs(np.sum(zeta)), f))


def f(t, f0, f1, t1):
    return f0 + t * (f1 - f0) / t1

t = np.linspace(0, 1, N, endpoint=False)
chirp = np.cos(2*np.pi*f(t, 0, 70, 1)*t)
chirp_response = np.convolve(chirp, bandpass)[:N]

c_fft = np.fft.fft(chirp, N)
cr_fft = np.fft.fft(chirp_response, N)
fft = cr_fft / c_fft

fft_indices, freq, magnitude, power_db = zoom_fft(fft, N, Fs)

fig, ax = plt.subplots(2,1)

ax[0].plot(bandpass)

ax[1].plot(freq[fft_indices], power_db[fft_indices], 'b')
ax[1].set_xlabel("Frequency")
ax[1].set_ylabel("Power dB", color='b')
ax[1].tick_params(axis='y', labelcolor='b')

ax1_twin = ax[1].twinx()
ax1_twin.plot(freq[fft_indices], np.rad2deg(np.angle(fft[fft_indices])), 'r')
#ax1_twin.plot(freq[fft_indices], power_db[fft_indices], 'r')
ax1_twin.set_ylabel("Phase", color='r')
ax1_twin.tick_params(axis='y', labelcolor='r')

fig.tight_layout()
plt.show()
