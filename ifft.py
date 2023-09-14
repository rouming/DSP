#
# https://stackoverflow.com/questions/53269177/i-only-get-noise-in-the-audio-after-taking-a-fft-and-varying-frequency-component
#
# Below is a simple program that (a) reads a wave file, (b) Fourier
# transforms the data, (c) modifies the amplitudes at specific
# frequencies, (d) reverses the Fourier transform to convert the data
# back to time domain, and (e) saves the result to another wave file
# that you can play with any of the usual audio playback programs.
#
# For purposes of demonstrating what you can do with the signal in a
# simple way, we attenuate the amplitude at 1 kHz,we add a continuous
# tone at 440 Hz and we add a Gaussian shaped pulse at 880.
#

from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import numpy as np
import soundfile as sf
from scipy.ndimage import uniform_filter1d
from scipy.ndimage import gaussian_filter1d
from scipy.signal import savgol_filter
from matplotlib.colors import LightSource
from matplotlib import cm

import drawsvg as dw

#plt.rcParams['figure.dpi'] = 100
plt.rcParams['figure.figsize'] = (150, 15)


# Input the wave file
data, rate = sf.read("homyak.wav")
#data, rate = sf.read("tones.wav")

chunk_dur_s = 0.2
overlap_dur_s = 0.15
beg_pos_s = 0
dur_s = len(data) / rate
chunk_len = int(chunk_dur_s * rate)
overlap_len = int(overlap_dur_s * rate)
assert chunk_len > overlap_len

beg_ind = int(beg_pos_s * rate)

# Get the list of frequencies
freq = np.fft.rfftfreq(chunk_len, d=1./rate)
freq_lim = (np.abs(freq - 1000)).argmin()

freq = freq[:freq_lim]

chunks_n = int((len(data) - chunk_len) / (chunk_len - overlap_len)) + 1

y_time = np.linspace(0, dur_s, chunks_n)
X, Y = np.meshgrid(freq, y_time)
Z = np.empty(shape=(0, len(freq)))

while beg_ind + chunk_len < len(data):
    chunk = data[beg_ind:beg_ind+chunk_len]
    assert len(chunk) == chunk_len
    beg_ind += (chunk_len - overlap_len)

    # Fourier transform
    fft_data = np.fft.rfft(chunk)
    mag_data = np.abs(fft_data)[:freq_lim]

    hist_window = 50


    # amplitude to decibel
    mag_data[ mag_data == 0 ] = 1e-9 # avoid zeros
    db = 20.*np.log10(mag_data)
    mag_data = db


    f1 = savgol_filter(mag_data, hist_window, 5,
                       axis=0, mode="nearest")
    f2 = uniform_filter1d(mag_data, size=hist_window,
                          axis=0, mode="reflect")
    f3 = gaussian_filter1d(mag_data, sigma=6,
                           axis=0, mode="reflect")

    Z = np.append(Z, [f2], axis=0)


    # Find the bin closest to 4kHz and attenuate
    #idx = (np.abs(freq - 4.E3)).argmin()
    #fft_data[idx] *= 1./100

    # Find the bin closest to 7kHz and attenuate
    #idx = (np.abs(freq - 7.E3)).argmin()
    #fft_data[idx] *= 1./100

    #for i in range(3000, len(FFT_data)):
    #    fft_data[i] = 0

    #idx_low = (np.abs(freq - 200)).argmin()
    #idx_high = (np.abs(freq - 4000)).argmin()
    #idx_low = 0
    #idx_high = len(fft_data)


    # Find the bin closest to 440 Hz and set a continuous tone
    #idx = (np.abs(freq - 440)).argmin()
    #fft_data[idx] = np.max(np.abs(fft_data))

    #zeros = np.zeros(fft_data.shape)
    #zeros += 3000 * np.exp( -((freq-880)*1000.)**2 )


    ## Add a Gaussian pulse, width in frequency is inverse of its duration
    #fft_data += np.max(np.abs(fft_data))/2. * np.exp( -((freq-880)/5.)**2 )


    # Convert back to time domain
    #newdata = np.fft.irfft(fft_data)
    #newdata = np.fft.irfft(zeros)

    # And save it to a new wave file
    #sf.write(file="test.wav", data=newdata, samplerate=rate)



fig = plt.figure()
ax3d = fig.add_subplot(111, projection='3d')

# Scale 'y' axis
ax3d.set_box_aspect(aspect = (1,3,1))

#ax3d.plot_wireframe(X, Y, Z, cstride=0)
ax3d.plot_surface(X, Y, Z, cmap = plt.cm.cividis)



ax = fig.add_subplot(212)
ax.plot(freq, f1)


plt.show()



# Convert 'y' axis to svg coordinate system
y = f1 * -1

w = int(np.ceil(np.max(freq)))
h = int(np.ceil(np.max(y)))
p = np.array([freq, y]).transpose().flatten().tolist()

d = dw.Drawing(w, h*4, id_prefix='pic')
#d.view_box = (0,0,10,10)
lines = dw.Lines(p[0], p[1], *p[2:], fill='none', stroke='black')
lines = dw.Use(lines, 0, 0, stroke='red', transform='scale(1, 4)')
d.append(lines)
d.save_svg('example.svg')
