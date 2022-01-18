import pygame
import random
import button

pygame.init()
pygame.mixer.init()

clock = pygame.time.Clock()
fps = 60

# game window
bottom_panel = 175
screen_width = 1000
screen_height = 825 + bottom_panel
screen = pygame.display.set_mode((screen_width, screen_height))

#define game variables
current_fighter = 1
total_fighters = 3
action_cooldown = 0
action_wait_time = 90
attack = False
potion = False
potion_effect = 15
clicked = False
game_over = 0
muted = False

#set caption
pygame.display.set_caption("Battle")


#define fonts
font = pygame.font.Font("Fonts/PixelFont.ttf", 26)
#font = pygame.font.SysFont('Times New Roman', 26)

#define colors
red = (184, 20, 2)
green = (74, 194, 68)

# loading images
# Background image
background_img = pygame.image.load("ImageBattle/BigBackground/BigBackground.png").convert_alpha()
# panel image
panel_img = pygame.image.load("ImageBattle/BigIcons/BigPanel.png").convert_alpha()
#button images
potion_img = pygame.image.load("ImageBattle/Icons/potion.png").convert_alpha()
restart_img = pygame.image.load("ImageBattle/Icons/restart.png").convert_alpha()
#load victory and defeat images
victory_img = pygame.image.load("ImageBattle/Icons/victory.png").convert_alpha()
defeat_img = pygame.image.load("ImageBattle/Icons/defeat.png").convert_alpha()
mute_button_img = pygame.image.load("ImageBattle/Icons/mute_button.png").convert_alpha()
mute_button_muted_img = pygame.image.load("ImageBattle/Icons/mute_button_muted.png").convert_alpha()
sweep_attack_button_img = pygame.image.load("ImageBattle/Icons/Sweep_Attack.png").convert_alpha()
#sword image
sword_img = pygame.image.load("ImageBattle/Icons/sword.png").convert_alpha()
#stunned image
stun_img = pygame.image.load("ImageBattle/Icons/stun_ring.png")

#heal sound effect
heal_sound = pygame.mixer.Sound("soundBattle/Knight/Heal/Warrior_Heal_0.wav")
baker_heal_sound = pygame.mixer.Sound("soundBattle/Baker/Heal/Baker_Heal_0.wav")
#win sound effect
win_sound = pygame.mixer.Sound("soundBattle/Music/Battle_Win.wav")
#lose sound effect
lose_sound = pygame.mixer.Sound("soundBattle/Music/Battle_Lose.wav")
#stunned sound effect
stun_applied_sound = pygame.mixer.Sound("soundBattle/General/stun_applied.wav")
#stun removed sound effect
stun_removed_sound = pygame.mixer.Sound("soundBattle/General/stun_removed.wav")

#music
pygame.mixer.music.load("soundBattle/Music/Battle_Music.mp3")
pygame.mixer.music.play()


#create function for drawing text
def draw_text(text, font, text_color, x, y):
    img = font.render(text, True, text_color)
    screen.blit(img, (x, y))


# function for drawing background
def draw_bg():
    screen.blit(background_img, (0, 0))


# function for drawing panel
def draw_panel():
    #draw panel rectangle
    screen.blit(panel_img, (0, screen_height - bottom_panel))

    #show knight stats
    draw_text(f'{baker.name} HP: {baker.hp}', font, red, 100, screen_height - bottom_panel + 10)

    for count, i in enumerate(bandit_list):
        #show name and health
        draw_text(f'{i.name} HP: {i.hp}', font, red, 550, (screen_height - bottom_panel + 10) + count * 60)


