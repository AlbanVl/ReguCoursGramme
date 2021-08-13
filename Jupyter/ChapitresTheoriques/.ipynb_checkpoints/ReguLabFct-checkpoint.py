# -*- coding: utf-8 -*-
"""
Created on Tue May 11 10:23:05 2021

Fonctions utiles pour utiliser python en régu

@author: Alban Van Laethem
"""

from control.matlab import *
import control.nichols as cn
import numpy as np
import matplotlib.pyplot as plt
import scipy as sp
import math
from matplotlib.offsetbox import AnchoredText # To print text inside a plot

# =============================================================================
# Objet pour contenir toutes les infos importantes provenant du step
# =============================================================================
class info():
    RiseTime = None
    SettlingTime = None
    SettlingMin = None
    SettlingMax = None
    Overshoot = None
    Undershoot = None
    Peak = None
    PeakTime = None    
    RiseTime = None
    DCGain = None

#%% Fonction stepWithInfo
# Fonction qui trace le step et les points intéressants tout en renvoyant ces infos importantes.
# ATTENTION! Overshoot en %
# Objet info pour stocker les différentes infos importantes

def stepWithInfo(sys, info, settlingTimeWithin=0.05, RiseTimeThresholdMin=.10, RiseTimeThresholdMax=.90, resolution = 10000, NameOfFigure = "", sysName = '', linestyle='-'):
    [yout, t] = step_(sys, resolution, NameOfFigure, sysName, linestyle=linestyle)
    step_info(t,yout, info, settlingTimeWithin, RiseTimeThresholdMin, RiseTimeThresholdMax) # Rajoute les points intéressants au graphe
    
#%% Fonction pour tracer les résultats du step
def step_(sys, resolution = 10000, NameOfFigure = "", sysName = '', linestyle='-'):
    if NameOfFigure == "" :
        plt.figure()
    else:
        plt.figure(NameOfFigure)
    [yout, t] = step(sys)
    [yout, t] = step(sys, np.linspace(t[0], t[-1], resolution)) # Pour modifier la résolution
    
    # Arrondi les valeurs à x décimales
    yout = np.around(yout, decimals=6)
    t = np.around(t, decimals=6)
        
    plt.plot(t, yout, label=sysName, linestyle=linestyle)
    plt.title("Step Response")
    plt.ylabel("Amplitude")
    plt.xlabel("Time (seconds)")
    if sysName != '':
        plt.legend()
    
    return [yout, t]

