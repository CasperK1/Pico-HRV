from filefifo import Filefifo

data = Filefifo(10, name='exercises/capture_250Hz_01.txt')

prev = data.get()
curr = data.get()
peaks = []
sample_count = 0

# First 4 peaks to get 3 intervals
while len(peaks) < 4:
    next_val = data.get()
    sample_count += 1

    # Calculate slopes
    curr_slope = curr - prev
    next_slope = next_val - curr

    # Peak is where slope changes from positive to negative
    if curr_slope > 0 and next_slope <= 0:
        peaks.append(sample_count)

    prev = curr
    curr = next_val

print(f"First 4 peaks at lines {peaks}\n")
# Calculate intervals
for i in range(len(peaks) - 1):
    # Get difference between consecutive peaks
    interval = peaks[i+1] - peaks[i]
    seconds = interval / 250
    freq = 1 / seconds
    print(f"Interval {i+1}: {interval} samples = {seconds:.4f}s")
    print(f"Frequency: {freq:.5f} Hz\n")
