#!/usr/bin/python3

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D


def main():
    fig = plt.figure()
    ax = fig.add_subplot(221)
    ax.set_title("SIN")
    ax.set_xlabel('real')
    ax.set_ylabel('imag')


    f = 10
    p1 = 1j * np.exp(2j*np.pi*f)
    p2 = 1j * np.exp(-2j*np.pi*f)
    p3 = p2 - p1

    print("SIN = %.3f" % (np.sin(2*np.pi*f)))
    print(p3/2)

    V = np.array([p1, p2, p3])
    origin = np.zeros((2, len(V)))

    ax.quiver(*origin, [V.real], [V.imag], color=['black', 'black', 'green'], scale=15)

    ax = fig.add_subplot(223)
    ax.set_title("COS")
    ax.set_xlabel('real')
    ax.set_ylabel('imag')

    p1 = np.exp(2j*np.pi*f)
    p2 = np.exp(-2j*np.pi*f)
    p3 = p1 + p2

    print("COS = %.3f" % (np.cos(2*np.pi*f)))
    print(p3/2)


    V = np.array([p1, p2, p3])
    origin = np.zeros((2, len(V)))

    ax.quiver(*origin, [V.real], [V.imag], color=['black', 'black', 'red'], scale=15)


    ##########
    samp_freq = 50
    f1 = 5
    f2 = 15
    t = np.linspace(0, 1, samp_freq, endpoint=False)
    #
    # Bandpass real signals: cos(f1) + sin(f2)
    #
    signal = \
        np.cos(2*np.pi*t*(f1-1)) + \
        np.cos(2*np.pi*t*(f1-0)) + \
        np.cos(2*np.pi*t*(f1+1)) + \
        \
        np.sin(2*np.pi*t*(f2-1)) + \
        np.sin(2*np.pi*t*(f2-0)) + \
        np.sin(2*np.pi*t*(f2+1))


    signal = \
        np.cos(2*np.pi*t*(f1-0))



    #
    # Complex signal with positive f1 frequency
    #
    if False:
        signal = \
            np.cos(2*np.pi*t*f1) + \
            \
            1j*np.sin(2*np.pi*t*f1)


    #signal = signal * np.exp(-1j*2*np.pi*t*f1)
    signal = signal * np.cos(2*np.pi*t * 2)


    ###
    signal = np.exp(-1j*10*np.pi*t)

    fft = np.fft.fft(signal)
    freq = np.fft.fftfreq(signal.size, d=1./samp_freq)

    X = freq
    Y = np.zeros(len(freq))
    Z = np.zeros(len(freq))

    U = np.zeros(len(freq))
    V = fft.real
    W = fft.imag

    ax = fig.add_subplot(122, projection='3d')
    ax.quiver(X, Y, Z, U, V, W)

    ax.set_title("COS + SIN")
    ax.set_xlabel('freq')
    ax.set_ylabel('real')
    ax.set_zlabel('imag')

    ax.set_xlim3d(-50, 50)
    ax.set_ylim3d(-50, 50)
    ax.set_zlim3d(-50, 50)

    plt.show()

    return


if __name__ == "__main__":
    main()
