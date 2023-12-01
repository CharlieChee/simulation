import sys
import numpy as np
import random
import matplotlib
import matplotlib.pyplot as plt
from matplotlib import colors
import math
import pandas as pd
import simpy
import queue
class packet(object):
    def __init__(self, arrival_time, ident, pktSize):
      global seqno
      seqno += 1
      self.arrival_time = arrival_time
      self.ident = ident
      self.pktSize = pktSize
      self.seqno = seqno

class queueClass(object):
   def __init__(self, env, serviceRate):
    self.env=env
    self.inService=False
    self.buffer = queue.Queue()
    self.serviceRate=serviceRate

   def service(self):
    while not self.buffer.empty():
        p=self.buffer.get()
        self.inService = True
        service_time = p.pktSize/ self.serviceRate
        yield self.env.timeout(service_time)
        response_time = self.env.now - p.arrival_time
        #print(f"Response time for packet from source {p.ident}: {response_time}")
        response_times.append({'source_id': p.ident, 'response_time': response_time})
        self.inService = False


   def reception(self, source ,pkt):
      self.buffer.put(pkt)
      if not self.inService:
        self.env.process(self.service())


class VoiceSource(object):
  def __init__ (self, env, rate, q, ident, pktSize):
    self.env =env
    self.rate= rate
    self.q=q
    self.ident = ident
    self.pktSize =pktSize
    self.action =env.process(self.run())

  def run(self):
    packetspersc=self.rate/self.pktSize
    while True:
      yield self.env.timeout(1 / packetspersc)
      p= packet(self.env.now,self.ident, self.pktSize)
      #print(f"Voice packet generated at {self.env.now}, Source ID: {self.ident}")
      self.q.reception(self, p)


class DataSource(object):
  def __init__ (self, env, rate, q, ident):
    self.env =env
    self.rate= rate
    self.q=q
    self.ident = ident
    self.action =env.process(self.run())

  def run(self):
    while True:
      pktsize = random.choices([400, 4000, 12000], weights=[0.4, 0.3, 0.3])[0]
      packetspersc=self.rate/pktsize
      yield self.env.timeout(np.random.exponential(1 /packetspersc))
      #yield self.env.timeout(1 /packetspersc)
      p= packet(self.env.now,self.ident, pktsize)
      #print(f"Data packet generated at {self.env.now}, Source ID: {self.ident}")
      self.q.reception(self, p)


class BurstySource(object):
    def __init__(self, env, ton, toff, peak_rate, q, ident, pktSize):
        self.env = env
        self.peak_rate = peak_rate
        self.ton = ton
        self.toff = toff
        self.q = q
        self.ident = ident
        self.pktSize = pktSize
        self.action = env.process(self.run())

        self.transition_matrix = np.array([[0, 1],  # State ON always transitions to OFF
                                           [1, 0]])  # State OFF always transitions to ON
        # Start with a random state
        self.current_state = np.random.choice([0, 1])

    def run(self):
        while True:
            # State ON
            if self.current_state == 0:
                on_duration = np.random.exponential(self.ton)
                end_on = self.env.now + on_duration
                while self.env.now < end_on:
                    yield self.env.timeout(1 / (self.peak_rate / self.pktSize))
                    p = packet(self.env.now, self.ident, self.pktSize)
                    self.q.reception(self, p)

            # State OFF
            else:
                off_duration = np.random.exponential(self.toff)
                yield self.env.timeout(off_duration)

            self.current_state = np.random.choice([0, 1], p=self.transition_matrix[self.current_state])


def calculate_ton_toff(b, ton):
    toff = ton * (b - 1)
    return toff
def run_simulation(b_val):
    env= simpy.Environment()
    queue_rate=100e6
    q= queueClass(env, queue_rate)
    response_times = []
    s1 = VoiceSource(env, 20e6, q, 1, 800)  # Voice
    s2 = DataSource(env, 30e6, q, 2)  # Data
    lambda_average=30e6
    pktSize=8000
    ton=0.001
    peak_rate=b_val*lambda_average
    toff=calculate_ton_toff(b_val,ton)
    s3 = BurstySource(env, ton ,toff, peak_rate, q, 3, pktSize)
    env.run(until=simulationDuration)

import math
def compute_block_metrics(re, block_size):
    return [np.mean(re[i:i + block_size]) for i in range(0, len(re), block_size)]
def average_of_squares(Z):
    k = len(Z)
    sum_of_squares = np.sum(np.square(Z))
    return sum_of_squares / k

def compute_confidence_interval(data, T, t):
    num_blocks = int(T / t)
    block_size = max(1, len(data) // num_blocks)
    block_metrics = compute_block_metrics(data, block_size)
    #print (block_metrics)


# Example usage
    sigma=math.sqrt((average_of_squares(block_metrics))-(np.square(np.mean(block_metrics))))
    #sigma_t = np.std(block_metrics)

    # Calculate ε_t for each block
    epsilon_t = 4.5 * sigma
    epsilon_T= (np.sqrt(block_duration/total_duration))* epsilon_t
    # Scale ε_t to compute ε_T for the entire simulation duration T

    mean_response_time = np.mean(data)
    lower_ci = mean_response_time - epsilon_T
    upper_ci = mean_response_time + epsilon_T

    return mean_response_time, (lower_ci, upper_ci)

# Example usage
from datetime import datetime

def save_times_to_txt(b_value, voice_times, data_times, bursty_times):
    # Current time in specified format
    current_time = datetime.now().strftime("%H_%M")

    # File names based on b_value and current time
    voice_filename = f"/Users/jichanglong/Desktop/simulation/data/voice_times_{b_value}.txt"
    data_filename = f"/Users/jichanglong/Desktop/simulation/data/data_times_{b_value}.txt"
    bursty_filename = f"/Users/jichanglong/Desktop/simulation/data/bursty_times_{b_value}.txt"

    # Save each list to a txt file
    with open(voice_filename, 'w') as file:
        file.writelines('\n'.join(map(str, voice_times)))

    with open(data_filename, 'w') as file:
        file.writelines('\n'.join(map(str, data_times)))

    with open(bursty_filename, 'w') as file:
        file.writelines('\n'.join(map(str, bursty_times)))

    return voice_filename, data_filename, bursty_filename

simulationDuration = 1000 # Duration for which to run each simulation
total_duration = simulationDuration  # Total duration of the simulation in seconds or appropriate time unit
block_duration = 10 # Duration of each block in the same time unit

seqno=0
np.random.seed(10)

r=[]

b_values = [20, 30,  40, 50, 60, 70, 80, 90, 100]
#b_values = [1, 2, 3, 4, 5]
for i in b_values:
    response_times = []
    run_simulation(i)
    print(f"Simulation completed for burstiness (b) = {i}")
    voice_times = [i['response_time'] for i in response_times if i['source_id'] == 1]
    data_times = [i['response_time'] for i in response_times if i['source_id'] == 2]
    bursty_times = [i['response_time'] for i in response_times if i['source_id'] == 3]
    voice_file, data_file, bursty_file = save_times_to_txt(i, voice_times, data_times, bursty_times)
    print(f"Saved times to {voice_file}, {data_file}, and {bursty_file}")

