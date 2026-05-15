"""
╔══════════════════════════════════════════════════════════════╗
║  CYBERDECK NeoPixel Controller                             ║
║  RP2040 Zero + WS2812B × 16 LEDs                           ║
║  赛博朋克风格 RGB 灯带控制器                                ║
╚══════════════════════════════════════════════════════════════╝

效果模式:
  0 - breathe : 呼吸灯（荧光青 slow pulse）
  1 - scan    : 扫描线（一道亮光沿灯带滑行，赛博朋克经典）
  2 - glitch  : 故障闪烁（随机闪+偶尔全灭，模拟电子故障）
  3 - boot    : 开机动画（从中间向两端逐个点亮）
  4 - rainbow : 彩虹流动

硬件连接:
  - WS2812B DIN → GP16 (可配置)
  - 模式按钮   → GP17 (低电平有效，内部上拉)

依赖 (CircuitPython):
  - adafruit_neopixel
  - adafruit_debounce (可选，用于按钮去抖)

将此文件保存为 code.py 到 CIRCUITPY 驱动器根目录即可自动运行。
"""

import time
import math
import random
import board
import neopixel
import digitalio

# ══════════════════════════════════════════════════════════════
#  可配置参数
# ══════════════════════════════════════════════════════════════

# WS2812B 数据引脚 (RP2040 Zero GPIO)
NEOPIXEL_PIN = board.GP16

# 模式切换按钮引脚 (低电平有效)
BUTTON_PIN = board.GP17

# LED 数量
NUM_PIXELS = 16

# 默认亮度 (0.0 ~ 1.0)
DEFAULT_BRIGHTNESS = 0.4

# 按钮去抖时间 (秒)
DEBOUNCE_SEC = 0.25

# ══════════════════════════════════════════════════════════════
#  赛博朋克调色板
# ══════════════════════════════════════════════════════════════

CYAN     = (0, 255, 240)     # #00fff0 荧光青 (主色)
MAGENTA  = (255, 0, 255)     # #ff00ff 品红   (强调)
PURPLE   = (123, 47, 247)    # #7b2ff7 电紫   (次要)
NEON_RED = (255, 45, 111)    # #ff2d6f 霓虹红 (警告)
CYBER_GREEN = (0, 255, 100)  # #00ff64 荧光绿
OFF      = (0, 0, 0)         # 熄灭

# glitch 模式使用的颜色池
GLITCH_PALETTE = [CYAN, MAGENTA, PURPLE, NEON_RED, CYBER_GREEN]

# ══════════════════════════════════════════════════════════════
#  模式常量
# ══════════════════════════════════════════════════════════════

MODE_BREATHE = 0
MODE_SCAN    = 1
MODE_GLITCH  = 2
MODE_BOOT    = 3
MODE_RAINBOW = 4
MODE_COUNT   = 5

MODE_NAMES = ["breathe", "scan", "glitch", "boot", "rainbow"]

# ══════════════════════════════════════════════════════════════
#  硬件初始化
# ══════════════════════════════════════════════════════════════

pixels = neopixel.NeoPixel(
    NEOPIXEL_PIN,
    NUM_PIXELS,
    brightness=DEFAULT_BRIGHTNESS,
    auto_write=False,
    pixel_order=neopixel.GRB,  # WS2812B 标准顺序
)

# 模式按钮
button = digitalio.DigitalInOut(BUTTON_PIN)
button.direction = digitalio.Direction.INPUT
button.pull = digitalio.Pull.UP  # 内部上拉，按下 = LOW

# ══════════════════════════════════════════════════════════════
#  工具函数
# ══════════════════════════════════════════════════════════════

def scale_color(color, factor):
    """将 RGB 颜色按 factor (0.0~1.0) 缩放亮度"""
    return (
        max(0, min(255, int(color[0] * factor))),
        max(0, min(255, int(color[1] * factor))),
        max(0, min(255, int(color[2] * factor))),
    )


