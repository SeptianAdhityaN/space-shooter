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
    self.rect.center = (SCREEN_WIDTH//2, SCREEN_HEIGHT - 50)
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
        x_axis = joystick.get_axis(0)  # Horizontal movement (left stick)
        y_axis = joystick.get_axis(1)  # Vertical movement (left stick)
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
        self.image =pg.transform.scale(self.image, (50, 50))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.speed = -10  # Peluru bergerak ke atas

    def update(self):
        self.rect.y += self.speed
        if self.rect.bottom < 0:  # Hapus peluru jika keluar dari layar
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
        self.health = 5  # Menambahkan nyawa untuk musuh

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > SCREEN_HEIGHT:
            self.rect.x = rand.randint(0, SCREEN_WIDTH - 75)
            self.rect.y = rand.randint(-100, -50)
            self.speed = rand.randint(1, 5)

    def draw_health(self):
        # Menghitung panjang bar kesehatan berdasarkan nyawa
        health_bar_length = 50
        health_ratio = self.health / 5  # 3 adalah nyawa maksimum
        health_bar_length_current = health_bar_length * health_ratio

        # Posisi bar kesehatan
        health_bar = pg.Rect(self.rect.centerx - health_bar_length // 2, self.rect.bottom + 5, health_bar_length, 5)
        health_bar_current = pg.Rect(self.rect.centerx - health_bar_length // 2, self.rect.bottom + 5, health_bar_length_current, 5)

        # Menggambar bar kesehatan
        pg.draw.rect(screen, RED, health_bar)  # Border
        if self.health > 0:
            pg.draw.rect(screen, GREEN, health_bar_current)  # Bar kesehatan yang terisi

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
    global highest_score
    # Inisialisasi sprite group
    all_sprites = pg.sprite.Group()
    enemies = pg.sprite.Group()
    bullets = pg.sprite.Group()  # Group untuk peluru

    # Membuat Player
    player = Player()
    all_sprites.add(player)

    # Membuat Enemies
    for i in range(5):
        enemy = Enemy()
        all_sprites.add(enemy)
        enemies.add(enemy)

    # Membuat Skor dan level
    score = 0
    start = pg.time.get_ticks()
    level = 1

    # Loop Game
    running = True
    game_over = False 
    while running:
        clock.tick(FPS)
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
            
            # Menembakkan peluru dengan mouse atau joystick
            if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:  # Mouse kiri
                hit_sound.play()
                bullet = Bullet(player.rect.centerx, player.rect.top)
                all_sprites.add(bullet)
                bullets.add(bullet)
            if pg.joystick.get_count() > 0:
                if joystick.get_button(2):  # Misalkan tombol  di joystick
                    hit_sound.play()
                    bullet = Bullet(player.rect.centerx, player.rect.top)
                    all_sprites.add(bullet)
                    bullets.add(bullet)

            # Restart game dengan joystick
            if pg.joystick.get_count() > 0:
                if joystick.get_button(0) and game_over:
                    start_game()

                if joystick.get_button(1) and game_over:
                    running = False
        
        # Logika naik level
        if score > level * 10:
            level += 1
            for i in range(5):
                enemy = Enemy()
                enemy.speed = rand.randint(5, 10)
                all_sprites.add(enemy)
                enemies.add(enemy)

        # Logic Game Over
        if not game_over:
            all_sprites.update()

            # Cek tabrakan antara peluru dan musuh
            hits = pg.sprite.groupcollide(enemies, bullets, False, True)
            for enemy in hits:
                enemy.health -= 1  # Mengurangi nyawa musuh
                if enemy.health <= 0:
                    enemy.kill()  # Menghapus musuh jika nyawanya habis
                    kill_sound.play()

            # Cek Player hit Enemy
            hits = pg.sprite.spritecollide(player, enemies, False)
            if hits:
                game_over = True
                game_over_time = (pg.time.get_ticks() - start) // 1000

                # Logika Highest Score
                if game_over_time > highest_score:
                    highest_score = game_over_time

                game_over_sound.play()

            # Menghitung Skor
            score = (pg.time.get_ticks() - start) // 1000

        draw_bg()

        all_sprites.draw(screen)

        # Gambar nyawa musuh
        for enemy in enemies:
            enemy.draw_health()

        font = pg.font.SysFont(None, 30)
        text = font.render(f"Score: {score}", True, WHITE)
        screen.blit(text, (10, 10))

        font = pg.font.SysFont(None, 30)
        text = font.render(f"Level: {level}", True, WHITE)
        screen.blit(text, (10, 10+20))

        if game_over:
            over_text = font.render(f"Game Over! Your Highest Score: {highest_score}", True, WHITE)
            screen.blit(over_text, (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2))

            # Tombol Restart
            draw_button("Restart Game", SCREEN_WIDTH // 2 - 165, SCREEN_HEIGHT // 2 + 75, 350, 50, BLUE, RED, start_game)

        pg.display.flip()
    
    pg.quit()


def main_menu():
    menu = True
    while menu:
        # Background
        screen.blit(bg_image, (0, 0))

        # Judul Game
        font = pg.font.SysFont(None, 70)
        draw_text("Space Shooter", font, WHITE, SCREEN_WIDTH//4 + 150, SCREEN_HEIGHT//4 + 100)

        # Tombol Start
        draw_button("Start Game", SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2, 300, 50, BLUE, RED, start_game)

        # Tombol Quit
        for event in pg.event.get():
            if event.type == pg.QUIT:
                menu = False

        pg.display.update()

# Jalankan Menu Utama
if __name__ == "__main__":
  main_menu()