#%% Fonction step_info
def step_info(t, yout, info, settlingTimeWithin=0.05, RiseTimeThresholdMin=.10, RiseTimeThresholdMax=.90):
    # Calcul du dépassement en prenant la valeur max retourné par step et en la divisant par la valeur finale
    osIndice = np.where(yout == np.amax(yout)) # renvoie un tuple d'array
    osIndice = osIndice[-1][-1] # Pour avoir le dernier indice répondant à la condition
    plt.plot(t[osIndice], yout[osIndice],'ko')
    plt.plot([t[osIndice], t[osIndice]], [0, yout[osIndice]], 'k-.', linewidth=0.5) # Vertical
    plt.plot([t[0], t[osIndice]], [yout[osIndice], yout[osIndice]], 'k-.', linewidth=0.5) # Horizontale
    info.Peak = yout.max()
    info.Overshoot = (yout.max()/yout[-1]-1)*100
    info.PeakTime = float(t[osIndice])
    #print ("Overshoot:", info.Overshoot)
    
    # Calcul du temps de montée en fonction du treshold (par défaut: de 10% à 90% de la valeur finale)
    RiseTimeThresholdMinIndice = next(i for i in range(0,len(yout)-1) if yout[i]>yout[-1]*RiseTimeThresholdMin)
    RiseTimeThresholdMaxIndice = next(i for i in range(0,len(yout)-1) if yout[i]>yout[-1]*RiseTimeThresholdMax)
    
    RiseTimeThreshold = [None] * 2
    RiseTimeThreshold[0] = t[RiseTimeThresholdMinIndice]-t[0]
    RiseTimeThreshold[1] = t[RiseTimeThresholdMaxIndice]-t[0]
    info.RiseTime = RiseTimeThreshold[1] - RiseTimeThreshold[0]
    #print ("RiseTime:", info.RiseTime)
    
    plt.plot(t[RiseTimeThresholdMaxIndice], yout[RiseTimeThresholdMaxIndice],'ko')
    plt.plot([t[RiseTimeThresholdMinIndice], t[RiseTimeThresholdMinIndice]], [0, yout[RiseTimeThresholdMaxIndice]], 'k-.', linewidth=0.5) # Limite gauche
    plt.plot([t[RiseTimeThresholdMaxIndice], t[RiseTimeThresholdMaxIndice]], [0, yout[RiseTimeThresholdMaxIndice]], 'k-.', linewidth=0.5) # Limite droite
    plt.plot([t[0], t[RiseTimeThresholdMaxIndice]], [yout[RiseTimeThresholdMaxIndice], yout[RiseTimeThresholdMaxIndice]], 'k-.', linewidth=0.5) # Limite horizontale
    
    
    # Calcul du temps de réponse à x% (5% par défaut)
    settlingTimeIndice = next(i for i in range(len(yout)-1, 1, -1) if abs(yout[i]/yout[-1])>(1+settlingTimeWithin) or abs(yout[i]/yout[-1])<(1-settlingTimeWithin))
    info.SettlingTime= t[settlingTimeIndice]-t[0]
    #print ("SettlingTime:", info.SettlingTime)
    
    plt.plot(t[settlingTimeIndice], yout[settlingTimeIndice],'ko')
    plt.plot([0, max(t)], [yout[-1]*(1+settlingTimeWithin), yout[-1]*(1+settlingTimeWithin)], 'k-.', linewidth=0.5) # Limite haute
    plt.plot([0, max(t)], [yout[-1]*(1-settlingTimeWithin), yout[-1]*(1-settlingTimeWithin)], 'k-.', linewidth=0.5) # Limite basse
    plt.plot([t[settlingTimeIndice], t[settlingTimeIndice]], [0, yout[settlingTimeIndice]], 'k-.', linewidth=0.5) # Vertical
    
    # Traçage du gain statique
    info.DCGain = yout[-1]
    plt.plot(t[-1], yout[-1],'ko')
    plt.plot([0, max(t)], [yout[-1], yout[-1]], 'k:', linewidth=0.5)
    #print ("DC gain:", info.DCGain)
    
#%% Recherche du gain et de la fréquence à une certaine phase

# =============================================================================
# Get the values of the gain and the frequency at a given phase of the system.
# 
# Get the values of the gain and the frequency at a given phase from given arrays of gains, phases and frequencies.
#
# Parameters:
#     * sys (LTI) - System analysed
#     * phaseValue (float) - Phase at which we want to get the gain and frequency values
#     * mag (1D array) - Array of gains (not in dB)
#     * phase (1D array) - Array of phases
#     * omega (1D array) - Array of frequencies (in radians)
#     * printValue (boolean) - print values if True (by default)
#     
# Returns:
#     * mag (float) - The gain value for the given phase
#     * omega (float) - The gain value in rad/sec for the given phase
# =============================================================================
    
def getValues(sys, phaseValue, mag = None, phase = None, omega = None, printValue = True, NameOfFigure = ""):
    lowLimit = -2
    highLimit = 2
    if NameOfFigure == "" :
        plt.figure()
    else:
        plt.figure(NameOfFigure)
    
    if(np.all(mag == None) and np.all(phase == None) and np.all(omega == None)):
        w = np.logspace(lowLimit, highLimit, 10000) # liste de fréquences afin d'augmenter la résolution de calcul (par défaut: 50 éléments)
        mag, phase, omega = bode(sys, w, dB = True, Hz = False, deg = True)
        phase = phase*180/math.pi # Pour avoir les phases en degrés plutôt qu'en radians
        idx = (np.abs(phase-phaseValue)).argmin()
        while idx == np.size(phase)-1 or idx == 0:
            if idx == 0:
                lowLimit-=1
            else:
                highLimit+=1
            w = np.logspace(lowLimit, highLimit, 10000) # liste de fréquences afin d'augmenter la résolution de calcul (par défaut: 50 éléments)
            mag, phase, omega = bode(sys, w, dB = True, Hz = False, deg = True)
            phase = phase*180/math.pi # Pour avoir les phases en degrés plutôt qu'en radians
            idx = (np.abs(phase-phaseValue)).argmin()
            
    else:
        phase = phase*180/math.pi # Pour avoir les phases en degrés plutôt qu'en radians
        idx = (np.abs(phase-phaseValue)).argmin()
    
    if printValue:
        mag_dB = 20*np.log10(mag[idx]) # Pour avoir les gains en dB
        print(f"Gain à {phaseValue}° = {mag_dB} dB")
        print(f"Fréquence à {phaseValue}° = {omega[idx]} rad/sec")
    
    return mag[idx], omega[idx]

