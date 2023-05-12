import matplotlib.pyplot as plt
import math

# Generate some sample data
x = range(15)
y = [i**2 for i in x]

# Calculate the number of rows and columns needed
num_plots = len(x)
num_cols = 2 if num_plots > 10 else 1
num_rows = math.ceil(num_plots / num_cols)

print(num_plots)
print(num_cols)
print(num_rows)

# Create a figure and subplots
fig, axs = plt.subplots(nrows=num_rows, ncols=num_cols, figsize=(10, 4*num_rows))

# Plot the data on the subplots
for i, ax in enumerate(axs.flat):
    print(ax, i)
    if i < num_plots:
        ax.plot(x[i], y[i])
        ax.set_title(f"Plot {i+1}")
        ax.set_xlabel("X")
        ax.set_ylabel("Y")

# Display the plot
plt.tight_layout()
plt.show()
