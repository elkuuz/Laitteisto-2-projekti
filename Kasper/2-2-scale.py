from filefifo import Filefifo # type: ignore

# Initialize Filefifo with the data file
data = Filefifo(10, name='sample_data/capture_250Hz_01.txt')

# First pass: find min and max values in the first 2 seconds (500 samples)
sample_count = 250 * 2  # 2 seconds of data at 250Hz
min_val = float('inf')
max_val = float('-inf')

for _ in range(sample_count):
    value = data.get()
    if value < min_val:
        min_val = value
    if value > max_val:
        max_val = value

print(f"Found min: {min_val}, max: {max_val}")

# Reset the filefifo to start from beginning
data = Filefifo(10, name='sample_data/capture_250Hz_01.txt')

# Second pass: scale and print data for 10 seconds (2500 samples)
sample_count = 250 * 10  # 10 seconds of data at 250Hz
value_range = max_val - min_val

for _ in range(sample_count):
    value = data.get()
    # Scale to 0-100 range
    scaled_value = ((value - min_val) / value_range) * 100
    print(scaled_value)