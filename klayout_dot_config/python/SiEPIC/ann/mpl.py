
# Enter your Python code here

def plot():
    import matplotlib.pyplot as plt
    import numpy as np
    
    x = np.linspace(0, 2 * np.pi, 20)
    y = np.sin(x)
    yp = None
    xi = np.linspace(x[0], x[-1], 100)
    yi = np.interp(xi, x, y, yp)
    
    fig, ax = plt.subplots()
    ax.plot(x, y, 'o', xi, yi, '.')
    plt.show()
    print("Preparing to save figure...")
    plt.savefig('foo.png', bbox_inches='tight')