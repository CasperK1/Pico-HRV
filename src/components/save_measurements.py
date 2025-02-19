import os
import ujson

class Measurements():
    def __init__(self):
        self.file_name = "data.json"
        self.current_dir = os.getcwd()
        self.dummy_data = {"time": 1609459392, "Mean HR": 74.86, "RMSSD": 74, "PPI (ms)": 801.54, "id": "e661640843963727", "SDNN": 55.6}
        self.initialize()

    def initialize(self):
        if self.file_name not in os.listdir():
            with open(self.file_name, "w") as file:
                ujson.dump([self.dummy_data], file)
        with open(self.file_name, "r") as file:
            try:
                data = ujson.load(file)
                if not isinstance(data, list):
                    data = []
            except: 
                data.append(self.dummy_data)
                with open(self.file_name, "w") as file:
                    ujson.dump(data, file)
                

    def add_to_file(self, measurement):
        with open(self.file_name, "r") as file:
            data = ujson.load(file)
        
        new_data = measurement
        data.append(new_data)

        with open(self.file_name, "w") as file:
            ujson.dump(data, file)
    
    def get_from_file(self):
        with open(self.file_name, "r") as file:
            print("reading file")
            data = ujson.load(file)
        return data

