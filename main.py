import pygame as pg
import random as rand

# Inisialisasi
pg.init()
pg.joystick.init()
pg.mixer.init()

# Cek apakah ada joystick yang terhubung
if pg.joystick.get_count() > 0:
    joystick = pg.joystick.Joystick(0)
    joystick.init()

# Tambahkan Jendela
SCREEN_WIDTH, SCREEN_HEIGHT = 1280, 720
screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pg.display.set_caption("Space Shooter")

# Kecepatan Game
clock = pg.time.Clock()
FPS = 60

highest_score = 0
boss_spawned = False

# Warna
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)

bg_image = pg.image.load(".\\assets\\images\\bg.png").convert_alpha()
bg_image = pg.transform.scale(bg_image, (SCREEN_WIDTH, SCREEN_HEIGHT))

kill_sound = pg.mixer.Sound(".\\assets\\bank_sound\\kill.mp3")
kill_sound.set_volume(2)
hit_sound = pg.mixer.Sound(".\\assets\\bank_sound\\hit.mp3")
hit_sound.set_volume(0.5)
backsound = pg.mixer.Sound(".\\assets\\bank_sound\\backsound.mp3")
backsound.set_volume(0.5)
backsound.play(-1)
game_over_sound = pg.mixer.Sound(".\\assets\\bank_sound\\game_over.mp3")
game_over_sound.set_volume(0.7)

def draw_bg():
    screen.blit(bg_image, (0, 0))

# Class Player
class Player(pg.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pg.image.load(".\\assets\\images\\player.png").convert_alpha()
        self.image = pg.transform.scale(self.image, (75, 75))
        self.rect = self.image.get_rect()
        self.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50)
        self.speed = 5

    def update(self):
        keys = pg.key.get_pressed()
        if keys[pg.K_a] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[pg.K_d] and self.rect.right < SCREEN_WIDTH:
            self.rect.x += self.speed
        if keys[pg.K_w] and self.rect.top > 0:
            self.rect.y -= self.speed
        if keys[pg.K_s] and self.rect.bottom < SCREEN_HEIGHT:
            self.rect.y += self.speed

        # Joystick movement
        if pg.joystick.get_count() > 0:
            x_axis = joystick.get_axis(0)
            y_axis = joystick.get_axis(1)
            self.rect.x += int(x_axis * self.speed)
            self.rect.y += int(y_axis * self.speed)

        # Batasi agar tidak keluar dari jendela
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT

