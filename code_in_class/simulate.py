import sys
import numpy as np
import simpy

# Simulation duration and parameters
simulationDuration = 10000000.0
D = 100e6  # constant bit rate in bps
T_on_video = 10e-3  # average duration of "ON" for video in seconds
np.random.seed(10)

class QueueClass(object):
    def __init__(self, env, queueCapa, serviceRate):
        self.env = env
        self.inService = 0
        self.queueLength = 0
        self.queueCapacity = queueCapa
        self.serviceRate = serviceRate

    def service(self):
        self.inService = 1
        yield self.env.timeout(np.random.exponential(1.0/self.serviceRate))
        self.queueLength -= 1
        if self.queueLength > 0:
            self.env.process(self.service())
        else:
            self.inService = 0

    def reception(self, source):
        if self.queueLength + 1 <= self.queueCapacity:
            self.queueLength += 1
            if self.inService == 0:
                self.env.process(self.service())
        else:
            source.queueLosses += 1

class PoissonSource(object):
    def __init__(self, env, rate, q, traffic_type="data"):
        self.env = env
        self.rate = rate
        self.q = q  # the queue
        self.traffic_type = traffic_type
        self.nbEmissions = 0
        self.queueLosses = 0
        self.action = env.process(self.run())

    def generate_packet_length(self):
        if self.traffic_type == "data":
            return np.random.choice([400, 4000, 15000], p=[0.4, 0.3, 0.3])
        elif self.traffic_type == "voice":
            return 800
        elif self.traffic_type == "video":
            on_duration = np.random.exponential(T_on_video)
            video_packet_size = 8000  # 1000 bytes
            n_on_packets = int(on_duration * D / video_packet_size)
            return video_packet_size if n_on_packets else 0
        else:
            return 0

    def run(self):
        while True:
            packet_length = self.generate_packet_length()
            service_rate = D / packet_length if packet_length != 0 else 1
            self.q.serviceRate = service_rate
            yield self.env.timeout(np.random.exponential(scale=1.0/self.rate))
            self.nbEmissions += 1
            self.q.reception(self)

env = simpy.Environment()

# Data traffic
q_data = QueueClass(env, 10000, D/np.mean([400, 4000, 15000]))
ps_data = PoissonSource(env, 0.9, q_data, "data")

# Voice traffic
q_voice = QueueClass(env, 10000, D/800)
ps_voice = PoissonSource(env, 0.9, q_voice, "voice")

# Video traffic
q_video = QueueClass(env, 10000, D/8000)
ps_video = PoissonSource(env, 0.9, q_video, "video")

env.run(until=simulationDuration)

print("Data loss rate:", ps_data.queueLosses * 1.0 / ps_data.nbEmissions)
print("Voice loss rate:", ps_voice.queueLosses * 1.0 / ps_voice.nbEmissions)
print("Video loss rate:", ps_video.queueLosses * 1.0 / ps_video.nbEmissions)
