import pygame

# Initialize Pygame
pygame.init()

# Set up the display
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Visualize Tool")

# Colors
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)


rect = pygame.Rect(100,100,50,50)
def readInputFile():
        lines=""
        with open('input.txt') as f:
            lines += f.readline()
        return lines
lines = readInputFile()

# Main game loop
running = True
while running:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Update game logic (if any)

    # Draw graphics
    screen.fill(WHITE)  # Fill the screen with white
    pygame.draw.rect(screen,BLUE,rect)  # Draw a blue rectangle


    #read input file
   

    #control the rect 
    
   
    for line in lines:
        if line == "u":
            rect.y -= 10
        elif line == "d":
            rect.y += 10
        elif line == "l":
            rect.x -= 10
        elif line == "r":
            rect.x += 10
        #sleep
        pygame.time.delay(50)
    line = ""

    # Keep the rectangle on the screen
    if rect.x < 0:
        rect.x = 0
    if rect.y < 0:
        rect.y = 0
    if rect.x > screen_width - rect.width:
        rect.x = screen_width - rect.width
    if rect.y > screen_height - rect.height:
        rect.y = screen_height - rect.height


    # Update the display
    pygame.display.flip()

# Quit Pygame
pygame.quit()