# Class Bullet
class Bullet(pg.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pg.image.load(".\\assets\\images\\bullet.png").convert_alpha()
        self.image = pg.transform.scale(self.image, (50, 50))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.speed = -10

    def update(self):
        self.rect.y += self.speed
        if self.rect.bottom < 0:
            self.kill()

# Class Enemy
class Enemy(pg.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pg.image.load(".\\assets\\images\\enemies.png").convert_alpha()
        self.image = pg.transform.scale(self.image, (100, 100))
        self.rect = self.image.get_rect()
        self.rect.x = rand.randint(0, SCREEN_WIDTH - 75)
        self.rect.y = rand.randint(-100, -50)
        self.speed = rand.randint(1, 5)
        self.health = 5

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > SCREEN_HEIGHT:
            self.rect.x = rand.randint(0, SCREEN_WIDTH - 75)
            self.rect.y = rand.randint(-100, -50)
            self.speed = rand.randint(1, 5)

    def draw_health(self):
        health_bar_length = 50
        health_ratio = self.health / 5
        health_bar_length_current = health_bar_length * health_ratio

        health_bar = pg.Rect(self.rect.centerx - health_bar_length // 2, self.rect.bottom + 5, health_bar_length, 5)
        health_bar_current = pg.Rect(self.rect.centerx - health_bar_length // 2, self.rect.bottom + 5, health_bar_length_current, 5)

        pg.draw.rect(screen, RED, health_bar)
        if self.health > 0:
            pg.draw.rect(screen, GREEN, health_bar_current)

# Class Boss
class Boss(pg.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pg.image.load(".\\assets\\images\\boss.png").convert_alpha()
        self.image = pg.transform.scale(self.image, (200, 200))
        self.rect = self.image.get_rect()
        self.rect.x = rand.randint(0, SCREEN_WIDTH - 200)
        self.rect.y = rand.randint(-200, -100)
        self.speed = rand.randint(2, 4)
        self.health = 30

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > SCREEN_HEIGHT:
            self.rect.x = rand.randint(0, SCREEN_WIDTH - 200)
            self.rect.y = rand.randint(-200, -100)
            self.speed = rand.randint(2, 4)

    def draw_health(self):
        health_bar_length = 150
        health_ratio = self.health / 30
        health_bar_length_current = health_bar_length * health_ratio

        health_bar = pg.Rect(self.rect.centerx - health_bar_length // 2, self.rect.bottom + 10, health_bar_length, 10)
        health_bar_current = pg.Rect(self.rect.centerx - health_bar_length // 2, self.rect.bottom + 10, health_bar_length_current, 10)

        pg.draw.rect(screen, RED, health_bar)
        if self.health > 0:
            pg.draw.rect(screen, GREEN, health_bar_current)

def draw_text(text, font, color, x, y):
    screen_text = font.render(text, True, color)
    screen.blit(screen_text, [x, y])

def draw_button(text, x, y, w, h, inactive_color, active_color, action=None):
    mouse = pg.mouse.get_pos()
    click = pg.mouse.get_pressed()
    if x + w > mouse[0] > x and y + h > mouse[1] > y:
        pg.draw.rect(screen, active_color, (x, y, w, h))
        if click[0] == 1 and action is not None:
            action()
    else:
        pg.draw.rect(screen, inactive_color, (x, y, w, h))

    font = pg.font.SysFont(None, 40)
    text_surf = font.render(text, True, WHITE)
    screen.blit(text_surf, (x + (w / 4), y + (h / 4)))

def start_game():
    global highest_score, boss_spawned
    all_sprites = pg.sprite.Group()
    enemies = pg.sprite.Group()
    bullets = pg.sprite.Group()
    bosses = pg.sprite.Group()

    player = Player()
    all_sprites.add(player)

    for i in range(5):
        enemy = Enemy()
        all_sprites.add(enemy)
        enemies.add(enemy)

    score = 0
    start = pg.time.get_ticks()
    level = 1

    running = True
    game_over = False 
    while running:
        clock.tick(FPS)
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
            
            if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                hit_sound.play()
                bullet = Bullet(player.rect.centerx, player.rect.top)
                all_sprites.add(bullet)
                bullets.add(bullet)
            if pg.joystick.get_count() > 0:
                if event.type == pg.JOYBUTTONDOWN and event.button == 2:
                    hit_sound.play()
                    bullet = Bullet(player.rect.centerx, player.rect.top)
                    all_sprites.add(bullet)
                    bullets.add(bullet)

        # Update
        all_sprites.update()

        # Collision antara peluru dan musuh
        hits = pg.sprite.groupcollide(enemies, bullets, False, True)
        for hit in hits:
            hit.health -= 1
            if hit.health <= 0:
                hit.kill()
                score += 5
                kill_sound.play()
                new_enemy = Enemy()
                all_sprites.add(new_enemy)
                enemies.add(new_enemy)

        # Collision antara peluru dan boss
        boss_hits = pg.sprite.groupcollide(bosses, bullets, False, True)
        for hit in boss_hits:
            hit.health -= 1
            if hit.health <= 0:
                hit.kill()
                score += 25
                kill_sound.play()
        
        # Logika naik level
        if score >= level * 50:
            level += 1
            # Musuh baru dengan kecepatan yang lebih cepat
            for i in range(5):
                enemy = Enemy()
                # Musuh makin cepat tiap level
                enemy.speed = rand.randint(1 + level, 5 + level) 
                all_sprites.add(enemy)
                enemies.add(enemy)

        # Boss muncul setiap skor kelipatan 100
        if score % 100 == 0 and score > 0 and not boss_spawned:
            boss = Boss()
            all_sprites.add(boss)
            bosses.add(boss)
            boss_spawned = True  # Menandai bahwa bos telah muncul untuk skor ini

        # Reset flag ketika skor tidak lagi kelipatan 100
        if score % 100 != 0:
            boss_spawned = False

        # Memperbarui Highest Score
        if score > highest_score:
            highest_score = score

        # Deteksi tabrakan antara pemain dan musuh/boss
        if pg.sprite.spritecollideany(player, enemies) or pg.sprite.spritecollideany(player, bosses):
            game_over_sound.play()
            draw_bg()
            draw_text("GAME OVER", pg.font.SysFont(None, 100), RED, SCREEN_WIDTH // 4 + 125, SCREEN_HEIGHT // 3)
            pg.display.flip()
            pg.time.wait(2000)  # Tunggu 2 detik sebelum keluar
            running = False  # Mengakhiri game

        # Menggambar ulang layar
        draw_bg()
        all_sprites.draw(screen)

        # Gambar Health untuk musuh dan boss
        for enemy in enemies:
            enemy.draw_health()

        for boss in bosses:
            boss.draw_health()

        draw_text(f"Score: {score}", pg.font.SysFont(None, 50), WHITE, 10, 20)
        draw_text(f"Highest Score: {highest_score}", pg.font.SysFont(None, 50), WHITE, 10, 20+50)

        pg.display.flip()

def main_menu():
    intro = True

    while intro:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                quit()
            
        draw_bg()
        draw_text("Space Shooter", pg.font.SysFont(None, 100), WHITE, SCREEN_WIDTH // 4 + 50, SCREEN_HEIGHT // 4)
        
        draw_button("Start", SCREEN_WIDTH // 4 + 150, SCREEN_HEIGHT // 4 + 165, 300, 75, GREEN, RED, start_game)
        draw_button("Quit", SCREEN_WIDTH // 4 + 150, SCREEN_HEIGHT // 4 + 165 + 150, 300, 75, GREEN, RED, pg.quit)

        if pg.joystick.get_count() > 0:
            if joystick.get_button(0):
                start_game()
            if joystick.get_button(1):
                pg.quit()
                quit()

        pg.display.update()
        clock.tick(15)
    pg.quit()

if __name__ == "__main__":
    main_menu()
