#!/bin/bash
# ═══════════════════════════════════════════════════════════════
#  CYBERDECK DietPi 一键配置脚本
#  赛博朋克风格终端主题 — NanoPi 2 便携电脑
# ═══════════════════════════════════════════════════════════════
#  用法: sudo bash setup.sh
#  兼容: DietPi (Debian armhf) / FriendlyCore
# ═══════════════════════════════════════════════════════════════

set -euo pipefail

# ── 赛博朋克配色 ──
BG="#0a0a0f"        # 深黑偏蓝
CYAN="#00fff0"      # 荧光青
MAGENTA="#ff00ff"   # 品红
PURPLE="#7b2ff7"    # 电紫
RED="#ff2d6f"       # 霓虹红
GREEN="#00ff64"     # 荧光绿
SILVER="#c0c0c0"    # 银灰

# 脚本所在目录（用于定位同目录的其他文件）
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo ""
echo "  ╔══════════════════════════════════════╗"
echo "  ║   CYBERDECK DietPi Theme Setup      ║"
echo "  ║   赛博朋克终端主题一键配置           ║"
echo "  ╚══════════════════════════════════════╝"
echo ""

# 检查 root 权限
if [ "$EUID" -ne 0 ]; then
    echo "[!] 请使用 sudo 运行此脚本"
    exit 1
fi

# ─────────────────────────────────────────────────────────────
#  [1/7] 安装必要软件包
# ─────────────────────────────────────────────────────────────
echo "[1/7] 安装必要软件包..."
apt-get update -qq
apt-get install -y --no-install-recommends \
    neofetch \
    cmatrix \
    toilet \
    figlet \
    tmux \
    vim \
    fonts-powerline \
    locales \
    ca-certificates \
    curl

# 尝试安装 lolcat (不在所有仓库中)
apt-get install -y lolcat 2>/dev/null || echo "    lolcat 不可用，跳过"

echo "    ✓ 软件包安装完成"

# ─────────────────────────────────────────────────────────────
#  [2/7] 配置 Shell 提示符 (.bashrc)
# ─────────────────────────────────────────────────────────────
echo "[2/7] 配置 Shell 提示符..."

# 备份原 .bashrc
cp -n /root/.bashrc /root/.bashrc.bak 2>/dev/null || true

cat >> /root/.bashrc << 'BASHRC_EOF'

# ═══════════════════════════════════════════════
#  CYBERDECK Shell Theme — 赛博朋克风格
# ═══════════════════════════════════════════════

# 荧光青色提示符: 用户名@主机名 + 路径
# 格式: ◈ root@cyberdeck:~$
export PS1='\[\033[38;5;51m\]◈ \u@\h\[\033[38;5;252m\]:\[\033[38;5;46m\]\w\[\033[38;5;252m\]\$\[\033[0m\] '

# 命令行颜色
export GCC_COLORS='error=01;31:warning=01;35:note=01;36:caret=01;32:locus=01;34'
export GREP_COLORS='mt=01;38;5;51:fn=38;5;201:ln=38;5;201:bn=38;5;201:se=00'

# ls 颜色 (赛博朋克风)
export LS_COLORS='di=01;36:ln=01;35:so=01;32:pi=00:ex=01;38;5;51:bd=01;33:cd=01;33:su=01;31:sg=01;31:tw=01;34:ow=01;34'

# less 颜色
export LESS='-R'
export LESS_TERMCAP_mb=$'\033[01;35m'   # 闪烁: 品红
export LESS_TERMCAP_md=$'\033[01;36m'   # 粗体: 荧光青
export LESS_TERMCAP_me=$'\033[0m'
export LESS_TERMCAP_so=$'\033[38;5;201m\033[48;5;17m'  # 搜索: 品红字+深蓝底
export LESS_TERMCAP_se=$'\033[0m'
export LESS_TERMCAP_us=$'\033[04;35m'   # 下划线: 品红
export LESS_TERMCAP_ue=$'\033[0m'

# 别名 (赛博朋克味)
alias ls='ls --color=auto'
alias ll='ls -la --color=auto'
alias la='ls -A --color=auto'
alias l='ls -CF --color=auto'
alias grep='grep --color=auto'
alias egrep='egrep --color=auto'
alias fgrep='fgrep --color=auto'

