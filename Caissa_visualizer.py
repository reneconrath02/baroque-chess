import pygame
from const import *
class Caissa_visualizer:

    def __init__(self):
        self.highest = False
        self.root = None
        self.best_branch = [10, 10, 10, 10]
        self.best_move = "(3, 0), (5, 5)"
        self.working_branch = {}
        self.working_branch['ply_2'] = 0
        self.working_branch['left'] = 0
        self.working_branch['right'] = 0
        self.working_branch['left_states'] = []
        self.working_branch['right_states'] = [0, 0]
        self.cutoffs = [False for i in range(3)]
        self.zobs = [False for i in range(3)]

    def __repr__(self):
        s = ''
        s += "root: " + str(self.root) + "\n"
        s += "best branch: " + str(self.best_branch) + "\n"
        s += "working branch: " + str(self.working_branch) + "\n"
        return s

    def update_working_children(self, eval, zobbed):
        if self.highest:
            self.update_children_maximizer(eval, zobbed)
        else:
            self.update_children_minimizer(eval, zobbed)

    def update_children_maximizer(self, eval, zobbed):
        v = round(eval, 2)
        # best on left, working on right
        if v > self.working_branch['right_states'][0]:
            self.working_branch['right_states'][0] = v
        else:
            self.working_branch['right_states'][1] = v
            if zobbed:
                self.zobs[2] = True
    def update_children_minimizer(self, eval, zobbed):
        v = round(eval, 2)
        # best on left, working on right
        if v < self.working_branch['right_states'][0]:
            self.working_branch['right_states'][0] = v
        else:
            self.working_branch['right_states'][1] = v
            if zobbed:
                self.zobs[2] = True

    def update_ply_1(self, eval, zobbed):
        v = round(eval, 2)
        self.working_branch['right'] = v
        if zobbed:
            self.zobs[1] = True

    def update_ply_2(self, eval, zobbed):
        v = round(eval, 2)
        self.working_branch['ply_2'] = v
        self.working_branch['left'] = v
        self.working_branch['left_states'] = [v]
        if zobbed:
            self.zobs[0] = True

    def update_best_branch(self, eval):
        v = round(eval, 2)
        self.best_branch = [v for i in range(4)]

    def clear_cutoffs(self):
        self.cutoffs = [False for i in range(9)]

    def clear_zobs(self):
        self.zobs = [False for i in range(9)]

    def show_state_graph(self, screen):
        if self.highest:
            self.draw_best_branch(screen)
            self.draw_working_branch(screen)
        else:
            self.draw_best_branch_minimize(screen)
            self.draw_working_branch_minimize(screen)
        self.draw_cutoffs(screen)

    def draw_best_branch(self, screen):
        color_white = (255,255,255)
        color_black = (0, 0, 0)
        smallfont = pygame.font.SysFont('arial',35)

        triangle_wid = 50
        triangle_hei = 86

        color_orange = (252, 186, 3)
        mid_y = WIDTH / 2

        # top triangle, representing current best found
        pygame.draw.polygon(screen, color_orange, ((mid_y, 5), (mid_y - triangle_wid, triangle_hei), (mid_y + triangle_wid, triangle_hei)))
        if self.best_branch[0] is not None:
            root_text = smallfont.render(str(self.best_branch[0]), True, color_black)
            screen.blit(root_text, (mid_y - 25, triangle_hei / 2))

        x_val = WIDTH / 3 - 100
        section_2_h = 200
        start_pos = (mid_y, triangle_hei)
        end_pos = (x_val, section_2_h)
        section_2_h = 200
        pygame.draw.line(screen, color_black, start_pos, end_pos, width=2)
        pygame.draw.polygon(screen, color_orange, ((x_val, section_2_h + triangle_hei), (x_val - triangle_wid, section_2_h), (x_val + triangle_wid, section_2_h)))
        if self.best_branch[1] is not None:
            t_text = smallfont.render(str(self.best_branch[1]), True, color_black)
            screen.blit(t_text, (x_val - 20, section_2_h + 10))
            smallfonter = pygame.font.SysFont('arial',25)
            t_text = smallfonter.render(str(self.best_move), True, color_black)
            screen.blit(t_text, (x_val + 40, section_2_h + 20))

        layer3_x = x_val
        section_3_h = 400
        start_pos = (x_val, section_2_h + triangle_hei)
        end_pos = (layer3_x, section_3_h)
        pygame.draw.line(screen, color_black, start_pos, end_pos, width=2)
        pygame.draw.polygon(screen, color_orange, ((layer3_x, section_3_h), (layer3_x - triangle_wid, section_3_h + triangle_hei), (layer3_x + triangle_wid, section_3_h + triangle_hei)))
        if self.best_branch[2] is not None:
            t_text = smallfont.render(str(self.best_branch[2]), True, color_black)
            screen.blit(t_text, (layer3_x - 20, section_3_h + 35))

        sq = 50
        layer4_x = layer3_x - 25
        section_4_h = 600
        start_pos = (layer3_x, section_3_h + triangle_hei)
        end_pos = (layer4_x + 25,section_4_h)
        pygame.draw.line(screen, color_black, start_pos, end_pos, width=2)
        rect = pygame.Rect(layer4_x,section_4_h,sq,sq)
        pygame.draw.rect(screen,color_black,rect)
        if self.best_branch[3] is not None:
            t_text = smallfont.render(str(self.best_branch[3]), True, color_white)
            screen.blit(t_text, rect)

    def draw_best_branch_minimize(self, screen):
        color_white = (255,255,255)
        color_black = (0, 0, 0)
        smallfont = pygame.font.SysFont('arial',35)

        triangle_wid = 50
        triangle_hei = 86

        color_orange = (252, 186, 3)
        mid_y = WIDTH / 2

        pygame.draw.polygon(screen, color_orange, ((mid_y, triangle_hei), (mid_y - triangle_wid, 5), (mid_y + triangle_wid, 5)))
        if self.best_branch[0] is not None:
            root_text = smallfont.render(str(self.best_branch[0]), True, color_black)
            screen.blit(root_text, (mid_y - 20, triangle_hei / 2 - 30))

        x_val = WIDTH / 3 - 100
        section_2_h = 200
        start_pos = (mid_y, triangle_hei)
        end_pos = (x_val, section_2_h)
        section_2_h = 200
        pygame.draw.line(screen, color_black, start_pos, end_pos, width=2)
        pygame.draw.polygon(screen, color_orange, ((x_val, section_2_h), (x_val - triangle_wid, section_2_h+triangle_hei), (x_val + triangle_wid, section_2_h+triangle_hei)))
        if self.best_branch[1] is not None:
            t_text = smallfont.render(str(self.best_branch[1]), True, color_black)
            screen.blit(t_text, (x_val - 15, section_2_h + 30))
            smallfonter = pygame.font.SysFont('arial',25)
            t_text = smallfonter.render(str(self.best_move), True, color_black)
            screen.blit(t_text, (x_val + 40, section_2_h + 20))

        layer3_x = x_val
        section_3_h = 400
        start_pos = (x_val, section_2_h + triangle_hei)
        end_pos = (layer3_x, section_3_h)
        pygame.draw.line(screen, color_black, start_pos, end_pos, width=2)
        pygame.draw.polygon(screen, color_orange, ((layer3_x, section_3_h + triangle_hei), (layer3_x - triangle_wid, section_3_h), (layer3_x + triangle_wid, section_3_h)))
        if self.best_branch[2] is not None:
            t_text = smallfont.render(str(self.best_branch[2]), True, color_black)
            screen.blit(t_text, (layer3_x - 15, section_3_h + 15))

        sq = 50
        layer4_x = layer3_x - 25
        section_4_h = 600
        start_pos = (layer3_x, section_3_h + triangle_hei)
        end_pos = (layer4_x + 25,section_4_h)
        pygame.draw.line(screen, color_black, start_pos, end_pos, width=2)
        rect = pygame.Rect(layer4_x,section_4_h,sq,sq)
        pygame.draw.rect(screen,color_black,rect)
        if self.best_branch[3] is not None:
            t_text = smallfont.render(str(self.best_branch[3]), True, color_white)
            screen.blit(t_text, rect)

    def draw_working_branch(self, screen):
        color_white = (255,255,255)
        color_black = (0, 0, 0)
        color_yellow = (255, 201, 41)
        color_teal = (79, 200, 224)
        smallfont = pygame.font.SysFont('arial',35)

        triangle_wid = 50
        triangle_hei = 86

        color_orange = (252, 186, 3)
        mid_y = WIDTH / 2

        x_val = 800
        section_2_h = 200
        start_pos = (mid_y, triangle_hei)
        end_pos = (x_val, section_2_h)
        pygame.draw.line(screen, color_black, start_pos, end_pos, width=2)
        pygame.draw.polygon(screen, color_orange, ((x_val, section_2_h + triangle_hei), (x_val - triangle_wid, section_2_h), (x_val + triangle_wid, section_2_h)))
        if self.working_branch["ply_2"] is not None:
            if self.zobs[0]:
                text_eval = smallfont.render(str(self.working_branch["ply_2"]) , True , color_teal)
            else:
                text_eval = smallfont.render(str(self.working_branch["ply_2"]) , True , color_black)
            screen.blit(text_eval, (x_val - 15, section_2_h + 15))

        # left triangle
        section_3_h = 400
        layer3_x = x_val - 100
        start_pos = (x_val, section_2_h + triangle_hei)
        end_pos = (layer3_x, section_3_h)
        pygame.draw.line(screen, color_black, start_pos, end_pos, width=2)
        pygame.draw.polygon(screen, color_orange, ((layer3_x, section_3_h), (layer3_x - triangle_wid, section_3_h + triangle_hei), (layer3_x + triangle_wid, section_3_h + triangle_hei)))
        if self.working_branch["left"] is not None:
            text_eval = smallfont.render(str(self.working_branch["left"]) , True , color_black)
            screen.blit(text_eval, (layer3_x - 20, section_3_h + 35))

        # right triangle
        layer3_x = x_val + 100
        start_pos = (x_val, section_2_h + triangle_hei)
        end_pos = (layer3_x, section_3_h)
        pygame.draw.line(screen, color_black, start_pos, end_pos, width=2)
        pygame.draw.polygon(screen, color_orange, ((layer3_x, section_3_h), (layer3_x - triangle_wid, section_3_h + triangle_hei), (layer3_x + triangle_wid, section_3_h + triangle_hei)))
        if self.working_branch["right"] is not None:
            if self.zobs[1]:
                text_eval = smallfont.render(str(self.working_branch["right"]) , True , color_teal)
            else:
                text_eval = smallfont.render(str(self.working_branch["right"]) , True , color_black)
            screen.blit(text_eval, (layer3_x - 20, section_3_h + 35))

        layer3_x = x_val - 100
        section_4_h = 600
        left_states = self.working_branch['left_states']
        for i in range(len(left_states)):
            # draw some squares?
            layer4_x = 0
            if i == 0:
                layer4_x = layer3_x - 90
            elif i == 1:
                layer4_x = layer3_x - 25
            elif i == 2:
                layer4_x = layer3_x + 40
            sq = 50
            start_pos = (layer3_x, section_3_h + triangle_hei)
            end_pos = (layer4_x + 25,section_4_h)
            pygame.draw.line(screen, color_black, start_pos, end_pos, width=2)
            rect = pygame.Rect(layer4_x,section_4_h,sq,sq)
            pygame.draw.rect(screen,color_black,rect)
            if left_states[i] is not None:
                text_eval = smallfont.render(str(left_states[i]) , True , color_white)
                screen.blit(text_eval, rect)

        layer3_x = x_val + 100
        section_4_h = 600
        right_states = self.working_branch['right_states']
        for i in range(len(right_states)):
            layer4_x = 0
            if i == 0:
                layer4_x = layer3_x - 90
            elif i == 1:
                layer4_x = layer3_x - 25
            elif i == 2:
                layer4_x = layer3_x + 40
            sq = 50
            start_pos = (layer3_x, section_3_h + triangle_hei)
            end_pos = (layer4_x + 25,section_4_h)
            pygame.draw.line(screen, color_black, start_pos, end_pos, width=2)
            rect = pygame.Rect(layer4_x,section_4_h,sq,sq)
            pygame.draw.rect(screen,color_black,rect)
            if right_states[i] is not None:
                if i == 1 and self.zobs[2]:
                    text_eval = smallfont.render(str(right_states[i]) , True , color_yellow)
                else:
                    text_eval = smallfont.render(str(right_states[i]) , True , color_white)
                screen.blit(text_eval, rect)

    def draw_working_branch_minimize(self, screen):
        color_white = (255,255,255)
        color_black = (0, 0, 0)
        color_yellow = (255, 201, 41)
        color_teal = (79, 200, 224)
        smallfont = pygame.font.SysFont('arial',35)

        triangle_wid = 50
        triangle_hei = 86

        color_orange = (252, 186, 3)
        mid_y = WIDTH / 2

        x_val = 800
        section_2_h = 200
        start_pos = (mid_y, triangle_hei)
        end_pos = (x_val, section_2_h)
        pygame.draw.line(screen, color_black, start_pos, end_pos, width=2)
        pygame.draw.polygon(screen, color_orange, ((x_val, section_2_h), (x_val - triangle_wid, section_2_h + triangle_hei), (x_val + triangle_wid, section_2_h + triangle_hei)))
        if self.working_branch["ply_2"] is not None:
            if self.zobs[0]:
                text_eval = smallfont.render(str(self.working_branch["ply_2"]) , True , color_teal)
            else:
                text_eval = smallfont.render(str(self.working_branch["ply_2"]) , True , color_black)
            screen.blit(text_eval, (x_val - 15, section_2_h + 30))

        # left triangle
        section_3_h = 400
        layer3_x = x_val - 100
        start_pos = (x_val, section_2_h + triangle_hei)
        end_pos = (layer3_x, section_3_h)
        pygame.draw.line(screen, color_black, start_pos, end_pos, width=2)
        pygame.draw.polygon(screen, color_orange, ((layer3_x, section_3_h + triangle_hei), (layer3_x - triangle_wid, section_3_h), (layer3_x + triangle_wid, section_3_h)))
        if self.working_branch["left"] is not None:
            text_eval = smallfont.render(str(self.working_branch["left"]) , True , color_black)
            screen.blit(text_eval, (layer3_x - 20, section_3_h + 15))

        # right triangle
        layer3_x = x_val + 100
        start_pos = (x_val, section_2_h + triangle_hei)
        end_pos = (layer3_x, section_3_h)
        pygame.draw.line(screen, color_black, start_pos, end_pos, width=2)
        pygame.draw.polygon(screen, color_orange, ((layer3_x, section_3_h + triangle_hei), (layer3_x - triangle_wid, section_3_h), (layer3_x + triangle_wid, section_3_h)))
        if self.working_branch["right"] is not None:
            if self.zobs[1]:
                text_eval = smallfont.render(str(self.working_branch["right"]) , True , color_teal)
            else:
                text_eval = smallfont.render(str(self.working_branch["right"]) , True , color_black)
            screen.blit(text_eval, (layer3_x - 15, section_3_h + 15))

        layer3_x = x_val - 100
        section_4_h = 600
        left_states = self.working_branch['left_states']
        for i in range(len(left_states)):
            layer4_x = 0
            if i == 0:
                layer4_x = layer3_x - 90
            elif i == 1:
                layer4_x = layer3_x - 25
            elif i == 2:
                layer4_x = layer3_x + 40
            sq = 50
            start_pos = (layer3_x, section_3_h + triangle_hei)
            end_pos = (layer4_x + 25,section_4_h)
            pygame.draw.line(screen, color_black, start_pos, end_pos, width=2)
            rect = pygame.Rect(layer4_x,section_4_h,sq,sq)
            pygame.draw.rect(screen,color_black,rect)
            if left_states[i] is not None:
                text_eval = smallfont.render(str(left_states[i]) , True , color_white)
                screen.blit(text_eval, rect)

        layer3_x = x_val + 100
        section_4_h = 600
        right_states = self.working_branch['right_states']
        for i in range(len(right_states)):
            layer4_x = 0
            if i == 0:
                layer4_x = layer3_x - 90
            elif i == 1:
                layer4_x = layer3_x - 25
            elif i == 2:
                layer4_x = layer3_x + 40
            sq = 50
            start_pos = (layer3_x, section_3_h + triangle_hei)
            end_pos = (layer4_x + 25,section_4_h)
            pygame.draw.line(screen, color_black, start_pos, end_pos, width=2)
            rect = pygame.Rect(layer4_x,section_4_h,sq,sq)
            pygame.draw.rect(screen,color_black,rect)
            if right_states[i] is not None:
                if i == 1 and self.zobs[2]:
                    text_eval = smallfont.render(str(right_states[i]) , True , color_yellow)
                else:
                    text_eval = smallfont.render(str(right_states[i]) , True , color_white)
                screen.blit(text_eval, rect)

    def draw_cutoffs(self, screen):
        color_red = (252, 11, 3)
        cutoff_pos1 = []
        cutoff_pos2 = []
        start_pos = (670, 180)
        end_pos = (750, 140)
        cutoff_pos1.append((start_pos, end_pos))
        start_pos = (680, 180)
        end_pos = (760, 140)
        cutoff_pos2.append((start_pos, end_pos))

        start_pos = (800, 350)
        end_pos = (900, 300)
        cutoff_pos1.append((start_pos, end_pos))
        start_pos = (810, 350)
        end_pos = (910, 300)
        cutoff_pos2.append((start_pos, end_pos))

        start_pos = (875, 550)
        end_pos = (950, 500)
        cutoff_pos1.append((start_pos, end_pos))
        start_pos = (885, 550)
        end_pos = (960, 500)
        cutoff_pos2.append((start_pos, end_pos))

        for i in range(len(cutoff_pos1)):
            if self.cutoffs[i]:
                pygame.draw.line(screen, color_red, cutoff_pos1[i][0], cutoff_pos1[i][1], width=2)
                pygame.draw.line(screen, color_red, cutoff_pos2[i][0], cutoff_pos2[i][1], width=2)

    def show_stats(self, screen, tracking_dict):
        color_black = (0, 0, 0)
        start_x = 25
        start_y = 0
        space_y = 25
        smallfont = pygame.font.SysFont('Calibri',25)
        text = "Static evals: " + str(tracking_dict['N_STATIC_EVALS'])
        text_eval = smallfont.render(text, True, color_black)
        textRect = pygame.Rect(start_x,start_y + space_y,450,50)
        screen.blit(text_eval, textRect)

        text = "Zobrist Lookups: " + str(tracking_dict['N_ZOBRIST_LOOKUPS'])
        text_eval = smallfont.render(text, True, color_black)
        textRect = pygame.Rect(start_x,start_y + space_y * 2,450,50)
        screen.blit(text_eval, textRect)

        text = "Alpha beta cutoffs: " + str(tracking_dict['N_CUTOFFS'])
        text_eval = smallfont.render(text, True, color_black)
        textRect = pygame.Rect(start_x,start_y + space_y * 3,450,50)
        screen.blit(text_eval, textRect)

        text = "Total states expanded: " + str(tracking_dict['N_STATES_EXPANDED'])
        text_eval = smallfont.render(text, True, color_black)
        textRect = pygame.Rect(start_x,start_y + space_y * 4,450,50)
        screen.blit(text_eval, textRect)


