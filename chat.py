import pygame
from config import Config
import Caissa_BC_Player_Remark_Generation as Caissa


class Chat:

    def __init__(self):
        self.message = ""
        self.config = Config()

    # blit methods
    def clear_chat(self, surface):
        color_white = (255, 255, 255)
        # rect
        rect = (800, 0, 400, 800)
        # blit
        pygame.draw.rect(surface, color_white, rect)

    # blit methods
    def show_message(self, surface):
        font = pygame.font.SysFont('monospace', 45, bold=True)
        black = (0, 0, 0)
        drawText(surface, self.message, black, font)

    def new_message(self, eval):
        self.message = Caissa.make_remark(eval)

    def reset(self):
        self.__init__()

# draw some text into an area of a surface
# automatically wraps words
# returns any text that didn't get blitted
def drawText(surface, text, color, font, aa=False, bkg=None):
    rect = pygame.Rect(800, 0, 400, 800)
    y = rect.top
    lineSpacing = -2

    # get the height of the font
    fontHeight = font.size("Tg")[1]

    while text:
        i = 1

        # determine if the row of text will be outside our area
        if y + fontHeight > rect.bottom:
            break

        # determine maximum width of line
        while font.size(text[:i])[0] < rect.width and i < len(text):
            i += 1

        # if we've wrapped the text, then adjust the wrap to the last word
        if i < len(text):
            i = text.rfind(" ", 0, i) + 1

        # render the line and blit it to the surface
        if bkg:
            image = font.render(text[:i], 1, color, bkg)
            image.set_colorkey(bkg)
        else:
            image = font.render(text[:i], aa, color)

        surface.blit(image, (rect.left, y))
        y += fontHeight + lineSpacing

        # remove the text we just blitted
        text = text[i:]

    return text