# 赛博朋克快捷命令
alias matrix='cmatrix -s -B -C cyan'
alias cyber-prompt='toilet -f future -F crop -F metal "CYBERDECK" 2>/dev/null || figlet -f future "CYBERDECK"'
alias sysinfo='neofetch --colors 6 5 6 5 6 5'

BASHRC_EOF

echo "    ✓ Shell 提示符配置完成"

# ─────────────────────────────────────────────────────────────
#  [3/7] 配置 .Xresources 终端颜色
# ─────────────────────────────────────────────────────────────
echo "[3/7] 配置 .Xresources 终端颜色..."

cat > /root/.Xresources << 'XRES_EOF'
! ═══════════════════════════════════════════════
!  CYBERDECK Terminal Color Scheme
!  赛博朋克终端配色 — 16色方案
! ═══════════════════════════════════════════════

! 全局
*.background:  #0a0a0f
*.foreground:  #c0c0c0
*.cursorColor: #00fff0

! 16 色定义
! ── 标准色 (0-7) ──
*.color0:  #0a0a0f     ! Black     — 深黑偏蓝
*.color1:  #ff2d6f     ! Red       — 霓虹红
*.color2:  #00ff64     ! Green     — 荧光绿
*.color3:  #00fff0     ! Yellow    — 荧光青 (替代黄)
*.color4:  #7b2ff7     ! Blue      — 电紫
*.color5:  #ff00ff     ! Magenta   — 品红
*.color6:  #00fff0     ! Cyan      — 荧光青
*.color7:  #c0c0c0     ! White     — 银灰

! ── 高亮色 (8-15) ──
*.color8:  #1a1a2f     ! Bright Black   — 深紫灰
*.color9:  #ff2d6f     ! Bright Red     — 霓虹红
*.color10: #00ff64     ! Bright Green   — 荧光绿
*.color11: #00fff0     ! Bright Yellow  — 荧光青
*.color12: #7b2ff7     ! Bright Blue    — 电紫
*.color13: #ff00ff     ! Bright Magenta — 品红
*.color14: #00fff0     ! Bright Cyan    — 荧光青
*.color15: #e0e0e0     ! Bright White   — 亮银灰

! 终端字体 (Powerline 兼容)
*.font: xft:DejaVu Sans Mono for Powerline:size=10
*.boldFont: xft:DejaVu Sans Mono for Powerline:size=10:bold

! 终端行为
*.scrollBar: false
*.scrollBar_right: false
*.saveLines: 10000
*.cursorBlink: true
*.cursorUnderline: false

XRES_EOF

# 合并 Xresources (如果 X 可用)
if command -v xrdb &>/dev/null; then
    xrdb -merge /root/.Xresources 2>/dev/null || true
fi

echo "    ✓ 终端配色配置完成"

# ─────────────────────────────────────────────────────────────
#  [4/7] 配置开机 ASCII art 欢迎界面 (/etc/motd)
# ─────────────────────────────────────────────────────────────
echo "[4/7] 配置开机欢迎界面..."

# 复制预制的 boot_ascii.txt 到 /etc/motd
if [ -f "${SCRIPT_DIR}/boot_ascii.txt" ]; then
    cp "${SCRIPT_DIR}/boot_ascii.txt" /etc/motd
else
    # 如果 boot_ascii.txt 不存在，内联生成
    cat > /etc/motd << 'MOTD_EOF'
    ╔═════════════════════════════════════════════════════════╗
    ║                                                         ║
    ║    ██████╗██╗   ██╗██████╗ ███████╗██████╗             ║
    ║   ██╔════╝██║   ██║██╔══██╗██╔════╝██╔══██╗            ║
    ║   ██║     ██║   ██║██████╔╝█████╗  ██████╔╝            ║
    ║   ██║     ██║   ██║██╔══██╗██╔══╝  ██╔══██╗            ║
    ║   ╚██████╗╚██████╔╝██║  ██║███████╗██║  ██║            ║
    ║    ╚═════╝ ╚═════╝ ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝            ║
    ║                                                         ║
    ║   ███╗   ██╗███████╗███████╗████████╗███████╗██████╗   ║
    ║   ████╗  ██║██╔════╝██╔════╝╚══██╔══╝██╔════╝██╔══██╗  ║
    ║   ██╔██╗ ██║█████╗  ███████╗   ██║   █████╗  ██║  ██║  ║
    ║   ██║╚██╗██║██╔══╝  ╚════██║   ██║   ██╔══╝  ██║  ██║  ║
    ║   ██║ ╚████║███████╗███████║   ██║   ███████╗██████╔╝  ║
    ║   ╚═╝  ╚═══╝╚══════╝╚══════╝   ╚═╝   ╚══════╝╚═════╝   ║
    ║                                                         ║
    ║   [ SYSTEM READY ]    NanoPi 2 • DietPi • ARM Cortex-A9║
    ║                                                         ║
    ╚═════════════════════════════════════════════════════════╝
