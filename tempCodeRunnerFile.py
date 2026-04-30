
     def __init__(self, player, duration=200):
          super().__init__()
          #Load slash      
          self.image= pygame.image.load("slash2.png").convert_alpha()
          
          #Scale the image
          self.image = pygame.transform