#%% Compute reasonable defaults for axes
def default_frequency_range(syslist):
    """Compute a reasonable default frequency range for frequency
    domain plots.
    Finds a reasonable default frequency range by examining the features
    (poles and zeros) of the systems in syslist.
    Parameters
    ----------
    syslist : list of Lti
        List of linear input/output systems (single system is OK)
    Returns
    -------
    omega : array
        Range of frequencies in rad/sec
    Examples
    --------
    >>> from matlab import ss
    >>> sys = ss("1. -2; 3. -4", "5.; 7", "6. 8", "9.")
    >>> omega = default_frequency_range(sys)
    """
    # This code looks at the poles and zeros of all of the systems that
    # we are plotting and sets the frequency range to be one decade above
    # and below the min and max feature frequencies, rounded to the nearest
    # integer.  It excludes poles and zeros at the origin.  If no features
    # are found, it turns logspace(-1, 1)
    
    # Find the list of all poles and zeros in the systems
    features = np.array(())
    
    # detect if single sys passed by checking if it is sequence-like
    if (not getattr(syslist, '__iter__', False)):
        syslist = (syslist,)

    for sys in syslist:
        try:
            # Add new features to the list
            features = np.concatenate((features, np.abs(sys.pole())))
            features = np.concatenate((features, np.abs(sys.zero())))
        except:
            pass

    # Get rid of poles and zeros at the origin
    features = features[features != 0];

    # Make sure there is at least one point in the range
    if (features.shape[0] == 0): features = [1];

    # Take the log of the features
    features = np.log10(features)

    #! TODO: Add a check in discrete case to make sure we don't get aliasing
                        
    # Set the range to be an order of magnitude beyond any features
    omega = sp.logspace(np.floor(np.min(features))-1, 
                        np.ceil(np.max(features))+1)   

    return omega

#%% Fonction to trace Nichols as needed for the laboratory
# Nichols reviewed by Alban Van Laethem
def nichols(sys_list, omega=None, grid=None, labels=[''], NameOfFigure = "", data = False, fig = None, ax = None, linestyle='-'):
    """Nichols plot for a system

    Plots a Nichols plot for the system over a (optional) frequency range.

    Parameters
    ----------
    sys_list : list of LTI, or LTI
        List of linear input/output systems (single system is OK)
    omega : array_like
        Range of frequencies (list or bounds) in rad/sec
    grid : boolean, optional
        True if the plot should include a Nichols-chart grid. Default is True.
    data : boolean, optional
        True if we must return x and y
    ax : axes.subplots.AxesSubplot
        The axe on which to plot
    linestyle : -. , -- , : , - (default)
        The style of the plot line

    Returns
    -------
    if data == True:
        x : 1D array
            Abscisse vector
        y : 1D array
            Ordinate vector
        
    """
    # Open a figure with the given name or open a new one
    if NameOfFigure == "" :
        plt.figure()
    else:
        plt.figure(NameOfFigure)
    
    ax = ax or plt.gca()
    
    # Get parameter values
    #grid = config._get_param('nichols', 'grid', grid, True)


    # If argument was a singleton, turn it into a list
    if not getattr(sys_list, '__iter__', False):
        sys_list = (sys_list,)

    # Select a default range if none is provided
    if omega is None:
        omega = default_frequency_range(sys_list)

    for id, sys in enumerate(sys_list):
        # Get the magnitude and phase of the system
        mag_tmp, phase_tmp, omega = sys.freqresp(omega)
        mag = np.squeeze(mag_tmp)
        phase = np.squeeze(phase_tmp)

        # Convert to Nichols-plot format (phase in degrees,
        # and magnitude in dB)
        x = unwrap(sp.degrees(phase), 360)
        y = 20*sp.log10(mag)

        # Generate the plot
        if labels != ['']:
            ax.plot(x, y, label=labels[id], linestyle=linestyle)
        else:
            ax.plot(x, y, linestyle=linestyle)

    ax.set_xlabel('Phase (deg)')
    ax.set_ylabel('Magnitude (dB)')
    ax.set_title('Nichols Plot')

    # Mark the -180 point
    ax.plot([-180], [0], 'r+', label='_nolegend_')

    # Add grid
    if grid:
        nichols_grid()
        
    # Add legend
    if labels != ['']:
        plt.legend()
    
    if data == True:
        return x, y

