import tkinter
import view.main as main

root = tkinter.Tk()
root.title("Let's Talk!")
root.tk.call('wm', 'iconphoto', root.w, tkinter.PhotoImage(file='./resources/favico.png'))
app = main.Main(master=root)
app.mainloop()