def lerp_color(a, b, t):
    """在颜色 a 和 b 之间线性插值, t ∈ [0, 1]"""
    return (
        int(a[0] + (b[0] - a[0]) * t),
        int(a[1] + (b[1] - a[1]) * t),
        int(a[2] + (b[2] - a[2]) * t),
    )


def hsv_to_rgb(h, s, v):
    """
    HSV → RGB 转换
    h: 色相 [0, 1)
    s: 饱和度 [0, 1]
    v: 明度 [0, 1]
    返回 (R, G, B) 各 0~255
    """
    if s == 0.0:
        val = int(v * 255)
        return (val, val, val)

    i = int(h * 6.0)
    f = h * 6.0 - i
    p = v * (1.0 - s)
    q = v * (1.0 - s * f)
    t = v * (1.0 - s * (1.0 - f))
    i %= 6

    if   i == 0: r, g, b = v, t, p
    elif i == 1: r, g, b = q, v, p
    elif i == 2: r, g, b = p, v, t
    elif i == 3: r, g, b = p, q, v
    elif i == 4: r, g, b = t, p, v
    else:        r, g, b = v, p, q

    return (int(r * 255), int(g * 255), int(b * 255))


def clear_pixels():
    """熄灭所有 LED"""
    pixels.fill(OFF)
    pixels.show()


# ══════════════════════════════════════════════════════════════
#  效果: breathe (呼吸灯)
# ══════════════════════════════════════════════════════════════

def effect_breathe(t):
    """
    呼吸灯效果 — 荧光青色缓慢脉冲
    使用正弦函数驱动亮度，周期约 4 秒
    所有 LED 同步呼吸，营造赛博朋克"心跳"氛围

    参数:
      t: 当前时间 (monotonic)
    """
    # 正弦呼吸: 0.15 ~ 1.0 亮度范围 (避免全灭，保留微光)
    breath = (math.sin(t * math.pi * 0.5) + 1.0) / 2.0  # 0.0 ~ 1.0
    intensity = 0.15 + 0.85 * breath  # 0.15 ~ 1.0

    color = scale_color(CYAN, intensity)
    pixels.fill(color)
    pixels.show()


# ══════════════════════════════════════════════════════════════
#  效果: scan (扫描线)
# ══════════════════════════════════════════════════════════════

def effect_scan(t):
    """
    扫描线效果 — 一道亮光沿灯带滑行
    赛博朋克经典视觉: 类似 CRT 扫描线或科幻UI中的光标追踪

    主光点: 全亮度荧光青
    拖尾: 3~4 个渐暗的拖尾光点
    其余: 微弱的底色 (不完全是黑色，像CRT余辉)

    参数:
      t: 当前时间
    """
    # 扫描速度: 约 2 秒走完全程
    pos = (t * 8.0) % NUM_PIXELS  # 8.0 = 速度 (LED/秒)
    idx = int(pos)
    frac = pos - idx  # 小数部分用于子像素平滑

    # 先填充微弱底色 (CRT 余辉)
    for i in range(NUM_PIXELS):
        pixels[i] = scale_color(CYAN, 0.03)

    # 拖尾 (在主光点后面渐暗)
    tail_len = 4
    for j in range(tail_len):
        tail_idx = (idx - j - 1) % NUM_PIXELS
        fade = 1.0 - (j + 1) / tail_len  # 1.0 → 0.0
        fade *= fade  # 二次衰减，更自然
        pixels[tail_idx] = scale_color(CYAN, fade * 0.6)

    # 主光点 (全亮度 + 子像素补偿)
    main_brightness = 1.0 - frac * 0.3  # 接近下一个位置时略暗
    pixels[idx % NUM_PIXELS] = scale_color(CYAN, main_brightness)

    # 前方预光 (子像素: 即将到达的位置微亮)
    next_idx = (idx + 1) % NUM_PIXELS
    pixels[next_idx] = scale_color(CYAN, frac * 0.5)

    pixels.show()


# ══════════════════════════════════════════════════════════════
#  效果: glitch (故障闪烁)
# ══════════════════════════════════════════════════════════════

# glitch 效果的状态变量
_glitch_timer = 0.0
_glitch_all_off = False
_glitch_pattern = [OFF] * NUM_PIXELS
_glitch_next_update = 0.0

