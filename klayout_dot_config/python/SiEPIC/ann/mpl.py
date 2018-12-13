
# Enter your Python code here
import os

def plot():
    import matplotlib.pyplot as plt
    from matplotlib.figure import Figure
    import numpy as np
    
    x = np.linspace(0, 2 * np.pi, 20)
    y = np.sin(x)
    yp = None
    xi = np.linspace(x[0], x[-1], 100)
    yi = np.interp(xi, x, y, yp)
    #plt.figure(figsize=(800/my_dpi, 800/my_dpi))
    fig, ax = plt.subplots()
    ax.plot(x, y, 'o', xi, yi, '.')
    print("Preparing to save figure...")
    wd = os.getcwd()
    temppath = os.path.join(os.path.dirname(os.path.realpath(__file__)), "temp")
    print(wd)
    print(temppath)
    os.chdir(temppath)
    plt.savefig('foo.png', bbox_inches='tight')
    os.chdir(wd)
    print(os.getcwd())
    
if __name__ == "__main__":
    plot()