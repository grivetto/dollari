import matplotlib.pyplot as plt
import os
fig, ax = plt.subplots()
ax.plot([1, 2, 3], [1, 2, 3])
ax.set_title("Profit Chart (Mock)")
plt.savefig("/home/sergio/.openclaw/workspace/denaro/profit_chart.png")
