import tempfile
import tkinter as tk
from tkinter import messagebox
from tkinter.filedialog import askopenfilename
from matplotlib.backend_bases import NavigationToolbar2
import pandas as pd
from rumus import *
import pygmt
from PIL import Image, ImageTk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from window_stress_time_function import *


def open_file():
    """
    Open a file for editing.

    Parameters:
    None

    Returns:
    None
    """
    global filepath
    filepath = askopenfilename(
        filetypes=[("Text Files", "*.dat")]
    )
    if not filepath:
        return
    text = pd.read_csv(filepath, sep='\s+', header=None, skiprows=1)
    if check_file_format(text) != True:
        filepath = None
    messagebox.showinfo("File Opened", "File opened successfully")

    # TODO: use function to check the file format


# TODO: Add a function to checking the file format when open file
def check_file_format(text):
    """
    Check the file format

    Example:
    strain_xx strain_yy strain_xy long lat
    -66.7 88.4 -15.1 120.9 -1.75

    Parameters:
    text (pandas dataframe): the data from the file

    Returns:
    bool: True if the file format is correct, False if the file format is incorrect
    """
    # check the number of columns
    if text.shape[1] != 5:
        messagebox.showerror('File Format Incorrect',
                             'The number of columns is incorrect')
        return False
    # check all the strain_xx
    for i in range(0, len(text[0])):
        if text[0][i] < -1000 or text[0][i] > 1000:
            messagebox.showerror(
                'File Format Incorrect', 'The strain_xx value is out of range (-1000, 1000) in line {}'.format(i+2))
            return False
    # check all the strain_yy
    for i in range(0, len(text[1])):
        if text[1][i] < -1000 or text[1][i] > 1000:
            messagebox.showerror(
                'File Format Incorrect', 'The strain_yy value is out of range (-1000, 1000) in line {}'.format(i+2))
            return False
    # check all the strain_xy
    for i in range(0, len(text[2])):
        if text[2][i] < -1000 or text[2][i] > 1000:
            messagebox.showerror(
                'File Format Incorrect', 'The strain_xy value is out of range (-1000, 1000) in line {}'.format(i+2))
            return False
    # check all the long
    for i in range(0, len(text[3])):
        if text[3][i] < -180 or text[3][i] > 180:
            messagebox.showerror(
                'File Format Incorrect', 'The long value is out of range (-180, 180) in line {}'.format(i+2))
            return False
    # check all the lat
    for i in range(0, len(text[4])):
        if text[4][i] < -90 or text[4][i] > 90:
            messagebox.showerror(
                'File Format Incorrect', 'The lat value is out of range (-90, 90) in line {}'.format(i+2))
            return False
    return True


