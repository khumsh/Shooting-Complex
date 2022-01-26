import pygame
import sys, os, random
import math

# 게임 초기화
pygame.init()

# 게임창 옵션 설정
screen_width = 800
screen_height = 640
size = [screen_width, screen_height] # 창 크기
screen = pygame.display.set_mode(size)

title = "Shooting Complex"
pygame.display.set_caption(title)

# 게임 내 필요한 설정
clock = pygame.time.Clock()
background_color = (0, 0, 20)

# 폰트 설정
myFont = pygame.font.Font('data/American Captain.ttf', 30)
game_over_font = pygame.font.Font('data/American Captain.ttf', 90)

# 이미지
background_img = pygame.image.load('data/img/background/background.png').convert()
bullet_img = pygame.image.load('data/img/player/shoot/bullet.png').convert_alpha()
bullet_img = pygame.transform.scale(bullet_img, (int(bullet_img.get_width() * 3), int(bullet_img.get_height() * 3)))
gun_img = pygame.image.load('data/img/player/shoot/gun.png').convert_alpha()
enemy_bullet = pygame.image.load('data/img/enemy/attack.png').convert_alpha()
heart = pygame.image.load('data/img/heart.png').convert_alpha()
black_heart = pygame.image.load('data/img/black_heart.png').convert_alpha()

