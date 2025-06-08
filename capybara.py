import pygame, sys, random, os

def resource_path(relative_path):
    try: 
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

pygame.init()
pygame.mixer.init()

pygame.init()
screen = pygame.display.set_mode((1280,720))
clock = pygame.time.Clock()
pygame.display.set_caption("Capybara Game")

#Classes
class Capy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        
        self.running_sprites = []
        
        self.running_sprites.append(pygame.transform.scale(pygame.image.load(resource_path("capy/capybara.png")),(100,100)))
        self.running_sprites.append(pygame.transform.scale(pygame.image.load(resource_path("capy/capybara.png")),(100,100)))
        
        self.x = x
        self.y = y
        self.stand_y = y
        
        self.jump_velocity = 0
        self.gravity = 0.4
        self.is_jumping = False
        
        self.current_image = 0
        self.image = self.running_sprites[self.current_image]
        self.rect = self.image.get_rect(center=(self.x,self.y))
        self.mask = pygame.mask.from_surface(self.image)

    def update(self):
        self.animate()
        self.jump()
    
    def animate(self):
        self.current_image += 0.05
        if self.current_image > 2:
            self.current_image = 0
            
        self.image = self.running_sprites[int(self.current_image)]
        self.mask = pygame.mask.from_surface(self.image) 
        #Sound
        self.jump_sound = pygame.mixer.Sound(resource_path("capy/jump.mp3"))  
        self.jump_sound.set_volume(0.5)
    
    def jump(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE] and not self.is_jumping:
            self.jump_velocity = -12  
            self.is_jumping = True
            self.jump_sound.play()

        self.jump_velocity += self.gravity
        self.y += self.jump_velocity

        if self.y >= self.stand_y:  
            self.y = self.stand_y
            self.jump_velocity = 0
            self.is_jumping = False

        self.rect.centery = self.y
        
class Bush(pygame.sprite.Sprite):
    def __init__(self, x, y, speed):
        super().__init__()
        width = random.randint(90, 120)
        height = random.randint(45, 65)
        self.image = pygame.transform.scale(
            pygame.image.load(resource_path("capy/bush.png")).convert_alpha(), 
            (width, height)
        )
        self.rect = self.image.get_rect(midbottom=(x, y))
        self.speed = speed  
        self.mask = pygame.mask.from_surface(self.image)
        

    def update(self):
        self.rect.x -= self.speed
        if self.rect.right < 0:
            self.kill()
            

class Bird(pygame.sprite.Sprite):
    def __init__(self, x, y, speed, upper_limit, lower_limit):
        super().__init__()
        self.image = pygame.transform.scale(pygame.image.load(resource_path("capy/bird.png")), (60, 60)) 
        self.rect = self.image.get_rect(midbottom=(x, y))
        self.speed_x = speed
        self.speed_y = 2
        self.direction = 1 
        self.upper_limit = upper_limit
        self.lower_limit = lower_limit
        self.mask = pygame.mask.from_surface(self.image)

    def update(self):
        self.rect.x -= self.speed_x
        self.rect.y += self.speed_y * self.direction

        if self.rect.top <= self.upper_limit or self.rect.bottom >= self.lower_limit:
            self.direction *= -1

        if self.rect.right < 0:
            self.kill()

class Cloud(pygame.sprite.Sprite):
    def __init__(self, x, y, speed):
        super().__init__()
        original_image = pygame.image.load(resource_path("capy/cloud.png")).convert_alpha()

        scale_factor = random.uniform(0.5, 1) 
        width = int(original_image.get_width() * scale_factor)
        height = int(original_image.get_height() * scale_factor)


        self.image = pygame.transform.scale(original_image, (width, height))
        self.rect = self.image.get_rect(midbottom=(x, y))

        self.speed = speed

    def update(self):
        self.rect.x -= self.speed
        if self.rect.right < 0:
            self.kill()

MIN_SPAWN_DISTANCE = 700  

def can_spawn_at_x(new_x, groups):
    for group in groups:
        for sprite in group:
            if abs(sprite.rect.x - new_x) < MIN_SPAWN_DISTANCE:
                return False
    return True 


filename = "highscore.txt"

def ensure_file_has_value():
    if os.path.isfile(filename):
        with open(filename, "r+") as f:
            content = f.read().strip()
            if content == "":
                f.seek(0)
                f.write("0")
                f.truncate()
    else:
        with open(filename, "w") as f:
            f.write("0")
            