# Fighter class
class Fighter:
    def __init__(self, x, y, name, max_hp, strength, potions, stun_chance=0, heal_sound=None):
        self.name = name

        self.max_hp = max_hp
        self.hp = max_hp

        self.strength = strength

        # 0 to 100 integer
        self.stun_chance = stun_chance
        self.stunned = False

        self.start_potions = potions
        self.potions = potions
        self.heal_sound = heal_sound

        self.alive = True

        self.animation_list = []
        self.frame_index = 0
        self.action = 0  # 0:idle, 1:attack, 2:hurt, 3:dead

        self.update_time = pygame.time.get_ticks()

        #load sound effects
        self.sound_list = []
        self.after_atk_sound_list = []

        for i in range(5):
            attack_sound = pygame.mixer.Sound(f"soundBattle/{self.name}/Attack/{i}.wav")
            self.sound_list.append(attack_sound)

        for i in range(4):
            after_atk_sound = pygame.mixer.Sound(f"soundBattle/{self.name}/AfterSFX/{i}.wav")
            pygame.mixer.Sound.set_volume(after_atk_sound, 0.5)
            self.after_atk_sound_list.append(after_atk_sound)



        #load idle images
        #load idle images
        #load idle images
        temp_list = []

        for i in range(8):
            img = pygame.image.load(f"ImageBattle/{self.name}/Idle/{i}.png")
            img = pygame.transform.scale(img, (img.get_width() * 3, img.get_height() * 3))
            temp_list.append(img)
        self.animation_list.append(temp_list)

        #load attack images
        temp_list = []

        for i in range(8):
            img = pygame.image.load(f"ImageBattle/{self.name}/Attack/{i}.png")
            img = pygame.transform.scale(img, (img.get_width() * 3, img.get_height() * 3))
            temp_list.append(img)
        self.animation_list.append(temp_list)

        #load hurt images
        temp_list = []

        for i in range(3):
            img = pygame.image.load(f"ImageBattle/{self.name}/Hurt/{i}.png")
            img = pygame.transform.scale(img, (img.get_width() * 3, img.get_height() * 3))
            temp_list.append(img)
        self.animation_list.append(temp_list)

        # load death image
        temp_list = []

        for i in range(10):
            img = pygame.image.load(f"ImageBattle/{self.name}/Death/{i}.png")
            img = pygame.transform.scale(img, (img.get_width() * 3, img.get_height() * 3))
            temp_list.append(img)
        self.animation_list.append(temp_list)


        self.image = self.animation_list[self.action][self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

    def update(self):
        animation_cooldown = 100
        # Handle animation
        # Update image
        self.image = self.animation_list[self.action][self.frame_index]

        # check if enough time has passed since the last update
        if pygame.time.get_ticks() - self.update_time > animation_cooldown:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1

        # if the animation has run out, reset back to the start
        if self.frame_index >= len(self.animation_list[self.action]):
            if self.action == 3:
                self.frame_index = len(self.animation_list[self.action]) - 1
            else:
                self.idle()


    def idle(self):
        #set variables for idle animation
        self.action = 0
        self.frame_index = 0
        self.update_time = pygame.time.get_ticks()


    def attack(self, target):
        # set variables for attack animation
        #deal damage to enemy
        rand = random.randint(-3, 3)
        damage = self.strength + rand
        target.hp -= damage
        #run enemy hurt animation
        target.hurt()

        #stunning target
        if random.randint(0, 100) <= self.stun_chance:
            stun_applied_sound.play()
            target.stunned = True

        #check if target died
        if target.hp < 1:
            target.hp = 0
            target.alive = False
            target.death()
        damage_text = DamageText(target.rect.centerx, target.rect.y, str(damage), red)
        damage_text_group.add(damage_text)

        #play attack sound
        self.sound_list[random.randint(0, len(self.sound_list) - 1)].play()
        self.after_atk_sound_list[random.randint(0, len(self.after_atk_sound_list) - 1)].play()


        #set variables to attack animation
        self.action = 1
        self.frame_index = 0
        self.update_time = pygame.time.get_ticks()


    def multi_target_attack(self, target1, target2):
        # set variables for attack animation
        #deal damage to enemy
        rand = random.randint(-2, 2)
        damage = (self.strength - 3) + rand

        targetList = [target1, target2]
        for target in targetList:
            target.hp -= damage
            #run enemy hurt animation
            target.hurt()

            #chance to stun target
            if random.randint(0, 100) <= (self.stun_chance - (self.stun_chance / 2)):
                target.stunned = True

            #check if target died
            if target.hp < 1:
                target.hp = 0
                target.alive = False
                target.death()
        for target in targetList:
            damage_text = DamageText(target.rect.centerx, target.rect.y, str(damage), red)
            damage_text_group.add(damage_text)

        #play attack sound
        self.sound_list[random.randint(0, len(self.sound_list) - 1)].play()
        self.after_atk_sound_list[random.randint(0, len(self.after_atk_sound_list) - 1)].play()

        #set variables to attack animation
        self.action = 1
        self.frame_index = 0
        self.update_time = pygame.time.get_ticks()


    def hurt(self):
        # set variables for hurt animation
        self.action = 2
        self.frame_index = 0
        self.update_time = pygame.time.get_ticks()

    def death(self):
        # set variables for death animation
        self.action = 3
        self.frame_index = 0
        self.update_time = pygame.time.get_ticks()

    def reset(self):
        self.alive = True
        self.potions = self.start_potions
        self.hp = self.max_hp
        self.frame_index = 0
        self.action = 0
        self.update_time = pygame.time.get_ticks()
        self.stunned = False

    def stunned_anim(self):
        #if its the enemies turn and they are stunned
        #this will play and remove it
        stun_removed_sound.play()
        self.stunned = False

    def draw(self):
        screen.blit(self.image, self.rect)


class HealthBar:
    def __init__(self, x, y, hp, max_hp):
        self.x = x
        self.y = y
        self.hp = hp
        self.max_hp = max_hp

    def draw(self, hp):
        #update with new health
        self.hp = hp
        #calculate health ratio
        ratio = self.hp / self.max_hp

        pygame.draw.rect(screen, red, (self.x, self.y, 150, 20))
        pygame.draw.rect(screen, green, (self.x, self.y, 150 * ratio, 20))


class DamageText(pygame.sprite.Sprite):
    def __init__(self, x, y, damage, color):
        pygame.sprite.Sprite.__init__(self)
        self.image = font.render(damage, True, color)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.counter = 0

    def update(self):
        #move damage text up
        self.rect.y -= 0.8
        #delete the text after a few seconds
        self.counter += 1
        if self.counter > 45:
            self.kill()



damage_text_group = pygame.sprite.Group()


#create fighters x,    y,  name,   hp, str, pot, stun chance, heal sound effect
#knight = Fighter(275, 525, 'Knight', 30, 10, 3, 20, heal_sound)
baker = Fighter(275, 525, 'Baker', 40, 7, 5, 30, baker_heal_sound)
bandit1 = Fighter(625, 535, 'Snake-Man', 20, 6, 1, 0, heal_sound)
bandit2 = Fighter(775, 535, 'Snake-Man', 20, 6, 1, 0, heal_sound)


def stunned():
    # run this before most stuff
    # it'll check if the bandit is stunned
    # and if it is it will display the stun_img
    for bandit in bandit_list:
        stun_img_location = (bandit.rect.x + 30, bandit.rect.y - 5)
        if bandit.alive:
            if bandit.stunned:
                screen.blit(stun_img, stun_img_location)



# noinspection PyListCreation
#create bandit list, you can fight multiple enemies at once
bandit_list = []
bandit_list.append(bandit1)
bandit_list.append(bandit2)

#create fighter health-bars
#knight_health_bar = HealthBar(100, screen_height - bottom_panel + 40, knight.hp, knight.max_hp)
baker_health_bar = HealthBar(100, screen_height - bottom_panel + 40, baker.hp, baker.max_hp)
bandit1_health_bar = HealthBar(550, screen_height - bottom_panel + 40, bandit1.hp, bandit1.max_hp)
bandit2_health_bar = HealthBar(550, screen_height - bottom_panel + 100, bandit2.hp, bandit2.max_hp)


#create buttons
potion_button = button.Button(screen, 100, screen_height - bottom_panel + 70, potion_img, 64, 64)
restart_button = button.Button(screen, 405, 420, restart_img, 120, 30)
mute_button = button.Button(screen, 910, 16, mute_button_img, 64, 64)
mute_button_muted = button.Button(screen, 910, 16, mute_button_muted_img, 64, 64)

#attack buttons
sweep_attack_button = button.Button(screen, 180, screen_height - bottom_panel + 70, sweep_attack_button_img, 64, 64)






running = True
while running:

    clock.tick(fps)

    # draw background
    draw_bg()

    # draw panel
    draw_panel()
    baker_health_bar.draw(baker.hp)
    #knight_health_bar.draw(knight.hp)
    bandit1_health_bar.draw(bandit1.hp)
    bandit2_health_bar.draw(bandit2.hp)

    # draw fighters
    baker.update()
    baker.draw()
    #knight.update()
    #knight.draw()

    for bandit in bandit_list:
        bandit.update()
        bandit.draw()

    damage_text_group.update()
    damage_text_group.draw(screen)

    # mute and unmute buttons
    if not muted:
        if mute_button.draw():
            pygame.mixer.music.set_volume(0)
            muted = True
    if muted:
        if mute_button_muted.draw():
            pygame.mixer.music.set_volume(1)
            muted = False


    #control player actions
    #reset action variables
    attack = False
    potion = False
    target = None
    sweep_attack = False
    #make sure mouse is visible
    pygame.mouse.set_visible(True)

    pos = pygame.mouse.get_pos()
    for count, bandit in enumerate(bandit_list):
        if bandit.rect.collidepoint(pos):
            #hide mouse
            pygame.mouse.set_visible(False)
            #show sword in place of mouse cursor
            screen.blit(sword_img, pos)

            if clicked and bandit.alive:
                attack = True
                target = bandit_list[count]

    #potion stuff
    if potion_button.draw():
        potion = True
    #show number of potions remaining
    draw_text(str(baker.potions), font, red, 150, screen_height - bottom_panel + 70)

    if sweep_attack_button.draw():
        sweep_attack = True


    if game_over == 0:
        #check if anything in stunned
        stunned()
        #player action
        if baker.alive:
            if current_fighter == 1:
                action_cooldown += 1
                if action_cooldown >= action_wait_time:
                    #look for player action
                    #attack
                    if attack and target is not None:
                        baker.attack(target)
                        current_fighter += 1
                        action_cooldown = 0
                    #potion
                    if potion:
                        if baker.potions > 0:
                            #check if potion would heal the player beyond max health
                            if baker.max_hp - baker.hp > potion_effect:
                                heal_amount = potion_effect
                            else:
                                heal_amount = baker.max_hp - baker.hp

                            baker.heal_sound.play()
                            baker.hp += heal_amount
                            baker.potions -= 1
                            damage_text = DamageText(baker.rect.centerx, baker.rect.y, str(heal_amount), green)
                            damage_text_group.add(damage_text)
                            current_fighter += 1
                            action_cooldown = 0
                    #sweep attack
                    if sweep_attack:
                        baker.multi_target_attack(bandit1, bandit2)
                        current_fighter += 1
                        action_cooldown = 0
        else:
            game_over = -1

        #enemy action
        for count, bandit in enumerate(bandit_list):
            if current_fighter == 2 + count:
                if bandit.alive:
                    action_cooldown += 1
                    if action_cooldown >= action_wait_time:
                        #check if bandit is stunned
                        if bandit.stunned:
                            bandit.stunned_anim()
                            current_fighter += 1
                            action_cooldown = 0
                        else:
                            # check if bandit needs to heal first
                            if (bandit.hp / bandit.max_hp) < 0.5 and bandit.potions > 0:
                                # check if potion would heal the bandit beyond max health
                                if bandit.max_hp - bandit.hp > potion_effect:
                                    heal_amount = potion_effect
                                else:
                                    heal_amount = bandit.max_hp - bandit.hp

                                heal_sound.play()
                                bandit.hp += heal_amount
                                bandit.potions -= 1
                                damage_text = DamageText(bandit.rect.centerx, bandit.rect.y, str(heal_amount), green)
                                damage_text_group.add(damage_text)
                                current_fighter += 1
                                action_cooldown = 0
                            else:
                                #attack
                                bandit.attack(baker)
                                current_fighter += 1
                                action_cooldown = 0
                else:
                    current_fighter += 1

        #if all fighters have had a turn, then reset
        if current_fighter > total_fighters:
            current_fighter = 1

    #check if all bandits are dead
    alive_bandits = 0
    for bandit in bandit_list:
        if bandit.alive:
            alive_bandits += 1
    if alive_bandits == 0:
        game_over = 1

    #check if game is over
    if game_over != 0:
        #stop music
        pygame.mixer.music.stop()

        if game_over == 1:
            screen.blit(victory_img, (325, 350))
        if game_over == -1:
            screen.blit(defeat_img, (290, 50))

        if restart_button.draw():
            baker.reset()

            for bandit in bandit_list:
                bandit.reset()
            current_fighter = 1
            action_cooldown = 0
            game_over = 0
            # play music again
            pygame.mixer.stop()
            pygame.mixer.music.play()


    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            clicked = True
        else:
            clicked = False

    pygame.display.update()

pygame.quit()