MOTD_EOF
fi

# 禁用 DietPi 默认 motd 覆盖
if [ -f /etc/dietpi/motd ]; then
    mv /etc/dietpi/motd /etc/dietpi/motd.bak 2>/dev/null || true
fi

echo "    ✓ 开机欢迎界面配置完成"

# ─────────────────────────────────────────────────────────────
#  [5/7] 配置 Powerline 字体
# ─────────────────────────────────────────────────────────────
echo "[5/7] 配置 Powerline 字体..."

# 安装 Powerline 字体 (如果尚未安装)
if [ ! -d /usr/share/fonts/powerline ] && [ ! -d /usr/share/fonts/truetype/powerline ]; then
    mkdir -p /usr/share/fonts/truetype/powerline
    # 下载 Powerline Symbols 字体
    curl -sL "https://github.com/powerline/powerline/raw/develop/font/PowerlineSymbols.otf" \
        -o /usr/share/fonts/truetype/powerline/PowerlineSymbols.otf 2>/dev/null || true
    # 下载 DejaVu Sans Mono for Powerline
    curl -sL "https://github.com/powerline/fonts/raw/master/DejaVuSansMono/DejaVu%20Sans%20Mono%20for%20Powerline.ttf" \
        -o "/usr/share/fonts/truetype/powerline/DejaVu Sans Mono for Powerline.ttf" 2>/dev/null || true
    # 刷新字体缓存
    fc-cache -f 2>/dev/null || true
fi

echo "    ✓ Powerline 字体配置完成"

# ─────────────────────────────────────────────────────────────
#  [6/7] 配置 tmux 赛博朋克主题
# ─────────────────────────────────────────────────────────────
echo "[6/7] 配置 tmux 主题..."

# 复制预制的 tmux.conf
if [ -f "${SCRIPT_DIR}/tmux.conf" ]; then
    cp "${SCRIPT_DIR}/tmux.conf" /root/.tmux.conf
else
    # 内联生成 (与 tmux.conf 文件相同)
    cat > /root/.tmux.conf << 'TMUX_EOF'
# ═══════════════════════════════════════════════
#  CYBERDECK tmux Configuration
#  赛博朋克主题状态栏
# ═══════════════════════════════════════════════

# 256 色支持
set -g default-terminal "screen-256color"
set -ga terminal-overrides ",xterm-256color:Tc"

# ── 状态栏 ──
set -g status-position bottom
set -g status-style "bg=#0a0a0f,fg=#00fff0"
set -g status-interval 1

# 左侧: 会话名
set -g status-left-length 30
set -g status-left "#[fg=#00fff0,bold] ⚡ #S #[fg=#7b2ff7]│#[default] "

# 右侧: 用户@主机 + 负载 + 时间
set -g status-right-length 60
set -g status-right "#[fg=#ff00ff]#(whoami)@#H #[fg=#7b2ff7]│ #[fg=#00fff0]#(cut -d' ' -f1-3 /proc/loadavg) #[fg=#7b2ff7]│ #[fg=#ff2d6f]%H:%M:%S #[default]"

# ── 窗口标签 ──
set -g window-status-format "#[fg=#c0c0c0] #I:#W "
set -g window-status-current-format "#[fg=#0a0a0f,bg=#00fff0,bold] #I:#W "
set -g window-status-activity-style "fg=#ff2d6f,bg=#0a0a0f"

# ── 分割窗格边框 ──
set -g pane-border-style "fg=#7b2ff7,bg=default"
set -g pane-active-border-style "fg=#00fff0,bg=default"

