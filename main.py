import tkinter as tk
from tkinter import filedialog, Text, Scrollbar
import urllib.request
from src.whitespaceAlgo import text_extraction
from src.relevancyScore import relevancy_table
from src.conditionExtraction import topic_extract, condition_extraction
import socket
import numpy as np
from tkinter import ttk


class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.pack()
        self.create_widgets()

    def create_widgets(self):
        
        self.select_button = tk.Button(self)
        self.select_button["text"] = "Select PDF Files"
        self.select_button["command"] = self.select_files
        self.select_button.pack(side="top", pady=10)
        
        self.search_term_label = tk.Label(self, text="Search Term")
        self.search_term_label.pack(side="top", pady=10)

        self.search_term_entry = tk.Entry(self)
        self.search_term_entry.pack(side="top", pady=10)

        self.run_button = tk.Button(self)
        self.run_button["text"] = "Run Function"
        self.run_button["command"] = self.run_function
        self.run_button.pack(side="top", pady=10)

        self.quit = tk.Button(self, text="QUIT", fg="red",
                              command=self.master.destroy)
        self.quit.pack(side="bottom", pady=10)
        
        self.scrollbar = Scrollbar(self)
        self.scrollbar.pack(side="right", fill="both")

        self.output = Text(self, height=10, yscrollcommand=self.scrollbar.set)
        self.scrollbar.config(command=self.output.yview)
        self.output.pack(side="bottom", fill="both", expand=True)
        
        self.option1_value = tk.IntVar()
        self.option2_value = tk.IntVar()
        self.option3_value = tk.IntVar()
        
        #relevancy shift
        self.options_frame = tk.Frame(self)
        self.options_heading = tk.Label(self.options_frame, text="Select Relevancy Parameters")
        self.options_heading.pack(side="top")
        self.option1 = tk.Checkbutton(self.options_frame, text="Title Score", variable=self.option1_value)
        self.option1.pack(side="top")
        self.option2 = tk.Checkbutton(self.options_frame, text="Abstract Score", variable=self.option2_value)
        self.option2.pack(side="top")
        self.option3 = tk.Checkbutton(self.options_frame, text="Similiarity Score", variable=self.option3_value)
        self.option3.pack(side="top")
        self.next_button = tk.Button(self.options_frame, text="Next", command=self.next_frame)
        self.next_button.pack(side="top")

    def next_frame(self):
        # Get the values of the options and store them in instance variables
        # print(self.option1_value.get(), self.option2_value.get(), self.option3_value.get())
        # Remove the options frame
        self.options_frame.pack_forget()
        self.relevancy_params = [self.option1_value.get(), self.option2_value.get(), self.option3_value.get()]
        # self.relevant_ids, res2 = relevancy_table(self.relevancy_params, self.search_term)
        res2 = 1
        self.relevant_ids = [0,1]
        if res2 == 0:
            self.output.insert('1.0', "Error in Relevancy Scoring\n")
        else:
            self.output.insert('1.0', "Relevacy Scoring Successful\n")
            self.topic_options, res3 = topic_extract(self.relevant_ids)
            # res3 = 1
            # self.topic_options = ['a', 'b', 'c']
            if res3 == 0:
                self.output.insert('1.0', "Error in Topic Extraction\n")
            else:
                self.output.insert('1.0', "Topic Extraction Successful\n")
                self.topic_frame = tk.Frame(self)
                self.topic_heading = tk.Label(self.topic_frame, text="Select related words you want to search for")
                self.topic_heading.pack(side="top")
                self.topic_list = tk.Listbox(self.topic_frame, selectmode="multiple")
                for topic in self.topic_options:
                    self.topic_list.insert("end", topic)
                self.topic_next_button = tk.Button(self.topic_frame, text="Next", command=self.next_frame2)
                self.topic_next_button.pack(side="top")
                self.topic_list.pack(side="top")
                self.topic_frame.pack(side="top", pady=10)
                
    def next_frame2(self):
        # Get the indices of the selected items
        self.topic_frame.pack_forget()
        selected_indices = self.topic_list.curselection()

        # Get the selected items
        selected_topics = [self.topic_list.get(i) for i in selected_indices]

        # Now you can use the selected topics for further processing
        self.conditions, res4 = condition_extraction(selected_topics)
        # res4 = 1
        # self.conditions = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q']
        if res4 == 0:
            self.output.insert('1.0', "Error in Condition Extraction\n")
        else:
            self.output.insert('1.0', "Condition Extraction Successful\n")
            for condition in self.conditions:
                self.output.insert('1.0', f"{condition}\n")
    
    def select_files(self):
        self.filepaths = filedialog.askopenfilenames(filetypes=[("PDF files", "*.pdf")])

    def run_function(self):
        if self.check_internet():
            if hasattr(self, 'filepaths'):
                self.search_term = self.search_term_entry.get()
                self.search_term_label.pack_forget()
                self.search_term_entry.pack_forget()
                data_table = self.start_process()
            else:
                self.output.insert('1.0', "No files selected\n")
        else:
            self.output.insert('1.0', "No internet connection\n")
    
    def progress_callback(self, progress):
    # Update the progress bar
        self.progress["value"] = progress * 100
            
    def start_process(self):
        for filepath in self.filepaths:
                    self.output.insert('1.0', f"Running function on {filepath}\n")
        self.progress = ttk.Progressbar(self, length=200, mode='determinate')
        self.progress.pack(side="top")
        self.progress.start()
        # res1 = text_extraction(np.array(self.filepaths))
        self.progress.stop()
        self.progress.pack_forget()
        res1 = 1
        if res1 == 0:
            self.output.insert('1.0', "Error in Text Extraction\n")
        else:
            self.output.insert('1.0', "Text Extraction Successful\n")
            self.options_frame.pack(side="top", pady=10)
        return self.filepaths

    def check_internet(self):
        try:
            # urllib.request.urlopen('http://google.com', timeout=1)
            socket.create_connection(("1.1.1.1", 53))
            return True
        except urllib.request.URLError:
            return False

root = tk.Tk()
root.geometry("500x500")  # Set the window size to 500x500
app = Application(master=root)
app.mainloop()