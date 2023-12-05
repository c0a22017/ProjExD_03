import os
import random
import sys
import time

import pygame as pg

WIDTH = 1600  # ゲームウィンドウの幅
HEIGHT = 900  # ゲームウィンドウの高さ
NUM_OF_BOMBS = 5  # 爆弾の数
MAIN_DIR = os.path.split(os.path.abspath(__file__))[0]

def check_bound(obj_rct: pg.Rect) -> tuple[bool, bool]:
    yoko, tate = True, True
    if obj_rct.left < 0 or WIDTH < obj_rct.right:
        yoko = False
    if obj_rct.top < 0 or HEIGHT < obj_rct.bottom:
        tate = False
    return yoko, tate

class Bird:
    delta = {
        pg.K_UP: (0, -5),
        pg.K_DOWN: (0, +5),
        pg.K_LEFT: (-5, 0),
        pg.K_RIGHT: (+5, 0),
    }

    def __init__(self, num: int, xy: tuple[int, int]):
        img0 = pg.transform.rotozoom(pg.image.load(f"{MAIN_DIR}/fig/{num}.png"), 0, 2.0)
        img = pg.transform.flip(img0, True, False)
        self.imgs = {
            (+5, 0): img,
            (+5, -5): pg.transform.rotozoom(img, 45, 1.0),
            (0, -5): pg.transform.rotozoom(img, 90, 1.0),
            (-5, -5): pg.transform.rotozoom(img0, -45, 1.0),
            (-5, 0): img0,
            (-5, +5): pg.transform.rotozoom(img0, 45, 1.0),
            (0, +5): pg.transform.rotozoom(img, -90, 1.0),
            (+5, +5): pg.transform.rotozoom(img, -45, 1.0),
        }
        self.img = self.imgs[(+5, 0)]
        self.rct = self.img.get_rect()
        self.rct.center = xy
        self.beams = []

    def change_img(self, num: int, screen: pg.Surface):
        self.img = pg.transform.rotozoom(pg.image.load(f"{MAIN_DIR}/fig/{num}.png"), 0, 2.0)
        screen.blit(self.img, self.rct)

    def update(self, key_lst: list[bool], screen: pg.Surface):
        sum_mv = [0, 0]
        for k, mv in __class__.delta.items():
            if key_lst[k]:
                sum_mv[0] += mv[0]
                sum_mv[1] += mv[1]
        self.rct.move_ip(sum_mv)
        if check_bound(self.rct) != (True, True):
            self.rct.move_ip(-sum_mv[0], -sum_mv[1])
        if not (sum_mv[0] == 0 and sum_mv[1] == 0):
            self.img = self.imgs[tuple(sum_mv)]
        screen.blit(self.img, self.rct)

    def get_direction(self):
        return next(direction for direction, img in self.imgs.items() if img == self.img)

    def fire_beam(self):
        direction = self.get_direction()
        new_beam = Beam(self.rct, direction)
        self.beams.append(new_beam)

    def update_beams(self, screen: pg.Surface):
        beams_to_remove = []
        for beam in self.beams:
            beam.update(screen)
            if not check_bound(beam.rct):
                beams_to_remove.append(beam)
        for beam in beams_to_remove:
            self.beams.remove(beam)

class Bomb:
    def __init__(self, image_path: str, rad: int):
        self.img = pg.transform.scale(pg.image.load(image_path), (2 * rad, 2 * rad))
        self.img.set_colorkey((0, 0, 0))
        self.rct = self.img.get_rect()
        self.rct.center = random.randint(0, WIDTH), random.randint(0, HEIGHT)
        self.vx, self.vy = +5, +5

    def update(self, screen: pg.Surface):
        yoko, tate = check_bound(self.rct)
        if not yoko:
            self.vx *= -1
        if not tate:
            self.vy *= -1
        self.rct.move_ip(self.vx, self.vy)
        screen.blit(self.img, self.rct)

class Beam:
    def __init__(self, bird_rect: pg.Rect, direction: tuple[int, int]):
        self.img = pg.image.load(f"{MAIN_DIR}/fig/beam.png")
        self.rct = self.img.get_rect()
        self.rct.midleft = bird_rect.midright
        self.vx, self.vy = direction  # Use the direction as the initial veloci ty

    def update(self, screen: pg.Surface):
        self.rct.move_ip(self.vx, self.vy)
        screen.blit(self.img, self.rct)

class Score:
    def __init__(self):
        self.font = pg.font.SysFont("hgp創英角ﾎﾟｯﾌﾟ体", 30)
        self.score = 0
        self.img = self.font.render(f"スコア：{self.score}", 0, (0, 0, 255))
        self.cx = 100
        self.cy = HEIGHT - 50

    def update(self, score: pg.Surface):
        self.img = self.font.render(f"スコア：{self.score}", 0, (0, 0, 255))
        score.blit(self.img, (self.cx, self.cy))

  
def main():
    pg.display.set_caption("たたかえ！こうかとん")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    bg_img = pg.image.load(f"{MAIN_DIR}/fig/pg_bg.jpg")
    bird = Bird(3, (900, 400))
    bombs = [Bomb(f"{MAIN_DIR}/fig/baikin.png", 50) for _ in range(NUM_OF_BOMBS)]
    fonto = pg.font.Font(None, 80)
    moji = fonto.render("GAME OVER", True, (255, 0, 0))
    scores = Score()

    clock = pg.time.Clock()
    tmr = 0
    game_over = False

    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return
            elif event.type == pg.KEYDOWN and event.key == pg.K_SPACE:
                bird.fire_beam()

        screen.blit(bg_img, [0, 0])

        bird.update_beams(screen)

        for i, bomb in enumerate(bombs):
            if bomb is not None:
                if bird.rct.colliderect(bomb.rct):
                    game_over = True
                    break

                for beam in bird.beams:
                    if bomb.rct.colliderect(beam.rct):
                        bombs[i] = None
                        bird.beams.remove(beam)
                        bird.change_img(6, screen)
                        scores.score += 1
                        pg.display.update()

        if not game_over:
            for bomb in bombs:
                if bomb is not None:
                    bomb.update(screen)

            if bird.beams:
                for beam in bird.beams:
                    if beam:
                        beam.update(screen)

            bird.update(pg.key.get_pressed(), screen)
            scores.update(screen)
            pg.display.update()
            tmr += 1
            clock.tick(50)

            # Check if the score is 5 or more
            if scores.score >= 5:
                # Display the "gra.png" image
                clear_img = pg.image.load(f"{MAIN_DIR}/fig/hentai.png")
                screen.blit(clear_img, [400, 200])
                pg.display.update()
                time.sleep(2)  # You can adjust the time the image is displayed
                return
        else:
            screen.blit(moji, [1600, 900])  # Adjust the position to display "GAME OVER"
            pg.display.update()
            time.sleep(4)
            return  # Return from the function when game_over is True


if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()