import threading
import tkinter
from datetime import datetime

import enums
import settings


# Receive and print server messages
class MessageReceiverHandler(threading.Thread):
    def __init__(self, master):
        super().__init__()
        self.master = master

    def run(self):
        while True:
            received = self.master.client_socket.recv(settings.BUFSIZE).decode(settings.ENCODING)

            received_type_args = received.split(" ", 1)
            received_type = received_type_args[0]
            if len(received_type_args) > 1:
                received_args = received_type_args[1].lstrip()
            else:
                received_args = None

            if received_type == enums.ClientAction.ACTIVE_CHANNEL.value:
                self.master.change_channel(received_args)
            elif received_type == enums.ClientAction.CHANNEL.value:
                new_channels = {}
                self.master.sidebar.delete(0, 'end')
                channels = received_args.split(";")
                for channel in channels:
                    self.master.sidebar.insert(tkinter.END, channel)
                    self.master.sidebar.itemconfig(tkinter.END, fg='black')
                    if channel in self.master.channels:
                        new_channels[channel] = self.master.channels[channel]
                    else:
                        new_channels[channel] = []
                self.master.channels = new_channels.copy()
            elif received_type == enums.ClientAction.KICK.value:
                self.master.insert_message("tomato", "$ " + received_args)
                self.master.client_socket.send(("/" + enums.ClientAction.EXIT.value).encode(settings.ENCODING))
            elif received_type == enums.ClientAction.EXIT.value:
                self.master.insert_message("blue", "$ " + received_args)
                break
            elif received_type == enums.MessageType.INFO.value:
                for line in received_args.splitlines():
                    self.master.insert_message("dodger blue", "$ " + line)
            elif received_type == enums.MessageType.WARNING.value:
                for line in received_args.splitlines():
                    self.master.insert_message("dark orange", "$ " + line)
            elif received_type == enums.MessageType.ERROR.value:
                for line in received_args.splitlines():
                    self.master.insert_message("red2", "$ " + line)
            elif received_type == enums.MessageType.MESSAGE.value:
                message_args = received_args.split(" ", 3)
                message_timestamp = float(message_args[0])
                message_username = message_args[1].lstrip()
                message_channel = message_args[2].lstrip()
                message_text = message_args[3].lstrip()
                self.master.insert_message("lime green", "[%s] %s: %s"
                                           % (datetime.fromtimestamp(message_timestamp)
                                              .strftime(settings.DATETIME_FORMAT),
                                              message_username, message_text), message_channel)
            elif received_type == enums.MessageType.HELP.value:
                for line in received_args.splitlines():
                    self.master.insert_message("dark goldenrod", line)
            elif received_type == enums.MessageType.MOTD.value:
                motd_args = received_args.split(" ", 1)
                motd_channel = motd_args[0].lstrip()
                motd_message = motd_args[1].lstrip()
                self.master.insert_message("gray50", motd_message, motd_channel)
            elif received_type == enums.MessageType.BROADCAST.value:
                broadcast_args = received_args.split(" ", 2)
                broadcast_timestamp = float(broadcast_args[0])
                broadcast_username = broadcast_args[1].lstrip()
                broadcast_text = broadcast_args[2].lstrip()
                self.master.insert_message("purple", "[BROADCAST] [%s] %s: %s"
                                           % (datetime.fromtimestamp(broadcast_timestamp)
                                              .strftime(settings.DATETIME_FORMAT), broadcast_username, broadcast_text))
            elif received_type == enums.MessageType.PRIVATE.value:
                private_args = received_args.split(" ", 2)
                private_timestamp = float(private_args[0])
                private_username = private_args[1].lstrip()
                private_text = private_args[2].lstrip()
                self.master.insert_message("lan green", "[PRIVATE MESSAGE] [%s] %s: %s"
                                           % (datetime.fromtimestamp(private_timestamp)
                                              .strftime(settings.DATETIME_FORMAT), private_username, private_text))
            else:
                self.master.insert_message("red", "$ Received server message could not be parsed!")

        # Close socket
        self.master.client_socket.close()

        # Close window
        self.master.master.quit()
