from fishing import Fishing
from tkinter import *
from tkinter import messagebox as mb
import threading

root = Tk()
root.geometry('300x100')
root.config(padx=15, pady=15)
root.title('Zatabot[BETA]')


def aboutProgramm():
    mb.showinfo('О программе',
                'Бот для albion online \n Версия: v0.1.8 [alpha] \n Автор: Zatakata \n Лицензия: activated')


def openSettings():
    settingsWindow = Toplevel(root)
    settingsWindow.config(padx=15, pady=15)
    settingsWindow.title('Настройки')

    Label(settingsWindow, text='Сила броска').grid(row=0, column=0)
    throwPower = Spinbox(settingsWindow, from_=0.1, to=1, increment=0.1)
    throwPower.grid(row=0, column=2)

    Label(settingsWindow, text='Кол-во бросков').grid(row=1, column=0)
    numberThrows = Spinbox(settingsWindow, from_=1, to=5000, increment=1)
    numberThrows.grid(row=1, column=2, pady=10)

    saveSettingsBtn = Button(settingsWindow, text='Сохранить')
    saveSettingsBtn.grid(row=2, column=0, columnspan=3, sticky=N+S+W+E)
    saveSettingsBtn.bind(
        '<Button-1>', lambda event: fishing.updateSettings(throwPower.get(), numberThrows.get()))


mainmenu = Menu(root)
mainmenu.add_command(label='О программе', command=aboutProgramm)
root.config(menu=mainmenu)

startBtn = Button(text='Запустить')
startBtn.grid(row=0, column=0, padx=5, pady=10, sticky=N+S+W+E)

settingsBtn = Button(text='Настройки', command=openSettings)
settingsBtn.grid(row=0, column=2, padx=5, pady=10, sticky=N+S+W+E)


fishing = Fishing(root, startBtn=startBtn)


startBtn.bind(
    '<Button-1>', lambda event: threading.Thread(target=fishing.on).start())

root.mainloop()
