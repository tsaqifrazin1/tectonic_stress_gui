import tkinter as tk
from rumus import *
# Create the main window
root = tk.Tk()
root.title("Calculate Tectonic Stress")

# Create the labels for each variable
label1 = tk.Label(root, text="shear_xx")
label1.grid(row=0, column=0, padx=5, pady=5)

label2 = tk.Label(root, text="shear_yy")
label2.grid(row=1, column=0, padx=5, pady=5)

label3 = tk.Label(root, text="shear_xy")
label3.grid(row=2, column=0, padx=5, pady=5)

# Create the input fields for each variable
entry1 = tk.Entry(root)
entry1.grid(row=0, column=1, padx=5, pady=5)

entry2 = tk.Entry(root)
entry2.grid(row=1, column=1, padx=5, pady=5)

entry3 = tk.Entry(root)
entry3.grid(row=2, column=1, padx=5, pady=5)

# Create input for E,v,miu
E = tk.StringVar()
E.set("80000000000")
v = tk.StringVar()
v.set("0.25")
miu = tk.StringVar()
miu.set("0.4")

# Create the labels for the additional variables
# Create the labels for the additional variables
label4 = tk.Label(root, text="E (Pa)")
label4.grid(row=0, column=2, padx=5, pady=5)

label5 = tk.Label(root, text="v")
label5.grid(row=1, column=2, padx=5, pady=5)

label6 = tk.Label(root, text="miu")
label6.grid(row=2, column=2, padx=5, pady=5)

# Create the input fields for the additional variables
entry4 = tk.Entry(root, textvariable=E)
entry4.grid(row=0, column=3, padx=5, pady=5)

entry5 = tk.Entry(root, textvariable=v)
entry5.grid(row=1, column=3, padx=5, pady=5)

entry6 = tk.Entry(root, textvariable=miu)
entry6.grid(row=2, column=3, padx=5, pady=5)

# Function to retrieve the input values
def get_values():
    shear_xx = float(entry1.get())
    shear_yy = float(entry2.get())
    shear_xy = float(entry3.get())
    E = float(entry4.get())
    v = float(entry5.get())
    miu = float(entry6.get())

    # Calculate Tectonic Stress
    stress_tensor = stress_from_strain_skripsi(shear_xx, shear_yy, shear_xy, E, v)

    w, v = principal_stress_from_eig(stress_tensor[0][0], stress_tensor[1][0], stress_tensor[2][0])

    theta = np.degrees((np.arctan(2*stress_tensor[2][0]/(stress_tensor[0][0] - stress_tensor[1][0])))/2)

    sigmax = w[1]
    sigmay = w[0]

    normal, shear = normal_and_shear_from_pdf(sigmax, sigmay, stress_tensor[2][0], theta)

    cfs = abs(shear) + miu * normal

    # Remove existing labels
    for widget in root.grid_slaves():
        if int(widget.grid_info()["row"]) > 3:
            widget.destroy()
    # Create labels to display the submitted values in the grid
    tk.Label(root, text="Tectonic Stress (Pa): ").grid(row=4, column=0, padx=5, pady=5)
    tk.Label(root, text='{:.2f}'.format(cfs)).grid(row=4, column=1, padx=5, pady=5)


# Create the button to submit the values
submit_button = tk.Button(root, text="Submit", command=get_values)
submit_button.grid(row=3, column=1, padx=5, pady=5)

# Start the main loop
root.mainloop()

# Start the main loop
root.mainloop()