#!/usr/bin/python3

import commpy
import scipy
import numpy as np
import matplotlib.pyplot as plt


def signal(t):
    Fcarrier = 30
    Fsymbols = 10

    symbols = (1,1,1, -1, 1,1, -1,-1, 1,1, -1)

    cos = np.cos(2*np.pi*t*Fcarrier)
    symbol = symbols[int(t*Fsymbols) % len(symbols)]

    return cos * symbol, symbol# + np.random.randn() * np.sqrt(0.1)

# Slow fourier transform :)
def sft(sig):
    n = len(sig)
    zeta = np.exp(-2 * np.pi * 1j / n)
    freq = np.array([np.array([sig[i] * zeta**(i * f) for i in range(0, n)]).sum()
            for f in range(0, n)])
    return freq

def cos(f, Fs):
    t = np.linspace(0, 1, int(Fs), endpoint=False)
    return np.cos(2*np.pi*f*t)

def sin(f, Fs):
    t = np.linspace(0, 1, int(Fs), endpoint=False)
    return np.sin(2*np.pi*f*t)

def freq_shift(freq_arr, shift_freq, Fs):
    nyquist = int(Fs) // 2
    out_arr = []
    for freq in freq_arr:
        shifted = freq - shift_freq
        if (shifted // nyquist) & 1:
            shifted = -shifted % nyquist
        else:
            shifted = shifted % nyquist
        out_arr.append(shifted)
        out_arr.append(shifted * -1)

        shifted = freq + shift_freq
        if (shifted // nyquist) & 1:
            shifted = -shifted % nyquist
        else:
            shifted = shifted % nyquist
        out_arr.append(shifted)
        out_arr.append(shifted * -1)

    # Unique and sorted
    return sorted(set(out_arr))

def fft(sig, Fs, plot=False, threshold=0.1):
    fft = np.fft.fftshift(np.fft.fft(sig))
    N = len(sig)
    # Why 1/N scale? See the 3.4 DFT MAGNITUDES, Richard Lyons
    magnitude = abs(fft) / N
    # In power dB
    power_db = 20 * np.log10(magnitude)
    freq = np.fft.fftshift(np.fft.fftfreq(N, d=1/Fs))
    if plot:
        t = np.linspace(0, 1, Fs, endpoint=False)
        plt.subplot(211)
        plt.plot(t, sig)
        plt.subplot(212)
        plt.plot(freq, magnitude)
        plt.show()
    ind = np.argwhere(magnitude > threshold).flatten()
    return ["%.2f Hz(%.2f dB, %.2f)" % (freq[i], power_db[i], magnitude[i]) for i in ind]

# 1,-1, ... sequence; so Fs / 2
def cos_Fsamp_div_2(Fs):
    return np.power(-1, np.arange(int(Fs)))

# -1,1, ... sequence; so Fs / 2
def neg_cos_Fsamp_div_2(Fs):
    return np.power(-1, np.arange(1, int(Fs) + 1))

# 1,0,-1,0 ... sequence; so Fs / 4
def cos_Fsamp_div_4(Fs):
    half_Fs = int(Fs) // 2
    return np.ravel((cos_Fsamp_div_2(half_Fs), np.zeros(half_Fs)), order='F')

# 0,1,0,-1 ... sequence; so Fs / 4
def sin_Fsamp_div_4(Fs):
    half_Fs = int(Fs) // 2
    return np.ravel((np.zeros(half_Fs), cos_Fsamp_div_2(half_Fs)), order='F')

# 0,-1,0,1 ... sequence; so Fs / 4
def neg_sin_Fsamp_div_4(Fs):
    half_Fs = int(Fs) // 2
    return np.ravel((np.zeros(half_Fs), neg_cos_Fsamp_div_2(half_Fs)), order='F')



N_per_sec = 1000
N = 1000
time = np.arange(N)/ N_per_sec

sig = []
symb = []
for t in time:
    si, sy = signal(t)
    sig.append(si)
    symb.append(sy)


####


cos = np.cos(2*np.pi*time*10)
#cos2 = np.cos(2*np.pi*time*250)
#sig = cos_Fsamp_div_2#cos * cos_Fsamp_div_4
sig = cos[::2] * np.power(-1, np.arange(N//2))

# Delete odd indices with zeros
#sig = np.delete(sig, np.arange(1, sig.size, 2))


fft = np.fft.fft(sig)
freq = np.fft.fftfreq(fft.size, d=(1/N_per_sec)*2)


fft = np.fft.fftshift(fft)
freq = np.fft.fftshift(freq)

indices = np.argwhere((fft > 1))
print("indices: ", indices)
print("FFT: ", abs(fft[indices]))
print("FREQ: ", freq[indices])

plt.subplot(211)
#plt.plot(time, sig, 'b')
#plt.plot(time, symb, 'r')

plt.subplot(212)
plt.plot(freq, abs(fft))


plt.show()




exit(0)




def get_pulse_shaping_kernel(Fs, Ts):
    # the RRC filter should span 3 baseband samples to the left and to the right. 
    # Hence, it introduces a delay of 3Ts seconds.
    t0 = 3*Ts

    # Calculate pusle shaping filter coefficients (N=number of samples in filter)
    _, rrc = commpy.filters.rrcosfilter(N=int(2*t0*Fs), alpha=1,Ts=Ts, Fs=Fs)
    t_rrc = np.arange(len(rrc)) / Fs  # the time points that correspond to the filter values

    return rrc, t_rrc, t0

Fs = int(60e3)   # the sampling frequency we use for the discrete simulation of analog signals
Fc = int(3e3)    # 3kHz carrier frequency
Ts = 1e-3        # 1 ms symbol spacing, i.e. the baseband samples are Ts seconds apart.
BN = 1/(2*Ts )   # the Nyquist bandwidth of the baseband signal.

samples_per_symbol = int(Ts*Fs) # number of samples per symbol in the "analog" domain
num_symbols = 1000

# Generate symbols
x_int = np.random.randint(0, 4, num_symbols) # 0 to 3
x_degrees = x_int*360/4.0 + 45 # 45, 135, 225, 315 degrees
x_radians = x_degrees*np.pi/180.0 # sin() and cos() takes in radians
x_symbols = np.cos(x_radians) + 1j*np.sin(x_radians) # this produces our QPSK complex symbols

# Add phase noise
phase_noise = np.random.randn(len(x_symbols)) * 0.1 # adjust multiplier for "strength" of phase noise
#x_symbols = x_symbols * np.exp(1j*phase_noise)

# Add AWGN with unity power
n = (np.random.randn(num_symbols) + 1j*np.random.randn(num_symbols))/np.sqrt(2)
noise_power = 0.01
#x_symbols = x_symbols + n * np.sqrt(noise_power)

x = np.zeros(samples_per_symbol*num_symbols, dtype='complex')
x[::samples_per_symbol] = x_symbols  # insert symbols every sample per symbol
t_x = np.arange(len(x))/Fs

# Shape pulses
rrc, t_rrc, t0 = get_pulse_shaping_kernel(Fs, Ts)
u = np.convolve(x, rrc)
t_u = np.arange(len(u))/Fs

i = u.real
q = u.imag

iup = i * np.cos(2*np.pi*t_u*Fc)
qup = q * -np.sin(2*np.pi*t_u*Fc)
s = iup + qup

#plt.plot(x_symbols.real, x_symbols.imag, '.')
#plt.plot(t[:70], np.real(x)[:70], '-x')

# artificial extra delay for the baseband samples
#plt.plot(((t_x+t0)/Ts)[:3000], x.real[:3000])
#plt.plot((t_u/Ts)[:3000], u.real[:3000])


sine = np.cos(2*np.pi*t_x*Fc)
square = scipy.signal.square(2*np.pi*t_x*Fc)
sig1 = square * sine
sig2 = sine * sine


print(np.var(sig1))
print(np.var(sig2))



plt.subplot(211)
plt.plot(t_x[:30], sig1[:30])

plt.subplot(212)
plt.plot(t_x[:30], sig2[:30])


#plt.plot((t_u/Ts)[:1000], s[:1000])


plt.grid(True)
plt.show()
