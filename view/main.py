import receiver
import tkinter
import socket
import settings


class Main(tkinter.Frame):
    """
    * Function to create the main view
    * @param tk.Frame frame object from tkinter lib
    """

    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.pack()
        self.create_widgets()
        master.geometry("%dx%d+0+0"
                        % (round(master.winfo_screenwidth() / 2), round(master.winfo_screenheight() / 2)))
        master.resizable(0, 0)
        self.firstclick = True
        master.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.channels = {}
        self.channel = None

        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.client_socket.connect((settings.SERVER_HOST, settings.SERVER_PORT))

        self.receive_thread = receiver.MessageReceiverHandler(self)
        self.receive_thread.start()

    """
    * Function to create view components
    * @param self to set the scope of the function
    """
    def create_widgets(self):
        # Set frame to the list box and scrollbar
        messages_frame = tkinter.Frame(self.master)
        self.my_msg = tkinter.StringVar()  # Variable to send the messages.
        self.my_msg.set("Type your messages here.")
        self.scrollbar = tkinter.Scrollbar(messages_frame)  # To navigate through past messages.
        self.msg_list = tkinter.Listbox(messages_frame, height=20, width=400, yscrollcommand=self.scrollbar.set, bd=5)
        self.sidebar = tkinter.Listbox(messages_frame, height=20, bd=5)
        self.sidebar.bind('<Double-Button>', self.on_sidebar_dbclick)
        self.sidebar.pack(side=tkinter.RIGHT)
        self.scrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)
        self.msg_list.pack(side=tkinter.LEFT, fill=tkinter.BOTH)
        self.msg_list.pack()
        messages_frame.pack()
        bottom_frame = tkinter.Frame(self.master)
        self.entry_field = tkinter.Entry(bottom_frame, textvariable=self.my_msg, width=100)
        self.entry_field.bind('<FocusIn>', self.on_entry_click)
        self.entry_field.bind("<Return>", self.send_message)
        self.send_button = tkinter.Button(bottom_frame, text="Send", width=20, command=self.send_message)
        self.send_button.pack(side="right")
        self.entry_field.pack(side="left")
        bottom_frame.pack()

    # Controller functions

    def on_entry_click(self, event):
        if self.firstclick:  # If this is the first time they clicked it
            self.firstclick = False
            self.entry_field.delete(0, "end")  # delete all the text in the entry

    def send_message(self, event=None):
        """Handles sending of messages."""
        message = self.my_msg.get().strip()

        if len(message) > 1000:
            self.msg_list.insert(tkinter.END, "The send message can not be longer than 100 characters!")
            self.msg_list.itemconfig(tkinter.END, fg="red")
        else:
            self.my_msg.set("")  # Clears input field.
            self.client_socket.send(message.encode(settings.ENCODING))

    def insert_message(self, color, message, channel="general"):
        if channel in self.channels:
            self.channels[channel].append({
                "message": message,
                "color": color
            })

        if channel == self.channel or channel == "general":
            self.msg_list.insert(tkinter.END, message)
            self.msg_list.itemconfig(tkinter.END, fg=color)
            self.msg_list.see(tkinter.END)

        if channel in self.channels and channel != "general" and channel != self.channel:
            index = self.sidebar.get(0, "end").index(channel)
            self.sidebar.itemconfig(index, fg='red')

    def on_sidebar_dbclick(self, event=None):
        channel_name = self.sidebar.get(tkinter.ANCHOR)
        self.client_socket.send(("/channel set " + channel_name).encode(settings.ENCODING))

    def change_channel(self, channel):
        index = self.sidebar.get(0, "end").index(channel)

        if self.channel in self.channels:
            channel_index = self.sidebar.get(0, "end").index(self.channel)
            self.sidebar.itemconfig(channel_index, fg='black')
        self.sidebar.itemconfig(index, fg='royal blue')
        self.channel = channel

        if channel in self.channels:
            self.msg_list.delete(0, 'end')
            for message in self.channels[channel]:
                self.msg_list.insert(tkinter.END, message["message"])
                self.msg_list.itemconfig(tkinter.END, fg=message["color"])
            self.msg_list.see(tkinter.END)

    def on_closing(self, event=None):
        try:
            # Close socket
            self.client_socket.shutdown(socket.SHUT_RDWR)
            self.client_socket.close()

            # Close window
            self.master.quit()
        except OSError:
            # Close window
            self.master.quit()