def high_score_w(highscore):
    with open(filename, "w") as file:
        file.write(f"{highscore}")

def ret_hs():
    try:
        with open(filename, "r") as file:
            highscore = file.read().strip()
            return int(highscore) if highscore.isdigit() else 0
    except Exception:
        return 0
        
#Background
transition_start = None
day_color = (198, 252, 255)
night_color = (29, 31, 47)
transition_time = 3000

#Speed
game_speed = 5

#Groups
capy_group = pygame.sprite.GroupSingle()
bush_group = pygame.sprite.Group()
bird_group = pygame.sprite.Group()
cloud_group = pygame.sprite.Group()

#Ground
ground = pygame.image.load(resource_path("capy/groundfinal.png"))
ground = pygame.transform.scale(ground, (1280,200))
ground_x = 0
# ground_rect = ground.get_rect(center=(640,400))
ground_rect = ground.get_rect(midbottom=(640, 720)) 
ground_top = ground_rect.top


#Objects
capy_start_y = (ground_rect.top - 15)
capysaur = Capy(100, capy_start_y)
capy_group.add(capysaur)

#Bush
BUSH_EVENT = pygame.USEREVENT + 1

# def update_bush_timer(speed):
#     base_interval = max(300, 1000 - (speed - 5) * 100)  
#     random_offset = random.randint(-200, 200)         
#     interval = max(250, base_interval + random_offset)  
#     pygame.time.set_timer(BUSH_EVENT, interval)

def schedule_next_bush(speed):
    base = max(300, 1000 - (speed - 5) * 100)
    random_offset = random.randint(-200, 200)
    interval = max(700, base + random_offset)
    pygame.time.set_timer(BUSH_EVENT, interval, loops=1)
    
bush_start_y = ground_rect.top - (-10)
first_bush_x = random.randint(800, 1000)
bush_group.add(Bush(first_bush_x, bush_start_y, game_speed))

schedule_next_bush(game_speed)

#Bird
BIRD_EVENT = pygame.USEREVENT + 2
pygame.time.set_timer(BIRD_EVENT, 4000)

#Cloud
CLOUD_EVENT = pygame.USEREVENT + 3
pygame.time.set_timer(CLOUD_EVENT, 3000)

#Score
score = 0
ensure_file_has_value()
highscore = int(ret_hs())
font = pygame.font.Font(None, 50) 
fonths = pygame.font.Font(None, 20) 
font_play = pygame.font.Font(None, 30) 
game_active = False
start_font = pygame.font.Font(None, 80)
end_font = pygame.font.Font(None, 80)
last_score_time = pygame.time.get_ticks() 
last_speed_increase_score = 0