# 사운드
bgm_sound = pygame.mixer.Sound('data/sound/bgm.wav')
laser_sound = pygame.mixer.Sound('data/sound/laser.wav')
death_sound = pygame.mixer.Sound('data/sound/death_sound.mp3')
player_hit_sound = pygame.mixer.Sound('data/sound/player_hit.mp3')
enemy_hit_sound = pygame.mixer.Sound('data/sound/enemy_hit.mp3')

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, scale, speed):
        pygame.sprite.Sprite.__init__(self)
        self.alive = True # 살아있는지

        self.speed = speed
        self.direction = 1 # 좌우 방향
        self.flip = False # 이미지 좌우 반전

        self.animation_list = [] # 애니메이션 리스트
        self.frame_index = 0 # 애니메이션 프레임 인덱스
        self.update_time = pygame.time.get_ticks() # 애니메이션 시간

        self.action = 0 # 상태 (0: idle, 1: run, 2: death)
        self.weapon_img = gun_img

        self.score = 0
        self.lives = 3 # 라이프

        self.drawing = True
              
        # 애니메이션 리스트 추가
        animation_types = ['idle', 'run', 'death']
        for animation in animation_types:
            temp_list = []
            # 애니메이션 프레임 수
            num_of_frames = len(os.listdir(f'data/img/player/{animation}'))
            for i in range(num_of_frames):
                img = pygame.image.load(f'data/img/player/{animation}/{animation}{i}.png').convert_alpha()
                img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
                temp_list.append(img)
            self.animation_list.append(temp_list)

        self.image = self.animation_list[self.action][self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x+30, y+40)

    def move(self, moving_left, moving_right, moving_up, moving_down):
        # 플레이어 이동 함수

        dx = 0 # x 변화량
        dy = 0 # y 변화량

        # 플레이어 이동 가능 범위
        # x: -5 ~ 735
        # y: -10 ~ 545

        if moving_left and self.rect.x > 10:
            dx = -self.speed
        if moving_right and self.rect.x < 735:
            dx = self.speed
        if moving_up and self.rect.y > 50:
            dy = -self.speed
        if moving_down and self.rect.y < 555:
            dy = self.speed

        # 위치 업데이트
        self.rect.x += dx
        self.rect.y += dy

    def update_animation(self):
        # 플레이어 애니메이션 업데이트 함수
        ANIM_COOLDOWN = 150 # 애니메이션 쿨타임

        self.image = self.animation_list[self.action][self.frame_index]

        if pygame.time.get_ticks() - self.update_time > ANIM_COOLDOWN:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1

        if self.frame_index >= len(self.animation_list[self.action]):
            if self.action != 2: # death가 아니라면 반복재생
                self.frame_index = 0
            elif self.action == 2: 
                # death라면
                # 게임 오버
                self.drawing = False
                #self.alive = False
                self.kill()

    def update_action(self, new_action):
        # 플레이어 액션 상태 업데이트 함수
        # 이전 액션과 같은지 확인
        if new_action != self.action:
            self.action = new_action

            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()

    def handle_weapon(self, display):
        mouse_x, mouse_y = pygame.mouse.get_pos()

        rel_x = mouse_x - self.rect.centerx
        rel_y = mouse_y - self.rect.centery

        angle = (180/math.pi) * -math.atan2(rel_y, rel_x)

        img = pygame.transform.scale(self.weapon_img, (int(self.weapon_img.get_width() * 5), int(self.weapon_img.get_height() * 5)))
        player_weapon_copy = pygame.transform.rotate(img, angle)

        display.blit(player_weapon_copy, (self.rect.x+25 - int(player_weapon_copy.get_width() / 2), self.rect.y+30 - int(player_weapon_copy.get_height() / 2)))

    def draw(self, display):
        # 플레이어 화면에 생성 함수
        display.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)

        if player.alive:
            self.handle_weapon(display)

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, dir_x, dir_y, type):
        pygame.sprite.Sprite.__init__(self)
        self.speed = 10
        self.enemy_bullet_speed = 2
        self.type = type # player_bullet, enemy_bullet

        if self.type == "player_bullet":
            self.image = bullet_img
        elif self.type == "enemy_bullet":
            self.image = enemy_bullet
        self.rect = self.image.get_rect()
        

        self.rect.center = (x, y) #(x-mouse_x/10+40, y-mouse_y/5+35)

        if self.type == "player_bullet":
            self.mouse_x = dir_x
            self.mouse_y = dir_y
            self.angle = math.atan2(y-dir_y, x-dir_x)
            self.x_velocity = math.cos(self.angle) * self.speed
            self.y_velocity = math.sin(self.angle) * self.speed
        elif self.type == "enemy_bullet":
            self.x_velocity = dir_x * self.enemy_bullet_speed
            self.y_velocity = dir_y * self.enemy_bullet_speed

        self.count = 0 # 총알이 벽에 부딪힌 횟수 (4가 되면 사라짐)

    def update(self):
        self.rect.x -= self.x_velocity
        self.rect.y -= self.y_velocity

        # 벽에 튕기기
        if self.rect.top <= 60 or self.rect.bottom >= screen_height:
            self.y_velocity *= -1
            self.count += 1
        if self.rect.right <= 50 or self.rect.left >= 750:
            self.x_velocity *= -1
            self.count += 1

        for enemy in enemy_group:
            if enemy.rect.colliderect(self.rect):
                if self.type == "player_bullet":
                    enemy_hit_sound.set_volume(0.5)
                    enemy_hit_sound.play()
                    enemy.kill()
                    self.kill()
                    enemy.attack() # 죽을 떄 공격
                    player.score += enemy.score
                    print("score:", player.score)

        if self.count > 2:
            self.kill()

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, scale, speed, type):
        pygame.sprite.Sprite.__init__(self)

        self.x = x
        self.y = y
        self.scale = scale
        self.speed = speed
        self.type = type # triangle, rectangle, circle, diamond

        if type == "triangle":
            self.score = 30
        elif type == "rectangle":
            self.score = 40
        elif type == "diamond":
            self.score = 40
        elif type == "circle":
            self.score = 80

        self.attack_rate = 100
        self.attack_cooltime = 0
        self.b_attack = False

        self.direction = 1 # 좌우 방향
        self.flip = False # 이미지 좌우 반전

        self.animation_list = [] # 애니메이션 리스트
        self.frame_index = 0 # 애니메이션 프레임 인덱스
        self.update_time = pygame.time.get_ticks() # 애니메이션 시간

        self.action = 0 # 상태 (0: idle, 1: move_down, 2: move_up)
              
        # 애니메이션 리스트 추가
        animation_types = ['idle', 'move_down', 'move_up']
        for animation in animation_types:
            temp_list = []
            # 애니메이션 프레임 수
            num_of_frames = len(os.listdir(f'data/img/enemy/{self.type}/{animation}'))
            for i in range(num_of_frames):
                img = pygame.image.load(f'data/img/enemy/{self.type}/{animation}/{animation}{i}.png').convert_alpha()
                img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
                temp_list.append(img)
            self.animation_list.append(temp_list)

        self.image = self.animation_list[self.action][self.frame_index]


        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

    def update(self):
        self.attack_cooltime += 1

        # 플레이어 추적해서 이동
        dif_x = player.rect.centerx-self.rect.centerx
        dif_y = player.rect.centery-self.rect.centery

        if dif_x != 0 or dif_y != 0:
            entity_movement = [dif_x/(abs(dif_x)+abs(dif_y))*self.speed, dif_y/(abs(dif_x)+abs(dif_y))*self.speed]
        else:
            entity_movement = [0, 0]

        if entity_movement[0] > 0 and entity_movement[0] < 1:
            entity_movement[0] = 1
        if entity_movement[1] > 0 and entity_movement[1] < 1:
            entity_movement[1] = 1

        self.rect.x += entity_movement[0]
        self.rect.y += entity_movement[1]

        # 좌우 반전
        if self.rect.x < player.rect.centerx:
            self.flip = True
            self.direction = -1
        else:
            self.flip = False
            self.direction = 1

        if entity_movement[1] > 0:
            self.update_action(1)
        else:
            self.update_action(2)

        # 공격
        if self.attack_cooltime >= self.attack_rate:
            self.speed = 0
            self.b_attack = True

            if self.attack_cooltime >= self.attack_rate + 40 and self.b_attack:
                self.attack_cooltime = 0

                #print("enemy attack")
                self.attack()

                self.speed = 1.5
                self.b_attack = False

    def update_action(self, new_action):
        # 적 액션 상태 업데이트 함수

        # 이전 액션과 같은지 확인
        if new_action != self.action:
            self.action = new_action

            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()

    def update_animation(self):
        # 적 애니메이션 업데이트 함수
        ANIM_COOLDOWN = 250 # 애니메이션 쿨타임

        self.image = self.animation_list[self.action][self.frame_index]

        if pygame.time.get_ticks() - self.update_time > ANIM_COOLDOWN:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1

        if self.frame_index >= len(self.animation_list[self.action]):
            self.frame_index = 0

    def attack(self):
        # 적 공격 함수
        if self.type == "triangle":
            enemy_bullet = Bullet(self.rect.centerx, self.rect.centery, 0, -1, "enemy_bullet")
            enemy_bullet1 = Bullet(self.rect.centerx, self.rect.centery, -1, 1, "enemy_bullet")
            enemy_bullet2 = Bullet(self.rect.centerx, self.rect.centery, 1, 1, "enemy_bullet")
            bullet_group.add(enemy_bullet)
            bullet_group.add(enemy_bullet1)
            bullet_group.add(enemy_bullet2)
        elif self.type == "rectangle":
            enemy_bullet = Bullet(self.rect.centerx, self.rect.centery, 1, 0, "enemy_bullet")
            enemy_bullet1 = Bullet(self.rect.centerx, self.rect.centery, 0, 1, "enemy_bullet")
            enemy_bullet2 = Bullet(self.rect.centerx, self.rect.centery, -1, 0, "enemy_bullet")
            enemy_bullet3 = Bullet(self.rect.centerx, self.rect.centery, 0, -1, "enemy_bullet")
            bullet_group.add(enemy_bullet)
            bullet_group.add(enemy_bullet1)
            bullet_group.add(enemy_bullet2)
            bullet_group.add(enemy_bullet3)
        elif self.type == "diamond":
            enemy_bullet = Bullet(self.rect.centerx, self.rect.centery, 1, 1, "enemy_bullet")
            enemy_bullet1 = Bullet(self.rect.centerx, self.rect.centery, -1, 1, "enemy_bullet")
            enemy_bullet2 = Bullet(self.rect.centerx, self.rect.centery, 1, -1, "enemy_bullet")
            enemy_bullet3 = Bullet(self.rect.centerx, self.rect.centery, -1, -1, "enemy_bullet")
            bullet_group.add(enemy_bullet)
            bullet_group.add(enemy_bullet1)
            bullet_group.add(enemy_bullet2)
            bullet_group.add(enemy_bullet3)
        elif self.type == "circle":
            enemy_bullet = Bullet(self.rect.centerx, self.rect.centery, 1, 1, "enemy_bullet")
            enemy_bullet1 = Bullet(self.rect.centerx, self.rect.centery, -1, 1, "enemy_bullet")
            enemy_bullet2 = Bullet(self.rect.centerx, self.rect.centery, 1, -1, "enemy_bullet")
            enemy_bullet3 = Bullet(self.rect.centerx, self.rect.centery, -1, -1, "enemy_bullet")
            enemy_bullet4 = Bullet(self.rect.centerx, self.rect.centery, 1, 0, "enemy_bullet")
            enemy_bullet5 = Bullet(self.rect.centerx, self.rect.centery, -1, 0, "enemy_bullet")
            enemy_bullet6 = Bullet(self.rect.centerx, self.rect.centery, 0, 1, "enemy_bullet")
            enemy_bullet7 = Bullet(self.rect.centerx, self.rect.centery, 0, -1, "enemy_bullet")
            bullet_group.add(enemy_bullet)
            bullet_group.add(enemy_bullet1)
            bullet_group.add(enemy_bullet2)
            bullet_group.add(enemy_bullet3)
            bullet_group.add(enemy_bullet4)
            bullet_group.add(enemy_bullet5)
            bullet_group.add(enemy_bullet6)
            bullet_group.add(enemy_bullet7)


    def draw(self, display):
        # 적 화면에 생성 함수
        display.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)

