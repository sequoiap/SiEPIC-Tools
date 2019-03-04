# Here are the steps for using pyplot instead of the wrapped Graph class
import matplotlib
matplotlib.use('tkagg')
import matplotlib.pyplot as plt

fig, ax = plt.subplots()
ax.plot([1,3,3,7,5])
ax.plot([2,2,5,1,4])

plt.show()