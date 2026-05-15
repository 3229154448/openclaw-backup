/*
 * ═══════════════════════════════════════════════════════════
 *  CYBERDECK CASE — NanoPi 2 赛博朋克便携电脑外壳
 *  OpenSCAD 源文件
 * ═══════════════════════════════════════════════════════════
 *
 * 设计目标: 为友善之臂 NanoPi 2 打造赛博朋克风格便携电脑外壳
 * 打印方式: 分上下两半打印，拼合组装
 *
 * ── 尺寸参数（方便调整） ──────────────────────────────────
 *
 * 外壳:
 *   case_w     = 128   外壳宽度 (X轴)
 *   case_d     = 95    外壳深度 (Y轴)
 *   case_h     = 32    外壳总高度 (Z轴)
 *   wall       = 2.0   壁厚
 *   lip        = 1.2   上下半咬合唇边高度
 *   lip_gap    = 0.3   唇边间隙（打印公差）
 *
 * 内部组件:
 *   nanopi_w   = 75    NanoPi 2 板宽
 *   nanopi_d   = 40    NanoPi 2 板深
 *   nanopi_h   = 12    NanoPi 2 + 插头高度余量
 *   screen_w   = 92    3.5寸 HDMI 屏幕宽度
 *   screen_d   = 56    3.5寸 HDMI 屏幕深度
 *   screen_h   = 8     屏幕模组厚度
 *   kb_w       = 120   40%键盘PCB宽度
 *   kb_d       = 42    40%键盘PCB深度
 *   kb_h       = 12    键盘+键帽高度
 *   batt_w     = 65    18650电池组宽度
 *   batt_d     = 55    18650电池组深度
 *   batt_h     = 18    电池组高度
 *
 * 接口开口 (Y轴右侧面板):
 *   usb_a_w    = 13    USB-A 口宽度
 *   usb_a_h    = 6     USB-A 口高度
 *   microusb_w = 11    micro USB 口宽度
 *   microusb_h = 4     micro USB 口高度
 *   rj45_w     = 16    RJ45 口宽度
 *   rj45_h     = 14    RJ45 口高度
 *   audio_d    = 6.5   3.5mm 音频口直径
 *
 * RGB灯带:
 *   rgb_t      = 5     灯带宽度 (WS2812B 5050)
 *   rgb_h      = 2     灯带厚度
 *
 * 透明顶面板 (亚克力):
 *   acry_w     = 120   顶面板宽度
 *   acry_d     = 87    顶面板深度
 *   acry_t     = 2     顶面板厚度
 *   slot_gap   = 0.3   卡槽间隙
 *
 * 散热格栅:
 *   grille_w   = 1.2   格栅条宽度
 *   grille_sp  = 2.8   格栅间距
 *   grille_n   = 15    格栅数量
 *
 * 赛博朋克配色方案 (喷漆/后处理参考):
 *   背景:  #0a0a0f  深黑偏蓝
 *   主色:  #00fff0  荧光青
 *   强调:  #ff00ff  品红
 *   次要:  #7b2ff7  电紫
 *   警告:  #ff2d6f  霓虹红
 *
 * ═══════════════════════════════════════════════════════════
 */

// ── 全局尺寸参数 ──────────────────────────────────────────

// 外壳
case_w     = 128;
case_d     = 95;
case_h     = 32;
wall       = 2.0;
lip        = 1.2;
lip_gap    = 0.3;

// NanoPi 2
nanopi_w   = 75;
nanopi_d   = 40;
nanopi_h   = 12;

// 3.5寸 HDMI 屏幕
screen_w   = 92;
screen_d   = 56;
screen_h   = 8;

// 40% 键盘
kb_w       = 120;
kb_d       = 42;
kb_h       = 12;

// 电池组 (2×18650)
batt_w     = 65;
batt_d     = 55;
batt_h     = 18;

// 接口开口
usb_a_w    = 13;
usb_a_h    = 6;
microusb_w = 11;
microusb_h = 4;
rj45_w     = 16;
rj45_h     = 14;
audio_d    = 6.5;

