# 创建时间： 2023/10/1 9:58
import sys
import pygame
import random

'''
    1.pygame.time模块中，使用pygame.time.get_ticks()之前，
需要先设置一个时钟对象，再在主循环中限制游戏帧率
    2.可以使用参数dx，dy来间接控制移动，可以优化手感，可是在需要
斜向运动的场景下会造成斜向运动速度慢的情况，实现斜向运动和水平竖直
运动速度一样可以使用向量来实现
'''

# 窗口长宽数据
screen_width = 850
screen_height = 500
# 游戏版本号
caption = "v1.16"
# 创建颜色
color_black = pygame.Color(0, 0, 0)
color_white = pygame.Color(200, 200, 200)
# 设置坦克移动速度
speed = 1
# 设置子弹同时存在数量上限
bullet_num = 5
# 创建时钟对象
clock = pygame.time.Clock()


class MainGame(object):
    # 创建窗口
    window = None
    # 敌方坦克数量
    enemytank_num = 3
    # 创建我方坦克
    tank_p1 = None
    # 创建敌方坦克列表来储存敌方坦克
    enemytank_list = []

    def __init__(self):
        pass

    def start_game(self):
        # 初始化展示模块
        pygame.display.init()
        # 设置窗口
        MainGame.window = pygame.display.set_mode([screen_width, screen_height])
        # 更改标题
        pygame.display.set_caption("坦克大战 %s" % caption)
        # 初始化我方坦克
        MainGame.tank_p1 = MyTank(400, 400)
        # 填充敌方坦克列表
        MainGame.fill_enemylist()
        while True:
            # 窗口填充黑色
            MainGame.window.fill(color_black)
            # 绘制文本
            MainGame.window.blit(self.set_text("敌方坦克剩余数量 %d" % MainGame.enemytank_num), (0, 0))
            # 获取事件
            self.get_event()
            # 展示我方坦克
            MainGame.tank_p1.display_tank()
            if not MainGame.tank_p1.stop:
                MainGame.tank_p1.move()
            # 展示敌方坦克
            MainGame.build_enemy()
            # 子弹发射
            # 获取当前时间
            MainGame.tank_p1.current_time = pygame.time.get_ticks()
            # 如果当前时间和上次发射时间间隔超过冷却时间，就可以再次发射
            if MainGame.tank_p1.current_time - MainGame.tank_p1.pass_time >= MainGame.tank_p1.cooldown:
                MainGame.tank_p1.shot_on = True
            self.build_bullet(MainGame.tank_p1)
            # 持续刷新窗口
            pygame.display.update()
            # 限制游戏帧率
            clock.tick(60)

    @staticmethod
    # 初始化敌方坦克，并将坦克放在列表中
    def fill_enemylist():
        for i in range(0, MainGame.enemytank_num):
            left = random.randint(1, 800)
            top = random.randint(1, 450)
            enemy = EnemyTank(left, top)
            MainGame.enemytank_list.append(enemy)

    @staticmethod
    # 循环遍历enemytank_list展示敌方坦克
    def build_enemy():
        for enemy in MainGame.enemytank_list:
            enemy.display_tank()
            # 敌方坦克随机移动
            enemy.random_move()
            # 敌方坦克子弹展示
            if enemy.current_time - enemy.pass_time >= enemy.cooldown:
                enemy.shot_on = True
            MainGame.build_bullet(enemy)
            rand_num = random.randint(0, 100)
            if rand_num < 10:
                enemy.shot()

    @staticmethod
    # 循环遍历bullet_list来分别展示子弹，并让其运动
    def build_bullet(tank):
        for bullet in tank.bullet_list:
            bullet.display_bullet()
            bullet.move(tank)

    @staticmethod
    def set_text(text):
        # 初始化字体模块
        pygame.font.init()
        # 创建文字对象
        font = pygame.font.SysFont("kaiti", 18, False)
        text_surface = font.render(text, True, color_white)
        return text_surface

    def get_event(self):
        # 获取操作，遍历操作并识别
        for event in pygame.event.get():
            # 关闭窗口
            if event.type == pygame.QUIT:
                self.end_game()
            if event.type == pygame.KEYDOWN:
                # 坦克移动操作，按下相应操作键的时候移动
                if event.key == pygame.K_UP:
                    MainGame.tank_p1.direction = "U"
                    MainGame.tank_p1.stop = False
                    MainGame.tank_p1.dx = 0
                    MainGame.tank_p1.dy = -1
                elif event.key == pygame.K_DOWN:
                    MainGame.tank_p1.direction = "D"
                    MainGame.tank_p1.stop = False
                    MainGame.tank_p1.dx = 0
                    MainGame.tank_p1.dy = 1
                elif event.key == pygame.K_LEFT:
                    MainGame.tank_p1.direction = "L"
                    MainGame.tank_p1.stop = False
                    MainGame.tank_p1.dx = -1
                    MainGame.tank_p1.dy = 0
                elif event.key == pygame.K_RIGHT:
                    MainGame.tank_p1.direction = "R"
                    MainGame.tank_p1.stop = False
                    MainGame.tank_p1.dx = 1
                    MainGame.tank_p1.dy = 0
                # 坦克射击操作
                elif event.key == pygame.K_SPACE:
                    MainGame.tank_p1.shot()
            # 坦克移动操作，抬起操作键的时候更新停止判断
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_UP or event.key == pygame.K_DOWN:
                    MainGame.tank_p1.dy = 0
                if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                    MainGame.tank_p1.dx = 0

    @staticmethod
    def end_game():
        print("谢谢使用！")
        pygame.quit()
        sys.exit()


