from filefifo import Filefifo

data = Filefifo(10, name='capture_250Hz_01.txt')

# Get first samples
prev = data.get()
curr = data.get()

peaks = []
sample_count = 0

# First 4 peaks to get 3 intervals
while len(peaks) < 4:
    next_val = data.get()
    sample_count += 1
    
    # using >= when there is identical peak value at multiple lines
    if curr >= prev and curr > next_val:
        peaks.append(sample_count)
        
    prev = curr
    curr = next_val
    
    
print(f"First 4 peaks at lines {peaks}\n")

# Calculate intervals
for i in range(len(peaks) - 1): 
    interval = peaks[i+1] - peaks[i]  # Get difference between consecutive peaks
    seconds = interval / 250
    freq = 1 / seconds
    print(f"Interval {i+1}: {interval} samples = {seconds:.4f}s")
    print(f"Frequency: {freq:.5f} Hz\n")