#GAME CODE
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
            
        if event.type == BUSH_EVENT:
            if not bush_group or all(bush.rect.right < 1000 for bush in bush_group):
                bush_y = ground_top + 10
                
                attempts = 0
                while attempts < 10:
                    bush_x = random.randint(1300, 1500)
                    if can_spawn_at_x(bush_x, [bush_group, bird_group]):
                        bush_group.add(Bush(bush_x, bush_y, game_speed))
                        schedule_next_bush(game_speed)
                        break
                    attempts += 1
                

        
        if event.type == BIRD_EVENT and game_active and score > 50:
            bird_y = random.randint(200, 400)
            upper_limit = 100
            lower_limit = 500
            
            attempts = 0
            while attempts < 100:
                bird_x = random.randint(1300, 1500)
                if can_spawn_at_x(bird_x, [bush_group, bird_group]):
                    bird_group.add(Bird(bird_x, bird_y, game_speed, upper_limit, lower_limit))
                    break
                attempts += 1
                
    
        if event.type == pygame.KEYDOWN:
            if not game_active and event.key == pygame.K_SPACE:
                game_active = True
                score = 0
                game_speed = 5
                bush_group.empty()
                capysaur.y = capy_start_y
                capysaur.rect.centery = capy_start_y
                capysaur.jump_velocity = 0
                capysaur.is_jumping = False
                schedule_next_bush(game_speed)
        
        if event.type == CLOUD_EVENT:
            x = 1300
            y = random.randint(50, 400)
            speed = 1 
            cloud_group.add(Cloud(x, y, speed))
               
        
        # if event.type == pygame.KEYDOWN:
        #     if event.key == pygame.K_RETURN:
        #         pygame.quit()
        #         sys.exit()
    
    current_time = pygame.time.get_ticks()
    if current_time - last_score_time >= 500 and game_active == True: 
        score += 1
        last_score_time = current_time
    
     
     
    #Assets
    if 100 <= score <= 200 and transition_start is None:
        transition_start = pygame.time.get_ticks()

    if transition_start:
        elapsed = pygame.time.get_ticks() - transition_start
        t = min(elapsed / transition_time, 1)  # Clamp to 1
        bg_color = (
            int(day_color[0] + (night_color[0] - day_color[0]) * t),
            int(day_color[1] + (night_color[1] - day_color[1]) * t),
            int(day_color[2] + (night_color[2] - day_color[2]) * t),
        )
    else:
        bg_color = day_color

    screen.fill(bg_color)
    cloud_group.update()
    cloud_group.draw(screen)
    screen.blit(ground, (ground_x, ground_rect.top))
    screen.blit(ground, (ground_x + 1280, ground_rect.top))
    capy_group.draw(screen)
    bush_group.draw(screen)
    bird_group.draw(screen)
    
    if not game_active :
        screen.fill((198, 252, 255))
        screen.blit(ground, (ground_x, ground_rect.top))
        screen.blit(ground, (ground_x + 1280, ground_rect.top))
        cloud_group.update()
        cloud_group.draw(screen)
        transition_start = None
        
        if score > 0:
            end_text = end_font.render("Game Over", True, (0, 0, 0))
            end_rect = end_text.get_rect(center=(640, 280))
            screen.blit(end_text, end_rect)
            score_text = font.render(f"Score: {score}", True, (0, 0, 0))
            score_rect = score_text.get_rect(midtop=(640, end_rect.bottom + 10))
            screen.blit(score_text, score_rect)
            if highscore < score:
                highscore = score
                high_score_w(highscore)
            highscore_text = font.render(f"High Score: {highscore}", True, (0, 0, 0))
            highscore_rect = highscore_text.get_rect(midtop=(640, score_rect.bottom + 10))
            screen.blit(highscore_text,highscore_rect)
            play_text = font_play.render("(Press SPACE to play again)", True, (0,0,0))
            play_rect = play_text.get_rect(midtop=(640, highscore_rect.bottom + 50))
            screen.blit(play_text, play_rect)
                    

        if score == 0:
            start_text = start_font.render("Press SPACE to Play", True, (0, 0, 0))
            text_rect = start_text.get_rect(center=(640, 360))
            screen.blit(start_text, text_rect)

        pygame.display.update()
        clock.tick(120)
        continue
    
    score_text = font.render(f"Score: {score}", True, (0, 0, 0))
    score_position = score_text.get_rect(topleft=(20, 20))
    screen.blit(score_text, score_position)


    display_highscore = max(score, highscore)

    if display_highscore != 0:
        highscore_text = fonths.render(f"High Score: {display_highscore}", True, (0, 0, 0))
        hs_position = highscore_text.get_rect(topleft=(20, score_position.bottom + 10))
        screen.blit(highscore_text, hs_position)
    
    
    if score % 5  == 0 and score != 0 and score != last_speed_increase_score:
        game_speed += 1
        last_speed_increase_score = score
        schedule_next_bush(game_speed) 
        
    ground_x -= game_speed
    
    # screen.blit(ground,(ground_x,360))
    # screen.blit(ground,(ground_x + 1280,360))
    # screen.blit(ground, (ground_x, ground_rect.top))
    # screen.blit(ground, (ground_x + 1280, ground_rect.top))
      
    if ground_x <= -1280:
        ground_x = 0
    
    capy_group.update()
    # capy_group.draw(screen)
    
    bush_group.update()
    # bush_group.draw(screen)
    
    bird_group.update()
    
    if pygame.sprite.spritecollide(capy_group.sprite, bush_group, False, pygame.sprite.collide_mask):
        game_active = False
        bush_group.empty()
        
    if pygame.sprite.spritecollide(capy_group.sprite, bird_group, False, pygame.sprite.collide_mask):
        game_active = False
        bird_group.empty()
    
    
    pygame.display.update()
    clock.tick(120)
