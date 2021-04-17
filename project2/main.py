import matplotlib.pyplot as plt
import numpy as np

with open("results_home.txt") as file:
    x_5 = []
    y_5 = []
    x_4 = []
    y_4 = []
    x_3 = []
    y_3 = []
    prev_k = -1
    curr_x = None
    curr_y = None
    for row in file:
        n, k, r, prob, runtime = list(map(float, row.split()))
        if k != prev_k:
            prev_k = k
            if prev_k == 3:
                curr_x = x_3
                curr_y = y_3
            elif prev_k == 4:
                curr_x = x_4
                curr_y = y_4
            elif prev_k == 5:
                curr_x = x_5
                curr_y = y_5
        curr_y.append(runtime)
        curr_x.append(r)

fig, (ax1, ax2, ax3) = plt.subplots(3, 1)
fig.suptitle("Comparison")

ax1.plot(x_3, y_3, '.-')
ax1.set_xlabel('r')
ax1.set_ylabel('Runtime (s), k=3')

ax2.plot(x_4, y_4, '.-')
ax2.set_xlabel('r')
ax2.set_ylabel('Runtime (s), k=4')

ax3.plot(x_5, y_5, ".-")
ax3.set_xlabel('r')
ax3.set_ylabel('Runtime (s), k=5')

# plt.show()
plt.savefig("image_runtime.png")

