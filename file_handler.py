
from tkinter import filedialog

import pandas as pd

from global_functions import add_logs


class FileHandler:

    def __init__(self):
        self.file_handler = filedialog;
        self.selected_file = None;
        self.data_frame = None;

    def show_get_file_path(self) -> str:
        self.selected_file = self.file_handler.askopenfilename(
            title="Selecciona el archivo CSV",
            filetypes=[("CSV files", "*.csv")],
            defaultextension=".csv"
        )

        if self.selected_file:
            return self.selected_file
    
    def process_csv_file(self, path: str):
        try:
            add_logs(f"Procesando archivo CSV: {path}")
            self.data_frame = pd.read_csv(path)
            add_logs("Resumen del archivo")
            add_logs(self.data_frame.describe())
            return self.data_frame
        except Exception as e:
            add_logs(f"Error al procesar el archivo CSV: {e}")
    
    def process_export_csv(self, data: pd.DataFrame):
        try:
            saved_file = self.file_handler.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[('Archivo CSV', '*.csv')],
                title="Guardar como"
            );
            if saved_file :
                data.to_csv(saved_file, sep="," ,index=False)
            else:
                raise Exception("Error al guardar el archivo")
        except Exception as e:
            add_logs(f"Error al exportar al csv {e}")