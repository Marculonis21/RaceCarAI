#!/usr/bin/env python

import sys
import numpy as np 
import matplotlib.pyplot as plt

assert len(sys.argv) == 3

def moving_average(x, w):
    return np.convolve(x, np.ones(w), 'valid') / w

print(sys.argv[1])
data = np.load(sys.argv[1])
print(data.shape)


if sys.argv[2] == "GA":
    maxes = []
    avgs = []
    for run in range(data.shape[0]):
        run_data = data[run]
        maxes.append(np.max(run_data, axis=1))
        avgs.append(np.mean(run_data, axis=1))

    max_means = np.mean(maxes, axis=0)
    max_max = np.max(maxes, axis=0)
    m_q25 = np.percentile(maxes, q=25, axis=0)
    m_q75 = np.percentile(maxes, q=75, axis=0)

    avg_means = np.mean(avgs, axis=0)
    a_q25 = np.percentile(avgs, q=25, axis=0)
    a_q75 = np.percentile(avgs, q=75, axis=0)

    plt.plot(np.arange(max_means.shape[0]), max_means, label="max-mean")
    plt.fill_between(np.arange(m_q25.shape[0]),m_q25,m_q75,alpha=0.25)

    plt.plot(np.arange(avg_means.shape[0]), avg_means, label="avg-mean")
    plt.fill_between(np.arange(a_q25.shape[0]),a_q25,a_q75,alpha=0.25)

    plt.plot(np.arange(max_max.shape[0]), max_max, label="max-max")

if sys.argv[2] == "DDPG":
    r_max_max10 = moving_average(np.max(data, axis=0),10)
    r_max_means = moving_average(np.mean(data, axis=0),10)
    max_means = np.mean(data, axis=0)
    q25 = np.percentile(data, q=25, axis=0)
    q75 = np.percentile(data, q=75, axis=0)

    plt.plot(np.arange(r_max_means.shape[0]), r_max_means, label="max-mean rolling average")
    plt.plot(np.arange(r_max_max10.shape[0]), r_max_max10, label = "max-max rolling average")
    plt.fill_between(np.arange(q25.shape[0]),q25,q75,alpha=0.25)
    plt.axvline(x = 346, color = 'black', label = 'noise decay - halflife')

plt.xlabel("Gens/Runs")
plt.ylabel("Fitness")
plt.tight_layout()
plt.legend()
plt.show()
