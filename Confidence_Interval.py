import math
import numpy as np
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
    #sigma=math.sqrt((average_of_squares(block_metrics))-(np.square(np.mean(block_metrics))))
    sigma = np.std(block_metrics)

    # Calculate ε_t for each block
    epsilon_t = 4.5 * sigma
    epsilon_T= (np.sqrt(block_duration/total_duration))* epsilon_t
    # Scale ε_t to compute ε_T for the entire simulation duration T

    mean_response_time = np.mean(data)
    lower_ci = mean_response_time - epsilon_t
    upper_ci = mean_response_time + epsilon_t

    return mean_response_time, (lower_ci, upper_ci)

voice_time = {}
for i in range(10):
    with open('/Users/jichanglong/Desktop/simulation/data/voice_times_'+str(i+1)+'.txt', 'r') as file:
        voice_time[i+1] = [float(line.strip()) for line in file]

data_time = {}
for i in range(10):
    with open('/Users/jichanglong/Desktop/simulation/data/data_times_'+str(i+1)+'.txt', 'r') as file:
        data_time[i+1] = [float(line.strip()) for line in file]

bursty_time = {}
for i in range(10):
    with open('/Users/jichanglong/Desktop/simulation/data/bursty_times_'+str(i+1)+'.txt', 'r') as file:
        bursty_time[i+1] = [float(line.strip()) for line in file]

r = []
total_duration = 1000
block_duration = 10
b = [1,2,3,4,5,6,7,8,9,10]
for i in b:
    mean_v, confidence_interval_v = compute_confidence_interval(voice_time[i], total_duration, block_duration)
    mean_d, confidence_interval_d = compute_confidence_interval(data_time[i] , total_duration, block_duration)
    mean_b, confidence_interval_b = compute_confidence_interval(bursty_time[i], total_duration, block_duration)
    r.append({'mean_voice':np.average(voice_time[i]), 'mean_data': np.average(data_time[i]), 'mean_video': np.average(bursty_time[i]),'b value': i+1,'ci_v':confidence_interval_v,'ci_d':confidence_interval_d,'ci_b':confidence_interval_b})


import matplotlib.pyplot as plt

# Extracting data for plotting
b_values = [entry['b value'] for entry in r]
mean_voice = [entry['mean_voice'] for entry in r]
mean_data = [entry['mean_data'] for entry in r]
mean_video = [entry['mean_video'] for entry in r]

# Extracting confidence intervals
ci_v = [entry['ci_v'] for entry in r]
ci_d = [entry['ci_d'] for entry in r]
ci_b = [entry['ci_b'] for entry in r]

# Calculating the errors for the confidence intervals
errors_voice = [(mean - ci[0], ci[1] - mean) for mean, ci in zip(mean_voice, ci_v)]
errors_data = [(mean - ci[0], ci[1] - mean) for mean, ci in zip(mean_data, ci_d)]
errors_video = [(mean - ci[0], ci[1] - mean) for mean, ci in zip(mean_video, ci_b)]

# Separating lower and upper errors for plotting
errors_voice_lower, errors_voice_upper = zip(*errors_voice)
errors_data_lower, errors_data_upper = zip(*errors_data)
errors_video_lower, errors_video_upper = zip(*errors_video)

# Plotting with error bars
plt.figure(figsize=(10, 6))
# Bursty (Video)
lower_video, upper_video = zip(*ci_b)
plt.fill_between(b_values, lower_video, upper_video, color='red', alpha=0.2)
plt.plot([i-1 for i in b_values], mean_video, label='Bursty (Video)', marker='o', color='red')

# Voice
lower_voice, upper_voice = zip(*ci_v)
plt.fill_between(b_values, lower_voice, upper_voice, color='blue', alpha=0.2)
plt.plot([i-1 for i in b_values], mean_voice, label='Voice', marker='o', color='blue')
lower_data, upper_data = zip(*ci_d)
plt.fill_between(b_values, lower_data, upper_data, color='green', alpha=0.2)
plt.plot([i-1 for i in b_values], mean_data, label='Data', marker='o', color='green')



plt.xlabel('Burstiness (b value)')
plt.ylabel('Average Response Time')
plt.title('Average Response Time vs Burstiness for Voice Source')
plt.legend()
plt.grid(True)
plt.show()