def calculate_tectonic_stress():
    """
    Calculate the tectonic stress

    Parameters:
    None

    Returns:
    None
    """
    global E
    global v
    global miu
    global long_min
    global long_max
    global lat_min
    global lat_max
    global display
    global list_cfs
    if 'filepath' not in globals() or filepath == None:
        messagebox.showerror('No File Opened', 'Please open a file first')
        return

    E = float(inp_E.get())
    v = float(inp_v.get())
    miu = float(inp_miu.get())
    long_min = float(inp_long_min.get())
    long_max = float(inp_long_max.get())
    lat_min = float(inp_lat_min.get())
    lat_max = float(inp_lat_max.get())

    text = pd.read_csv(filepath, sep='\s+', header=None, skiprows=1)

    # Calculate the tectonic stress and save it to a file
    list_cfs = []
    with open('output.dat', 'w') as f:
        for i in range(0, len(text[0])):
            stress_tensor = stress_from_strain_skripsi(
                text[0][i]*1e-9, text[1][i]*1e-9, text[2][i]*1e-9, E, v)
            w, vec = principal_stress_from_eig(
                stress_tensor[0][0], stress_tensor[1][0], stress_tensor[2][0])
            degrees = np.arctan(vec[1][0]/vec[0][0])
            azimuth = abs(np.degrees(degrees)) - 180
            theta = np.degrees(
                (np.arctan(2*stress_tensor[2][0]/(stress_tensor[0][0] - stress_tensor[1][0])))/2)

            if(w[0] > w[1]):
                sigmax = w[0]
                sigmay = w[1]
            else:
                sigmax = w[1]
                sigmay = w[0]

            normal, strain = normal_and_shear_from_pdf(
                sigmax, sigmay, stress_tensor[2][0], theta)

            cfs = abs(strain) + miu * normal
            list_cfs.append(cfs)

            f.writelines("{}  {}  {}  {}  {}  {}\n".format(str(text[3][i]), str(
                text[4][i]), str(w[0]/100), str(w[1]/100), str(azimuth), cfs))

    data = pd.read_csv('output.dat', sep='\s+', header=None)
    data_used = data.iloc[:, 0:5].copy(deep=True)
    fig = pygmt.Figure()
    region = [long_min, long_max, lat_min, lat_max]
    proj = 'M' + str(12) + 'c'
    fig.basemap(region=region, projection=proj, frame='a0.5')
    fig.coast(region=region, projection=proj,
              land='white', shorelines="1/0.5p")
    fig.plot(
        data='indonesiafaults.gmt',
    )
    for i in range(len(text[0])):
        fig.plot(x=data[0][i], y=data[1][i], style='c0.2c', fill='red')
        data_used[1][i] = data_used[1][i] + 0.07
        fig.velo(
            data=data_used.iloc[[i]],
            spec='x10',
            pen='0.5p',
            fill='black',
        )
        fig.text(x=data[0][i], y=data[1][i]-0.02,
                 text='CFS: {:.2f}'.format(data[5][i]), font='8p,Helvetica-Bold,black')
        fig.text(x=data[0][i], y=data[1][i]-0.05,
                 text=i, font='8p,Helvetica-Bold,red')
    fig.savefig('azimuth.png', dpi=300)

    frm_time_series = find_canvas_by_text(root, 'Time Series')
    frm_time_series.destroy() if frm_time_series else None

    root.resizable(True, True)
    root.geometry("785x480")
    root.resizable(False, False)

    image = Image.open('azimuth.png')
    image.thumbnail((474,447), Image.LANCZOS, reducing_gap=5.0)
    display = ImageTk.PhotoImage(image)
    frm_image = tk.LabelFrame(root, borderwidth=0, highlightthickness=0,
                              text='Azimuth', labelanchor='n', font=('Helvetica', 12, 'bold'))
    frm_image.place(width=785, height=480)
    image = tk.Label(frm_image, image=display, background='white', width=474, height=447, padx=10, pady=10)
    image.place(anchor='center', relx=0.5, rely=0.5)


