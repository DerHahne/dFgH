class Person:
    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y 
        self.timesNotDetected = 0
    def getId(self):
        return self.id
    def getX(self):
        return self.x
    def getY(self):
        return self.y
    def getTimesNotDetected(self):
        return self.timesNotDetected
    def updateCoords(self, newX, newY):
        self.x = newX
        self.y = newY
        self.timesNotDetected = 0
    def incrementTimesNotDetected(self):
        self.timesNotDetected += 1
