import os
fs_stat = os.statvfs('/')
print("Free space (bytes):", fs_stat[0] * fs_stat[3])  # Block size * Free blocks
