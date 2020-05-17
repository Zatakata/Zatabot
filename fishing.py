from tkinter import *
import cv2
import numpy as np
from PIL import ImageGrab
import time
import pyautogui
import threading
from random import randint

pyautogui.FAILSAFE = False  # Отключает выброс исключения при коррдинатах 0:0


class Fishing:
    def __init__(self, root, startBtn):
        # главное окно приложения
        self.root = root

        # кнопка запуска бота
        self.startBtn = startBtn

        # начальный шаблон поплавка
        self.temp = cv2.imread("data/temp.png")
        self.temp = cv2.cvtColor(self.temp, cv2.COLOR_BGR2GRAY)

        # Координаты поплавка на экране
        self._xFloat = 0
        self._yFloat = 0

        # Ширина и высота шаблона поплавка
        self._wFloat = self.temp.shape[1::-1][0]
        self._hFloat = self.temp.shape[1::-1][1]

        # Позиция поплавка в миниигре
        self._xFloatMinigame = 90

        # Кол-во пойманных рыб
        self.caught = 0
        # Состояние бота (вкл/выкл)
        self._isRun = False
        # Сила забрасывания поплавка
        self._throwPower = 100
        # Кол-во забросов поплавка в цикле
        self._numberThrows = 1

        # Использование еды
        self._useFood = False
        # Использование наживки
        self._baitCount = 0

    # Сохранение настроек бота
    def update_settings(self, throwPower, numberThrows):
        self._throwPower = throwPower
        self._numberThrows = numberThrows

    # Запуск бота
    def on(self):
        self._isRun = True

        Label(self.root, text='Пойманой рыбы: ').grid(row=1, column=0, padx=5)

        self.countFish = Label(self.root, text=self.caught)
        self.countFish.grid(row=1, column=1, padx=5)

        self.startBtn.unbind('<Button-1>')
        self.startBtn.config(text='Остановить')
        self.startBtn.bind(
            '<Button-1>', lambda event: threading.Thread(target=self.off).start())

        time.sleep(2)  # Задержка перед включение бота
        self.init()

    # Остановка бота
    def off(self):
        self._isRun = False

        self.startBtn.unbind('<Button-1>')
        self.startBtn.config(text='Запустить')
        self.startBtn.bind(
            '<Button-1>', lambda event: threading.Thread(target=self.on).start())

    # Переснять шаблон
    def _reshoot_temp(self):
        matchTemp = ImageGrab.grab(
            bbox=(self._xFloat, self._yFloat, self._xFloat + self._wFloat, self._yFloat + self._hFloat))
        matchTemp.save('data/temp.png')

    # Перезапуск бота
    def _restart(self):
        self.off()
        pyautogui.typewrite('s')

        time.sleep(7)

        self._isRun = True
        self._fishing_loop()

    # съесть еду
    def _eat_food(self):
        self._useFood = True
        t = threading.Timer(1800.0, self._eat_food)
        t.start()

    # Заброс удочки
    def _throw_float(self, x=1600, y=400, power=0.5):
        pyautogui.moveTo(x, y)
        pyautogui.mouseDown(button='left')
        time.sleep(power)
        pyautogui.mouseUp(button='left')
        # Рандомное перемещение курсора
        pyautogui.moveTo(randint(100, 1920 - x), randint(100, 1080 - y))
        time.sleep(2)

    def _find_float(self):  # Поиск поплавка на скрине
        baseScreen = ImageGrab.grab(bbox=(0, 0, 1920, 1080))
        baseScreen.save("data/base_screen.png")
        baseScreen = cv2.imread("data/base_screen.png")
        baseScreen = cv2.cvtColor(baseScreen, cv2.COLOR_BGR2GRAY)
        cv2.imwrite("data/base_screen_gray.png", baseScreen)

        res = cv2.matchTemplate(
            baseScreen, self.temp, cv2.TM_CCOEFF_NORMED)
        loc = np.where(res >= 0.7)

        for pt in zip(*loc[::-1]):
            x = int(pt[0])
            y = int(pt[1])

        return (x, y)

    # Проверка попловка на клев
    def _check_nibble(self, x, y):
        i = 0
        lastValue = 0
        while self._isRun:
            matchTemp = ImageGrab.grab(
                bbox=(self._xFloat, self._yFloat, x + self._wFloat, y + self._hFloat))

            mean = np.mean(matchTemp)

            if i == 0:
                lastValue = mean / 10
                i += 1
                continue

            # print(abs(round(lastValue - (mean / 10))))
            if abs(round(lastValue - (mean / 10))) > 0:
                # print('клюнул')
                pyautogui.moveTo(x, y)
                pyautogui.click()
                break

            lastValue = mean / 10
        matchTemp.save('data/temp.png')

    # Метод который играет в миниигру
    def _play_minigame(self):
        temp = cv2.imread('data/minigame_temp.png', 0)
        time.sleep(0.5)
        while self._isRun:
            scaleGame = ImageGrab.grab(
                bbox=(840, 540, 1080, 570))
            scaleGame.save('data/scaleGame.png')

            scaleGame = cv2.imread('data/scaleGame.png')
            scaleGame = cv2.cvtColor(scaleGame, cv2.COLOR_BGR2GRAY)

            res = cv2.matchTemplate(
                scaleGame, temp, cv2.TM_CCOEFF_NORMED)
            loc = np.where(res >= 0.7)

            for pt in zip(*loc[::-1]):
                self._xFloatMinigame = int(pt[0])

            if self._xFloatMinigame < 120:
                pyautogui.mouseDown(button='left')
            else:
                pyautogui.mouseUp(button='left')

            if len(loc[0]) == 0:
                pyautogui.mouseUp(button='left')
                # print('Выловил!')
                break

    # инициализация бота при запуске
    def init(self):
        self.caught = 0
        self._throw_float()
        x, y = self._find_float()
        self._xFloat = x
        self._yFloat = y
        self._check_nibble(self._xFloat, self._yFloat)
        self._play_minigame()
        time.sleep(randint(5, 10))

        self._eat_food()
        time.sleep(1)

        self._fishing_loop()

    # Цикл работы бота
    def _fishing_loop(self):
        while self._isRun:
            t = threading.Timer(60.0, self._reshoot_temp)
            t.start()
            t2 = threading.Timer(130.0, self._restart)
            t2.start()

            self._throw_float()
            self._find_float()
            self._check_nibble(self._xFloat, self._yFloat)
            t2.cancel()
            self._play_minigame()
            if self._useFood:
                pyautogui.typewrite('2')
                self._useFood = False
                time.sleep(2)

            self._baitCount += 1
            if self._baitCount >= 10:
                pyautogui.typewrite('1')
                time.sleep(2)

                self._baitCount = 0

            self.caught += 1
            self.countFish.update()
            t.cancel()

            time.sleep(randint(3, 7))