# ── 消息样式 ──
set -g message-style "bg=#0a0a0f,fg=#ff00ff,bold"
set -g message-command-style "bg=#0a0a0f,fg=#00ff64,bold"

# ── 时钟 ──
set -g clock-mode-colour "#00fff0"
set -g clock-mode-style 24

# ── 复制模式 ──
set -g mode-style "bg=#7b2ff7,fg=#c0c0c0"

# ── 功能配置 ──
set -g mouse on
set -g history-limit 10000
set -g base-index 1
set -g pane-base-index 1
set -g renumber-windows on
set -g set-titles on
set -g set-titles-string "#H → #S:#W"

# ── 快捷键 ──
# 前缀键: Ctrl+a (比 Ctrl+b 更顺手)
unbind C-b
set -g prefix C-a
bind C-a send-prefix

# 分割窗格
bind | split-window -h -c "#{pane_current_path}"
bind _ split-window -v -c "#{pane_current_path}"

# 窗格导航 (Alt + vim方向键)
bind -n M-h select-pane -L
bind -n M-j select-pane -D
bind -n M-k select-pane -U
bind -n M-l select-pane -R

# 窗口导航 (Shift + 左/右)
bind -n S-Left previous-window
bind -n S-Right next-window

# 重载配置
bind r source-file ~/.tmux.conf \; display "⚡ Cyberdeck tmux reloaded!"

# 快速启动矩阵效果 (Ctrl+a + m)
bind m run "cmatrix -s -B -C cyan 2>/dev/null || echo 'Install cmatrix'"

# ── 视觉 ──
set -g escape-time 0
set -g repeat-time 300
set -g focus-events on
TMUX_EOF
fi

echo "    ✓ tmux 主题配置完成"

# ─────────────────────────────────────────────────────────────
#  [7/7] 安装终端配色脚本 + 最终设置
# ─────────────────────────────────────────────────────────────
echo "[7/7] 安装终端配色脚本..."

# 复制终端配色脚本
if [ -f "${SCRIPT_DIR}/terminal_colors.sh" ]; then
    cp "${SCRIPT_DIR}/terminal_colors.sh" /usr/local/bin/cyberdeck-colors
    chmod +x /usr/local/bin/cyberdeck-colors
    echo "    ✓ terminal_colors.sh → /usr/local/bin/cyberdeck-colors"
fi

# 设置默认 shell 为 bash
usermod -s /bin/bash root 2>/dev/null || true

# 设置主机名
hostnamectl set-hostname cyberdeck 2>/dev/null || echo "cyberdeck" > /etc/hostname 2>/dev/null || true
# 添加 hostname 到 /etc/hosts
if ! grep -q "cyberdeck" /etc/hosts 2>/dev/null; then
    echo "127.0.1.1  cyberdeck" >> /etc/hosts
fi

# 在 .bashrc 末尾追加开机显示 neofetch
if ! grep -q "neofetch" /root/.bashrc 2>/dev/null; then
    cat >> /root/.bashrc << 'NEOFETCH_EOF'

# 开机显示系统信息 + ASCII art
if [ -n "${TERM:-}" ] && [ "${TERM}" != "dumb" ]; then
    neofetch --colors 6 5 6 5 6 5 2>/dev/null || true
fi

NEOFETCH_EOF
fi

echo "    ✓ 最终设置完成"

# ─────────────────────────────────────────────────────────────
#  完成
# ─────────────────────────────────────────────────────────────
echo ""
echo "  ╔════════════════════════════════════════╗"
echo "  ║  ✓ CYBERDECK Theme Setup Complete!    ║"
echo "  ║  ✓ 赛博朋克终端主题配置完成！         ║"
echo "  ╚════════════════════════════════════════╝"
echo ""
echo "  重启后生效："
echo "    sudo reboot"
echo ""
echo "  手动加载（不用重启）："
echo "    source ~/.bashrc"
echo "    tmux source ~/.tmux.conf"
echo ""
echo "  快捷命令："
echo "    matrix       — 黑客帝国矩阵效果"
echo "    cyber-prompt — 赛博朋克 ASCII art 标题"
echo "    sysinfo      — 系统信息 neofetch"
echo ""
