def draw_text_with_outline(surface, text, font, x, y, text_color, outline_color):
    base = font.render(text, True, text_color)
    outline = font.render(text, True, outline_color)

    # Vẽ viền xung quanh
    surface.blit(outline, (x-2, y))
    surface.blit(outline, (x+2, y))
    surface.blit(outline, (x, y-2))
    surface.blit(outline, (x, y+2))

    # Vẽ chữ chính
    surface.blit(base, (x, y))