import random
import time
import pygame
import sys
import math
import numpy as np
from datetime import datetime

# 初始化pygame
pygame.init()

class SeasonalTree:
    """季节模型：模拟树叶在春夏秋冬四季中的变化"""
    
    def __init__(self):
        # 窗口设置
        self.width, self.height = 800, 600
        pygame.display.init()  # 确保显示模块正确初始化
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("四季树叶变化模拟")
        
        # 确保字体模块初始化
        pygame.font.init()
        self.font = pygame.font.SysFont('SimHei', 24)  # 中文字体
        self.small_font = pygame.font.SysFont('SimHei', 16)  # 小号字体用于显示环境信息
        
        # 季节定义
        self.seasons = ["春", "夏", "秋", "冬"]
        self.current_season = 0
        self.current_day = 0
        self.days_per_season = 90  # 每个季节90天
        self.season_duration = 7500  # 每个季节持续7.5秒
        self.day_update_interval = int(self.season_duration / self.days_per_season)  # 计算天数更新间隔
        
        # 时间和日期
        self.current_time = 12  # 当前时间（小时）
        self.time_speed = 0.05  # 时间流逝速度
        self.last_time_update = pygame.time.get_ticks()
        self.time_elapsed = 0  # 用于时间更新
        
        # 环境参数
        self.temperature = 15  # 初始温度
        self.humidity = 60     # 初始湿度
        self.wind_strength = 0  # 风力
        self.precipitation = 0  # 降水量
        self.weather_conditions = ["晴朗", "多云", "雨", "雪", "雷暴"]
        self.current_weather = 0  # 默认晴朗
        self.weather_duration = 0  # 天气持续时间
        
        # 地面和土壤相关参数
        self.ground_level = self.height - 180  # 更进一步提高地面位置，确保树木完全显示
        self.soil_height = 160  # 增加土壤厚度
        self.soil_color = (120, 100, 80)  # 默认土壤颜色
        self.grass_blades = []  # 草
        
        # 树干和树枝相关参数
        self.trunk_color = (139, 69, 19)  # 棕色
        self.trunk_x = self.width // 2  # 树干x坐标（中心位置）
        self.trunk_base_y = self.ground_level  # 树干基部y坐标（紧贴地面）
        self.trunk_height = 180  # 设置固定高度，确保树干不会太高
        self.branches = []  # 存储树枝
        
        # 生成树枝结构
        self.generate_branches()
        
        # 树叶参数
        self.leaf_count = 0
        self.leaf_color = (0, 0, 0)
        self.leaf_size = 0
        self.max_leaf_count = 600  # 增加最大叶子数量
        self.max_leaf_size = 8     # 叶子大小上限
        self.leaf_positions = []   # 存储固定的叶子位置
        self.leaf_types = []       # 叶子类型（圆形、椭圆形等）
        self.leaves = []           # 实际叶子列表
        self.ground_leaves = []    # 地面上的落叶
        
        # 季节叶子生成和落叶参数
        self.leaf_spawn_rate = [0.1, 0.05, 0.12, 0.02, 0.01]  # 春夏秋冬雷暴的叶子生成概率
        self.max_leaves_count = [450, 600, 300, 70, 50]     # 各季节的最大叶子数量，增加数量
        self.max_ground_leaves = [30, 50, 150, 80, 40]      # 各季节地面上的落叶数量上限
        
        # 初始化固定的叶子位置
        self.generate_leaf_positions()
        
        # 动态效果参数
        self.target_leaf_count = 0
        self.target_leaf_color = (0, 0, 0)
        self.current_leaf_color = (0, 0, 0)
        self.falling_leaves = []   # 用于存储下落的叶子
        self.leaf_transition_speed = 1.0  # 叶子颜色过渡速度
        
        # 云和降水效果
        self.clouds = []
        self.raindrops = []
        self.snowflakes = []
        self.generate_clouds(5)  # 初始生成5朵云
        
        # 生成草地
        self.generate_grass(100)  # 生成100根草
        
        # 昆虫和鸟类
        self.insects = []
        self.birds = []
        
        # 按钮相关
        self.buttons = []
        self.create_buttons()
        
        # 时钟
        self.clock = pygame.time.Clock()
        
        # 昼夜循环
        self.sky_colors = {
            "dawn": (255, 200, 170),    # 黎明
            "day": (135, 206, 235),     # 白天
            "dusk": (255, 150, 100),    # 黄昏
            "night": (25, 25, 50)       # 夜晚
        }
        self.current_sky_color = self.sky_colors["day"]
        
        # 初始化动画参数
        self.animation_frame = 0
        
        # 添加星星状态跟踪
        self.stars = []
        self.generate_stars(100)  # 生成100颗星星
        
        # 初始化第一个季节
        self.apply_seasonal_effect()
        
        # 添加暂停状态变量
        self.paused = False
        
        # 添加雷暴相关参数
        self.lightning_active = False
        self.lightning_timer = 0
        self.lightning_duration = 10  # 闪电持续时间（帧）
        self.lightning_cooldown = 0
        self.lightning_strike_pos = None
        
        # 添加天体系统
        self.sun_pos = (0, 0)
        self.moon_pos = (0, 0)
        self.sun_radius = 30
        self.moon_radius = 25
        self.sun_color = (255, 255, 0)
        self.moon_color = (200, 200, 200)
        
        # 添加黑色叶子（被雷劈中的叶子）
        self.black_leaves = []
    
    def create_buttons(self):
        """创建所有实体按钮"""
        # 季节切换按钮移到右上角，增加大小和醒目度
        button_width = 80  # 增加按钮宽度
        button_height = 40  # 增加按钮高度
        padding = 10  # 增加按钮间距
        
        # 定义季节按钮的特殊颜色
        season_colors = [
            (100, 200, 100),  # 春季 - 绿色
            (200, 200, 50),   # 夏季 - 黄色
            (200, 100, 50),   # 秋季 - 橙色
            (150, 150, 250)   # 冬季 - 蓝色
        ]
        
        for i, season in enumerate(self.seasons):
            button_x = self.width - 360 + i * (button_width + padding)
            button_y = 20  # 放在右上角
            
            self.buttons.append({
                'rect': pygame.Rect(button_x, button_y, button_width, button_height),
                'text': season,
                'action': 'season',
                'value': i,
                'color': season_colors[i],  # 使用特殊的季节颜色
                'hover_color': (min(season_colors[i][0] + 30, 255), 
                               min(season_colors[i][1] + 30, 255), 
                               min(season_colors[i][2] + 30, 255)),  # 悬停时颜色变亮
                'active_color': (min(season_colors[i][0] + 50, 255), 
                                min(season_colors[i][1] + 50, 255), 
                                min(season_colors[i][2] + 50, 255))  # 激活时颜色更亮
            })
            
        # 天气切换按钮放在左上角
        weather_btn_x = 20
        weather_btn_y = 20
        for i, weather in enumerate(self.weather_conditions):
            self.buttons.append({
                'rect': pygame.Rect(weather_btn_x, weather_btn_y + i * (button_height + padding), 
                                  button_width + 20, button_height),
                'text': weather,
                'action': 'weather',
                'value': i,
                'color': (80, 80, 80),
                'hover_color': (100, 100, 100),
                'active_color': (130, 130, 130)
            })
            
        # 风力按钮
        self.buttons.append({
            'rect': pygame.Rect(weather_btn_x, weather_btn_y + 4 * (button_height + padding), 
                                button_width + 20, button_height),
            'text': "增加风力",
            'action': 'wind',
            'value': 1,
            'color': (80, 100, 120),
            'hover_color': (100, 120, 140),
            'active_color': (120, 140, 160)
        })
        
        self.buttons.append({
            'rect': pygame.Rect(weather_btn_x, weather_btn_y + 5 * (button_height + padding), 
                                button_width + 20, button_height),
            'text': "重置风力",
            'action': 'wind_reset',
            'value': 0,
            'color': (80, 100, 120),
            'hover_color': (100, 120, 140),
            'active_color': (120, 140, 160)
        })
        
        # 添加暂停/继续按钮
        self.buttons.append({
            'rect': pygame.Rect(weather_btn_x, weather_btn_y + 6 * (button_height + padding), 
                                button_width + 20, button_height),
            'text': "暂停/继续",
            'action': 'pause',
            'value': None,
            'color': (160, 60, 60),
            'hover_color': (180, 80, 80),
            'active_color': (200, 100, 100)
        })
        
        # 添加雷暴按钮
        self.buttons.append({
            'rect': pygame.Rect(weather_btn_x, weather_btn_y + 4 * (button_height + padding), 
                              button_width + 20, button_height),
            'text': "雷暴",
            'action': 'weather',
            'value': 4,  # 雷暴天气的索引
            'color': (100, 0, 0),
            'hover_color': (150, 0, 0),
            'active_color': (200, 0, 0)
        })
    
    def generate_branches(self):
        """生成树枝结构，遵循自然生长规律和分形特性"""
        # 主干 - 确保紧贴地面
        trunk_start = (self.trunk_x, self.trunk_base_y)
        trunk_end = (self.trunk_x, self.trunk_base_y - self.trunk_height)
        self.branches.append((trunk_start, trunk_end, 25))  # 主干
        
        # 添加分支，控制递归深度以保持树形美观
        self.add_fractal_branches(trunk_start, trunk_end, 25, 0, 5)  # 减少最大深度到5，避免树过于复杂
    
    def add_fractal_branches(self, start, end, thickness, depth, max_depth):
        """使用分形算法生成更自然的树枝结构"""
        if depth >= max_depth or thickness < 1:  # 降低停止生成的厚度阈值，允许生成更多细枝
            return
            
        x1, y1 = start
        x2, y2 = end
        dx, dy = x2 - x1, y2 - y1
        length = math.sqrt(dx*dx + dy*dy)
        
        # 分支方向和角度
        main_angle = math.atan2(dy, dx)
        
        # 根据深度和角度调整分支数量和特性
        if depth == 0:  # 主干
            branch_count = 4  # 主干分支减少到4个，避免过于拥挤
            length_range = (0.55, 0.65)  # 主干分支更短一些，使树更矮
            angle_range = (-math.pi/4, math.pi/4)  # 适当增加角度范围，使树更宽
        elif depth < 3:  # 主要次级分支
            branch_count = random.randint(2, 3)  # 次级分支2-3个，避免过于复杂
            length_range = (0.5, 0.65)  # 更短的分支
            angle_range = (-math.pi/4.5, math.pi/4.5)
        else:  # 细小末端分支
            branch_count = random.randint(1, 2)  # 末端分支1-2个
            length_range = (0.4, 0.6)  # 末端分支更短
            angle_range = (-math.pi/4, math.pi/4)
        
        # 创建一个均匀分布的角度列表，使分支更均匀
        angles = []
        if branch_count > 1:
            # 如果分支朝上，则分支呈扇形分布
            if -math.pi/2 < main_angle < math.pi/2:
                angle_step = (angle_range[1] - angle_range[0]) / (branch_count - 1)
                for i in range(branch_count):
                    angles.append(angle_range[0] + i * angle_step)
            else:
                # 随机角度
                for i in range(branch_count):
                    angles.append(random.uniform(angle_range[0], angle_range[1]))
        else:
            angles = [random.uniform(angle_range[0], angle_range[1])]
            
        # 随机打乱角度
        random.shuffle(angles)
        
        for i in range(branch_count):
            # 分支长度系数随深度减小
            length_factor = random.uniform(length_range[0], length_range[1]) * (1 - depth/max_depth * 0.15)
            new_length = length * length_factor
            
            # 使用预先计算的角度
            angle_offset = angles[i % len(angles)]
            
            # 添加随机扰动，使树看起来更自然
            new_angle = main_angle + angle_offset + random.uniform(-0.05, 0.05)
            
            # 新分支终点
            new_x = x2 + math.cos(new_angle) * new_length
            new_y = y2 + math.sin(new_angle) * new_length
            
            # 分支粗细按比例减小，但确保末端分支不会太细
            thickness_factor = length_factor * (0.8 - depth * 0.02)
            new_thickness = max(1, thickness * thickness_factor)
            
            # 添加新分支
            self.branches.append((end, (new_x, new_y), new_thickness))
            
            # 递归添加子分支
            self.add_fractal_branches(end, (new_x, new_y), new_thickness, depth + 1, max_depth)
    
    def generate_leaf_positions(self):
        """生成叶子的固定位置，考虑树的生长形态"""
        # 跳过主干，只在分支上生成叶子
        branch_segments = self.branches[1:]
        leaf_distribution = []
        
        for branch in branch_segments:
            start, end, thickness = branch
            branch_length = math.sqrt((end[0] - start[0])**2 + (end[1] - start[1])**2)
            # 粗的分支有更多的叶子
            num_leaves = int(thickness * 1.0) + 3  # 增加叶子基础数量
            
            # 在分支上和周围生成叶子位置
            for i in range(num_leaves):
                # 沿着分支的位置，越靠近分支末端叶子越密集
                t = (i / num_leaves)**1.5  # 非线性分布，更集中在末端
                x = start[0] + (end[0] - start[0]) * t
                y = start[1] + (end[1] - start[1]) * t
                
                # 分支方向和垂直方向
                branch_angle = math.atan2(end[1] - start[1], end[0] - start[0])
                perp_angle = branch_angle + math.pi/2
                
                # 叶子在分支周围的分布，模拟树叶生长模式
                # 增加每个位置生成的叶子数量
                leaf_count = 3 if thickness < 5 else 2  # 细枝上生成更多叶子
                
                for j in range(leaf_count):  # 每个位置生成多个叶子
                    angle_offset = random.uniform(-0.8, 0.8)
                    dist_factor = random.uniform(0.5, 2.0)
                    
                    # 计算偏移量，粗的分支偏移更大
                    offset = thickness * 0.3 * dist_factor
                    leaf_angle = perp_angle + angle_offset
                    
                    # 计算最终位置
                    leaf_x = x + math.cos(leaf_angle) * offset
                    leaf_y = y + math.sin(leaf_angle) * offset
                    
                    # 加入随机扰动，模拟自然生长
                    leaf_x += random.uniform(-2, 2)
                    leaf_y += random.uniform(-2, 2)
                    
                    # 确定叶子类型
                    leaf_type = random.randint(0, 2)  # 0=圆形, 1=椭圆形, 2=小簇
                    
                    self.leaf_positions.append((leaf_x, leaf_y))
                    self.leaf_types.append(leaf_type)
    
    def generate_clouds(self, count):
        """生成云朵，修复offsets错误"""
        self.clouds = []
        for _ in range(count):
            # 创建基本的云结构
            cloud = {
                'x': random.randint(-100, self.width + 100),
                'y': random.randint(50, 150),
                'width': random.randint(100, 200),
                'height': random.randint(40, 80),
                'speed': random.uniform(0.2, 0.5),
                'offsets': [],  # 存储偏移量
                'sizes': []     # 存储大小
            }
            
            # 生成5个圆形组成一朵云
            for i in range(5):
                # 生成随机偏移量
                offset_x = random.uniform(-30, 30)
                offset_y = random.uniform(-15, 15)
                cloud['offsets'].append((offset_x, offset_y))
                
                # 生成随机大小
                size = random.randint(20, 50)
                cloud['sizes'].append(size)
            
            self.clouds.append(cloud)
    
    def generate_grass(self, count):
        """生成草地"""
        self.grass_blades = []
        for _ in range(count):
            x = random.randint(0, self.width)
            height = random.randint(5, 15)
            self.grass_blades.append({
                'x': x,
                'height': height,
                'phase': random.uniform(0, 2 * math.pi)
            })
    
    def draw(self):
        """绘制整个场景"""
        # 绘制天空
        self.draw_sky()
        
        # 绘制云彩和天气效果
        self.draw_weather()
        
        # 绘制草地
        self.draw_grass()
        
        # 绘制地面
        self.draw_ground()
        
        # 绘制树木
        self.draw_tree()
        
        # 绘制叶子
        self.draw_leaves()
        
        # 绘制飘落的叶子
        self.draw_falling_leaves()
        
        # 绘制野生动物
        self.draw_wildlife()
        
        # 绘制按钮
        self.draw_buttons()
        
        # 绘制信息面板
        self.draw_info_panel()
        
        # 绘制天体
        self.draw_astronomical_bodies()
        
        # 绘制闪电
        if self.lightning_active:
            self.draw_lightning()
        
        # 绘制黑色叶子
        self.draw_black_leaves()
    
    def draw_sky(self):
        """绘制天空，考虑昼夜变化"""
        # 根据时间确定天空颜色
        if self.current_time < 6:  # 凌晨
            sky_color = (20, 20, 50)  # 深蓝色夜空
        elif self.current_time < 7:  # 黎明
            t = (self.current_time - 6) / 1  # 0-1之间的值
            sky_color = (
                int(20 + t * (135 - 20)),  # 从深蓝到淡蓝
                int(20 + t * (206 - 20)),
                int(50 + t * (235 - 50))
            )
        elif self.current_time < 18:  # 白天
            sky_color = (135, 206, 235)  # 天蓝色
            
            # 根据季节调整天空颜色
            if self.current_season == 0:  # 春天
                sky_color = (173, 216, 230)  # 淡蓝色
            elif self.current_season == 1:  # 夏天
                sky_color = (135, 206, 235)  # 明亮的蓝色
            elif self.current_season == 2:  # 秋天
                sky_color = (176, 196, 222)  # 带灰的蓝色
            else:  # 冬天
                sky_color = (220, 226, 240)  # 带白的淡蓝色
        elif self.current_time < 19:  # 黄昏
            t = (self.current_time - 18) / 1  # 0-1之间的值
            sky_color = (
                int(135 - t * (135 - 20)),  # 从淡蓝到深蓝
                int(206 - t * (206 - 20)),
                int(235 - t * (235 - 50))
            )
        else:  # 夜晚
            sky_color = (20, 20, 50)  # 深蓝色夜空
            
        # 填充天空
        self.screen.fill(sky_color)
        
        # 夜晚显示星星，但在下雪天气时不显示
        if (self.current_time < 6 or self.current_time > 19) and self.current_weather != 3:
            for star in self.stars:
                # 使用正弦函数生成缓慢周期性的亮度变化
                # 每颗星星有自己的闪烁速度和相位
                blink_factor = math.sin(self.animation_frame * star['blink_speed'] + star['phase'])
                # 将正弦值转换为0.6-1.0的亮度范围，使星星始终可见但亮度变化
                brightness = 0.6 + (blink_factor + 1) * 0.2
                
                # 星星颜色 - 使用亮度调整
                star_color = (int(255 * brightness), int(255 * brightness), int(255 * brightness))
                
                # 绘制星星 - 使用记录的位置和大小
                pygame.draw.circle(self.screen, star_color, (int(star['x']), int(star['y'])), star['size'])
            
            # 偶尔添加一些流星效果
            if random.random() < 0.005 and not self.paused:  # 每200帧约1次，且非暂停状态
                start_x = random.randint(0, self.width)
                start_y = random.randint(0, self.ground_level // 3)
                end_x = start_x + random.randint(50, 150) * (1 if random.random() > 0.5 else -1)
                end_y = start_y + random.randint(30, 80)
                
                # 确保流星不会超出屏幕边界
                end_x = max(0, min(self.width, end_x))
                end_y = max(0, min(self.ground_level - 50, end_y))
                
                # 绘制流星
                pygame.draw.line(self.screen, (255, 255, 255), (start_x, start_y), (end_x, end_y), 1)

    def draw_weather(self):
        """绘制天气效果"""
        # 绘制云彩
        for cloud in self.clouds:
            # 根据时间和天气调整云的颜色
            if self.current_time < 6 or self.current_time > 19:  # 夜间
                cloud_color = (100, 100, 120)  # 夜间云色更暗
            else:
                if self.current_weather == 1:  # 多云
                    cloud_color = (220, 220, 220)
                elif self.current_weather == 2:  # 雨
                    cloud_color = (120, 120, 130)
                elif self.current_weather == 3:  # 雪
                    cloud_color = (240, 240, 250)
                else:  # 晴朗
                    cloud_color = (250, 250, 250)
            
            # 绘制云朵 (多个重叠的圆形)
            x, y = cloud['x'], cloud['y']
            for i in range(5):
                offset = cloud['offsets'][i]
                size = cloud['sizes'][i]
                pygame.draw.circle(self.screen, cloud_color, (int(x + offset[0]), int(y + offset[1])), size)
        
        # 绘制雨滴
        if self.current_weather == 2:  # 下雨
            for drop in self.raindrops:
                pygame.draw.line(self.screen, (200, 200, 250), 
                                (drop[0], drop[1]), 
                                (drop[0] + self.wind_strength * 2, drop[1] + 10), 1)
        
        # 绘制雪花
        elif self.current_weather == 3:  # 下雪
            for flake in self.snowflakes:
                pygame.draw.circle(self.screen, (250, 250, 250), 
                                  (int(flake[0]), int(flake[1])), 
                                  int(flake[2]))

    def draw_wildlife(self):
        """绘制野生动物（昆虫和鸟类）"""
        # 只在春夏绘制昆虫和鸟类
        if self.current_season not in [0, 1]:
            return
            
        # 季节性生物
        if self.current_season == 0:  # 春天
            # 绘制蝴蝶
            for insect in self.insects:
                x, y = insect['pos']
                size = insect['size']
                phase = insect['phase'] + self.animation_frame * 0.2
                
                # 蝴蝶翅膀
                wing_open = (math.sin(phase) + 1) / 2  # 0-1 之间波动
                
                # 画蝴蝶身体
                pygame.draw.line(self.screen, (40, 40, 40), (x, y - size), (x, y + size), 2)
                
                # 画翅膀
                wing_width = size * 3 * wing_open
                wing_height = size * 2
                
                # 左翅膀
                wing_left = pygame.Rect(
                    int(x - wing_width), int(y - wing_height/2), 
                    int(wing_width), int(wing_height)
                )
                pygame.draw.ellipse(self.screen, (200, 150, 255), wing_left)
                
                # 右翅膀
                wing_right = pygame.Rect(
                    int(x), int(y - wing_height/2), 
                    int(wing_width), int(wing_height)
                )
                pygame.draw.ellipse(self.screen, (200, 150, 255), wing_right)
        
        elif self.current_season == 1:  # 夏天
            # 绘制蜜蜂
            for insect in self.insects:
                x, y = insect['pos']
                size = insect['size']
                
                # 蜜蜂身体
                pygame.draw.circle(self.screen, (250, 200, 0), (int(x), int(y)), size)
                pygame.draw.circle(self.screen, (0, 0, 0), (int(x + size), int(y)), size)
                
                # 蜜蜂翅膀
                wing_y = y - size * 0.8
                pygame.draw.ellipse(self.screen, (255, 255, 255), 
                                 (int(x - size), int(wing_y), int(size*1.5), int(size)))
        
        # 绘制鸟
        for bird in self.birds:
            x, y = bird['pos']
            size = bird['size']
            direction = bird['direction']
            phase = bird['phase'] + self.animation_frame * 0.1
            
            # 鸟翅膀扇动
            wing_y = math.sin(phase) * size * 0.5
            
            # 鸟身体和翅膀
            body_color = (80, 80, 80) if self.current_season == 0 else (200, 50, 50)
            
            # 鸟身体
            pygame.draw.circle(self.screen, body_color, (int(x), int(y)), size)
            
            # 鸟头
            pygame.draw.circle(self.screen, body_color, (int(x + direction * size), int(y - size*0.5)), int(size*0.7))
            
            # 鸟翅膀
            wing_points = [
                (x, y),
                (x + direction * size, y - wing_y),
                (x + direction * size * 2, y)
            ]
            pygame.draw.polygon(self.screen, (50, 50, 50), wing_points)

    def run(self):
        """运行程序，提高帧率与响应速度"""
        last_update = pygame.time.get_ticks()
        running = True
        
        # 展示使用说明
        welcome_message = [
            "四季树叶模拟器",
            "点击季节按钮切换季节",
            "空格键增加风力",
            "R键重置风力",
            "W键改变天气",
            "点击树干使叶子掉落",
            "按1-4键快速切换春夏秋冬",
            "按P键暂停/继续时间流逝"
        ]
        
        show_welcome = True
        welcome_start = pygame.time.get_ticks()
        
        # 主循环
        while running:
            # 处理事件
            running = self.handle_events()
            
            # 更新天数和动画，提高响应速度
            current_time = pygame.time.get_ticks()
            if current_time - last_update > self.day_update_interval // 2:  # 提高更新频率
                self.update()
                last_update = current_time
            
            # 绘制
            self.draw()
            
            # 显示欢迎信息
            if show_welcome and pygame.time.get_ticks() - welcome_start < 8000:
                # 半透明背景
                s = pygame.Surface((self.width, 200))
                s.set_alpha(180)
                s.fill((0, 0, 0))
                self.screen.blit(s, (0, 100))
                
                # 显示欢迎信息
                for i, line in enumerate(welcome_message):
                    text = self.font.render(line, True, (255, 255, 255))
                    self.screen.blit(text, (self.width//2 - text.get_width()//2, 120 + i * 30))
            else:
                show_welcome = False
            
            pygame.display.flip()
            self.clock.tick(60)  # 提高帧率到60帧
        
        pygame.quit()
        sys.exit()
    
    def update(self):
        """更新状态，提高响应速度"""
        # 更新动画帧，即使暂停也继续更新动画
        self.animation_frame += 1
        
        # 如果暂停状态，不更新时间和季节相关内容
        if self.paused:
            # 只更新落叶、云和降水的动态效果，保持视觉连续性
            self.update_falling_leaves()
            self.update_clouds()
            self.update_precipitation()
            self.update_wildlife()
            return
        
        # 更新天数和季节
        self.current_day += 1
        if self.current_day >= self.days_per_season:
            self.current_day = 0
            self.current_season = (self.current_season + 1) % 4
            print(f"切换到{self.seasons[self.current_season]}季")
            self.apply_seasonal_effect()
        
        # 更新时间，更快的响应
        current_time = pygame.time.get_ticks()
        if current_time - self.last_time_update > 50:  # 每50毫秒更新一次，提高响应速度
            self.current_time = (self.current_time + self.time_speed) % 24
            self.last_time_update = current_time
            
            # 减少天气随机变化的频率，避免干扰用户操作
            if random.random() < 0.005:  # 降低随机天气变化概率
                self.update_weather()
        
        # 动态更新叶子数量，但避免闪烁
        if self.current_season != 3:  # 冬天不更新落叶
            if abs(self.leaf_count - self.target_leaf_count) > 0:
                if self.leaf_count < self.target_leaf_count:
                    # 春天和夏天叶子生长得更快
                    growth_rate = 3 if self.current_season in [0, 1] else 1
                    self.leaf_count = min(self.leaf_count + growth_rate, self.target_leaf_count)
                    self.generate_leaves()
                elif self.leaf_count > self.target_leaf_count:
                    # 秋天叶子掉落更快
                    if self.current_season == 2:
                        fall_rate = 5
                        leaves_to_remove = min(fall_rate, self.leaf_count - self.target_leaf_count)
                        
                        for _ in range(leaves_to_remove):
                            if self.leaves:
                                # 优先从叶子底部移除，更符合自然规律
                                self.leaves.sort(key=lambda leaf: -leaf[1])  # 按高度从上到下排序
                                leaf = self.leaves.pop()  # 移除最底部的叶子
                                
                                # 创建下落的叶子，添加物理效果
                                self.falling_leaves.append({
                                    'pos': (leaf[0], leaf[1]),
                                    'size': leaf[2],
                                    'speed': random.uniform(0.5, 2.0),
                                    'swing': random.uniform(-1, 1) * self.wind_strength,
                                    'rotation': random.uniform(0, 360),
                                    'rotation_speed': random.uniform(-5, 5),
                                    'type': random.randint(0, 2),  # 随机叶子类型
                                    'color': self.current_leaf_color,  # 保持颜色一致
                                    'x': leaf[0],
                                    'y': leaf[1]
                                })
                        self.leaf_count = len(self.leaves)
        
        # 动态更新叶子颜色
        r1, g1, b1 = self.current_leaf_color
        r2, g2, b2 = self.target_leaf_color
        
        # 平滑过渡颜色，速度受季节影响
        transition_speed = 0.03 * self.leaf_transition_speed
        
        self.current_leaf_color = (
            r1 + int((r2 - r1) * transition_speed),
            g1 + int((g2 - g1) * transition_speed),
            b1 + int((b2 - b1) * transition_speed)
        )
        
        self.leaf_color = self.current_leaf_color
        
        # 更新落叶
        self.update_falling_leaves()
        
        # 更新云的位置
        self.update_clouds()
        
        # 更新降水（雨或雪）
        self.update_precipitation()
        
        # 更新野生动物
        self.update_wildlife()
        
        # 更新天体位置
        self.update_astronomical_bodies()
        
        # 处理闪电效果
        self.handle_lightning()
    
    def handle_events(self):
        """处理事件，提高按键响应速度"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            # 处理鼠标点击，立即响应
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                
                # 检查是否点击了任何按钮
                button_clicked = False
                for button in self.buttons:
                    if button['rect'].collidepoint(mouse_pos):
                        # 立即执行按钮对应的操作
                        if button['action'] == 'season':
                            self.change_season(button['value'])
                            button_clicked = True
                            break
                        elif button['action'] == 'weather':
                            self.change_weather(button['value'])
                            button_clicked = True
                            break
                        elif button['action'] == 'wind':
                            self.increase_wind()
                            button_clicked = True
                            break
                        elif button['action'] == 'wind_reset':
                            self.reset_wind()
                            button_clicked = True
                            break
                        elif button['action'] == 'pause':
                            self.paused = not self.paused
                            pause_status = "暂停" if self.paused else "继续"
                            print(f"时间已{pause_status}")
                            button_clicked = True
                            break
                        elif button['action'] == 'lightning':
                            # 触发闪电
                            if not self.lightning_active and self.lightning_cooldown == 0:
                                self.lightning_active = True
                                self.lightning_strike_pos = None
                
                # 如果没有点击按钮，检查是否点击了树干
                if not button_clicked and abs(mouse_pos[0] - self.trunk_x) < 25 and self.trunk_base_y - self.trunk_height < mouse_pos[1] < self.trunk_base_y:
                    # 模拟风吹或树干震动，导致一些叶子掉落
                    self.shake_tree()
            
            # 处理键盘事件，立即响应
            if event.type == pygame.KEYDOWN:
                # 空格键增加风力
                if event.key == pygame.K_SPACE:
                    self.increase_wind()
                
                # 按R键重置风力
                elif event.key == pygame.K_r:
                    self.reset_wind()
                
                # W键改变天气
                elif event.key == pygame.K_w:
                    self.change_weather((self.current_weather + 1) % 4)
                    
                # 按1-4键快速切换季节
                elif event.key == pygame.K_1:
                    self.change_season(0)  # 春
                elif event.key == pygame.K_2:
                    self.change_season(1)  # 夏
                elif event.key == pygame.K_3:
                    self.change_season(2)  # 秋
                elif event.key == pygame.K_4:
                    self.change_season(3)  # 冬
                
                # 按P键暂停/继续时间流逝
                elif event.key == pygame.K_p:
                    self.paused = not self.paused
                    pause_status = "暂停" if self.paused else "继续"
                    print(f"时间已{pause_status}")
        
        # 更新按钮悬停状态
        mouse_pos = pygame.mouse.get_pos()
        for button in self.buttons:
            button['hover'] = button['rect'].collidepoint(mouse_pos)
            
        return True
    
    def handle_button_click(self, mouse_pos):
        """处理按钮点击"""
        for button in self.buttons:
            if button['rect'].collidepoint(mouse_pos):
                # 执行按钮对应的操作
                if button['action'] == 'season':
                    self.change_season(button['value'])
                elif button['action'] == 'weather':
                    self.change_weather(button['value'])
                elif button['action'] == 'wind':
                    self.increase_wind()
                elif button['action'] == 'wind_reset':
                    self.reset_wind()
                elif button['action'] == 'pause':
                    self.paused = not self.paused
                    pause_status = "暂停" if self.paused else "继续"
                    print(f"时间已{pause_status}")
                elif button['action'] == 'lightning':
                    # 触发闪电
                    if not self.lightning_active and self.lightning_cooldown == 0:
                        self.lightning_active = True
                        self.lightning_strike_pos = None
                # 按钮点击效果（闪烁或动画）可以在这里添加
                break
    
    def increase_wind(self):
        """增加风力"""
        self.wind_strength = min(5.0, self.wind_strength + 1.0)
        # 风大时有些叶子会掉落
        if self.wind_strength > 2.5 and self.leaves:
            for _ in range(int(self.wind_strength * 2)):
                if self.leaves:
                    idx = random.randint(0, len(self.leaves)-1)
                    leaf = self.leaves.pop(idx)
                    self.falling_leaves.append({
                        'pos': (leaf[0], leaf[1]),
                        'size': leaf[2],
                        'speed': random.uniform(0.5, 2.0),
                        'swing': random.uniform(-2, 2) * self.wind_strength,
                        'rotation': random.uniform(0, 360),
                        'rotation_speed': random.uniform(-5, 5)
                    })
            self.leaf_count = len(self.leaves)
    
    def reset_wind(self):
        """重置风力为季节默认值"""
        default_wind = [1.0, 0.7, 1.8, 2.5, 3.0]
        self.wind_strength = default_wind[self.current_season]
    
    def change_weather(self, weather_index):
        """改变天气状况"""
        self.current_weather = weather_index
        self.weather_duration = 100
        # 清空降水
        self.raindrops = []
        self.snowflakes = []
        
        # 更新风力
        if self.current_weather in [2, 3]:  # 雨或雪时风力较大
            self.wind_strength = random.uniform(1.0, 3.0)
        else:
            self.wind_strength = random.uniform(0.2, 1.5)
            
        # 下雪时可能会在地面积雪
        if self.current_weather == 3 and self.current_season == 3:  # 冬天下雪
            self.soil_color = (240, 240, 250)  # 雪地
    
    def shake_tree(self):
        """摇晃树，使一些叶子掉落"""
        if not self.leaves:
            return
            
        # 掉落数量取决于季节
        if self.current_season == 0:  # 春
            drop_count = random.randint(1, 3)
        elif self.current_season == 1:  # 夏
            drop_count = random.randint(2, 5)
        elif self.current_season == 2:  # 秋
            drop_count = random.randint(5, 10)
        else:  # 冬
            drop_count = random.randint(0, 2)
        
        drop_count = min(drop_count, len(self.leaves))
        for _ in range(drop_count):
            if self.leaves:
                idx = random.randint(0, len(self.leaves)-1)
                leaf = self.leaves.pop(idx)
                self.falling_leaves.append({
                    'pos': (leaf[0], leaf[1]),
                    'size': leaf[2],
                    'speed': random.uniform(1.0, 3.0),
                    'swing': random.uniform(-3, 3),
                    'rotation': random.uniform(0, 360),
                    'rotation_speed': random.uniform(-8, 8)
                })
        
        self.leaf_count = len(self.leaves)
    
    def change_season(self, season):
        """手动更改季节"""
        self.current_season = season
        self.current_day = 0  # 重置天数
        self.apply_seasonal_effect()
    
    def update_leaves(self):
        """生成树叶，使叶子位置固定不闪烁"""
        # 限制叶子数量不超过位置数量
        effective_count = min(self.leaf_count, len(self.leaf_positions))
        
        # 如果已有叶子，则保持现有叶子位置不变，只增加或减少叶子
        if hasattr(self, 'leaves') and self.leaves:
            current_count = len(self.leaves)
            
            if effective_count > current_count:
                # 需要添加新叶子
                # 找出当前未使用的位置
                used_positions = set((leaf[0], leaf[1]) for leaf in self.leaves)
                available_positions = [pos for pos in self.leaf_positions if pos not in used_positions]
                
                # 如果可用位置不足，就随机使用已有位置
                if len(available_positions) < (effective_count - current_count):
                    available_positions = self.leaf_positions
                
                # 随机选择需要的数量的新位置
                new_positions = random.sample(available_positions, effective_count - current_count)
                
                # 添加新叶子
                for x, y in new_positions:
                    # 随机大小变化但保持稳定
                    size_variation = random.uniform(0.9, 1.1)
                    size = self.leaf_size * size_variation
                    self.leaves.append((x, y, size))
                    
            elif effective_count < current_count:
                # 需要移除一些叶子，按季节特点移除
                if self.current_season == 2:  # 秋天，主要从底部移除叶子
                    # 按高度排序，移除最低的叶子
                    self.leaves.sort(key=lambda leaf: -leaf[1])  # 从高到低排序
                    self.leaves = self.leaves[:effective_count]
                else:  # 其他季节随机移除
                    # 随机抽样保留指定数量的叶子
                    indices = list(range(len(self.leaves)))
                    random.shuffle(indices)
                    self.leaves = [self.leaves[i] for i in indices[:effective_count]]
        else:
            # 如果还没有叶子，需要初始化
            self.leaves = []
            if effective_count > 0:
                # 按季节特点选择叶子位置
                if self.current_season in [0, 1]:  # 春夏
                    # 优先选择树顶部的位置
                    positions_with_height = [(pos, 1.0 - (pos[1] / self.ground_level)) for pos in self.leaf_positions]
                    positions_with_height.sort(key=lambda x: -x[1])  # 按高度降序排序
                    positions_to_use = [pos for pos, _ in positions_with_height[:effective_count]]
                else:  # 秋冬
                    # 均匀随机选择
                    positions_to_use = random.sample(self.leaf_positions, effective_count)
                
                # 创建叶子
                for x, y in positions_to_use:
                    # 随机大小变化但保持稳定
                    size_variation = random.uniform(0.9, 1.1)
                    size = self.leaf_size * size_variation
                    
                    # 保存叶子
                    self.leaves.append((x, y, size))
    
    def update_falling_leaves(self):
        """更新落叶的位置和旋转"""
        new_falling_leaves = []
        for leaf in self.falling_leaves:
            # 更新位置，考虑风力和重力
            x, y = leaf['pos']
            
            # 添加风的影响和随机摆动
            swing = leaf['swing'] + math.sin(self.animation_frame * 0.05) * self.wind_strength
            
            # 落叶运动物理效果
            new_x = x + swing
            new_y = y + leaf['speed']
            
            # 更新旋转
            leaf['rotation'] = (leaf['rotation'] + leaf['rotation_speed']) % 360
            
            # 检查是否落到地面
            if new_y < self.ground_level:
                leaf['pos'] = (new_x, new_y)
                new_falling_leaves.append(leaf)
            # 有小概率叶子会堆积在地面上
            elif random.random() < 0.1 and self.current_season in [2, 3]:  # 秋冬
                # 不再在这里直接绘制，这是更新方法
                pass
        
        self.falling_leaves = new_falling_leaves
    
    def update_clouds(self):
        """更新云的位置"""
        for cloud in self.clouds:
            # 云的移动方向受风力影响
            cloud['x'] += cloud['speed'] * self.wind_strength
            
            # 如果云飘出屏幕，从另一侧重新进入
            if cloud['x'] > self.width + 100:
                cloud['x'] = -cloud['width'] - 50
                cloud['y'] = random.randint(50, 150)
            elif cloud['x'] < -cloud['width'] - 100:
                cloud['x'] = self.width + 50
                cloud['y'] = random.randint(50, 150)
    
    def update_precipitation(self):
        """更新降水（雨或雪）"""
        # 雨
        if self.current_weather in [2, 4]:  # 下雨或雷暴
            # 随机生成新雨滴
            for _ in range(10):  # 增加雨滴数量
                self.raindrops.append([
                    random.randint(0, self.width),
                    random.randint(0, self.ground_level // 2)
                ])
            
            # 更新现有雨滴位置
            new_raindrops = []
            for drop in self.raindrops:
                drop[1] += 15  # 增加雨滴下落速度
                drop[0] += self.wind_strength * 2  # 增加风力影响
                
                if drop[1] < self.ground_level:
                    new_raindrops.append(drop)
            
            # 限制雨滴数量
            self.raindrops = new_raindrops[:500]  # 增加最大雨滴数量
        
        # 雪
        elif self.current_weather == 3:  # 下雪
            # 随机生成新雪花
            for _ in range(2):
                self.snowflakes.append([
                    random.randint(0, self.width),
                    random.randint(0, self.ground_level // 2),
                    random.uniform(1, 3)  # 雪花大小
                ])
            
            # 更新现有雪花位置
            new_snowflakes = []
            for flake in self.snowflakes:
                # 雪花下落慢一些，有随机摆动
                flake[1] += random.uniform(1, 3)
                flake[0] += math.sin(self.animation_frame * 0.05 + flake[1] * 0.1) * 2 + self.wind_strength
                
                if flake[1] < self.ground_level:
                    new_snowflakes.append(flake)
            
            # 限制雪花数量
            self.snowflakes = new_snowflakes[:200]
        else:
            # 清空降水
            self.raindrops = []
            self.snowflakes = []
    
    def update_wildlife(self):
        """更新野生动物"""
        # 更新昆虫位置
        new_insects = []
        for insect in self.insects:
            x, y = insect['pos']
            
            # 随机移动
            dx = random.uniform(-2, 2) + math.sin(self.animation_frame * 0.1) * 2
            dy = random.uniform(-1, 1) + math.cos(self.animation_frame * 0.1) * 2
            
            # 昆虫受风影响
            dx += self.wind_strength * 0.5
            
            # 边界检查
            x = max(50, min(self.width - 50, x + dx))
            y = max(50, min(self.ground_level - 50, y + dy))
            
            insect['pos'] = (x, y)
            insect['phase'] += 0.2  # 翅膀扇动速度
            
            new_insects.append(insect)
        
        self.insects = new_insects
        
        # 更新鸟的位置
        new_birds = []
        for bird in self.birds:
            x, y = bird['pos']
            speed = bird['speed']
            direction = bird['direction']
            
            # 鸟飞行
            x += speed * direction
            
            # 如果飞出屏幕，从另一侧进入
            if x > self.width + 50:
                x = -50
                y = random.randint(50, self.ground_level - 100)
            elif x < -50:
                x = self.width + 50
                y = random.randint(50, self.ground_level - 100)
            
            bird['pos'] = (x, y)
            bird['phase'] += 0.3  # 翅膀扇动速度
            
            new_birds.append(bird)
        
        self.birds = new_birds
        
        # 根据季节随机生成昆虫和鸟类
        if self.current_season == 0:  # 春天，较多昆虫和鸟类
            if len(self.insects) < 10 and random.random() < 0.05:  # 增加昆虫生成概率
                self.add_insect()
            if len(self.birds) < 6 and random.random() < 0.03:  # 增加鸟类生成概率
                self.add_bird()
        elif self.current_season == 1:  # 夏天，大量昆虫和鸟类
            if len(self.insects) < 15 and random.random() < 0.06:  # 增加昆虫生成概率
                self.add_insect()
            if len(self.birds) < 8 and random.random() < 0.04:  # 增加鸟类生成概率
                self.add_bird()
        elif self.current_season == 2:  # 秋天，鸟类数量增加并统一方向
            if len(self.birds) < 12 and random.random() < 0.05:  # 增加鸟类生成概率
                self.add_bird()
            for bird in self.birds:
                bird['direction'] = 1  # 统一方向
        else:  # 冬天，很少有昆虫和鸟类
            # 昆虫和鸟类逐渐消失
            if self.insects and random.random() < 0.05:
                self.insects.pop()
            if self.birds and random.random() < 0.02:
                self.birds.pop()
    
    def add_insect(self):
        """添加一个昆虫"""
        self.insects.append({
            'pos': (random.randint(50, self.width - 50), random.randint(50, self.ground_level - 100)),
            'size': random.randint(3, 5),
            'phase': random.uniform(0, 2 * math.pi)
        })
    
    def add_bird(self):
        """添加一只鸟"""
        self.birds.append({
            'pos': (random.randint(0, self.width), random.randint(50, self.ground_level - 150)),
            'size': random.randint(6, 10),
            'direction': 1 if random.random() < 0.5 else -1,  # 飞行方向
            'speed': random.uniform(1, 3),
            'phase': random.uniform(0, 2 * math.pi)
        })
    
    def update_weather(self):
        """更新天气状况"""
        # 天气持续时间减少
        if self.weather_duration > 0:
            self.weather_duration -= 1
        else:
            # 随机天气变化
            # 不同季节有不同的天气概率
            if self.current_season == 0:  # 春天
                weather_probs = [0.6, 0.3, 0.1, 0.0, 0.0]  # 主要晴朗和多云，偶尔有雨
            elif self.current_season == 1:  # 夏天
                weather_probs = [0.7, 0.2, 0.1, 0.0, 0.0]  # 更多晴朗，偶尔有雨
            elif self.current_season == 2:  # 秋天
                weather_probs = [0.4, 0.4, 0.2, 0.0, 0.0]  # 更多多云和雨
            else:  # 冬天
                weather_probs = [0.3, 0.3, 0.1, 0.3, 0.1]  # 有雪
            
            # 根据概率选择天气
            if random.random() < 0.02:  # 2%的概率天气发生变化
                r = random.random()
                cumulative = 0
                for i, prob in enumerate(weather_probs):
                    cumulative += prob
                    if r <= cumulative:
                        self.current_weather = i
                        break
                
                # 设置天气持续时间
                self.weather_duration = random.randint(30, 120)
                
                # 更新风力
                if self.current_weather in [2, 3]:  # 雨或雪时风力较大
                    self.wind_strength = random.uniform(1.0, 3.0)
                else:
                    self.wind_strength = random.uniform(0.2, 1.5)
                
                # 更新降水量
                self.precipitation = 0 if self.current_weather < 2 else random.randint(1, 10)
        
        # 更新温度（根据季节和时间）
        base_temp = [15, 28, 18, 0, -10][self.current_season]  # 春夏秋冬基础温度
        day_night_factor = math.sin((self.current_time - 6) * math.pi / 12)  # 6点最冷，18点最热
        day_night_range = [8, 10, 8, 5, 5][self.current_season]  # 昼夜温差
        
        # 天气影响
        weather_temp_modifier = 0
        if self.current_weather == 1:  # 多云
            weather_temp_modifier = -2
        elif self.current_weather == 2:  # 雨
            weather_temp_modifier = -5
        elif self.current_weather == 3:  # 雪
            weather_temp_modifier = -10
        
        # 计算最终温度
        target_temp = base_temp + day_night_factor * day_night_range + weather_temp_modifier
        
        # 温度平滑变化
        if abs(self.temperature - target_temp) > 0.1:
            self.temperature += (target_temp - self.temperature) * 0.01
        
        # 更新湿度（根据天气）
        if self.current_weather == 0:  # 晴朗
            target_humidity = 40 + random.randint(-10, 10)
        elif self.current_weather == 1:  # 多云
            target_humidity = 60 + random.randint(-10, 10)
        elif self.current_weather == 2:  # 雨
            target_humidity = 90 + random.randint(-5, 5)
        else:  # 雪
            target_humidity = 70 + random.randint(-10, 10)
        
        # 湿度平滑变化
        if abs(self.humidity - target_humidity) > 1:
            self.humidity += (target_humidity - self.humidity) * 0.05
            self.humidity = max(0, min(100, self.humidity))
    
    def spring_effect(self):
        """春天效果：树叶开始生长，颜色变浅绿"""
        # 树叶数量增加
        self.target_leaf_count = int(self.max_leaf_count * 0.75)  # 春天树叶达到75%
        
        # 树叶颜色设置为浅绿色
        self.target_leaf_color = (120, 220, 100)  # 嫩绿色
        
        # 树叶大小
        self.leaf_size = self.max_leaf_size * 0.7  # 春天的叶子偏小，正在生长
        
        # 季节特征参数
        self.leaf_transition_speed = 1.5  # 春天叶子变化速度较快
        
        # 清空下落的叶子
        self.falling_leaves = []
        
        # 春天天气和环境参数
        self.temperature = 15  # 春天温度适中
        self.humidity = 70    # 春天湿度较高
        self.wind_strength = 1.0  # 春天风力适中
        
        # 生成春天的云
        self.generate_clouds(4)
        
        # 春天的草生长旺盛
        self.generate_grass(120)
    
    def summer_effect(self):
        """夏天效果：树叶达到最大数量，颜色深绿"""
        # 树叶数量达到最大
        self.target_leaf_count = self.max_leaf_count
        
        # 树叶颜色设置为深绿色
        self.target_leaf_color = (30, 130, 30)  # 深绿色
        
        # 树叶保持最大尺寸
        self.leaf_size = self.max_leaf_size
        
        # 季节特征参数
        self.leaf_transition_speed = 1.0  # 夏天叶子稳定
        
        # 清空下落的叶子
        self.falling_leaves = []
        
        # 夏天天气和环境参数
        self.temperature = 28  # 夏天温度高
        self.humidity = 60    # 夏天湿度适中
        self.wind_strength = 0.7  # 夏天风力较小
        
        # 生成夏天的云
        self.generate_clouds(3)
        
        # 夏天的草茂盛
        self.generate_grass(150)
    
    def autumn_effect(self):
        """秋天效果：树叶变黄变红，开始掉落"""
        # 树叶数量减少
        self.target_leaf_count = int(self.max_leaf_count * 0.5)  # 秋天树叶剩余50%
        
        # 树叶颜色设置为金黄色
        self.target_leaf_color = (220, 150, 30)  # 金黄色
        
        # 树叶尺寸略微缩小
        self.leaf_size = self.max_leaf_size * 0.8
        
        # 季节特征参数
        self.leaf_transition_speed = 2.0  # 秋天叶子变化更快
        
        # 秋天天气和环境参数
        self.temperature = 18  # 秋天温度适中偏低
        self.humidity = 50    # 秋天湿度偏低
        self.wind_strength = 1.8  # 秋天风力较大
        
        # 生成秋天的云
        self.generate_clouds(6)
        
        # 秋天的草开始枯萎
        self.generate_grass(80)
    
    def winter_effect(self):
        """冬天效果：树叶几乎全部掉落"""
        # 树叶数量最少
        self.target_leaf_count = int(self.max_leaf_count * 0.1)  # 冬天只剩10%的树叶
        
        # 剩余树叶变成白色
        self.target_leaf_color = (255, 255, 255)  # 白色
        
        # 树叶尺寸最小
        self.leaf_size = self.max_leaf_size * 0.5
        
        # 季节特征参数
        self.leaf_transition_speed = 0.7  # 冬天变化缓慢
        
        # 冬天天气和环境参数
        self.temperature = 0   # 冬天温度低
        self.humidity = 40    # 冬天湿度低
        self.wind_strength = 2.5  # 冬天风力大
        
        # 生成冬天的云
        self.generate_clouds(7)
        
        # 冬天的草稀少
        self.generate_grass(40)
        
        # 设置地面为雪白
        self.soil_color = (240, 240, 250)  # 雪地
        
        # 停止落叶
        self.falling_leaves = []
        
        # 确保冬天有下雪现象
        self.current_weather = 3  # 设置为下雪天气
    
    def apply_seasonal_effect(self):
        """根据当前季节应用相应效果"""
        if self.current_season == 0:  # 春
            self.spring_effect()
        elif self.current_season == 1:  # 夏
            self.summer_effect()
        elif self.current_season == 2:  # 秋
            self.autumn_effect()
        else:  # 冬
            self.winter_effect()
        
        # 初始化当前颜色
        if self.current_day == 0:
            self.current_leaf_color = self.target_leaf_color
        
        # 重置天气为晴朗，避免非冬天时下雪
        self.current_weather = 0  # 0表示晴朗
        
        # 重置天气持续时间
        self.weather_duration = 0
        self.update_weather()
        
        # 生成新的树叶
        self.generate_leaves()
    
    def generate_leaves(self):
        """生成树叶，使叶子位置固定不闪烁"""
        # 限制叶子数量不超过位置数量
        effective_count = min(self.leaf_count, len(self.leaf_positions))
        
        # 如果已有叶子，则保持现有叶子位置不变，只增加或减少叶子
        if hasattr(self, 'leaves') and self.leaves:
            current_count = len(self.leaves)
            
            if effective_count > current_count:
                # 需要添加新叶子
                # 找出当前未使用的位置
                used_positions = set((leaf[0], leaf[1]) for leaf in self.leaves)
                available_positions = [pos for pos in self.leaf_positions if pos not in used_positions]
                
                # 如果可用位置不足，就随机使用已有位置
                if len(available_positions) < (effective_count - current_count):
                    available_positions = self.leaf_positions
                
                # 随机选择需要的数量的新位置
                new_positions = random.sample(available_positions, effective_count - current_count)
                
                # 添加新叶子
                for x, y in new_positions:
                    # 随机大小变化但保持稳定
                    size_variation = random.uniform(0.9, 1.1)
                    size = self.leaf_size * size_variation
                    self.leaves.append((x, y, size))
                    
            elif effective_count < current_count:
                # 需要移除一些叶子，按季节特点移除
                if self.current_season == 2:  # 秋天，主要从底部移除叶子
                    # 按高度排序，移除最低的叶子
                    self.leaves.sort(key=lambda leaf: -leaf[1])  # 从高到低排序
                    self.leaves = self.leaves[:effective_count]
                else:  # 其他季节随机移除
                    # 随机抽样保留指定数量的叶子
                    indices = list(range(len(self.leaves)))
                    random.shuffle(indices)
                    self.leaves = [self.leaves[i] for i in indices[:effective_count]]
        else:
            # 如果还没有叶子，需要初始化
            self.leaves = []
            if effective_count > 0:
                # 按季节特点选择叶子位置
                if self.current_season in [0, 1]:  # 春夏
                    # 优先选择树顶部的位置
                    positions_with_height = [(pos, 1.0 - (pos[1] / self.ground_level)) for pos in self.leaf_positions]
                    positions_with_height.sort(key=lambda x: -x[1])  # 按高度降序排序
                    positions_to_use = [pos for pos, _ in positions_with_height[:effective_count]]
                else:  # 秋冬
                    # 均匀随机选择
                    positions_to_use = random.sample(self.leaf_positions, effective_count)
                
                # 创建叶子
                for x, y in positions_to_use:
                    # 随机大小变化但保持稳定
                    size_variation = random.uniform(0.9, 1.1)
                    size = self.leaf_size * size_variation
                    
                    # 保存叶子
                    self.leaves.append((x, y, size))
    
    def draw_grass(self):
        """绘制草地"""
        for blade in self.grass_blades:
            # 根据季节确定草的颜色
            if self.current_season == 0:  # 春
                grass_color = (100, 200, 50)  # 嫩绿色
            elif self.current_season == 1:  # 夏
                grass_color = (50, 180, 30)  # 深绿色
            elif self.current_season == 2:  # 秋
                grass_color = (180, 190, 40)  # 黄绿色
            else:  # 冬
                grass_color = (150, 140, 100)  # 枯黄色
            
            # 如果下雪，草会被雪覆盖
            if self.current_weather == 3 and self.current_season == 3:
                grass_color = (220, 220, 230)  # 雪覆盖的草
            
            # 计算草的摆动
            sway = math.sin(self.animation_frame * 0.05 + blade['phase']) * 2 * self.wind_strength
            
            # 绘制草叶
            pygame.draw.line(
                self.screen,
                grass_color,
                (blade['x'], self.ground_level),
                (blade['x'] + sway, self.ground_level - blade['height']),
                1
            )
    
    def draw_buttons(self):
        """绘制所有实体按钮"""
        mouse_pos = pygame.mouse.get_pos()
        
        for button in self.buttons:
            # 确定按钮颜色（悬停、激活或默认）
            color = button['color']
            
            # 检查是否是当前选中的季节或天气
            is_active = False
            if button['action'] == 'season' and button['value'] == self.current_season:
                is_active = True
            elif button['action'] == 'weather' and button['value'] == self.current_weather:
                is_active = True
            elif button['action'] == 'pause' and self.paused:
                is_active = True
                
            if is_active:
                color = button['active_color']
            elif button['rect'].collidepoint(mouse_pos):
                color = button['hover_color']
            
            # 绘制按钮背景
            pygame.draw.rect(self.screen, color, button['rect'])
            pygame.draw.rect(self.screen, (50, 50, 50), button['rect'], 2)  # 加粗边框
            
            # 绘制按钮文本
            button_text = button['text']
            # 对于暂停按钮，根据状态显示不同文字
            if button['action'] == 'pause':
                button_text = "继续" if self.paused else "暂停"
            
            if button['action'] == 'season':
                text = self.font.render(button_text, True, (0, 0, 0))  # 黑色文字，更醒目
            else:
                text = self.small_font.render(button_text, True, (255, 255, 255))
            text_rect = text.get_rect(center=button['rect'].center)
            self.screen.blit(text, text_rect)
    
    def draw_info_panel(self):
        """绘制信息面板"""
        # 底部半透明信息面板
        panel_rect = pygame.Rect(0, self.height - 80, self.width, 80)
        panel_surface = pygame.Surface((self.width, 80), pygame.SRCALPHA)
        panel_surface.fill((0, 0, 0, 128))  # 半透明黑色
        self.screen.blit(panel_surface, panel_rect)
        
        # 计算面板中心位置
        panel_center_x = self.width // 2
        top_row_y = self.height - 70
        bottom_row_y = self.height - 40
        
        # 创建所有文本
        season_text = self.font.render(f"当前季节: {self.seasons[self.current_season]}", True, (255, 255, 255))
        day_text = self.font.render(f"第 {self.current_day} 天", True, (255, 255, 255))
        time_text = self.font.render(f"时间: {int(self.current_time):02d}:00", True, (255, 255, 255))
        weather_text = self.font.render(f"天气: {self.weather_conditions[self.current_weather]}", True, (255, 255, 255))
        temp_text = self.font.render(f"温度: {self.temperature:.1f}°", True, (255, 255, 255))
        humidity_text = self.font.render(f"湿度: {int(self.humidity)}%", True, (255, 255, 255))
        wind_text = self.font.render(f"风力: {float(self.wind_strength):.1f}", True, (255, 255, 255))
        
        # 添加暂停状态显示
        pause_status = "[ 已暂停 ]" if self.paused else ""
        pause_text = self.font.render(pause_status, True, (255, 100, 100))
        
        # 计算每行文本的总宽度，考虑暂停状态文本
        top_row_width = season_text.get_width() + time_text.get_width() + temp_text.get_width() + pause_text.get_width() + 80  # 添加间距
        bottom_row_width = day_text.get_width() + weather_text.get_width() + humidity_text.get_width() + wind_text.get_width() + 80  # 添加间距
        
        # 计算第一行每个文本的位置（居中）
        top_start_x = panel_center_x - (top_row_width // 2)
        season_x = top_start_x
        time_x = season_x + season_text.get_width() + 20
        temp_x = time_x + time_text.get_width() + 20
        pause_x = temp_x + temp_text.get_width() + 20
        
        # 计算第二行每个文本的位置（居中）
        bottom_start_x = panel_center_x - (bottom_row_width // 2)
        day_x = bottom_start_x
        weather_x = day_x + day_text.get_width() + 20
        humidity_x = weather_x + weather_text.get_width() + 20
        wind_x = humidity_x + humidity_text.get_width() + 20
        
        # 绘制第一行文本
        self.screen.blit(season_text, (season_x, top_row_y))
        self.screen.blit(time_text, (time_x, top_row_y))
        self.screen.blit(temp_text, (temp_x, top_row_y))
        self.screen.blit(pause_text, (pause_x, top_row_y))
        
        # 绘制第二行文本
        self.screen.blit(day_text, (day_x, bottom_row_y))
        self.screen.blit(weather_text, (weather_x, bottom_row_y))
        self.screen.blit(humidity_text, (humidity_x, bottom_row_y))
        self.screen.blit(wind_text, (wind_x, bottom_row_y))
    
    def draw_leaves(self):
        """绘制树叶"""
        for i, leaf in enumerate(self.leaves):
            x, y, size = leaf
            leaf_type = self.leaf_types[i % len(self.leaf_types)]  # 安全处理
            
            # 根据季节和昼夜调整叶子亮度
            r, g, b = self.leaf_color
            if self.current_time < 6 or self.current_time > 20:  # 夜晚
                brightness = 0.7  # 降低亮度
                r = int(r * brightness)
                g = int(g * brightness)
                b = int(b * brightness)
            
            color = (r, g, b)
            
            # 根据叶子类型绘制不同形状
            if leaf_type == 0:  # 圆形
                pygame.draw.circle(self.screen, color, (int(x), int(y)), int(size))
            elif leaf_type == 1:  # 椭圆形
                ellipse_rect = pygame.Rect(int(x - size*1.2), int(y - size*0.8), int(size*2.4), int(size*1.6))
                pygame.draw.ellipse(self.screen, color, ellipse_rect)
            else:  # 簇状
                for j in range(3):
                    angle = j * (2*math.pi/3)
                    offset_x = math.cos(angle) * size * 0.6
                    offset_y = math.sin(angle) * size * 0.6
                    pygame.draw.circle(self.screen, color, (int(x + offset_x), int(y + offset_y)), int(size*0.7))
    
    def draw_falling_leaves(self):
        """绘制飘落的叶子"""
        for leaf in self.falling_leaves:
            # 获取位置和大小
            x, y = leaf['pos']
            size = leaf['size']
            rotation = leaf['rotation']
            
            # 使用叶子自带的颜色（如果有），或者使用当前季节的叶子颜色
            if 'color' in leaf:
                color = leaf['color']
            else:
                # 使用当前季节的叶子颜色，并增加一些随机变化
                base_color = self.current_leaf_color
                r_var = random.randint(-15, 15)
                g_var = random.randint(-15, 15)
                b_var = random.randint(-15, 15)
                
                color = (
                    max(0, min(255, base_color[0] + r_var)),
                    max(0, min(255, base_color[1] + g_var)),
                    max(0, min(255, base_color[2] + b_var))
                )
            
            # 绘制带旋转效果的叶子
            if hasattr(leaf, 'type') and leaf['type'] == 0:
                # 椭圆形
                rotated_rect = pygame.Surface((size * 2, size), pygame.SRCALPHA)
                pygame.draw.ellipse(rotated_rect, color, (0, 0, size * 2, size))
                # 叶子旋转
                rotated_leaf = pygame.transform.rotate(rotated_rect, rotation)
                self.screen.blit(rotated_leaf, (x - rotated_leaf.get_width() // 2, y - rotated_leaf.get_height() // 2))
            elif hasattr(leaf, 'type') and leaf['type'] == 1:
                # 圆形
                pygame.draw.circle(self.screen, color, (int(x), int(y)), int(size))
            elif hasattr(leaf, 'type') and leaf['type'] == 2:
                # 针形
                end_x = x + math.cos(math.radians(rotation)) * size * 2
                end_y = y + math.sin(math.radians(rotation)) * size * 2
                pygame.draw.line(self.screen, color, (int(x), int(y)), (int(end_x), int(end_y)), 2)
            else:
                # 默认形状，椭圆或圆
                if rotation % 90 < 45:
                    # 椭圆形
                    ellipse_rect = pygame.Rect(int(x - size*1.2), int(y - size*0.8), int(size*2.4), int(size*1.6))
                    pygame.draw.ellipse(self.screen, color, ellipse_rect)
                else:
                    # 圆形
                    pygame.draw.circle(self.screen, color, (int(x), int(y)), int(size))

    def draw_ground(self):
        """绘制地面和土壤"""
        # 根据季节设置土壤颜色
        if self.current_season == 0:  # 春
            soil_color = (120, 100, 80)  # 湿润的土壤
        elif self.current_season == 1:  # 夏
            soil_color = (150, 120, 90)  # 干燥的土壤
        elif self.current_season == 2:  # 秋
            soil_color = (120, 100, 70)  # 带落叶的土壤
        else:  # 冬
            if self.current_weather == 3:  # 有雪
                soil_color = (240, 240, 250)  # 雪地
            else:
                soil_color = (100, 90, 80)  # 寒冷的土壤
        
        # 更新当前土壤颜色
        self.soil_color = soil_color
        
        # 绘制土壤
        pygame.draw.rect(self.screen, self.soil_color, 
                        (0, self.ground_level, self.width, self.soil_height))
        
        # 绘制分界线 - 土壤表面
        pygame.draw.line(self.screen, 
                        (self.soil_color[0]-20, self.soil_color[1]-20, self.soil_color[2]-20),
                        (0, self.ground_level), (self.width, self.ground_level), 2)
    
    def draw_tree(self):
        """绘制树干和树枝"""
        # 根据季节调整树干颜色
        if self.current_season == 0:  # 春
            trunk_color = (130, 70, 20)  # 湿润的树干
        elif self.current_season == 1:  # 夏
            trunk_color = (120, 65, 15)  # 正常的树干
        elif self.current_season == 2:  # 秋
            trunk_color = (110, 60, 15)  # 干燥的树干
        else:  # 冬
            trunk_color = (100, 55, 10)  # 寒冷的树干
        
        # 绘制树枝，考虑粗细
        for branch in self.branches:
            start, end, thickness = branch
            # 主干更粗，次级分支更细
            pygame.draw.line(self.screen, trunk_color, start, end, int(thickness))
    
    def draw_wildlife(self):
        """绘制野生动物（昆虫和鸟类）"""
        # 只在春夏绘制昆虫和鸟类
        if self.current_season not in [0, 1]:
            return
            
        # 季节性生物
        if self.current_season == 0:  # 春天
            # 绘制蝴蝶
            for insect in self.insects:
                x, y = insect['pos']
                size = insect['size']
                phase = insect['phase'] + self.animation_frame * 0.2
                
                # 蝴蝶翅膀
                wing_open = (math.sin(phase) + 1) / 2  # 0-1 之间波动
                
                # 画蝴蝶身体
                pygame.draw.line(self.screen, (40, 40, 40), (x, y - size), (x, y + size), 2)
                
                # 画翅膀
                wing_width = size * 3 * wing_open
                wing_height = size * 2
                
                # 左翅膀
                wing_left = pygame.Rect(
                    int(x - wing_width), int(y - wing_height/2), 
                    int(wing_width), int(wing_height)
                )
                pygame.draw.ellipse(self.screen, (200, 150, 255), wing_left)
                
                # 右翅膀
                wing_right = pygame.Rect(
                    int(x), int(y - wing_height/2), 
                    int(wing_width), int(wing_height)
                )
                pygame.draw.ellipse(self.screen, (200, 150, 255), wing_right)
        
        elif self.current_season == 1:  # 夏天
            # 绘制蜜蜂
            for insect in self.insects:
                x, y = insect['pos']
                size = insect['size']
                
                # 蜜蜂身体
                pygame.draw.circle(self.screen, (250, 200, 0), (int(x), int(y)), size)
                pygame.draw.circle(self.screen, (0, 0, 0), (int(x + size), int(y)), size)
                
                # 蜜蜂翅膀
                wing_y = y - size * 0.8
                pygame.draw.ellipse(self.screen, (255, 255, 255), 
                                 (int(x - size), int(wing_y), int(size*1.5), int(size)))
        
        # 绘制鸟
        for bird in self.birds:
            x, y = bird['pos']
            size = bird['size']
            direction = bird['direction']
            phase = bird['phase'] + self.animation_frame * 0.1
            
            # 鸟翅膀扇动
            wing_y = math.sin(phase) * size * 0.5
            
            # 鸟身体和翅膀
            body_color = (80, 80, 80) if self.current_season == 0 else (200, 50, 50)
            
            # 鸟身体
            pygame.draw.circle(self.screen, body_color, (int(x), int(y)), size)
            
            # 鸟头
            pygame.draw.circle(self.screen, body_color, (int(x + direction * size), int(y - size*0.5)), int(size*0.7))
            
            # 鸟翅膀
            wing_points = [
                (x, y),
                (x + direction * size, y - wing_y),
                (x + direction * size * 2, y)
            ]
            pygame.draw.polygon(self.screen, (50, 50, 50), wing_points)

    def generate_stars(self, count):
        """生成星星，为每颗星星分配位置、大小和闪烁周期"""
        self.stars = []
        for _ in range(count):
            # 随机生成星星的位置和大小
            x = random.randint(0, self.width)
            y = random.randint(0, self.ground_level - 100)
            size = random.uniform(0.8, 2.0)
            
            # 为每颗星星分配不同的闪烁周期和初始相位，使闪烁看起来不同步
            blink_speed = random.uniform(0.01, 0.03)  # 更慢的闪烁速度
            phase = random.uniform(0, 2 * math.pi)  # 随机初相位
            
            self.stars.append({
                'x': x,
                'y': y,
                'size': size,
                'blink_speed': blink_speed,
                'phase': phase
            })

    def update_astronomical_bodies(self):
        """更新太阳和月亮的位置"""
        # 计算时间对应的角度（0-24小时映射到0-2π）
        time_angle = (self.current_time / 24) * 2 * math.pi
        
        # 计算太阳位置（使用更自然的弧形轨迹）
        # 使用正弦函数创建更自然的弧形轨迹
        sun_x = self.width // 2 + math.cos(time_angle) * (self.width // 2 - 50)
        # 使用二次函数使太阳轨迹更自然，并确保太阳不会太低
        sun_y = self.height // 3 - math.sin(time_angle) * (self.height // 3 - 50) * (1 - abs(math.cos(time_angle)) * 0.3)
        # 确保太阳不会低于地平线
        sun_y = max(50, min(sun_y, self.ground_level - 50))
        self.sun_pos = (sun_x, sun_y)
        
        # 计算月亮位置（与太阳相反，但轨迹略有不同）
        moon_angle = time_angle + math.pi  # 与太阳相位相差12小时
        moon_x = self.width // 2 + math.cos(moon_angle) * (self.width // 2 - 50)
        # 月亮的轨迹比太阳略高一些
        moon_y = self.height // 3 - math.sin(moon_angle) * (self.height // 3 - 50) * (1 - abs(math.cos(moon_angle)) * 0.2)
        # 确保月亮不会低于地平线
        moon_y = max(50, min(moon_y, self.ground_level - 50))
        self.moon_pos = (moon_x, moon_y)
        
        # 根据时间调整太阳和月亮的亮度
        if 6 <= self.current_time <= 18:  # 白天
            # 太阳亮度随高度变化
            sun_height_factor = 1 - abs(math.sin(time_angle)) * 0.3
            self.sun_color = (255, 255, int(200 * sun_height_factor))
        else:  # 夜晚
            # 月亮亮度随高度变化
            moon_height_factor = 1 - abs(math.sin(moon_angle)) * 0.2
            self.moon_color = (int(200 * moon_height_factor), 
                             int(200 * moon_height_factor), 
                             int(200 * moon_height_factor))

    def draw_astronomical_bodies(self):
        """绘制太阳和月亮"""
        # 根据时间调整亮度
        if 6 <= self.current_time <= 18:  # 白天
            # 绘制太阳
            pygame.draw.circle(self.screen, self.sun_color, 
                             (int(self.sun_pos[0]), int(self.sun_pos[1])), 
                             self.sun_radius)
            # 太阳光芒（随高度变化）
            # 太阳光芒
            for i in range(8):
                angle = i * (math.pi / 4)
                start_x = self.sun_pos[0] + math.cos(angle) * self.sun_radius
                start_y = self.sun_pos[1] + math.sin(angle) * self.sun_radius
                end_x = self.sun_pos[0] + math.cos(angle) * (self.sun_radius + 10)
                end_y = self.sun_pos[1] + math.sin(angle) * (self.sun_radius + 10)
                pygame.draw.line(self.screen, self.sun_color, 
                               (int(start_x), int(start_y)), 
                               (int(end_x), int(end_y)), 2)
        else:  # 夜晚
            # 绘制月亮（固定圆形）
            if self.moon_pos[1] < self.ground_level:  # 只有当月亮在地面以上时才绘制
                pygame.draw.circle(self.screen, self.moon_color, 
                                 (int(self.moon_pos[0]), int(self.moon_pos[1])), 
                                 self.moon_radius)

    def handle_lightning(self):
        """处理闪电效果"""
        # 只在雷暴天气下随机触发闪电
        if self.current_weather == 4:  # 雷暴天气
            if random.random() < 0.02:  # 2%的概率触发闪电
                self.lightning_active = True
                self.lightning_timer = 0
                self.lightning_strike_pos = None
        
        if self.lightning_active:
            self.lightning_timer += 1
            if self.lightning_timer >= self.lightning_duration:
                self.lightning_active = False
                self.lightning_timer = 0
                
                # 随机选择一些叶子变成黑色
                if self.leaves:
                    # 确保不会选择超过现有叶子数量的索引
                    num_leaves_to_blacken = min(20, len(self.leaves))
                    if num_leaves_to_blacken > 0:
                        # 创建叶子索引的副本，避免在循环中修改列表
                        leaf_indices = list(range(len(self.leaves)))
                        blackened_indices = random.sample(leaf_indices, num_leaves_to_blacken)
                        # 按降序排序，这样从后往前删除不会影响前面的索引
                        blackened_indices.sort(reverse=True)
                        
                        for idx in blackened_indices:
                            if 0 <= idx < len(self.leaves):  # 额外的安全检查
                                leaf = self.leaves[idx]
                                self.black_leaves.append({
                                    'pos': (leaf[0], leaf[1]),
                                    'size': leaf[2],
                                    'speed': random.uniform(1.0, 3.0),
                                    'swing': random.uniform(-3, 3),
                                    'rotation': random.uniform(0, 360),
                                    'rotation_speed': random.uniform(-8, 8)
                                })
                                # 从原位置移除叶子
                                self.leaves.pop(idx)
    
    def draw_lightning(self):
        """绘制闪电效果"""
        if self.lightning_active:
            # 创建闪电路径
            if not self.lightning_strike_pos:
                # 随机选择闪电起始点（天空中的某个位置）
                start_x = random.randint(100, self.width - 100)
                start_y = random.randint(50, 150)
                self.lightning_strike_pos = (start_x, start_y)
            
            # 绘制主闪电
            points = [self.lightning_strike_pos]
            current_x, current_y = self.lightning_strike_pos
            
            # 生成闪电路径
            while current_y < self.ground_level:
                # 添加随机偏移
                current_x += random.uniform(-20, 20)
                current_y += random.uniform(10, 30)
                points.append((current_x, current_y))
            
            # 绘制闪电
            if len(points) > 1:
                pygame.draw.lines(self.screen, (255, 255, 255), False, points, 3)
                
                # 添加闪电发光效果
                for i in range(3):
                    glow_points = [(x + random.uniform(-2, 2), y + random.uniform(-2, 2)) 
                                 for x, y in points]
                    pygame.draw.lines(self.screen, (200, 200, 255), False, glow_points, 1)
    
    def draw_black_leaves(self):
        """绘制被雷劈中的黑色叶子"""
        for leaf in self.black_leaves:
            x, y = leaf['pos']
            size = leaf['size']
            rotation = leaf['rotation']
            
            # 绘制黑色叶子
            pygame.draw.circle(self.screen, (0, 0, 0), (int(x), int(y)), int(size))
            
            # 更新位置和旋转
            leaf['pos'] = (x + leaf['swing'], y + leaf['speed'])
            leaf['rotation'] = (leaf['rotation'] + leaf['rotation_speed']) % 360
            
            # 如果叶子落到地面，移除它
            if y > self.ground_level:
                self.black_leaves.remove(leaf)
    
# 主程序入口
if __name__ == "__main__":
    try:
        print("启动四季树叶模拟器：展示春夏秋冬季节变化")
        print("空格键增加风力,R键重置风力,W键改变天气,点击树干使叶子掉落")
        tree = SeasonalTree()
        tree.run()
    except Exception as e:
        print(f"程序出错: {str(e)}")
        pygame.quit()
        sys.exit()