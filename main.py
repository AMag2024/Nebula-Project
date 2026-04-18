import matplotlib.pyplot as plt
import numpy as np
import hashlib


user_input = input("Enter a seed phrase or number: ")

hash_bytes = hashlib.md5(user_input.encode()).hexdigest()
seed = int(hash_bytes, 16) % (2**32)
print(f"Your phrase '{user_input}' generated seed: {seed}")


rng = np.random.default_rng(seed)


test_values = rng.uniform(0, 1, size=5)
print(f"Test values: {test_values}")
print("Run again with the same phrase — these numbers should be identical!")