def spawn_enemy():
    # 적 생성 함수

    random_x = random.randint(100, 750)
    random_y = random.randint(50, 600)
    while abs(random_x - player.rect.centerx) < 100 and abs(random_x - player.rect.centerx) < 100:
        # 플레이어 가까이에 생성 안되도록
        random_x = random.randint(100, 750)
        random_y = random.randint(50, 600)
    random_type = random.randint(0, 6)

    if random_type == 0 or random_type == 1:
        enemy = Enemy(random_x, random_y, 1.5, 1.5, "triangle")
    elif random_type == 2 or random_type == 3:
        enemy = Enemy(random_x, random_y, 1.5, 1.5, "rectangle")
    elif random_type == 4 or random_type == 5:
        enemy = Enemy(random_x, random_y, 1.5, 1.5, "diamond")
    elif random_type == 6:
        enemy = Enemy(random_x, random_y, 1.5, 1.5, "circle")
    enemy_group.add(enemy)

def reset_game():
    for enemy in enemy_group:
        enemy.kill()
    for bullet in bullet_group:
        bullet.kill()

    # 변수 설정
    score_rate = 100 # 점수 오르는 주기
    score_cooltime = 0 # 점수 쿨타임

    moving_left = False
    moving_right = False
    moving_up = False
    moving_down = False

    clicking = False # 플레이어 클릭하는지 (클릭하면 공격)

    dt = 1
    attack_rate = 15 # 공격 주기
    attack_cooltime = 10 # 공격 쿨타임 

    fade_in = 0

    spawn_rate = random.randint(100, 250) # 적 생성 주기
    spawn_cooltime = 0 # 적 생성 쿨타임

    # 배경음악 재생
    pygame.mixer.music.load('data/sound/bgm.wav')
    pygame.mixer.music.play(-1)
    pygame.mixer.music.set_volume(0.4)

