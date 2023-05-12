import math
import re
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
from tkinter import messagebox

import matplotlib.pyplot as plt
import numpy as np

from rumus import average_segment
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg



def find_labelframe_by_text(widget, target_text):
    if isinstance(widget, tk.LabelFrame) and widget['text'] == target_text:
        return widget

    for child in widget.winfo_children():
        result = find_labelframe_by_text(child, target_text)
        if result:
            return result

    return None

def find_canvas_by_text(widget, target_text):
    is_found = False
    if isinstance(widget, tk.Canvas):
        items = widget.find_all()  # Get all items on the widget

        for item in items:
            if widget.type(item) == "text":  # Check if item is a text item
                text = widget.itemcget(item, "text")  # Get the text attribute of the item
                if text == target_text:
                    is_found = True
    if is_found:
        return widget

    for child in widget.winfo_children():
        result = find_canvas_by_text(child, target_text)
        if result:
            return result
    return None

def window_stress_time_function(root):
  # create a list to store the event fields
  event_list = []
  segment_list = []

  def add_event_field():
      print(entry_event_count.get(), entry_segment_count.get())

      if(entry_event_count.get().isdigit() == False or int(entry_event_count.get()) <= 0):
        messagebox.showerror("Error", "Event count must be integer and greater than 0")
        return
      if(entry_segment_count.get().isdigit() == False or int(entry_segment_count.get()) <= 0):
        messagebox.showerror("Error", "Segment count must be integer and greater than 0")
        return

      # create a frame to store the event fields
      global frm_event, frm_segment, frm_event_segment, frm_output
      frm_output = tk.Frame(canvas_frame)
      frm_output.pack(side="top", fill=tk.BOTH,expand=True)

      frm_event = tk.Frame(frm_output)
      frm_event_title = tk.Label(frm_event, text="Event")
      frm_event_title.pack()
      frm_event.pack()
      
      for i in range(0, int(entry_event_count.get())):
        new_event = tk.Entry(frm_event, text="Event " + str(i+1))
        new_event.pack(side="left", fill="x")
        event_list.append(new_event)
      
      # create a frame to store the segment fields
      frm_segment = tk.Frame(frm_output)
      frm_segment_title = tk.Label(frm_segment, text="Segment")
      frm_segment_title.pack()
      frm_segment.pack()

      frm_segment_total = tk.Frame(frm_segment)
      frm_segment_total.pack()
      for i in range(0, int(entry_event_count.get())):
        event_segment_list = []
        for j in range(0, int(entry_segment_count.get())):
          new_entry_text = tk.StringVar()
          new_entry_text.set('input file...')
          new_label = tk.Entry(frm_segment_total, textvariable=new_entry_text)
          new_label.grid(row=j, column=i*2)
          new_segment = tk.Button(frm_segment_total, text="Segment " + str(j+1) + " of Event " + str(i+1), bg="white", fg="black") 
          new_segment.grid(row=j, column=i*2+1)
          new_segment.config(command=lambda row=j, col=i, entry_text=new_entry_text: browse_file(row, col, entry_text))
          event_segment_list.append(new_label)
        segment_list.append(event_segment_list)

      btn_add_event.config(state="disabled")

      #create a frame and button to store event and segment fields
      frm_event_segment = tk.Frame(frm_output)
      frm_event_segment.pack()

      frm_event_segment_buttons = tk.Button(frm_event_segment, text="Calculate", command=calculate)
      frm_event_segment_buttons.pack()   

      canvas_frame.update()
      height = canvas_frame.winfo_height() + 15
      width = canvas_frame.winfo_width() + 15

      if(height > window.winfo_screenheight() or width > window.winfo_screenwidth()):
        window.attributes("-fullscreen", True)
      else:
        window.geometry(f"{width}x{height}")

  def destroy_all_segment_and_event():
      frm_output.pack_forget()
      frm_output.grid_forget()
      btn_add_event.config(state="normal")
      event_list.clear()
      segment_list.clear()
      window.geometry("275x400")

  def browse_file(row, col, entry_text):
      entry_text.set(filedialog.askopenfilename(initialdir = "/",title = "Select file",filetypes = (("dat files","*.dat"),("all files","*.*"))))
    
  def calculate():
      global new_event_list
      new_event_list = []
      for event in event_list:
        new_event_list.append(event.get())
      checking_event_name_format()
      data = {}
      for i in range(0, len(event_list)):
        segment_filepath={}
        for j in range(0, len(segment_list[i])):
          print(segment_list[i][j].get())
          segment_filepath['Segment {}'.format(j+1)] =  average_segment(segment_list[i][j].get(),j)

        data[event_list[i].get()]= segment_filepath


      create_figure_time_function(data, int(entry_year_start.get()), int(entry_year_end.get()), float(entry_cfs.get()))

  
  def checking_event_name_format():
     for idx, event_name_format in enumerate(new_event_list):
        event_split = event_name_format.split(":")
        if len(event_split) != 3:
           messagebox.showerror(
                'Event format incorrect', "Event format in Event {}. Please check the event format again.\n\nEvent format start with event name, the month the event occured and the year the event occured separated by ':'.".format(idx + 1))
           return
        if event_split[1].isdigit() == False or (1 <= int(event_split[1]) <= 12) == False:
           messagebox.showerror(
                'Event format incorrect', "Event format in Event {}. Please check the event format again.\n\nThe Month value is only between 1 to 12".format(idx + 1))
           return
        if event_split[2].isdigit() == False or (1 <= int(event_split[1]) <= 3000) == False:
           messagebox.showerror(
                'Event format incorrect', "Event format in Event {}. Please check the event format again.\n\nThe Year value is only between 0 to 3000".format(idx + 1))
           return

  def create_figure_time_function(data, year_start, year_end, cfs):
    print(type(data))
    color = ['red', 'blue', 'green', 'yellow', 'orange', 'purple', 'pink', 'brown']

    regex_pattern = r"^.*:([^:]*{})$".format("2017")

    cfs = [cfs]

    last_key = [key for key in data.keys()][-1]
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

    azimuth_frame = find_labelframe_by_text(root, "Azimuth")
    azimuth_frame.destroy() if azimuth_frame else None
    root.resizable(True, True)
    root.geometry("1200x850")
    root.resizable(False, False)

    frm_time_evolution = FigureCanvasTkAgg(fig, master=root)
    frm_time_evolution.draw()
    text_item = frm_time_evolution.get_tk_widget().create_text(200, 150, text="Time Series")

    # Configure text attributes
    frm_time_evolution.get_tk_widget().itemconfig(text_item, fill="blue", font=("Arial", 16, "bold"))

    # Display the FigureCanvasTkAgg widget
    frm_time_evolution.get_tk_widget().pack() 
         
  # create the main window
  window = tk.Toplevel(root)
  window.title("Stress Time Function")
  window.geometry("275x400")
  
  main_frame = tk.Frame(window)
  main_frame.pack(fill=tk.BOTH, expand=True)

  canvas = tk.Canvas(main_frame, borderwidth=0, highlightthickness=0)

  hscrollbar = ttk.Scrollbar(main_frame, orient=tk.HORIZONTAL, command=canvas.xview)
  hscrollbar.pack(side=tk.BOTTOM, fill=tk.X)

  vscrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=canvas.yview)
  vscrollbar.pack(side=tk.RIGHT, fill=tk.Y)

  canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
  canvas.configure(xscrollcommand=hscrollbar.set)
  canvas.configure(yscrollcommand=vscrollbar.set)

  canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox('all')))

  #create new frame for the canvas
  canvas_frame = tk.Frame(canvas)
  canvas_frame.pack(expand=True, fill=tk.BOTH)
  canvas.create_window((0, 0), window=canvas_frame, anchor='nw')

  #create frame for input fields
  frm_input = tk.Frame(canvas_frame)
  frm_input.pack(side="top", fill=tk.BOTH, expand=True)

  #create a field for total events
  lbl_cfs = tk.Label(frm_input, text="CFS")
  lbl_cfs.pack(expand=True, fill=tk.BOTH, padx=10, pady=10, anchor="center")

  #create entry for total events
  entry_cfs = tk.Entry(frm_input)
  entry_cfs.pack()

  #create a field for total events
  lbl_year_start = tk.Label(frm_input, text="Year Start")
  lbl_year_start.pack(expand=True, fill=tk.BOTH, padx=10, pady=10, anchor="center")

  #create entry for total events
  entry_year_start = tk.Entry(frm_input)
  entry_year_start.pack()

  #create a field for total events
  lbl_year_end = tk.Label(frm_input, text="Year End")
  lbl_year_end.pack(expand=True, fill=tk.BOTH, padx=10, pady=10, anchor="center")

  #create entry for total events
  entry_year_end = tk.Entry(frm_input)
  entry_year_end.pack()

  #create a field for total events
  lbl_event_count = tk.Label(frm_input, text="Total Events")
  lbl_event_count.pack(expand=True, fill=tk.BOTH, padx=10, pady=10, anchor="center")

  #create entry for total events
  entry_event_count = tk.Entry(frm_input)
  entry_event_count.pack()

  #create a field for total segment
  lbl_segment_count = tk.Label(frm_input, text="Total Segments")
  lbl_segment_count.pack()

  #create entry for total segments
  entry_segment_count = tk.Entry(frm_input)
  entry_segment_count.pack()

  # create a button to add a new event field on the right
  btn_add_event = tk.Button(frm_input, text="Add Event Field and Segment Field", command=add_event_field)
  btn_add_event.pack()

  # create a button to destroy all segment and event
  btn_destroy_all_segment_and_event = tk.Button(frm_input, text="Reload", command=destroy_all_segment_and_event)
  btn_destroy_all_segment_and_event.pack()

  window.mainloop()