#%% Fonction pour générer une ft de second ordre à partir de ses caractéristiques typiques
def generateTfFromCharac(G, wn, dzeta):
    ft = tf([G], [1/wn**2, 2*dzeta/wn, 1])
    return ft

#%% Fonction permettant d'ajouter du bruit à une fonction donnée
def addNoise(t, signal, variance=0.05, rndNb=None):
    """
    Add noise to a given signal

    Parameters
    ----------
    t : 1D array
        Time vector.
    signal : 1D array
        Signal at which to add noise.
    variance : float, optional
        Variance of random numbers. The default is 0.05.
    rndNb : int, optional
        Seed for RandomState. The default is None.

    Returns
    -------
    signal_noisy : 1D array
        Noisy signal.

    """
    if(rndNb!=None):
        np.random.seed(rndNb) # To master the random numbers
    noise = np.random.normal(0, variance, len(signal))
    signal_noisy = signal + noise
    
    plt.figure()
    plt.plot(t, signal, label="Original")
    plt.plot(t, signal_noisy, label="With noise")
    
    return signal_noisy

#%% Save data into a csv file
# =============================================================================
# Save the data of the transfert function into a csv file
# 
# Parameters:
#     * t (1D array) - Time vector
#     * y (1D array) - Response of the system 
#     * x (1D array, optional) - Input of the system(default = [0, 1, ..., 1])
#     
# Returns:
# =============================================================================
def saveFT(t, y, x=None, name="data"):
    if x == None:
        x = np.ones(len(t))
        x[0] = 0
    np.savetxt(name + ".csv",  
                np.transpose([t, x, y]), 
                delimiter =",",  
                fmt ='%s',
                header='Temps(s),Consigne,Mesure', 
                comments='') 

#%% Load data from a csv file
# =============================================================================
# Load the data of the transfert function from a given csv file
# 
# Parameters:
#     * file (String) - File name
#     
# Returns:
#     * t (1D array) - Time vector
#     * x (1D array) - Input of the system 
#     * y (1D array) - Response of the system 
# =============================================================================
def loadFT(file="data.csv"):
    # Reading of the data headers with a comma as delimiter
    head = np.loadtxt(file, delimiter=',', max_rows=1, dtype=np.str)
    # Reading of the data
    data = np.loadtxt(file, delimiter=',', skiprows=1, dtype=np.str)
    
    # Printing of the headers
    print(head)
    
    # Data selections based on header and convert to float
    # The sign - adapts the input data to be positive
    t = np.asarray(data[:, 0], dtype=np.float, order='C').flatten()
    x = np.asarray(data[:, 1], dtype=np.float, order='C').flatten()
    y = np.asarray(data[:, 2], dtype=np.float, order='C').flatten()
    
    return [t, x, y]

