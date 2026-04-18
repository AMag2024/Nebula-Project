import matplotlib.pyplot as plt
import numpy as np
import hashlib


plt.style.use('darl_background')
fig, ax = plt.subplots()


user_input = input("Enter a seed phrase or number: ")


#seed system
hash_bytes = hashlib.md5(user_input.encode()).hexdigest()
seed = int(hash_bytes, 16) % (2**32)
print(f"Your phrase '{user_input}' generated seed: {seed}")


rng = np.random.default_rng(seed)


test_values = rng.uniform(0, 1, size=5)
print(f"Test values: {test_values}")
print("Run again with the same phrase — these numbers should be identical!")
print("Hoshi is also a fat baby bird")