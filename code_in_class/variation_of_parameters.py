import simpy
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import queue

# Parameters
simulationDuration = 1000
queueCapacity = 1
serviceRate = 1
df_lossRates = pd.DataFrame(columns=['sourceId', 'time', 'lossRate', 'CI_lower', 'CI_upper']) # 添加了'CI_lower'和'CI_upper'

Z = 1.96  # for a 95% confidence interval

class Packet(object):
    seqno = 0

    def __init__(self, t, ident, pktSize):
        Packet.seqno += 1
        self.t = t
        self.ident = ident
        self.pktSize = pktSize
        self.seqno = Packet.seqno


class DeterministicQueue(object):
    def __init__(self, env, queueCapa, serviceTime):
        self.env = env
        self.inService = 0
        self.buffer = queue.Queue(maxsize=queueCapa)
        self.queueLength = 0
        self.queueCapacity = queueCapa
        self.serviceTime = serviceTime

    def service(self):
        p = self.buffer.get()
        self.queueLength -= p.pktSize
        yield self.env.timeout(self.serviceTime)
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


class PoissonSource(object):
    def __init__(self, env, rate, q, ident, pktSize):
        self.env = env
        self.rate = rate
        self.q = q
        self.ident = ident
        self.pktSize = pktSize
        self.nbEmissions = 0
        self.queueLosses = 0
        self.action = env.process(self.run())

    def run(self):
        while True:
            yield self.env.timeout(-np.log(1.0 - np.random.rand()) / self.rate)
            self.nbEmissions += 1
            p = Packet(self.env.now, self.ident, self.pktSize)
            self.q.reception(self, p)
            loss_rate = self.queueLosses / self.nbEmissions
            SE = np.sqrt(loss_rate * (1 - loss_rate) / self.nbEmissions)
            CI_lower = loss_rate - Z * SE
            CI_upper = loss_rate + Z * SE
            df_lossRates.loc[len(df_lossRates)] = {
                'sourceId': self.ident,
                'time': self.env.now,
                'lossRate': loss_rate,
                'CI_lower': CI_lower,
                'CI_upper': CI_upper
            }
env = simpy.Environment()
q = DeterministicQueue(env, queueCapacity, 1 / serviceRate)  # using deterministic service time
ps1 = PoissonSource(env, 0.1, q, 1, 1)
ps2 = PoissonSource(env, 0.7, q, 2, 1)
env.run(until=simulationDuration)

plt.figure(figsize=(10,6))

# Plotting the loss rates for Source 1
source1_data = df_lossRates[df_lossRates['sourceId'] == 1]
plt.plot(source1_data['time'], source1_data['lossRate'], linewidth=1, label='Source 1')
plt.fill_between(source1_data['time'], source1_data['CI_lower'], source1_data['CI_upper'], alpha=0.2)

# Plotting the loss rates for Source 2
source2_data = df_lossRates[df_lossRates['sourceId'] == 2]
plt.plot(source2_data['time'], source2_data['lossRate'], linewidth=1, label='Source 2')
plt.fill_between(source2_data['time'], source2_data['CI_lower'], source2_data['CI_upper'], alpha=0.2)

plt.grid(True, which="both", linestyle='--')
plt.ylim(ymin=0)
plt.ylabel('Loss rate')
plt.xlabel('Time units')
plt.title('Loss rate in function of the time with Deterministic Service Time and Two Sources')
plt.legend()
plt.show()