// RGB 灯带
rgb_t      = 5;
rgb_h      = 2;

// 透明亚克力顶面板
acry_w     = 120;
acry_d     = 87;
acry_t     = 2;
slot_gap   = 0.3;

// 散热格栅
grille_w   = 1.2;
grille_sp  = 2.8;
grille_n   = 15;

// 螺丝柱
post_d     = 6;
post_hole  = 2.2;  // M2 螺丝孔

// $fn 全局精度
$fn = 36;

// ── 内部尺寸计算 ──────────────────────────────────────────
inner_w = case_w - 2 * wall;
inner_d = case_d - 2 * wall;
inner_h = case_h - 2 * wall;
half_h  = case_h / 2;

// ── GPIO 露出口尺寸 (左侧 Y=0 面) ───────────────────────
gpio_open_w = 42;  // 40pin + 余量
gpio_open_h = 8;

// ═══════════════════════════════════════════════════════════
//  散热格栅辅助模块
// ═══════════════════════════════════════════════════════════
module vent_grille(length, n, bar_w, bar_sp, depth) {
    /*
     * 生成赛博朋克风格散热格栅
     * length: 格栅总长度
     * n:      栅条数量
     * bar_w:  每根栅条宽度
     * bar_sp: 栅条间距
     * depth:  栅条深度（壁厚方向）
     */
    total = n * (bar_w + bar_sp);
    start = -total / 2;
    for (i = [0 : n - 1]) {
        pos = start + i * (bar_w + bar_sp);
        translate([pos, -depth / 2, 0])
            cube([bar_w, depth, length]);
    }
}

// ═══════════════════════════════════════════════════════════
//  内部固定柱辅助模块
// ═══════════════════════════════════════════════════════════
module stand_off(x, y, h, d, hole) {
    /*
     * 生成带螺丝孔的固定柱
     * x, y: 位置
     * h:    高度
     * d:    柱外径
     * hole: 螺丝孔径
     */
    translate([x, y, 0])
        difference() {
            cylinder(h=h, d=d);
            translate([0, 0, h - 3])
                cylinder(h=3.5, d=hole);  // M2 自攻螺丝孔
        }
}

// ═══════════════════════════════════════════════════════════
//  RGB 灯带槽辅助模块 (内壁四周凹槽)
// ═══════════════════════════════════════════════════════════
module rgb_channel(w, d, t, h, depth) {
    /*
     * 在内壁四边挖出 RGB 灯带凹槽
     * w, d:  外壳内尺寸
     * t:     灯带宽度
     * h:     灯带厚度
     * depth: 凹槽深入壁的深度
     */
    // 前边 (X方向)
    translate([0, -depth/2, 0])
        cube([w, depth + t, h]);
    // 后边
    translate([0, d - t - depth/2, 0])
        cube([w, depth + t, h]);
    // 左边 (Y方向)
    translate([-depth/2, 0, 0])
        cube([depth + t, d, h]);
    // 右边
    translate([w - t - depth/2, 0, 0])
        cube([depth + t, d, h]);
}

// ═══════════════════════════════════════════════════════════
//  上下半咬合唇边 (盒扣结构)
// ═══════════════════════════════════════════════════════════
module lip_male(w, d, wall_t, lip_h, gap) {
    /*
     * 下半壳的凸唇 (male)
     * 沿内壁四周凸出，嵌入上半壳的凹槽
     */
    g = gap;
    t = wall_t - g;
    // 前边
    translate([wall_t, wall_t - g/2, 0])
        cube([w - 2*wall_t, t, lip_h]);
    // 后边
    translate([wall_t, d - wall_t - t + g/2, 0])
        cube([w - 2*wall_t, t, lip_h]);
    // 左边
    translate([wall_t - g/2, wall_t, 0])
        cube([t, d - 2*wall_t, lip_h]);
    // 右边
    translate([w - wall_t - t + g/2, wall_t, 0])
        cube([t, d - 2*wall_t, lip_h]);
}

