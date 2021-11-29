from PyQt5.QtWidgets import QApplication, QInputDialog, QWidget, QTableWidgetItem
from PyQt5 import QtCore, QtGui, QtWidgets
import os, sys
import pygame
from pygame.locals import *
import random
import math
if not pygame.font: print('Warning: fonts disabled')
if not pygame.mixer: print('Warning: sound disabled')
NAME = ''
class MyDialog(QWidget):
    def __init__(self,):
        super().__init__()
        self.initUI()

    def initUI(self):
        global NAME
        while NAME == '':
            NAME, okBtnPressed = QInputDialog.getText(self,
                                                      "Введите имя", '''Готов ли ты приисполниться в своем познании??
Как тетебя зовут, боец?''')
        if okBtnPressed:
            return

class BSprite(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
    def load_image(self,name, colorkey=None):
        fullname = os.path.join("images",name)
        try:
            image = pygame.image.load(fullname)
        except pygame.error as message:
            print('Cannot load image: ', name)
            raise SystemExit(message)
        image = image.convert()
        if colorkey is not None:
            if colorkey is -1:
                colorkey = image.get_at((0,0))
            image.set_colorkey(colorkey,RLEACCEL)
        return image, image.get_rect()

class PyStudentMain:
    """Main Class, initializes the game"""
    COLOR = ((20, 200, 0))
    MAX_SCORE = 1000

    def __init__(self, width=1200,height=800):
        app = QApplication(sys.argv)
        ex = MyDialog()
        pygame.init()
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((self.width, self.height))

        self.background = pygame.Surface(self.screen.get_size())
        self.background = self.background.convert()
        self.background.fill(PyStudentMain.COLOR)
        self.level = 0
        self.total_pellets = 0

    def run(self):
        self.loadSprites()

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()
                elif event.type == KEYDOWN:
                    if event.key in [K_RIGHT, K_LEFT, K_UP, K_DOWN]:
                        self.student.startmove(event.key)
                elif event.type == KEYUP:
                    if event.key in [K_RIGHT, K_LEFT, K_UP, K_DOWN]:
                        self.student.stopmove(event.key)
            #Screen
            self.screen.blit(self.background, (0, 0))
            self.student.update()
            self.rollForThreat()
            self.threat_sprites.update()
            self.student_sprites.draw(self.screen)
            self.pellet_sprites.draw(self.screen)
            self.threat_sprites.draw(self.screen)
            if len(self.pellet_sprites.sprites()) > 0 :
                lstCols = pygame.sprite.spritecollide(self.student,self.pellet_sprites, True)
                self.total_pellets += len(lstCols)
                self.level += len(lstCols)
                self.updateScores()
            else:
                self.loadPellets()
                self.level = min(PyStudentMain.MAX_SCORE,self.level + 15)
                self.updateScores()
            if len(self.pellet_sprites.sprites()) > 0:
                lstCols = pygame.sprite.groupcollide(self.student_sprites,self.threat_sprites,True,True)
                if len(lstCols) > 0:
                    self.loadStudent()
                    self.level = max(0,self.level-20)
                    self.updateScores()
            for sprite in self.threat_sprites.sprites():
                if sprite.offScreen():
                    sprite.kill()
            self.updateScores()
            pygame.display.flip()
            pygame.time.delay(10)


    def updateScores(self):
        if pygame.font:
            font = pygame.font.Font(None, 36)
            text = font.render("%s`s level: %d  --  Total Books: %s" % (NAME,self.level, self.total_pellets), 1, (255, 0, 0))
            textpos = text.get_rect(centerx=self.width/2)
            self.screen.blit(text, textpos)

    def rollForThreat(self):
        if random.randint(0,PyStudentMain.MAX_SCORE) < self.level:
            #TODO: Make sure threats don't spawn next to player
            self.threat_sprites.add(Threat(self.width,self.height,self.student.rect))

    def loadSprites(self):
        self.loadStudent()
        self.loadPellets()
        self.threat_sprites = pygame.sprite.Group()

    def loadPellets(self):
        nNumHorizontal = int(self.width/80)
        nNumVertical   = int(self.height/80)
        self.pellet_sprites = pygame.sprite.Group()
        for x in range(nNumHorizontal):
            for y in range(nNumVertical):
                self.pellet_sprites.add(Pellet(pygame.Rect(x*80,30+y*80,60,60)))

    def loadStudent(self):
        try:    self.student.kill()
        except: pass
        #Snakes
        self.student = Student(self.width,self.height)
        self.student_sprites = pygame.sprite.RenderPlain((self.student))

class Student(BSprite):
    X_DIST = 10
    Y_DIST = 10
    SAFE_DISTANCE = 175
    def __init__(self,maxX,maxY):
        BSprite.__init__(self)
        self.maxX = maxX
        self.maxY = maxY
        self.image_right, self.rect = self.load_image('student.png',-1)
        self.image_left, self.rect = self.load_image('student.png',-1)
        self.image_up, self.rect = self.load_image('student.png',-1)
        self.image_down, self.rect = self.load_image('student.png',-1)
        self.image = self.image_right
        self.pellets = 0
        self.xMove = 0
        self.yMove = 0

    def startmove(self,key):
        if   (key == K_RIGHT): self.xMove = Student.X_DIST
        elif (key == K_LEFT): self.xMove = -Student.X_DIST
        elif (key == K_DOWN): self.yMove = Student.Y_DIST
        elif (key == K_UP): self.yMove = -Student.Y_DIST

    def stopmove(self,key):
        if   (key == K_RIGHT): self.xMove = 0
        elif (key == K_LEFT): self.xMove = 0
        elif (key == K_DOWN): self.yMove = 0
        elif (key == K_UP): self.yMove = 0

    def getRightX(self):
        return self.rect.x + self.rect.width
    def getBottomY(self):
        return self.rect.y + self.rect.height

    def update(self):
        if self.xMove >= 0: self.image = self.image_right
        elif self.xMove < 0: self.image = self.image_left
        if self.yMove > 0: self.image = self.image_down
        elif self.yMove < 0: self.image = self.image_up
        if self.xMove != 0 or self.yMove != 0:
            localXMove = self.xMove
            localYMove = self.yMove
            if self.rect.x + self.xMove < 0 or self.getRightX() + self.xMove > self.maxX:
                localXMove = 0
            if self.rect.y + self.yMove < 0 or self.getBottomY() + self.yMove > self.maxY:
                localYMove = 0
            self.rect.move_ip(localXMove,localYMove)

class Pellet(BSprite):
    def __init__(self, rect=None):
        BSprite.__init__(self)
        self.image, self.rect = self.load_image('pellet.png',-1)
        if rect != None:
            self.rect = rect

def distance(tuple1,tuple2):
    return math.sqrt(math.pow(tuple1[0]-tuple2[0],2) + math.pow(tuple1[1]-tuple2[1],2))

class Threat(BSprite):
    MAX_SPEED = 3
    def __init__(self,maxX,maxY,studentRect=None):
        BSprite.__init__(self)
        self.maxX = maxX
        self.maxY = maxY
        self.image, self.rect = self.load_image('dart.png',-1)

        while True:
            x = random.randint(0,maxX-self.rect.width)
            y = random.randint(0,maxY-self.rect.height)
            self.rect = pygame.Rect(x,y,60,100)

            if studentRect != None and distance(studentRect,self.rect) < Student.SAFE_DISTANCE:
                continue
            break
        while True:
            self.xMove = random.randint(-Threat.MAX_SPEED,Threat.MAX_SPEED)
            self.yMove = random.randint(-Threat.MAX_SPEED,Threat.MAX_SPEED)
            if self.xMove != 0 or self.yMove != 0: break
    def update(self):
        if self.xMove != 0 or self.yMove != 0:
            self.rect.move_ip(self.xMove,self.yMove)

    def getRightX(self):
        return self.rect.x + self.rect.width
    def getBottomY(self):
        return self.rect.y + self.rect.height
    def offScreen(self):
        return self.rect.x < 0 or \
                self.rect.y < 0 or \
                self.getBottomY() > self.maxY or \
                self.getRightX() > self.maxX
if __name__ == "__main__":

    MainWindow = PyStudentMain()
    MainWindow.run()