class Tank(object):
    def __init__(self, left, top):
        self.direction = None
        # 创建图片集
        self.images = None
        # 默认导入图片为空白透明图片
        self.image = pygame.image.load(r"C:\D\Picture\material\Tank\None.png")
        # 获取图片的矩形区域
        self.rect = self.image.get_rect()
        # 设置图片坐标（left， top）
        self.rect.left = left
        self.rect.top = top
        self.speed = speed
        # 设置坦克的移动参数
        self.dx = 0
        self.dy = 0
        self.stop = False
        # 射击冷却计时
        self.pass_time = 0
        self.current_time = 0
        # 子弹储存列表
        self.bullet_list = []
        # 射击冷却时间（ms）
        self.cooldown = 200
        # 子弹是否可以射击
        self.shot_on = True

    def move(self):
        if self.direction == "U" and self.rect.top == 0:
            self.stop = True
        elif self.direction == "D" and self.rect.top == 450:
            self.stop = True
        elif self.direction == "L" and self.rect.left == 0:
            self.stop = True
        elif self.direction == "R" and self.rect.left == 800:
            self.stop = True
        if 0 <= self.rect.left <= 800 and 0 <= self.rect.top <= 450 and not self.stop:
            self.rect.left += self.dx * self.speed
            self.rect.top += self.dy * self.speed

    def shot(self):
        self.current_time = pygame.time.get_ticks()
        # 实现控制射击间隔
        if self.shot_on and len(self.bullet_list) < bullet_num:
            # 生成子弹
            bullet = Bullet(self)
            # 添加子弹到子弹列表中
            self.bullet_list.append(bullet)
            self.shot_on = False
            self.pass_time = pygame.time.get_ticks()

    def display_tank(self):
        self.image = self.images[self.direction]
        MainGame.window.blit(self.image, self.rect)


class MyTank(Tank):
    def __init__(self, left, top):
        super().__init__(left, top)
        self.images = {
            "U": pygame.image.load(r"C:\D\Picture\material\Tank\MyU.png"),
            "D": pygame.image.load(r"C:\D\Picture\material\Tank\MyD.png"),
            "L": pygame.image.load(r"C:\D\Picture\material\Tank\MyL.png"),
            "R": pygame.image.load(r"C:\D\Picture\material\Tank\MyR.png"),
        }
        self.direction = "U"
        self.image = self.images[self.direction]
        self.stop = True