def effect_glitch(t):
    """
    故障闪烁效果 — 模拟赛博朋克电子故障
    随机 LED 闪烁 + 偶尔全灭 + 不规则的颜色跳变

    行为:
      - 大部分时间: 随机位置闪烁赛博朋克色
      - 5% 概率: 全部熄灭 (模拟短路/断电)
      - 3% 概率: 全部随机色 (模拟数据损坏)
      - 更新间隔: 不规则 (50~200ms), 增加不稳定性

    参数:
      t: 当前时间
    """
    global _glitch_timer, _glitch_all_off
    global _glitch_pattern, _glitch_next_update

    # 不规则更新间隔
    if t < _glitch_next_update:
        # 直接显示当前 pattern
        for i in range(NUM_PIXELS):
            pixels[i] = _glitch_pattern[i]
        pixels.show()
        return

    # 更新间隔: 50~200ms (不规则)
    _glitch_next_update = t + random.uniform(0.05, 0.20)

    # ── 随机事件 ──
    roll = random.random()

    if roll < 0.05:
        # 5% 概率: 全部熄灭 (断电感)
        _glitch_pattern = [OFF] * NUM_PIXELS
        _glitch_all_off = True
    elif roll < 0.08:
        # 3% 概率: 全部随机色 (数据损坏)
        _glitch_pattern = [
            random.choice(GLITCH_PALETTE) for _ in range(NUM_PIXELS)
        ]
        _glitch_all_off = False
    else:
        # 正常故障闪烁: 约 30% 的 LED 随机亮起
        new_pattern = []
        for i in range(NUM_PIXELS):
            if random.random() < 0.30:
                # 随机选择赛博朋克色
                color = random.choice(GLITCH_PALETTE)
                # 随机亮度缩放 (0.3~1.0)
                brightness = random.uniform(0.3, 1.0)
                new_pattern.append(scale_color(color, brightness))
            else:
                # 偶尔保留上一次的状态 (闪烁残留)
                if random.random() < 0.2 and not _glitch_all_off:
                    new_pattern.append(scale_color(_glitch_pattern[i], 0.3))
                else:
                    new_pattern.append(OFF)
        _glitch_pattern = new_pattern
        _glitch_all_off = False

    for i in range(NUM_PIXELS):
        pixels[i] = _glitch_pattern[i]
    pixels.show()


# ══════════════════════════════════════════════════════════════
#  效果: boot (开机动画)
# ══════════════════════════════════════════════════════════════

_boot_start = None   # 动画开始时间
_boot_done = False    # 动画是否完成

def effect_boot(t):
    """
    开机动画 — 从中间向两端逐个点亮
    模拟系统逐级上电的自检过程

    阶段:
      1. 从中心 LED 向两侧扩展点亮 (荧光青)
      2. 全部点亮后短暂保持
      3. 闪烁一下 (品红) 表示就绪
      4. 完成后自动切换到 breathe 模式

    参数:
      t: 当前时间
    """
    global _boot_start, _boot_done

    if _boot_start is None:
        _boot_start = t
        _boot_done = False

    elapsed = t - _boot_start
    mid = NUM_PIXELS // 2  # 中心点

    # ── 阶段1: 逐个点亮 (每0.12秒扩展一个) ──
    if elapsed < 2.0:
        spread = int(elapsed / 0.12)  # 已扩展的LED数
        pixels.fill(OFF)
        for s in range(spread + 1):
            left = mid - s
            right = mid + s
            if 0 <= left < NUM_PIXELS:
                pixels[left] = CYAN
            if 0 <= right < NUM_PIXELS and right != left:
                pixels[right] = CYAN
        pixels.show()

    # ── 阶段2: 全亮保持 ──
    elif elapsed < 2.6:
        pixels.fill(CYAN)
        pixels.show()

    # ── 阶段3: 品红闪烁 ──
    elif elapsed < 2.8:
        pixels.fill(MAGENTA)
        pixels.show()
    elif elapsed < 3.0:
        pixels.fill(CYAN)
        pixels.show()

    # ── 阶段4: 完成 ──
    else:
        _boot_done = True
        pixels.fill(CYAN)
        pixels.show()