bullet_group = pygame.sprite.Group() # sprite 그룹 생성
enemy_group = pygame.sprite.Group()


player = Player(400, 320, 1.5, 3) # 플레이어

# 변수 설정

moving_left = False
moving_right = False
moving_up = False
moving_down = False

clicking = False # 플레이어 클릭하는지 (클릭하면 공격)

dt = 1
attack_rate = 15 # 공격 주기
attack_cooltime = 10 # 공격 쿨타임 

fade_in = 0

spawn_rate = random.randint(100, 250) # 적 생성 주기
spawn_cooltime = 0 # 적 생성 쿨타임

# 배경음악 재생
pygame.mixer.music.load('data/sound/bgm.wav')
pygame.mixer.music.play(-1)
pygame.mixer.music.set_volume(0.4)

game_run = True
while game_run:
    # FPS 설정
    clock.tick(60) # 1초에 60번 while문이 돌도록 (프레임 설정)

    mouse_x, mouse_y = pygame.mouse.get_pos() # 마우스 좌표

    attack_cooltime += dt
    spawn_cooltime += dt

    screen.fill(background_color) # 이미지 뒤 배경 색

    screen.blit(background_img, (0, 0)) # 백그라운드 이미지 넣기

    # 그룹 업데이트
    bullet_group.update() 
    bullet_group.draw(screen) # 총알이 제일 뒤로 보이도록 먼저 그리기

    if player.drawing:
        player.update_animation()
        player.draw(screen) # 플레이어 생성

    if player.alive:
        enemy_group.update()

    # hp 이미지
    if player.lives == 3:
        screen.blit(pygame.transform.flip(heart, False, False), (0, 0))
        screen.blit(pygame.transform.flip(heart, False, False), (30, 0))
        screen.blit(pygame.transform.flip(heart, False, False), (60, 0))
    elif player.lives == 2:
        screen.blit(pygame.transform.flip(heart, False, False), (0, 0))
        screen.blit(pygame.transform.flip(heart, False, False), (30, 0))
        screen.blit(pygame.transform.flip(black_heart, False, False), (60, 0))
    elif player.lives == 1:
        screen.blit(pygame.transform.flip(heart, False, False), (0, 0))
        screen.blit(pygame.transform.flip(black_heart, False, False), (30, 0))
        screen.blit(pygame.transform.flip(black_heart, False, False), (60, 0))
    else:
        screen.blit(pygame.transform.flip(black_heart, False, False), (0, 0))
        screen.blit(pygame.transform.flip(black_heart, False, False), (30, 0))
        screen.blit(pygame.transform.flip(black_heart, False, False), (60, 0))


    for enemy in enemy_group:
        enemy.update_animation()
        enemy.draw(screen)

    # 화면에 점수 표시
    score_text = myFont.render("Score: " + str(player.score), True, (255,255,255))
    screen.blit(score_text, [350, 0])

    # 플레이어 생존 시
    if player.alive:

        if clicking and attack_cooltime >= attack_rate:
            laser_sound.play()
            bullet = Bullet(player.rect.centerx, player.rect.centery, mouse_x, mouse_y, "player_bullet")
            bullet_group.add(bullet)
            player.score += 10
            
            print("score:", player.score)

            attack_cooltime = 0

        if moving_left or moving_right or moving_up or moving_down: # 이동중이라면
            player.update_action(1) # run 애니메이션으로 전환            
        else:
            player.update_action(0) # idle 애니메이션으로 전환
        player.move(moving_left, moving_right, moving_up, moving_down) # 플레이어 움직임

        if mouse_x < player.rect.x:
            player.flip = True
            player.direction = -1
        else:
            player.flip = False
            player.direction = 1

        # 충돌처리  
        for bullet in bullet_group:
            if bullet.rect.colliderect(player.rect):
                if (bullet.type == "player_bullet" and bullet.count != 0) or bullet.type == "enemy_bullet":
                    bullet.kill()
                    player_hit_sound.play()
                    player.lives -= 1
                    print("life:", player.lives)

                    if player.lives <= 0:
                        print("Game Over")
                        death_sound.set_volume(0.2)
                        death_sound.play()
                        player.update_action(2) # death 애니메이션으로 전환
                        fade_in = 10
                        player.alive = False
                        
                        

        for enemy in enemy_group:
            if enemy.rect.colliderect(player.rect):
                player_hit_sound.play()
                player.lives -= 1
                enemy.kill()
                print("life:", player.lives)
                if player.lives <= 0:
                    print("Game Over")
                    death_sound.set_volume(0.2)
                    death_sound.play()
                    player.update_action(2) # death 애니메이션으로 전환
                    fade_in = 10
                    player.alive = False

    if not player.alive and fade_in > 0:
        fade_in -= 1
        black_surf = pygame.Surface((screen_width,screen_height))
        black_surf.set_alpha(int(255*fade_in/10))
        screen.blit(black_surf,(0,0))
    elif not player.alive and fade_in <= 0:
        screen.blit(pygame.Surface((screen_width,screen_height)),(0,0))
        game_over_text = game_over_font.render("Game Over ", True, (255,0,0))
        press_r_text = myFont.render("press R to replay", True, (255,255,255))
        score_text = myFont.render("Score: " + str(player.score), True, (255,255,255))
        
        screen.blit(game_over_text, [screen_width/2 - 140, screen_height/2 - 100])
        screen.blit(press_r_text, [screen_width/2 - 80, screen_height/2])
        screen.blit(score_text, [350, 0])
   
    # 적 소환
    if spawn_cooltime >= spawn_rate and player.alive:
        if player.score < 500:
            spawn_rate = random.randint(150, 350)
        elif player.score < 700:
            spawn_rate = random.randint(130, 250)
        elif player.score < 1000:
            spawn_rate = random.randint(100, 200)
        else:
            spawn_rate = random.randint(50, 100)

        spawn_enemy()
        spawn_cooltime = 0


    # 각종 입력 감지
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game_run = False # 종료 (게임 loop 빠져 나감)
            #sys.exit()

        if event.type == pygame.KEYDOWN: # 키 누를 때
            if event.key == pygame.K_ESCAPE: # esc 키로 종료
                game_run = False
            if event.key == pygame.K_a:
                moving_left = True
            if event.key == pygame.K_d:
                moving_right = True
            if event.key == pygame.K_w:
                moving_up = True
            if event.key == pygame.K_s:
                moving_down = True
            if event.key == pygame.K_r and not player.alive:
                player = Player(400, 320, 1.5, 3) # 플레이어
                reset_game()

        if event.type == pygame.KEYUP: # 키 뗄 때
            if event.key == pygame.K_a:
                moving_left = False
            if event.key == pygame.K_d:
                moving_right = False
            if event.key == pygame.K_w:
                moving_up = False
            if event.key == pygame.K_s:
                moving_down = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                clicking = True # 클릭하면 True

        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                clicking = False # 클릭 뗄 때 False

    keys = pygame.key.get_pressed()

    # 업데이트
    pygame.display.flip()
    last_frame = screen.copy()

# 게임 종료
pygame.quit()