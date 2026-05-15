#!/bin/bash
# ═══════════════════════════════════════════════════════════════
#  CYBERDECK Terminal Colors — 赛博朋克终端配色脚本
#  设置 16 色终端配色方案 (ANSI escape sequences)
# ═══════════════════════════════════════════════════════════════
#  用法:
#    source terminal_colors.sh    — 在当前终端生效
#    cyberdeck-colors             — 安装后直接运行 (由 setup.sh 安装)
# ═══════════════════════════════════════════════════════════════
#
# 赛博朋克配色方案:
#   背景:   #0a0a0f  深黑偏蓝
#   主色:   #00fff0  荧光青
#   强调:   #ff00ff  品红
#   次要:   #7b2ff7  电紫
#   文字:   #c0c0c0  银灰
#   警告:   #ff2d6f  霓虹红
#   成功:   #00ff64  荧光绿
# ═══════════════════════════════════════════════════════════════

# ── 16色方案 (ANSI 0-15) ──────────────────────────────────────
#  格式: ESC ] 4 ; <索引> ; #<RRGGBB> BEL

#  color0  (Black)         #0a0a0f  深黑偏蓝 — 主背景
#  color1  (Red)           #ff2d6f  霓虹红 — 错误/警告
#  color2  (Green)         #00ff64  荧光绿 — 成功/可执行
#  color3  (Yellow)        #f0e040  赛博黄 — 提示/注意
#  color4  (Blue)          #7b2ff7  电紫 — 目录/链接
#  color5  (Magenta)       #ff00ff  品红 — 特殊/强调
#  color6  (Cyan)          #00fff0  荧光青 — 主色/关键字
#  color7  (White)         #c0c0c0  银灰 — 默认文字
#  color8  (Bright Black)  #1a1a2f  深紫灰 — 注释
#  color9  (Bright Red)    #ff4d7f  亮霓虹红
#  color10 (Bright Green)  #33ff88  亮荧光绿
#  color11 (Bright Yellow) #fffa50  亮赛博黄
#  color12 (Bright Blue)   #9b5ff7  亮电紫
#  color13 (Bright Magenta)#ff40ff  亮品红
#  color14 (Bright Cyan)   #40fff0  亮荧光青
#  color15 (Bright White)  #e0e0e0  亮银灰

apply_cyberdeck_colors() {
    # 检查终端是否支持真彩色/256色
    if [ -z "${TERM:-}" ] || [ "${TERM}" = "dumb" ]; then
        echo "Cyberdeck Colors: 非交互终端，跳过配色设置"
        return 1
    fi

    # ── 设置 16 色调色板 ──
    # 使用 OSC 4 序列设置终端颜色
    printf '\033]4;0;#0a0a0f\033\\'     # Black
    printf '\033]4;1;#ff2d6f\033\\'     # Red
    printf '\033]4;2;#00ff64\033\\'     # Green
    printf '\033]4;3;#f0e040\033\\'     # Yellow
    printf '\033]4;4;#7b2ff7\033\\'     # Blue
    printf '\033]4;5;#ff00ff\033\\'     # Magenta
    printf '\033]4;6;#00fff0\033\\'     # Cyan
    printf '\033]4;7;#c0c0c0\033\\'     # White
    printf '\033]4;8;#1a1a2f\033\\'     # Bright Black
    printf '\033]4;9;#ff4d7f\033\\'     # Bright Red
    printf '\033]4;10;#33ff88\033\\'    # Bright Green
    printf '\033]4;11;#fffa50\033\\'    # Bright Yellow
    printf '\033]4;12;#9b5ff7\033\\'    # Bright Blue
    printf '\033]4;13;#ff40ff\033\\'    # Bright Magenta
    printf '\033]4;14;#40fff0\033\\'    # Bright Cyan
    printf '\033]4;15;#e0e0e0\033\\'    # Bright White

    # ── 设置前景/背景/光标色 ──
    printf '\033]10;#c0c0c0\033\\'      # 前景: 银灰
    printf '\033]11;#0a0a0f\033\\'      # 背景: 深黑偏蓝
    printf '\033]12;#00fff0\033\\'      # 光标: 荧光青

    # ── 设置粗体/下划线颜色 ──
    printf '\033]1;#00fff0\033\\'       # 粗体: 荧光青
    printf '\033]2;#ff00ff\033\\'       # 下划线: 品红

    echo ""
    echo "  ╔══════════════════════════════════════╗"
    echo "  ║  ⚡ Cyberdeck Colors Applied!        ║"
    echo "  ║  ⚡ 赛博朋克终端配色已生效           ║"
    echo "  ╚══════════════════════════════════════╝"
    echo ""
}

# ── 配色预览: 显示 16 色方块 ──
preview_colors() {
    echo ""
    echo "  ══ CYBERDECK 16-Color Palette ══"
    echo ""
    echo "  标准色 (0-7):"
    for i in $(seq 0 7); do
        printf "  \033[48;5;${i}m  ${i}  \033[0m"
    done
    echo ""
    echo ""
    echo "  高亮色 (8-15):"
    for i in $(seq 8 15); do
        printf "  \033[48;5;${i}m  ${i}  \033[0m"
    done
    echo ""
    echo ""
    echo "  前景测试:"
    echo "    \033[38;5;1m■ 霓虹红 #ff2d6f\033[0m  \033[38;5;2m■ 荧光绿 #00ff64\033[0m  \033[38;5;3m■ 赛博黄 #f0e040\033[0m"
    echo "    \033[38;5;4m■ 电紫 #7b2ff7\033[0m    \033[38;5;5m■ 品红 #ff00ff\033[0m   \033[38;5;6m■ 荧光青 #00fff0\033[0m"
    echo "    \033[38;5;7m■ 银灰 #c0c0c0\033[0m    \033[38;5;8m■ 深紫灰 #1a1a2f\033[0m  \033[38;5;9m■ 亮霓虹 #ff4d7f\033[0m"
    echo ""
}

# ── 运行入口 ──
# 如果直接执行 (非 source), 则应用配色并预览
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    apply_cyberdeck_colors
    sleep 0.5
    preview_colors
fi