class EnemyTank(Tank):
    def __init__(self, left, top):
        super().__init__(left, top)
        self.images = {
            "U": pygame.image.load(r"C:\D\Picture\material\Tank\EnemyU.png"),
            "D": pygame.image.load(r"C:\D\Picture\material\Tank\EnemyD.png"),
            "L": pygame.image.load(r"C:\D\Picture\material\Tank\EnemyL.png"),
            "R": pygame.image.load(r"C:\D\Picture\material\Tank\EnemyR.png"),
        }
        self.direction = self.random_direction()
        self.image = self.images[self.direction]
        self.step = random.randint(50, 400)
        self.cooldown = 400

    @staticmethod
    # 利用随机数来控制坦克随机方向
    def random_direction():
        random_num = random.randint(1, 4)
        if random_num == 1:
            return "U"
        elif random_num == 2:
            return "D"
        elif random_num == 3:
            return "L"
        elif random_num == 4:
            return "R"

    # 坦克的随机移动（随机方向+随机步数）
    def random_move(self):
        if self.step <= 0:
            self.direction = self.random_direction()
            if self.direction == "U":
                self.step = random.randint(0, self.rect.top + 1)
                self.dx = 0
                self.dy = -1
            elif self.direction == "D":
                self.step = random.randint(0, 500 - self.rect.top)
                self.dx = 0
                self.dy = 1
            elif self.direction == "L":
                self.step = random.randint(0, self.rect.left + 1)
                self.dx = -1
                self.dy = 0
            elif self.direction == "R":
                self.step = random.randint(0, 850 - self.rect.left)
                self.dx = 1
                self.dy = 0
        else:
            self.stop = False
            self.move()
            self.step -= 1


class Bullet(object):
    def __init__(self, tank):
        self.image = pygame.image.load(r"C:\D\Picture\material\Tank\Bullet.png")
        self.direction = tank.direction
        self.rect = self.image.get_rect()
        if self.direction == "U":
            self.rect.left = tank.rect.left + (tank.rect.width - self.rect.width) / 2
            self.rect.top = tank.rect.top - self.rect.height
        if self.direction == "D":
            self.rect.left = tank.rect.left + (tank.rect.width - self.rect.width) / 2
            self.rect.top = tank.rect.top + tank.rect.height
        if self.direction == "L":
            self.rect.left = tank.rect.left - self.rect.width
            self.rect.top = tank.rect.top + (tank.rect.height - self.rect.height) / 2
        if self.direction == "R":
            self.rect.left = tank.rect.left + tank.rect.width
            self.rect.top = tank.rect.top + (tank.rect.height - self.rect.height) / 2
        self.speed = speed + 2

    def display_bullet(self):
        MainGame.window.blit(self.image, self.rect)

    def move(self, tank):
        if self.direction == "U":
            if self.rect.top > -self.rect.height:
                self.rect.top -= self.speed
            else:
                tank.bullet_list.remove(self)
        elif self.direction == "D":
            if self.rect.top < screen_height:
                self.rect.top += self.speed
            else:
                tank.bullet_list.remove(self)
        elif self.direction == "L":
            if self.rect.left > -self.rect.width:
                self.rect.left -= self.speed
            else:
                tank.bullet_list.remove(self)
        elif self.direction == "R":
            if self.rect.left < screen_width:
                self.rect.left += self.speed
            else:
                tank.bullet_list.remove(self)


class Obstacle(object):
    def __init__(self):
        self.image = pygame.image.load(r"C:\D\Picture\material\Tank\Obstacle.png")
        self.rect = self.image.get_rect()
        self.rect.top = 0
        self.rect.left = 0

    def display_obstacle(self):
        MainGame.window.blit(self.image, self.rect)


class Music(object):
    def __init__(self):
        pass

    def start_music(self):
        pass

    def end_music(self):
        pass


class Explode(object):
    def __init__(self):
        self.image = pygame.image.load(r"C:\D\Picture\material\Tank\Explode.png")
        self.rect = self.image.get_rect()
        self.rect.top = 0
        self.rect.left = 0

    def display_explode(self):
        MainGame.window.blit(self.image, self.rect)


MainGame().start_game()