#%%
# =============================================================================
# Get the class of the system
# 
# Parameters:
#     * sys (LTI) - System analysed
#     
# Returns:
#     * sysClass (int) - Class of the system
# =============================================================================
def getClass(sys):
    num, den = tfdata(sys)
    den = den[0][0] # To have the array as it's a list with one array
    # Reverse the direction of loop because the smallest power is at the last index
    for sysClass, item in enumerate(reversed(den)):
        if item != 0:
            return sysClass
        
#%%
# =============================================================================
# Get the order of the system
# 
# Parameters:
#     * sys (LTI) - System analysed
#     
# Returns:
#     * sysOrder (int) - Order of the system
# =============================================================================
def getOrder(sys):
    num, den = tfdata(sys)
    den = den[0][0] # To have the array as it's a list with one array
    sysOrder = len(den)-1
    return sysOrder

#%%
# =============================================================================
# PID Tuner to see the modifications of the PID parameters on a given system
# 
# Parameters:
#     * H (LTI) - Transfert function of the system (open loop) to regulate
#     * Kp (float, optionnal) - Proportionnal parameter of the PID controller (default = 1) 
#     * Ki (float, optionnal) - Integral parameter of the PID controller (default = 0) 
#           Reminder: Ki = Kp/tI
#     * Kd (float, optionnal) - Derivative parameter of the PID controller (default = 0)
#           Reminder: Kd = Kp*tD
#
# Returns:
#    
# =============================================================================
def pidTuner(H, Kp=1, Ki=0, Kd=0):
    from matplotlib.widgets import Slider, Button, RadioButtons
    
    # Create the figure
    fig = plt.figure("PID Tuner")
    axGraph = fig.subplots()
    plt.subplots_adjust(bottom=0.3)

    
    # Frames to contain the sliders
    axcolor = 'lightgoldenrodyellow'
    axKp = plt.axes([0.125, 0.2, 0.775, 0.03], facecolor=axcolor)
    axKi = plt.axes([0.125, 0.15, 0.775, 0.03], facecolor=axcolor)
    axKd = plt.axes([0.125, 0.1, 0.775, 0.03], facecolor=axcolor)
    
    # Slider
    sKp = Slider(axKp, 'Kp', Kp/20, Kp*20, valinit=Kp)
    
    if Ki == 0:
        sKi = Slider(axKi, 'Ki', 0, 100, valinit=Ki)
    else:
        sKi = Slider(axKi, 'Ki', Ki/20, Ki*20, valinit=Ki)
        
    if Kd == 0:
        sKd = Slider(axKd, 'Kd', 0, 100, valinit=Kd)
    else:
        sKd = Slider(axKd, 'Kd', Kd/20, Kd*20, valinit=Kd)
    
    def update(val):
        KpNew = sKp.val
        KiNew = sKi.val
        KdNew = sKd.val
        c = KpNew*tf(1,1) + KiNew*tf(1,[1, 0]) + KdNew*tf([1, 0],1)
        Gbo = c*H
        if radio.value_selected == 'Step':
            axGraph.clear()
            plotStep(axGraph, Gbo)
        elif radio.value_selected == 'Nichols':
            axGraph.clear()
            plotNichols(axGraph, Gbo)
            
        fig.canvas.draw_idle() # Refresh the plots
    sKp.on_changed(update)
    sKi.on_changed(update)
    sKd.on_changed(update)
    
    # Reset button
    resetax = plt.axes([0.8, 0.025, 0.1, 0.04])
    reset_button = Button(resetax, 'Reset', color=axcolor, hovercolor='0.975')
    
    def reset(event):
        sKp.reset()
        sKi.reset()
        sKd.reset()
    reset_button.on_clicked(reset)
    
    def plotNichols(ax, Gbo):
        nichols([Gbo_init, Gbo], NameOfFigure = "PID Tuner", ax=ax)
        # Print infos inside the plot
        textInfo = getNicholsTextInfos(Gbo)
        at = AnchoredText(textInfo,
            prop=dict(size=10), frameon=True,
            loc='lower right',
            )
        at.patch.set_boxstyle("round,pad=0.,rounding_size=0.2")
        axGraph.add_artist(at)
    
    def plotStep(ax, Gbo):
        Gbf = feedback(Gbo)
        [Y_New, T_new]= step(Gbf, T)
        ax.plot(T, linspace(1, 1, len(T)), linestyle=':', lw=1, color='grey') # 1 line
        l0, = ax.plot(T, Y, label="Initial system", lw=1)  # Original
        l, = ax.plot(T, Y_New, label="Modified system", lw=1)
        #l.set_ydata(Y_New)
        ax.set_title("Step Response")
        ax.set_ylabel("Amplitude")
        ax.set_xlabel("Time (seconds)")
    
    # Print button
    printax = plt.axes([0.6, 0.025, 0.1, 0.04])
    print_button = Button(printax, 'Infos', color=axcolor, hovercolor='0.975')
    
    # Function to create a string with the usefull info fo nichols plot
    def getNicholsTextInfos(Gbo):
        gm, pm, wg, wp = margin(Gbo) # Extract the gain margin (Gm) and the phase margin (Pm)
        gm = 20*np.log10(gm) # Conversion of gm in dB
        return """Phase Margin = {PM}°
Gain Margin = {GM} dB""".format(PM=pm, GM=gm)
    
    def printInfos(event):
        KpNew = sKp.val
        KiNew = sKi.val
        KdNew = sKd.val
        print("") # To let space before the informations
        print("Kp =", KpNew)
        print("Ki =", KiNew)
        print("Kd =", KdNew)
        c = KpNew*tf(1,1) + KiNew*tf(1,[1, 0]) + KdNew*tf([1, 0],1)
        print("Corr =", c)
        Gbo = c*H
        print("Gbo =", Gbo)
        if radio.value_selected == 'Step':
            Gbf = feedback(Gbo)
            [Y_New, T_new]= step(Gbf, T)
            stepInfo = info()
        
            plt.sca(axGraph) # To change the current axes to be the graphs's one
            step_info(T, Y_New, stepInfo)
            # Printing of the step infos
            temp = vars(stepInfo) # Transform into a dict to be able to iterate
            for item in temp:
                print(item, ':', temp[item])
            
        elif radio.value_selected == 'Nichols':
            gm, pm, wg, wp = margin(Gbo) # Extract the gain margin (Gm) and the phase margin (Pm)
            print("Phase Margin =", pm, "°")
            gm = 20*np.log10(gm) # Conversion of gm in dB
            print("Gain Margin =", gm, "dB")
            # Plotting
            if pm != math.inf:
                axGraph.plot([-180, -180+pm], [0, 0], 'k-', linewidth=1)
                axGraph.plot(-180+pm, 0,'ko')
            if gm != math.inf:
                axGraph.plot([-180, -180], [-gm, 0], 'k-', linewidth=1)   
                axGraph.plot(-180, -gm,'ko')
            
    print_button.on_clicked(printInfos)
    
    # Radio button
    rax = plt.axes([0.905, 0.5, 0.09, 0.1], facecolor=axcolor)
    radio = RadioButtons(rax, ('Step', 'Nichols'), active=0)

    def changeGraph(label):
        # Get the new parameters values
        KpNew = sKp.val
        KiNew = sKi.val
        KdNew = sKd.val
        c = KpNew*tf(1,1) + KiNew*tf(1,[1, 0]) + KdNew*tf([1, 0],1)
        Gbo = c*H
        # Deleting of the graphs
        axGraph.clear()
        # Base for the original graph
        if label == 'Step':
            plotStep(axGraph, Gbo)
        elif label == 'Nichols':
            plotNichols(axGraph, Gbo)
        
        fig.canvas.draw_idle() # To refresh the plots
            
    radio.on_clicked(changeGraph)
    
    # Declaration of the transfer function of the system in BO and BF with the given control parameters
    c = Kp*tf(1,1) + Ki*tf(1,[1, 0]) + Kd*tf([1, 0],1)
    Gbo_init = c*H
    Gbf_init = feedback(Gbo_init)
    [Y, T] = step(Gbf_init)

    # Plot the step
    plotStep(axGraph, Gbo_init)
    
    plt.show()
    
    return sKp, print_button, reset_button, radio # It's needed to return those variables to keep the widgets references or they don't work.
    