def window_tectonic_stress():
    """
    Calculate the tectonic stress

    Parameters:
    None

    Returns:
    None
    """
    global inp_E
    global inp_v
    global inp_miu
    global inp_long_min
    global inp_long_max
    global inp_lat_min
    global inp_lat_max
    if 'filepath' not in globals() or filepath == None:
        messagebox.showerror('No File Opened', 'Please open a file first')
        return

    global wdw_tectonic_stress
    wdw_tectonic_stress = tk.Toplevel(root)
    # Create the button to calculate the tectonic stress
    btn_tectonic_stress_calculate = tk.Button(
        wdw_tectonic_stress, text="Calculate", command=run_tectonic_stress)
    btn_tectonic_stress_calculate.grid(row=8, column=2, padx=5, pady=5)

    # Create the button to close the window
    btn_tectonic_stress_close = tk.Button(
        wdw_tectonic_stress, text="Close", command=wdw_tectonic_stress.destroy)
    btn_tectonic_stress_close.grid(row=8, column=3, padx=5, pady=5)

    # Create input for E,v,miu
    E = tk.StringVar()
    E.set("80000000")
    v = tk.StringVar()
    v.set("0.25")
    miu = tk.StringVar()
    miu.set("0.4")
    long_min = tk.StringVar()
    long_min.set("120")
    long_max = tk.StringVar()
    long_max.set("121")
    lat_min = tk.StringVar()
    lat_min.set("-2.5")
    lat_max = tk.StringVar()
    lat_max.set("-1")

    # Create the labels for the additional variables
    lbl_E = tk.Label(wdw_tectonic_stress, text="Modulus Young (kPa)")
    lbl_E.grid(row=0, column=2, padx=5, pady=5, sticky='w')

    lbl_v = tk.Label(wdw_tectonic_stress, text="Poisson ratio")
    lbl_v.grid(row=1, column=2, padx=5, pady=5, sticky='w')

    lbl_miu = tk.Label(wdw_tectonic_stress, text="Fric. Coefficient")
    lbl_miu.grid(row=2, column=2, padx=5, pady=5, sticky='w')

    lbl_long_min = tk.Label(wdw_tectonic_stress, text="Long Min")
    lbl_long_min.grid(row=3, column=2, padx=5, pady=5, sticky='w')

    lbl_long_max = tk.Label(wdw_tectonic_stress, text="Long Max")
    lbl_long_max.grid(row=4, column=2, padx=5, pady=5, sticky='w')

    lbl_lat_min = tk.Label(wdw_tectonic_stress, text="Lat Min")
    lbl_lat_min.grid(row=5, column=2, padx=5, pady=5, sticky='w')

    lbl_lat_max = tk.Label(wdw_tectonic_stress, text="Lat Max")
    lbl_lat_max.grid(row=6, column=2, padx=5, pady=5, sticky='w')

    # Create the input fields for the additional variables
    inp_E = tk.Entry(wdw_tectonic_stress, textvariable=E)
    inp_E.grid(row=0, column=3, padx=5, pady=5)

    inp_v = tk.Entry(wdw_tectonic_stress, textvariable=v)
    inp_v.grid(row=1, column=3, padx=5, pady=5)

    inp_miu = tk.Entry(wdw_tectonic_stress, textvariable=miu)
    inp_miu.grid(row=2, column=3, padx=5, pady=5)

    inp_long_min = tk.Entry(wdw_tectonic_stress, textvariable=long_min)
    inp_long_min.grid(row=3, column=3, padx=5, pady=5)

    inp_long_max = tk.Entry(wdw_tectonic_stress, textvariable=long_max)
    inp_long_max.grid(row=4, column=3, padx=5, pady=5)

    inp_lat_min = tk.Entry(wdw_tectonic_stress, textvariable=lat_min)
    inp_lat_min.grid(row=5, column=3, padx=5, pady=5)

    inp_lat_max = tk.Entry(wdw_tectonic_stress, textvariable=lat_max)
    inp_lat_max.grid(row=6, column=3, padx=5, pady=5)

    return


def start_loading_screen():
    global loading_screen
    # Create a new Toplevel window
    loading_screen = tk.Toplevel(root)

    # Set the window size and position it in the center of the screen
    loading_screen.geometry("100x75+{}+{}".format(
        int(root.winfo_screenwidth()/2 - 100), int(root.winfo_screenheight()/2 - 50)))

    # Create a label to display a message or animation
    message_label = tk.Label(loading_screen, text="Loading...")
    message_label.pack(pady=20)

    # Update the window to display the label
    loading_screen.update()
    return


def end_loading_screen():
    loading_screen.destroy()
    return


def run_tectonic_stress():
    start_loading_screen()
    calculate_tectonic_stress()
    end_loading_screen()
    return


# root window
root = tk.Tk()
root.geometry('785x480')
# root.resizable(False, False)
root.title('Menu Demo')


# create a menubar
menubar = tk.Menu(root)
root.config(menu=menubar)

# create the file_menu
file_menu = tk.Menu(
    menubar,
    tearoff=0
)

# add menu items to the File menu
file_menu.add_command(label='Open File', command=open_file)
file_menu.add_separator()


# add Exit menu item
file_menu.add_separator()
file_menu.add_command(
    label='Exit',
    command=root.destroy
)


menubar.add_cascade(
    label="File",
    menu=file_menu,
    underline=0
)
# create the Help menu
help_menu = tk.Menu(
    menubar,
    tearoff=0
)

help_menu.add_command(label='Calculate Tectonic Stress',
                      command=window_tectonic_stress)
help_menu.add_command(label='Calculate Stress Time Function',
                      command=lambda root=root: window_stress_time_function(root))

# add the Help menu to the menubar
menubar.add_cascade(
    label="Function",
    menu=help_menu,
    underline=0
)

root.mainloop()