module lip_female(w, d, wall_t, lip_h, gap) {
    /*
     * 上半壳的凹槽 (female)
     * 沿内壁四周挖出凹槽，容纳下半壳的凸唇
     */
    g = gap;
    t = wall_t;
    // 前边
    translate([wall_t, wall_t - g, -lip_h])
        cube([w - 2*wall_t, t + g, lip_h]);
    // 后边
    translate([wall_t, d - wall_t - t - g/2, -lip_h])
        cube([w - 2*wall_t, t + g, lip_h]);
    // 左边
    translate([wall_t - g, wall_t, -lip_h])
        cube([t + g, d - 2*wall_t, lip_h]);
    // 右边
    translate([w - wall_t - t - g/2, wall_t, -lip_h])
        cube([t + g, d - 2*wall_t, lip_h]);
}

// ═══════════════════════════════════════════════════════════
//  亚克力顶面板卡槽 (上半壳内壁顶部)
// ═══════════════════════════════════════════════════════════
module acrylic_slot(w, d, panel_w, panel_d, panel_t, slot_g, depth) {
    /*
     * 在上半壳内壁挖出亚克力顶面板滑入卡槽
     * 卡槽沿前后两条边，面板从侧面滑入
     */
    offset_x = (w - panel_w) / 2 - wall;
    offset_y = (d - panel_d) / 2 - wall;

    // 前边卡槽 (Y = offset_y 方向)
    translate([wall + offset_x - slot_g, wall - depth, 0])
        cube([panel_w + 2*slot_g, depth + wall, panel_t + slot_g]);
    // 后边卡槽
    translate([wall + offset_x - slot_g, d - wall - offset_y - slot_g, 0])
        cube([panel_w + 2*slot_g, depth + wall, panel_t + slot_g]);
}

// ═══════════════════════════════════════════════════════════
//  接口面板开口 (右侧 Y=case_d 面)
// ═══════════════════════════════════════════════════════════
module port_cutouts_right(w, d, h, wall_t) {
    /*
     * 右侧面板 (Y=d) 的接口开口
     * 从左到右: micro USB → USB-A → RJ45 → 3.5mm 音频
     * 开口中心高度 = h/2 (外壳高度中点)
     */
    cy = h / 2;  // 垂直中心
    margin = 8;

    // micro USB (最左)
    translate([margin, d - wall_t - 0.5, cy - microusb_h/2])
        cube([microusb_w, wall_t + 1, microusb_h]);

    // USB-A
    translate([margin + microusb_w + 5, d - wall_t - 0.5, cy - usb_a_h/2])
        cube([usb_a_w, wall_t + 1, usb_a_h]);

    // RJ45
    translate([margin + microusb_w + 5 + usb_a_w + 5, d - wall_t - 0.5, cy - rj45_h/2])
        cube([rj45_w, wall_t + 1, rj45_h]);

    // 3.5mm 音频 (圆形)
    translate([margin + microusb_w + 5 + usb_a_w + 5 + rj45_w + 6, d - wall_t - 0.5, cy])
        rotate([90, 0, 0])
            cylinder(h=wall_t + 1, d=audio_d + 0.5);
}

// ═══════════════════════════════════════════════════════════
//  GPIO 露出口 (左侧 Y=0 面)
// ═══════════════════════════════════════════════════════════
module gpio_cutout_left(w, d, h, wall_t) {
    /*
     * 左侧面 GPIO 40pin 露出口
     * 位于 NanoPi 2 安装位置对应的侧面
     */
    offset_x = wall + 8;  // NanoPi 2 X偏移
    cy = half_h;          // 对准板子中部

    translate([offset_x, -0.5, cy - gpio_open_h/2])
        cube([gpio_open_w, wall_t + 1, gpio_open_h]);
}

