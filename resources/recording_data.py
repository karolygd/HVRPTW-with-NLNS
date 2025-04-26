import csv
import os

class RecordingData:
    def __init__(self, file_name, headers:list[str]):

        # Define the CSV file name
        self.csv_filename = file_name +".csv"

        file_exists = os.path.exists(self.csv_filename)

        # Define the headers (column names)
        #headers = ["Iteration", "Objective Value", "Execution Time (s)", "Best Solution Found"]

        # Create the CSV file and write the headers
        if not file_exists:
            with open(self.csv_filename, mode="w", newline="") as file:
                writer = csv.writer(file)
                writer.writerow(headers)

    # Function to append a row for each iteration
    def log_iteration(self, iteration, **kwargs):
        row_data = [iteration] + [kwargs.get(header, "N/A") for header in kwargs.keys()]

        with open(self.csv_filename, mode="a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(row_data)