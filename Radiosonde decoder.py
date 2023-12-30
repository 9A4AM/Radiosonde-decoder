import functools
import os
import tkinter as tk
from concurrent import futures

thread_pool_executor = futures.ThreadPoolExecutor(max_workers=1)


def tk_after(target):

    @functools.wraps(target)
    def wrapper(self, *args, **kwargs):
        args = (self,) + args
        self.after(0, target, *args, **kwargs)

    return wrapper


def submit_to_pool_executor(executor):

    def decorator(target):

        @functools.wraps(target)
        def wrapper(*args, **kwargs):
            return executor.submit(target, *args, **kwargs)

        return wrapper

    return decorator


class MainFrame(tk.Frame):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.master.geometry('550x680')
        self.master.title("Radiosonde decoder by 9A4AM")
        self.entry = tk.StringVar()
        label = tk.Label(
            self.master, text="Press START button for start radiosonde decode")
        label.pack()
       # entry = tk.Entry(self.master, textvariable=self.entry)
       # entry.insert(-1, "8.8.8.8")
       # entry.pack()
        self.button = tk.Button(
        self.master, text="START", command=self.on_button)
        self.button.pack()
        label2 = tk.Label(
            self.master, text="Received frames")
        label2.pack()
        self.text = tk.Text(self.master)
        self.text.config(state=tk.DISABLED)
        self.text.pack(padx=5, pady=5)
        label3 = tk.Label(
            self.master, text="Last frame")
        label3.pack()
        self.text1 = tk.Text(self.master)
        self.text1.config(state=tk.DISABLED, height = 3, width = 76)
        self.text1.pack()
        label4 = tk.Label(
            self.master, text="Last data")
        label4.pack()
        self.text2 = tk.Text(self.master)
        self.text2.config(state=tk.DISABLED, height = 3, width = 76)
        self.text2.pack()
    @tk_after
    def button_state(self, enabled=True):
        state = tk.NORMAL
        if not enabled:
            state = tk.DISABLED
        self.button.config(state=state)


    @tk_after
    def clear_text(self):
        self.text.config(state=tk.NORMAL)
        self.text.delete(1.0, tk.END)
        self.text.config(state=tk.DISABLED)

    @tk_after
    def insert_text(self, text):
        self.text.config(state=tk.NORMAL)
        self.text.insert(tk.END, text)
        self.text.config(state=tk.DISABLED)
    @tk_after
    def clear_text1(self):
        self.text1.config(state=tk.NORMAL)
        self.text1.delete(1.0, tk.END)
        self.text1.config(state=tk.DISABLED)

    @tk_after
    def insert_text1(self, text):
        self.text1.config(state=tk.NORMAL)
        self.text1.insert(tk.END, text)
        self.text1.config(state=tk.DISABLED)

    @tk_after
    def clear_text2(self):
        self.text2.config(state=tk.NORMAL)
        self.text2.delete(1.0, tk.END)
        self.text2.config(state=tk.DISABLED)

    @tk_after
    def insert_text2(self, text):
        self.text2.config(state=tk.NORMAL)
        self.text2.insert(tk.END, text)
        self.text2.config(state=tk.DISABLED)
    def on_button(self):
        self.ping()





    @submit_to_pool_executor(thread_pool_executor)
    def ping(self):
        self.button_state(False)
        self.clear_text()

        self.insert_text('Starting decode Radiosonde \n')
        os.chdir("C:\RS\decoders")
       # result = os.startfile("RS41.bat")
       # result = os.popen("ping "+self.entry.get()+" -n 15")
       # result = os.popen(""+self.entry.get()+"")
       # result = os.popen("dir")
       # result = os.popen("dir")
       # os.startfile("RS41.bat")
        result = os.popen("RS41.bat")

        for line in result:
            self.insert_text(line)
            self.clear_text1()
            self.clear_text2()
            # label4.destroy()
           #  self.insert_text(stream[57:65])
           # entry = tk.Entry(self.master, textvariable=self.entry)
           # entry.insert(-1, "8.8.8.8")
           # entry.delete(0, end)
           # entry.insert(-1, stream[57:100])
           # entry.pack()
           # self.clear_text1
            self.insert_text1(line)
            self.insert_text2(line[9:17])
            self.insert_text2(line[48:89])
           # self.insert_text1(line)
           # label4 = tk.Label(
           # self.master, text=line[49:89])
           # label4.pack(padx=5, pady=10, side=tk.LEFT)
            # label4 = tk.Label(self.master, text=line[49:89])
            # label4.pack(padx=5, pady=10, side=tk.LEFT)
            # label4 = tk.Label(self.master, text="green", bg="green", fg="black")
            # label4.pack(padx=5, pady=20, side=tk.LEFT)
            # label4 = tk.Label(self.master, text="blue", bg="blue", fg="white")
            # label4.pack(padx=5, pady=20, side=tk.LEFT)
        self.insert_text('Radiosonde decode finished')
        self.button_state(True)


if __name__ == '__main__':
    app = tk.Tk()
    main_frame = MainFrame()
    app.mainloop()