def reset_boot():
    """重置开机动画状态（下次进入时重新播放）"""
    global _boot_start, _boot_done
    _boot_start = None
    _boot_done = False


# ══════════════════════════════════════════════════════════════
#  效果: rainbow (彩虹流动)
# ══════════════════════════════════════════════════════════════

def effect_rainbow(t):
    """
    彩虹流动效果 — 色相沿灯带连续变化
    全部 LED 形成流动的彩虹，速度适中

    实现:
      - 每个 LED 的色相 = 基础色相 + 位置偏移
      - 基础色相随时间递增 → 整体流动
      - 饱和度=1, 明度=0.8 (避免过亮刺眼)

    参数:
      t: 当前时间
    """
    base_hue = (t * 0.08) % 1.0  # 流动速度: 每秒 0.08 圈

    for i in range(NUM_PIXELS):
        # 每个 LED 的色相偏移
        hue = (base_hue + i / NUM_PIXELS) % 1.0
        color = hsv_to_rgb(hue, 1.0, 0.8)
        pixels[i] = color

    pixels.show()


# ══════════════════════════════════════════════════════════════
#  效果分发表
# ══════════════════════════════════════════════════════════════

EFFECT_TABLE = {
    MODE_BREATHE: effect_breathe,
    MODE_SCAN:    effect_scan,
    MODE_GLITCH:  effect_glitch,
    MODE_BOOT:    effect_boot,
    MODE_RAINBOW: effect_rainbow,
}


# ══════════════════════════════════════════════════════════════
#  模式切换逻辑
# ══════════════════════════════════════════════════════════════

def reset_mode_state(mode):
    """切换模式时重置各效果的内部状态"""
    global _glitch_timer, _glitch_all_off, _glitch_pattern, _glitch_next_update
    if mode == MODE_GLITCH:
        _glitch_timer = 0.0
        _glitch_all_off = False
        _glitch_pattern = [OFF] * NUM_PIXELS
        _glitch_next_update = 0.0
    elif mode == MODE_BOOT:
        reset_boot()


# ══════════════════════════════════════════════════════════════
#  主循环
# ══════════════════════════════════════════════════════════════

def main():
    """
    主循环:
    1. 检测按钮按下 → 切换模式
    2. 执行当前模式的效果函数
    3. boot 动画完成后自动切换到 breathe
    """
    current_mode = MODE_BOOT  # 开机先播放 boot 动画
    last_press_time = -1.0

    print("╔══════════════════════════════╗")
    print("║  CYBERDECK NeoPixel Ctrl     ║")
    print("║  RP2040 Zero + WS2812B ×16   ║")
    print("╚══════════════════════════════╝")
    print(f"Starting mode: {MODE_NAMES[current_mode]}")
    print("Press button (GP17) to switch mode.")

    while True:
        now = time.monotonic()

        # ── 按钮检测 (去抖) ──
        if not button.value:  # LOW = 按下
            if now - last_press_time > DEBOUNCE_SEC:
                last_press_time = now
                current_mode = (current_mode + 1) % MODE_COUNT
                reset_mode_state(current_mode)
                print(f"Mode → {MODE_NAMES[current_mode]}")

        # ── 执行当前效果 ──
        effect_fn = EFFECT_TABLE.get(current_mode)
        if effect_fn:
            effect_fn(now)

        # ── boot 动画完成后自动切换到 breathe ──
        if current_mode == MODE_BOOT and _boot_done:
            current_mode = MODE_BREATHE
            reset_mode_state(current_mode)
            print(f"Boot complete → {MODE_NAMES[current_mode]}")

        # ── 主循环延时 ──
        # breathe/scan/rainbow: 30fps; glitch: 由内部定时器控制
        time.sleep(0.033)


# ══════════════════════════════════════════════════════════════
#  启动
# ══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        clear_pixels()
        print("\nCyberdeck NeoPixel Controller stopped.")
