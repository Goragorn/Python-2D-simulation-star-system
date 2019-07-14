__author__ = 'Michal'

import pygame

from pygame.locals import *
import sys
import time
import math
import random

# Zastosowanie wzorca Singleton z metaclass
class SingletonMetaClass(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(SingletonMetaClass, cls).__call__(*args, **kwargs)
        else:
            cls._instances[cls].__init__(*args, **kwargs)
        return cls._instances[cls]


# Klasa WindowsSize jest singletonem utworzonym do przechowywania zmiennych odpowiedzialnych za wielkosc okna
class WindowSize(metaclass=SingletonMetaClass):

    def __init__(self, x, y):
        self._WindowSizeX = x
        self._WindowSizeY = y

    @property
    def windowSizeX(self):
        return self._WindowSizeX

    @property
    def windowSizeY(self):
        return self._WindowSizeY

    def setWindowSize(self, WindowSizeX, WindowSizeY):
        self._WindowSizeX = WindowSizeX
        self._WindowSizeY = WindowSizeY

# Klasa Sphere tworzy obiekty "planety" oraz posiada funkcje do poruszania ich
class Sphere (pygame.sprite.Sprite):
    SphereRadius = NotImplemented

    def __init__(self, color, radius, location, a, b, c, speed):
        pygame.sprite.Sprite.__init__(self)
        self.SphereRadius = radius
        # Utworzenie powierzni na której będzie narysowana kula
        self.frame = pygame.Surface((radius*2, radius*2))
        # Wypełnienie powierzchni kolorem białym
        self.frame.fill((255, 255, 255))
        # Wywołanie funkcji rysującej koło
        pygame.draw.circle(self.frame, color, (radius, radius), radius, 0)
        # Przekazanie do rect współrzędnych okręgu
        self.rect = self.frame.get_rect()
        # Lokalizacja okręgu
        self.rect.topleft = location
        # Prędkość
        self.predkosc = 0.00
        self.predkosc = speed
        # Przypisanie pierwotnej wylosowanej prędkości do dodatkowej zmiennej predkoscX,
        # predkoscX nazstepnie zostaje stale dodawana do predkosc przy wywołaniu funkcji
        self.predkoscX = self.predkosc
        # parametry a,b,c krzywych Lissajous
        self.a = 80
        self.b = 120
        self.c = 39.3

        self.a = a
        self.b = b
        self.c = c
        self.prevOoS = 0.0

        self.flagAccelerate = True
    # Funkcja: Obliczanie ogniska elipsy w zależności od parametru a oraz b
    # W przeciwnym wypadku elipsa jest kołem i środek koła jest ogniskiem
    def focusPoint (self):

        if(self.a < self.b):
            return math.sqrt((self.b * self.b) - (self.a * self.a))
        elif(self.a > self.b):
            return math.sqrt((self.a * self.a) - (self.b * self.b))
        else:
            return 0

    # Funkcja: wprawiająca w ruch planety
    def moveSpheres(self, windowSize):

        # Wyliczane są kolejne pozycje (x,y) z równań Lissajous
        # W zależności od parametrów a,b zostaje zastosowana I prawa Keplera
        # Słońce znajduje się w jednym z ognisk orbity po której porusza się planeta

        if (self.a < self.b):
            # Pozycja planety X
            self.rect.left = self.b * math.sin(self.predkoscX) + (WielkoscOkna.windowSizeX / 2) - self.focusPoint()/3
            # Pozycja planety Y
            self.rect.top = self.a * math.sin(self.predkoscX + self.c) + (WielkoscOkna.windowSizeY / 2)

            # Zastosowanie II prawa Keplera
            # Odleglosc od Słońca
            OoS = self.wektorOoS(self.rect.left, self.rect.top)

            # Jeżeli OoS jest większe od a oraz oddala się od Słońca to zwiększ prędkość
            if(OoS > self.a and self.prevOoS > 0 and OoS > self.prevOoS and self.flagAccelerate == True):
                self.predkosc += 0.005
                self.flagAccelerate = False
            elif (OoS > self.a and self.prevOoS > 0 and OoS < self.prevOoS and self.flagAccelerate == False):
                self.predkosc -= 0.005
                self.flagAccelerate = True
            self.prevOoS = OoS
        else:
            # Pozycja planety X
            self.rect.left = self.b * math.sin(self.predkoscX) + (WielkoscOkna.windowSizeX / 2)
            # Pozycja planety Y
            self.rect.top = self.a * math.sin(self.predkoscX + self.c) + (WielkoscOkna.windowSizeY / 2) - self.focusPoint()/3

            # Zastosowanie II prawa Keplera
            # Odleglosc od Słońca
            OoS = self.wektorOoS(self.rect.left, self.rect.top)

            # Jeżeli OoS jest większe od b oraz oddala się od Słońca to zwiększ prędkość
            if(OoS > self.b and self.prevOoS > 0 and OoS > self.prevOoS and self.flagAccelerate == True):
                self.predkosc += 0.005
                self.flagAccelerate = False
            elif (OoS > self.b and self.prevOoS > 0 and OoS < self.prevOoS and self.flagAccelerate == False):
                self.predkosc -= 0.005
                self.flagAccelerate = True
            self.prevOoS = OoS

        # Wprawianie w ruch planet poprzez dodawanie stałej wartości prędkości
        self.predkoscX += self.predkosc

    # Funkcja: sprawdzanie kolizji
    def collision(x1, y1, r1, x2, y2, r2):
        if(x2-x1)**2+(y2-y1)**2 <= (r1+r2)**2:
            return True
        else:
            return False

    # Funkcja: Odległość od Słońca(OoS)
    def wektorOoS(self, pozycjaX, pozycjaY):
        # Pozycja x Słońca
        pozycjaSX = WielkoscOkna.windowSizeX
        # Pozycja y Słońca
        pozycjaSY = WielkoscOkna.windowSizeY

        # Jeżeli pozycja x i y planety są większe od wsp. Słońca to oblicz OoS
        if(pozycjaX > pozycjaSX and pozycjaY > pozycjaSY):
            return math.sqrt(math.pow((pozycjaX - pozycjaSX), 2)+math.pow((pozycjaY-pozycjaSY), 2))

        elif(pozycjaX > pozycjaSX and pozycjaY < pozycjaSY):
            return math.sqrt(math.pow((pozycjaX - pozycjaSX), 2)+math.pow((pozycjaSY-pozycjaY), 2))

        elif(pozycjaX < pozycjaSX and pozycjaY > pozycjaSY):
            return math.sqrt(math.pow((pozycjaSX - pozycjaX), 2)+math.pow((pozycjaY-pozycjaSY), 2))

        elif(pozycjaX < pozycjaSX and pozycjaY < pozycjaSY):
            return math.sqrt(math.pow((pozycjaSX - pozycjaX), 2)+math.pow((pozycjaSY-pozycjaY), 2))
        else:
            return 0

# Klasa guzika
class Button(object):
    ButtomColor = NotImplemented
    ButtonWidth = NotImplemented
    ButtonHeight = NotImplemented
    ButtonX = NotImplemented
    ButtonY = NotImplemented
    ButtonText = NotImplemented
    ButtonPaddingTop = NotImplemented
    ButtonPaddingLeft = NotImplemented

    def __init__(self, text, color, width, height, pos_x, pos_y, padding_left, padding_top):
        self.font = pygame.font.SysFont('Arial', 20)
        self.ButtomColor = color
        self.ButtonHeight = height
        self.ButtonText = text
        self.ButtonWidth = width
        self.ButtonX = pos_x
        self.ButtonY = pos_y
        self.ButtonPaddingTop = padding_top
        self.ButtonPaddingLeft = padding_left

    # Funkcja dodania guzika
    def addButton(self):
        self.rect = pygame.draw.rect(screen, self.ButtomColor, (self.ButtonX, self.ButtonY, self.ButtonWidth, self.ButtonHeight))
        screen.blit(self.font.render(self.ButtonText, True, (0,0,0)), (self.ButtonPaddingLeft+self.ButtonX, self.ButtonPaddingTop+self.ButtonY))
        pygame.display.update()

    def ButtonClick(self, click_x, click_y):
        if click_x >= self.ButtonX and click_x <= (self.ButtonX+self.ButtonWidth)and click_y>=self.ButtonY and click_y<=(self.ButtonY+self.ButtonHeight):
            return True
        else:
            return False

# Klasa pola do wprowadzania danych
class TextBox(object):
    TextBoxString = NotImplemented

    # Funkcja pobierania znaków wprowadzanych przez uzytkownika
    def get_key():
        while 1:
            event = pygame.event.poll()
            if event.type == KEYDOWN:
                return event.key
            else:
                pass

    # Ryskowanie pola do wprowadzania tekstu
    def display_box(screen, message):
       "Print a message in a box in the middle of the screen"
       # TextBox.TextBoxString = message
       fontobject = pygame.font.Font(None, 18)
       pygame.draw.rect(screen, (0, 0, 0),
                       ((screen.get_width() / 2) - 100,
                        (screen.get_height() / 2) - 10,
                        200, 20), 0)
       pygame.draw.rect(screen, (0,0,0),
                       ((screen.get_width() / 2) - 102,
                        (screen.get_height() / 2) - 12,
                        204, 24), 1)
       if len(message) != 0:
         screen.blit(fontobject.render(message, 1, (255, 255, 255)),
                    ((screen.get_width() / 2) - 100, (screen.get_height() / 2) - 10))
       pygame.display.flip()

    # Funkcja do obsługi wprowadzanych danych
    def ask(self, screen, question):
      pygame.font.init()
      current_string = ""
      self.TextBoxString = []
      TextBox.display_box(screen, question + ": " + "".join(current_string))
      while 1:
        inkey = TextBox.get_key()
        if inkey == K_BACKSPACE:
          current_string = current_string[:-1]
        elif inkey == K_RETURN:
          self.TextBoxString.append(current_string.lstrip(", "))
          current_string=""
          break
        elif inkey == 44:
            self.TextBoxString.append(current_string.lstrip(", "))
            current_string=", "
        elif inkey <= 57 and inkey >= 48 or inkey==46:
          current_string += chr(inkey)
        TextBox.display_box(screen, question + ": " + "".join(self.TextBoxString) + current_string)
      return current_string


if __name__ == '__main__':
    pygame.init()
    WielkoscOkna = WindowSize(700, 500)

    # Wielkość okna
    windowSize = (WielkoscOkna.windowSizeX, WielkoscOkna.windowSizeY)
    fontBig = pygame.font.SysFont('Arial', 36)

    # Tytuł programu
    pygame.display.set_caption('Solar system')
    screen = pygame.display.set_mode(windowSize, 0, 32)
    # Wypełnienie kolorem białym
    screen.fill((255, 255, 255))

    background = pygame.Surface(windowSize)
    background.fill((255, 255, 255))

    # Utworzenie obiektów planet
    planety = []
    delete = []
    button = Button("Dodaj planete", (120, 120, 120), 110, 50, 570, 50, 5, 12)

    while True:
        doUsuniecia = []
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if button.ButtonClick(event.pos[0], event.pos[1]):

                    kolor = TextBox()
                    rozmiar = TextBox()
                    x = TextBox()
                    y = TextBox()
                    z = TextBox()
                    print(kolor.ask(screen, "Kolor w formacie (r,g,b)"))
                    print(rozmiar.ask(screen, "Rozmiar"))
                    print(x.ask(screen, "X"))
                    print(y.ask(screen, "Y"))
                    print(z.ask(screen, "Z"))
                    planety.append(Sphere(((int(kolor.TextBoxString[0])%256),
                                           (int(kolor.TextBoxString[1])%256),
                                           (int(kolor.TextBoxString[2])%256)),
                                          int(rozmiar.TextBoxString[0]),
                                          (10, 10),
                                          int(x.TextBoxString[0]), int(y.TextBoxString[0]), float(z.TextBoxString[0]),
                                          round(random.uniform(0.009, 0.05), 3)))
        screen.blit(background, (0,0))

        # Utworzenie obiektu Słońce
        sun = Sphere((255, 255, 0), 25, (350, 250), 0, 0, 0, 0)
        screen.blit(sun.frame, sun.rect)

        # Wywołanie ruchu planety
        for planeta in planety:
            planeta.moveSpheres(windowSize)
            screen.blit(planeta.frame, planeta.rect)
        if len(planety) > 1:
            for i in range(0, len(planety)):
                for j in range(0, len(planety)):
                    if i != j:
                        if Sphere.collision(planety[i].rect.x, planety[i].rect.y, planety[i].SphereRadius, planety[j].rect.x, planety[j].rect.y, planety[j].SphereRadius):
                            if(planety[i].SphereRadius > planety[j].SphereRadius):
                                if(float(planety[j].SphereRadius / planety[i].SphereRadius) < 0.33):
                                    doUsuniecia.append(int(j))
                                elif(float(planety[j].SphereRadius / planety[i].SphereRadius) < 0.66):
                                    doUsuniecia.append(int(i))
                                    doUsuniecia.append(int(j))
                                else:
                                    screen.blit(fontBig.render("Game Over!", True, (0, 0, 0)), (350, 230))
                                    time.sleep(5)
                                    pygame.quit()
                            elif(planety[j].SphereRadius > planety[i].SphereRadius):
                                if(float(planety[i].SphereRadius / planety[j].SphereRadius) < 0.33):
                                    doUsuniecia.append(int(i))
                                elif(float(planety[i].SphereRadius / planety[j].SphereRadius) < 0.66):
                                    doUsuniecia.append(int(i))
                                    doUsuniecia.append(int(j))
                                else:
                                    screen.blit(fontBig.render("Game Over!", True, (0, 0, 0)), (350, 230))
                                    time.sleep(5)
                                    pygame.quit()
                            elif(planety[j].SphereRadius == planety[i].SphereRadius):
                                if(planety[i].SphereRadius < 5):
                                    doUsuniecia.append(int(i))
                                    doUsuniecia.append(int(j))
                                else:
                                    screen.blit(fontBig.render("Game Over!", True, (0, 0, 0)), (350, 230))
                                    time.sleep(5)
                                    pygame.quit()

        doUsuniecia.sort()
        doUsuniecia.reverse()
        usun = -1
        for i in range(len(doUsuniecia)):
            if(usun != doUsuniecia[i] and len(planety) > 0):
                usun = doUsuniecia[i]
                planety.pop(usun)

        del doUsuniecia
        # Dodanie guzika
        button.addButton()
        # Aktualizacja ekranu
        pygame.display.update()
        time.sleep(0.02)
