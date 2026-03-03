import pygame

def render_outlined_text(text, font, text_color, outline_color, outline_width):
    # 1. Render the outline surface multiple times, shifted around the center
    #    A common method is to blit the outline color text at multiple offsets.
    
    # First, render the text in the outline color
    outline_surface = font.render(text, True, outline_color)
    outline_width_pixels = outline_surface.get_width() + 2 * outline_width
    outline_height_pixels = outline_surface.get_height() + 2 * outline_width
    
    # Create a new surface large enough for the outline effect
    # Use convert_alpha() for transparency support
    text_surface = pygame.Surface((outline_width_pixels, outline_height_pixels), pygame.SRCALPHA)
    
    # Blit the outline surface around the central point
    for dx in range(-outline_width, outline_width + 1):
        for dy in range(-outline_width, outline_width + 1):
            if dx != 0 or dy != 0: # Skip the center
                text_surface.blit(outline_surface, (dx + outline_width, dy + outline_width))

    # 2. Render the main text in the foreground color and blit it in the center
    inner_text_surface = font.render(text, True, text_color).convert_alpha()
    
    # Blit the inner text onto the center of the combined surface
    text_surface.blit(inner_text_surface, (outline_width, outline_width))
    
    return text_surface

# Example Usage:
if __name__ == '__main__':
    pygame.init()
    screen = pygame.display.set_mode((400, 200))
    pygame.display.set_caption("Outlined Text Example")

    # Define colors and font
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    BLUE = (0, 0, 255)
    FONT_SIZE = 64
    OUTLINE_PX = 5
    
    # Load a system font, or a custom one using pygame.font.Font(filepath, size)
    font = pygame.font.SysFont(None, FONT_SIZE) 

    # Create the outlined text surface
    title_surface = render_outlined_text("Hello World", font, BLUE, BLACK, OUTLINE_PX)
    title_rect = title_surface.get_rect(center=(200, 100)) # Center the text surface

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill(WHITE)
        screen.blit(title_surface, title_rect) # Blit the combined surface
        pygame.display.flip()

    pygame.quit()
