import array

class Filefifo:
    def __init__(self, dummy, filename):
        self.filename = filename
        self.data = self._read_file()
        self.index = 0

    def _read_file(self):
        with open(self.filename, 'r') as f:
            return array.array('f', map(float, f.readlines()))

    def read(self, num_samples):
        samples = array.array('f')
        for _ in range(num_samples):
            samples.append(self.data[self.index])
            self.index = (self.index + 1) % len(self.data)
        return samples

# Initialize Filefifo and read data
fifo = Filefifo(10, 'capture_250Hz_01.txt')
sampling_rate = 250  # samples per second

# Read two seconds of data
num_samples = 2 * sampling_rate
signal = fifo.read(num_samples)

# Find minimum and maximum values
min_val = min(signal)
max_val = max(signal)

# Scale the data to range 0 – 100
def scale_value(value, min_val, max_val):
    return (value - min_val) / (max_val - min_val) * 100

scaled_signal = array.array('f', (scale_value(val, min_val, max_val) for val in signal))

# Print scaled values to console
for val in scaled_signal:
    print(val)

# Read and scale 10 seconds of data for plotting
num_samples = 10 * sampling_rate
signal = fifo.read(num_samples)
scaled_signal = array.array('f', (scale_value(val, min_val, max_val) for val in signal))

# Print scaled values for plotting
for val in scaled_signal:
    print(val)