// ═══════════════════════════════════════════════════════════
//  上半壳 (TOP HALF)
// ═══════════════════════════════════════════════════════════
module top_half() {
    /*
     * 上半壳:
     * - 容纳屏幕和键盘
     * - 顶部有亚克力透明面板卡槽
     * - 内壁有RGB灯带凹槽
     * - 唇边凹槽 (female) 与下半壳咬合
     * - 顶面散热格栅
     */
    translate([0, 0, half_h])  // 抬升到上半部分
    difference() {
        // ── 外壳主体 ──
        cube([case_w, case_d, half_h]);

        // ── 内部空腔 ──
        translate([wall, wall, wall])
            cube([inner_w, inner_d, half_h - wall]);

        // ── 唇边凹槽 (female) ──
        translate([0, 0, wall])
            lip_female(case_w, case_d, wall, lip, lip_gap);

        // ── RGB 灯带凹槽 ──
        translate([wall, wall, half_h - wall - rgb_h - 1])
            rgb_channel(inner_w, inner_d, rgb_t, rgb_h, 1);

        // ── 亚克力顶面板卡槽 ──
        translate([0, 0, half_h - acry_t - 3])
            acrylic_slot(case_w, case_d, acry_w, acry_d, acry_t, slot_gap, 1.5);

        // ── 顶面散热格栅 (X方向，居中) ──
        translate([case_w/2, wall + 5, half_h - 0.5])
            vent_grille(inner_d - 10, grille_n, grille_w, grille_sp, wall + 1);

        // ── 右侧接口开口 ──
        port_cutouts_right(case_w, case_d, case_h, wall);

        // ── 左侧 GPIO 露出口 ──
        gpio_cutout_left(case_w, case_d, case_h, wall);

        // ── 赛博朋克棱角切面装饰 (顶面) ──
        // 左前角斜切
        translate([0, 0, half_h - 0.5])
            rotate([0, 0, 45])
                translate([-8, -8, 0])
                    cube([10, 10, wall + 1]);

        // 右前角斜切
        translate([case_w, 0, half_h - 0.5])
            rotate([0, 0, -45])
                translate([-2, -8, 0])
                    cube([10, 10, wall + 1]);
    }

    // ── 屏幕固定柱 (4个角) ──
    // 屏幕居中偏前放置
    scr_x = wall + (inner_w - screen_w) / 2;
    scr_y = wall + 3;
    scr_z = half_h + wall;

    translate([scr_x + 3, scr_y + 3, scr_z])
        stand_off(0, 0, half_h - 2*wall, post_d, post_hole);
    translate([scr_x + screen_w - 3, scr_y + 3, scr_z])
        stand_off(0, 0, half_h - 2*wall, post_d, post_hole);
    translate([scr_x + 3, scr_y + screen_d - 3, scr_z])
        stand_off(0, 0, half_h - 2*wall, post_d, post_hole);
    translate([scr_x + screen_w - 3, scr_y + screen_d - 3, scr_z])
        stand_off(0, 0, half_h - 2*wall, post_d, post_hole);

    // ── 键盘固定柱 (4个角) ──
    // 键盘在屏幕上方
    kb_x = wall + (inner_w - kb_w) / 2;
    kb_y = scr_y + screen_d + 3;

    translate([kb_x + 3, kb_y + 3, scr_z])
        stand_off(0, 0, half_h - 2*wall, post_d, post_hole);
    translate([kb_x + kb_w - 3, kb_y + 3, scr_z])
        stand_off(0, 0, half_h - 2*wall, post_d, post_hole);
    translate([kb_x + 3, kb_y + kb_d - 3, scr_z])
        stand_off(0, 0, half_h - 2*wall, post_d, post_hole);
    translate([kb_x + kb_w - 3, kb_y + kb_d - 3, scr_z])
        stand_off(0, 0, half_h - 2*wall, post_d, post_hole);
}

