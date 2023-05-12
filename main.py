import tkinter as tk
from rumus import *
import pygmt
import pandas as pd
from PIL import Image, ImageTk


# Create the main window
root = tk.Tk()
root.title("Calculate Tectonic Stress")

root.geometry("800x800")
root.resizable(False,False)

# Disable automatic resizing of widgets
root.grid_propagate(False)

# Configure grid rows and columns to expand and fill the space available
for i in range(10):
    root.grid_rowconfigure(i, weight=1)
for i in range(2):
    root.grid_columnconfigure(i, weight=1)

frame = tk.LabelFrame(root, text="Input Strain", padx=10, pady=10)
frame.pack(padx=1, pady=1, side='left', anchor='n')

# Create the labels for each variable
label1 = tk.Label(frame, text="strain_xx (nanostrain)")
label1.grid(row=0, column=0, padx=5, pady=5, sticky='w')

label2 = tk.Label(frame, text="strain_yy (nanostrain)")
label2.grid(row=1, column=0, padx=5, pady=5, sticky='w')

label3 = tk.Label(frame, text="strain_xy (nanostrain)")
label3.grid(row=2, column=0, padx=5, pady=5, sticky='w')

# Create the input fields for each variable
entry1 = tk.Entry(frame)
entry1.grid(row=0, column=1, padx=5, pady=5)

entry2 = tk.Entry(frame)
entry2.grid(row=1, column=1, padx=5, pady=5)

entry3 = tk.Entry(frame)
entry3.grid(row=2, column=1, padx=5, pady=5)

frame2 = tk.LabelFrame(root,padx=10, pady=10, text="Input Additional Variables")
frame2.pack(padx=1, pady=1, side='top', anchor='n')
# Create input for E,v,miu
E = tk.StringVar()
E.set("80000000")
v = tk.StringVar()
v.set("0.25")
miu = tk.StringVar()
miu.set("0.4")

# Create the labels for the additional variables
label4 = tk.Label(frame2, text="Modulus Young (kPa)")
label4.grid(row=0, column=2, padx=5, pady=5, sticky='w')

label5 = tk.Label(frame2, text="Poisson ratio")
label5.grid(row=1, column=2, padx=5, pady=5, sticky='w')

label6 = tk.Label(frame2, text="Fric. Coefficient")
label6.grid(row=2, column=2, padx=5, pady=5, sticky='w')

# Create the input fields for the additional variables
entry4 = tk.Entry(frame2, textvariable=E)
entry4.grid(row=0, column=3, padx=5, pady=5)

entry5 = tk.Entry(frame2, textvariable=v)
entry5.grid(row=1, column=3, padx=5, pady=5)

entry6 = tk.Entry(frame2, textvariable=miu)
entry6.grid(row=2, column=3, padx=5, pady=5)

# Create input for long, lat
long = tk.StringVar()
long.set('120.9')
lat = tk.StringVar()
lat.set('-1.75')


frame3 = tk.LabelFrame(root,padx=10, pady=10, text="Input Strain Coordinate")
frame3.pack(padx=14, pady=1, side='top', anchor='n', expand=True, fill='x')
# Create the labels for the additional variables
label7 = tk.Label(frame3, text="Longitude")
label7.grid(row=0, column=2, padx=5, pady=5, sticky='w',)

label8 = tk.Label(frame3, text="Latitude")
label8.grid(row=1, column=2, padx=5, pady=5, sticky='w')

# Create the input fields for the additional variables
entry7 = tk.Entry(frame3, textvariable=long)
entry7.grid(row=0, column=3, padx=5, pady=5)

entry8 = tk.Entry(frame3, textvariable=lat)
entry8.grid(row=1, column=3, padx=5, pady=5)


# Function to retrieve the input values
def get_values():
    global display
    strain_xx = float(entry1.get())*1e-9
    strain_yy = float(entry2.get())*1e-9
    strain_xy = float(entry3.get())*1e-9
    E = float(entry4.get())
    v = float(entry5.get())
    miu = float(entry6.get())
    long = float(entry7.get())
    lat = float(entry8.get())

    # Calculate Tectonic Stress
    stress_tensor = stress_from_strain_skripsi(strain_xx, strain_yy, strain_xy, E, v)

    w, v = principal_stress_from_eig(stress_tensor[0][0], stress_tensor[1][0], stress_tensor[2][0])

    theta = np.degrees((np.arctan(2*stress_tensor[2][0]/(stress_tensor[0][0] - stress_tensor[1][0])))/2)

    degrees = np.arctan(v[1][0]/v[0][0])
    azimuth = abs(np.degrees(degrees)) - 180

    sigmax = w[1]
    sigmay = w[0]

    lon_min = long - 1
    lon_max = long + 1
    lat_min = lat - 1
    lat_max = lat + 1

    normal, strain = normal_and_shear_from_pdf(sigmax, sigmay, stress_tensor[2][0], theta)

    cfs = abs(strain) + miu * normal

    # Remove existing labels
    for widget in root.grid_slaves():
        if int(widget.grid_info()["row"]) > 3:
            widget.destroy()
    
    with open('output.dat', 'w') as f:
        f.writelines("{}  {}  {}  {}  {}".format(str(long), str(lat+0.15), str(w[0]/100), str(w[1]/100), str(azimuth)))

    # Create labels to display the submitted values in the grid
    tk.Label(tectonic_stress_result, text="Tectonic Stress (kPa/tahun): ").grid(row=1, column=0, padx=1, pady=5, sticky='w')
    tk.Label(tectonic_stress_result, text='{:.2f}'.format(cfs)).grid(row=1, column=1, padx=5, pady=5, sticky='w')

    data = pd.read_csv('output.dat', sep='\s+', header=None)
    print(data)
    fig = pygmt.Figure()
    region = [lon_min, lon_max, lat_min, lat_max]
    proj = 'M' + str(12) + 'c'
    fig.basemap(region=region, projection=proj, frame='a0.5')
    fig.coast(region=region, projection=proj, land='white', shorelines="1/0.5p")
    fig.velo(
        data=data,
        spec='x10',
        pen='0.5p', 
        color='black',
    )
    fig.plot(x=long, y=lat, style='c0.2c', color='red', pen='0.5p')
    fig.plot(
        data='indonesiafaults.gmt',
    )
    fig.savefig('azimuth.png')
    image = Image.open('azimuth.png')
    image.thumbnail((474,447))
    display = ImageTk.PhotoImage(image)
    image = tk.Label(frame4, image=display, background='white', width=474, height=447, padx=10, pady=10)
    image.grid(row=0, column=0, padx=5, pady=5)


# Create the button to submit the values
tectonic_stress_result = tk.LabelFrame(root, text="Tectonic Stress Result", padx=15, pady=15)
tectonic_stress_result.place(anchor='w', rely=0.27, relx=0.001,  width=387, height=120)
submit_button = tk.Button(tectonic_stress_result, text="Submit", command=get_values)
submit_button.grid(row=0, column=0, padx=5, pady=5, sticky='e')

frame4 = tk.LabelFrame(root,padx=145, text="Azimuth")
frame4.place(anchor='w', rely=0.65, relx=0.001, width=785, height=480)
image = tk.Label(frame4)
image.grid(row=0, column=0)

# Start the main loop
root.mainloop()
