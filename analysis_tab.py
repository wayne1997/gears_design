import tkinter as tk
from tkinter import Frame, LabelFrame

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from scipy.interpolate import interp1d

import global_values
from global_functions import add_logs

mse_canvas = None

def show_analisys_tab(panel_left: LabelFrame, panel_right: LabelFrame):
    generate_panel_left(panel_left, panel_right)
    generate_panel_right(panel_right)

def generate_panel_left(panel_left, panel_right):
    btn = tk.Button(panel_left, text="Graficar", command=lambda: get_results(panel_right), anchor="center")
    btn.grid(row=0, column=0, padx=15, pady=15, sticky="nsew")

def generate_panel_right(panel):
    right_frame = tk.Frame(panel, width=300)
    right_frame.pack(side=tk.RIGHT, fill=tk.Y)

def get_results(panel):
    try:
        df_original = global_values.global_dataframe
        df_adjusted = global_values.correg_data_global
        if isinstance(df_original, pd.DataFrame) and not df_original.empty:
            if isinstance(df_adjusted, pd.DataFrame) and not df_adjusted.empty:
                plot_comparation_graph(df_original, df_adjusted, panel)
        else:
            add_logs("Información corrupta")
    except Exception as ex:
        add_logs(f"Un error ha ocurrido en la obtención de información: {ex}")


def show_not_available_tab(board: Frame):
    print("This window is not available")


#________________________GRAPH AND DATA MANAGEMENT SECTION_____________________________________________________________

def plot_comparation_graph(df_original: pd.DataFrame, df_adjusted: pd.DataFrame, panel: LabelFrame):
    global mse_canvas

    if mse_canvas: mse_canvas.get_tk_widget().destroy()

    fig, axe = plt.subplots(figsize=(7, 5))
    num_samples = len(df_adjusted)
    df_original_sample = df_original.iloc[::len(df_original)// num_samples] [::num_samples]
    mse_value_corrected = np.mean((df_original_sample['w2/w1'] - df_adjusted['f_correg']) ** 2)
    axe.plot(df_original["theta"], df_original['w2/w1'], label="Datos Originales", linestyle='-', color='blue', linewidth=2)
    axe.plot(df_adjusted["Theta"], df_adjusted["f_correg"], label="Datos Corregidos", linestyle='--' ,color='red', linewidth=3)
    axe.set_xlabel('θ')
    axe.set_ylabel('ω2/ω1')
    axe.set_title('Comparación de información')
    axe.legend(loc='upper right')
    axe.grid(True)
    mse_text = f"MSE: {mse_value_corrected:.2e}"
    axe.text(0.05, 0.90, mse_text, transform=axe.transAxes, fontsize=12, bbox=dict(facecolor='white', alpha=0.5))
    mse_canvas =FigureCanvasTkAgg(fig, master=panel)
    canvas_widget = mse_canvas.get_tk_widget()
    canvas_widget.pack(fill=tk.BOTH, expand=True)