// ═══════════════════════════════════════════════════════════
//  下半壳 (BOTTOM HALF)
// ═══════════════════════════════════════════════════════════
module bottom_half() {
    /*
     * 下半壳:
     * - 容纳 NanoPi 2 主板和电池组
     * - 底面散热格栅
     * - 内壁RGB灯带凹槽
     * - 唇边凸唇 (male) 与上半壳咬合
     * - 赛博朋克棱角装饰
     */
    difference() {
        // ── 外壳主体 ──
        cube([case_w, case_d, half_h]);

        // ── 内部空腔 ──
        translate([wall, wall, wall])
            cube([inner_w, inner_d, half_h - wall]);

        // ── 底面散热格栅 ──
        translate([case_w/2, case_d/2, -0.5])
            vent_grille(inner_d - 10, grille_n, grille_w, grille_sp, wall + 1);

        // ── 右侧接口开口 (下半壳也需留口，接口跨越分型线) ──
        port_cutouts_right(case_w, case_d, case_h, wall);

        // ── 左侧 GPIO 露出口 ──
        gpio_cutout_left(case_w, case_d, case_h, wall);

        // ── 底部赛博朋克棱角切面装饰 ──
        // 左后角斜切
        translate([0, case_d, -0.5])
            rotate([0, 0, -135])
                translate([-8, -2, 0])
                    cube([10, 10, wall + 1]);

        // 右后角斜切
        translate([case_w, case_d, -0.5])
            rotate([0, 0, 135])
                translate([-2, -2, 0])
                    cube([10, 10, wall + 1]);
    }

    // ── 唇边凸唇 (male) ──
    translate([0, 0, half_h - wall])
        lip_male(case_w, case_d, wall, lip, lip_gap);

    // ── NanoPi 2 固定柱 (4个角 + HDMI口侧偏移) ──
    np_x = wall + 8;
    np_y = wall + (inner_d - nanopi_d) / 2;

    translate([np_x + 3, np_y + 3, wall])
        stand_off(0, 0, half_h - 2*wall, post_d, post_hole);
    translate([np_x + nanopi_w - 3, np_y + 3, wall])
        stand_off(0, 0, half_h - 2*wall, post_d, post_hole);
    translate([np_x + 3, np_y + nanopi_d - 3, wall])
        stand_off(0, 0, half_h - 2*wall, post_d, post_hole);
    translate([np_x + nanopi_w - 3, np_y + nanopi_d - 3, wall])
        stand_off(0, 0, half_h - 2*wall, post_d, post_hole);

    // ── 电池固定柱 (4个角) ──
    bt_x = wall + (inner_w - batt_w) / 2;
    bt_y = np_y + nanopi_d + 5;

    translate([bt_x + 3, bt_y + 3, wall])
        stand_off(0, 0, half_h - 2*wall, post_d, post_hole);
    translate([bt_x + batt_w - 3, bt_y + 3, wall])
        stand_off(0, 0, half_h - 2*wall, post_d, post_hole);
    translate([bt_x + 3, bt_y + batt_d - 3, wall])
        stand_off(0, 0, half_h - 2*wall, post_d, post_hole);
    translate([bt_x + batt_w - 3, bt_y + batt_d - 3, wall])
        stand_off(0, 0, half_h - 2*wall, post_d, post_hole);

    // ── 内壁加强筋 (赛博朋克棱角风格) ──
    // 对角线加强筋
    translate([wall, wall, wall])
        hull() {
            translate([0, 0, 0]) cylinder(h=half_h - 2*wall, d=2);
            translate([inner_w, inner_d, 0]) cylinder(h=half_h - 2*wall, d=2);
        }
    translate([wall, wall, wall])
        hull() {
            translate([inner_w, 0, 0]) cylinder(h=half_h - 2*wall, d=2);
            translate([0, inner_d, 0]) cylinder(h=half_h - 2*wall, d=2);
        }
}

// ═══════════════════════════════════════════════════════════
//  渲染控制
// ═══════════════════════════════════════════════════════════
// 设置 view = "top" 或 "bottom" 分别渲染上下半壳
// 设置 view = "both" 同时显示两半 (预览用，3D打印时需分开)

view = "both";  // 修改此处: "top" / "bottom" / "both"

if (view == "top" || view == "both") {
    top_half();
}

if (view == "bottom" || view == "both") {
    if (view == "both") {
        translate([0, 0, 0])  // 下半壳在原位
    }
    bottom_half();
}

// 预览时，上半壳上移显示内部结构
if (view == "both") {
    // 此处仅用于可视化，实际打印时请分别设置 view="top" / view="bottom"
}
