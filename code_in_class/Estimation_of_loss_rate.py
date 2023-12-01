import sys
import numpy as np
import random
import matplotlib.pyplot as plt
import simpy
import queue
import pandas as pd

simulationDuration = 1000
periodPrintLR = 10
df_lossRates = pd.DataFrame(columns=['sourceId', 'time', 'lossRate'])
seqno = 0
np.random.seed(10)

def printLossRate(env, source):
    global df_lossRates
    source.cpterPrintLR += 1
    if source.cpterPrintLR == periodPrintLR:
        source.cpterPrintLR = 0
        df_lossRates.loc[len(df_lossRates)] = {'sourceId': source.ident, 'time': env.now, 'lossRate': source.queueLosses/source.nbEmissions}

class packet(object):
    def __init__(self, t, ident, pktSize):
        global seqno
        seqno += 1
        self.t = t
        self.ident = ident
        self.pktSize = pktSize
        self.seqno = seqno

class queueClass(object):
    def __init__(self, env, queueCapa, serviceRate):
        self.env = env
        self.inService = 0
        self.buffer = queue.Queue(maxsize=queueCapa)
        self.queueLength = 0
        self.queueCapacity = queueCapa
        self.serviceRate = serviceRate
        self.lastChange = 0
        self.cpterPrintLR = 0

    def service(self):
        p = self.buffer.get()
        self.queueLength -= p.pktSize
        yield self.env.timeout(1/self.serviceRate)
        self.inService = 0
        if self.queueLength > 0:
            self.env.process(self.service())

    def reception(self, source, pkt):
        if self.queueLength + pkt.pktSize <= self.queueCapacity:
            self.queueLength += pkt.pktSize
            self.buffer.put(pkt)
            if self.inService == 0:
                self.inService = 1
                self.env.process(self.service())
        else:
            source.queueLosses += 1
            printLossRate(self.env, source)

class poissonSource(object):
    def __init__(self, env, rate, q, ident, pktSize):
        self.env = env
        self.rate = rate
        self.q = q
        self.ident = ident
        self.pktSize = pktSize
        self.nbEmissions = 0
        self.queueLosses = 0
        self.cpterPrintLR = 0
        self.action = env.process(self.run())

    def run(self):
        while True:
            yield self.env.timeout(-np.log(1.0 - np.random.rand()) / self.rate)
            self.nbEmissions += 1
            p = packet(self.env.now, self.ident, self.pktSize)
            self.q.reception(self, p)

env = simpy.Environment()
q = queueClass(env, 1, 1.0)
ps1 = poissonSource(env, 0.8, q, 1, 1)
env.run(until=simulationDuration)

plt.plot(df_lossRates[df_lossRates['sourceId'] == 1]['time'], df_lossRates[df_lossRates['sourceId'] == 1]['lossRate'], linewidth=1, label='Source 1')
plt.grid(True, which="both", linestyle='--')
plt.ylim(ymin=0)
plt.ylabel('Loss rate')
plt.xlabel('Time units')
plt.title('Loss rate in function of the time')
plt.legend()
plt.show()
