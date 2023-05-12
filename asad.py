import math
import re
import matplotlib.pyplot as plt
import numpy as np


data = {
    'Poso:4:2017': {
        'Segment 1': -3.2,
        # 'Segment 2': -3.2,
    },
    'Palu:8:2018': {
        'Segment 1': -4.2,
        # 'Segment 2': -4.2,
    },
}

color = ['red', 'blue', 'green', 'yellow', 'orange', 'purple', 'pink', 'brown']

year_start = 2010
year_end = 2030
cfs = [2.4]

regex_pattern = r"^.*:([^:]*{})$".format("2017")

last_key = [key for key in data.keys()][-1]
print(last_key)
last_value = data[last_key]

total = {}
for element in last_value:
    sum = 0
    list = [0]
    for j in range(year_start, year_end):
        regex_pattern = r"^.*:([^:]*{})$".format(j) 
        match = [key for key in data.keys() if re.match(regex_pattern, key)]
        if(len(match) > 1):
            raise ValueError("More than one match")
        if(len(match)):
            for i in range(0, 12):
                if i == int(match[0].split(":")[1]):
                    sum = sum + \
                        data['{}'.format(match[0])]['{}'.format(
                            element)] + (cfs[0]/12)
                    list.append(sum)
                else:
                    sum = sum + (cfs[0]/12)
                    list.append(sum)
        else:
            for i in range(0, 12):
                sum = sum + (cfs[0]/12)
                list.append(sum)
    total[element] = list

maximum = {}
end = {}
# print(total)
for key in total:
    maximum[key] = max(total[key])
    if min(total[key]) < 0 :
        total[key] = [i+ (-1 * min(total[key])) for i in total[key]]
    end[key] = total[key][-1]
max_all = max(maximum.values())
year = []
for i in range(0, ((year_end - year_start)*12)+1):
    a = year_start + (math.floor(1/12)*i) + (1/12*i)
    year.append(a)

nrows = len(total) 
ncols = 1 
width_ratios = [5] 
height_ratios = [15 for i in range(0, len(total))]

fig, axs = plt.subplots(nrows=nrows, ncols=ncols,
                        figsize=(10, 15),
                        gridspec_kw={
                            'wspace': 0.7, 'width_ratios': width_ratios, 'height_ratios': height_ratios})
if nrows == 1:
    axs = np.array([axs])

print(type(axs))
fig.subplots_adjust(hspace=0)

fig.suptitle('Time Series {} - {}'.format(year_start, year_end), fontsize='x-large', fontweight="normal", y=0.92)
fig.supylabel("ΔCFS (kPa)", fontsize='x-large', fontweight="normal", x=0.025)
fig.supxlabel("Year", fontsize='x-large', ha='center', va='bottom', fontweight="normal", y=0.05)
print(total)
for ax_iter, ax in enumerate(axs.flat):
    for i in range(0, (len(total['Segment {}'.format(ax_iter+1)])-1)):
        match = [[re.split(r':', key), idx] for idx, key in enumerate(data.keys()) if re.split(r':', key)[2] == str(int(math.floor(year[i])))]
        if(len(match) > 0) and (int(match[0][0][2]) + int(match[0][0][1])/12) == year[i]:
            ax.plot(year[i:i+2], total['Segment {}'.format(ax_iter+1)][i:i+2], label = "{} {}".format(match[0][0][0], int(match[0][0][2])),color='{}'.format(color[match[0][1]]))
        else:
            ax.plot(year[i:i+2], total['Segment {}'.format(ax_iter+1)][i:i+2], color='green', label='\u0394CFS CSFS')
    ax.text(1.01, 0.4, 'Segment {}'.format(ax_iter+1), transform= ax.transAxes, fontsize=10)
    ax.text(-0.055, 0.6, "%.2f" % total['Segment {}'.format(ax_iter+1)][-1], fontsize=10, transform= ax.transAxes)
    ax.set_ylim([0, max_all])
    ax.set_xlim([year_start, year_end])
    ax.set_xticks(year[::60])
    ax.spines['top'].set_visible(False)
    if ax_iter != int(len(total))-1:
        ax.set_xticks([])
        ax.spines['bottom'].set_linestyle(':')
        ax.spines['bottom'].set_linewidth(1)
    if ax_iter == 0:
        ax.spines['top'].set_visible(True)

for ax in axs:
    ax.set_yticks([0])
    ax.set_yticklabels([])


handles, _ = plt.gca().get_legend_handles_labels()
labels = []
all_label = []
for handle in handles:
    if handle.get_label() not in all_label:
        labels.append(handle)
        all_label.append(handle.get_label())


# # Put a legend below current axis
plt.legend(labels, all_label, loc='upper center', ncol=3, bbox_to_anchor=(0.5, len(total)), fontsize=10)
plt.savefig('time_series.png', dpi=1000, bbox_inches='tight')
