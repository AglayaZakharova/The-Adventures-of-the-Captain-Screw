import pygame
from pygame.locals import *

pygame.init()

clock = pygame.time.Clock()
fps = 90

# Настройки экрана
screen_width = 1024
screen_height = 768
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Платформер")
bg_img = pygame.image.load('images/Background.png')

# Настройка сетки (нужна для удобного построения уровня)
tile_width = 64
tile_height = 48


def draw_grid():
    for line in range(0, 17):
        pygame.draw.line(screen, (255, 255, 0), (0, line * tile_height), (screen_width, line * tile_height), 1)
        pygame.draw.line(screen, (255, 255, 0), (line * tile_width, 0), (line * tile_width, screen_width), 1)


# Класс игрового мира
class World:
    def __init__(self, data):
        self.tile_list = []

        dirt_img = pygame.image.load('images/Dirt.png')
        dirt_surf_img = pygame.image.load('images/Dirt_surf.png')
        grass_img = pygame.image.load('images/Grass.png')

        # Считываем массив данных и конструируем уровень
        row_count = 0
        for row in data:
            col_count = 0
            for tile in row:
                if tile == 1:
                    h = dirt_img
                elif tile == 2:
                    h = dirt_surf_img
                elif tile == 3:
                    h = grass_img
                elif tile == 4:
                    enemy = Enemy(col_count * tile_width, row_count * tile_height + 25)
                    enemy_group.add(enemy)
                    col_count += 1
                    continue
                else:
                    col_count += 1
                    continue
                img = pygame.transform.scale(h, (tile_width, tile_height))
                img_rect = img.get_rect()
                img_rect.x = col_count * tile_width
                img_rect.y = row_count * tile_height
                tile = (img, img_rect)
                self.tile_list.append(tile)
                col_count += 1
            row_count += 1

    def draw(self):
        for tile in self.tile_list:
            screen.blit(tile[0], tile[1])
            # pygame.draw.rect(screen, (255, 255, 255), tile[1], 1)


# Класс игрока
class Player:
    def __init__(self, x, y):
        self.images_right = []
        self.images_left = []
        self.index = 0
        self.counter = 0
        for num in range(1, 4):
            img_right = pygame.image.load(f'images/Captain{num}.png')
            img_right = pygame.transform.scale(img_right, (48, 96))
            img_left = pygame.transform.flip(img_right, True, False)
            self.images_right.append(img_right)
            self.images_left.append(img_left)
        self.image = self.images_right[self.index]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        # Скорость
        self.vel_y = 0
        self.jumped = False
        self.direction = 0

    def update(self):
        dx = 0
        dy = 0
        walk_cooldown = 12

        key = pygame.key.get_pressed()
        if key[pygame.K_SPACE] and not self.jumped:
            self.vel_y = -20
            self.jumped = True
        if not key[pygame.K_SPACE]:
            self.jumped = False
        if key[pygame.K_LEFT]:
            dx -= 3
            self.counter += 1
            self.direction = -1
        if key[pygame.K_RIGHT]:
            dx += 3
            self.counter += 1
            self.direction = 1
        if not key[pygame.K_LEFT] and not key[pygame.K_RIGHT]:
            self.counter = 0
            self.index = 0
            if self.direction == 1:
                self.image = self.images_right[self.index]
            if self.direction == -1:
                self.image = self.images_left[self.index]

        # Добавляем анимацию
        if self.counter > walk_cooldown:
            self.counter = 0
            self.index += 1
            if self.index >= len(self.images_right):
                self.index = 1
            if self.direction == 1:
                self.image = self.images_right[self.index]
            if self.direction == -1:
                self.image = self.images_left[self.index]

        # Добавляем гравитацию
        self.vel_y += 1
        if self.vel_y > 4:
            self.vel_y = 4
        dy += self.vel_y

        # Проверяем препятствия
        for tile in world.tile_list:
            # По горизонтали
            if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                dx = 0
            # По вертикали
            if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                # Если игрок прыгает, т.е. блок над ним
                if self.vel_y < 0:
                    dy = tile[1].bottom - self.rect.top
                    self.vel_y = 0
                # Если игрок падает, т.е. блок под ним
                elif self.vel_y >= 0:
                    dy = tile[1].top - self.rect.bottom
                    self.vel_y = 0

        self.rect.x += dx
        self.rect.y += dy

        if self.rect.bottom > screen_height:
            self.rect.bottom = screen_height
            dy = 0
        if self.rect.right > screen_width:
            self.rect.right = screen_width
            dx = 0
        if self.rect.left < 0:
            self.rect.left = 0
            dx = 0

        # Помещаем игрока на экран
        screen.blit(self.image, self.rect)
        # pygame.draw.rect(screen, (255, 255, 255), self.rect, 1)


class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('images/Enemy.png')
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        self.move_direction = 1

    def update(self):
        self.rect.x += self.move_direction
        if self.rect.right == screen_width:
            self.move_direction *= -1
        if self.rect.left == 0:
            self.move_direction *= -1

        # pygame.draw.rect(screen, (255, 255, 255), self.rect, 1)


world_data = [
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [2, 0, 0, 0, 0, 2, 2, 0, 0, 0, 0, 0, 0, 0, 2, 2],
    [0, 0, 0, 0, 0, 0, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 3, 3, 3, 3, 0, 0, 0, 0, 0, 3, 0, 0, 0],
    [2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2],
    [1, 2, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [4, 0, 0, 0, 0, 0, 2, 2, 2, 0, 0, 0, 2, 0, 0, 0],
    [3, 3, 3, 0, 0, 0, 1, 1, 0, 0, 0, 0, 1, 2, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4],
    [2, 2, 2, 2, 2, 2, 2, 0, 0, 0, 0, 3, 3, 3, 3, 3]
]

# Объявляем игрока и мир
player = Player(10, screen_height - 150)
enemy_group = pygame.sprite.Group()
world = World(world_data)

# Запускаем игровой цикл
run = True
while run:

    clock.tick(fps)

    screen.blit(bg_img, (0, 0))
    enemy_group.update()
    enemy_group.draw(screen)
    world.draw()
    # draw_grid()
    player.update()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    pygame.display.update()

pygame.quit()
