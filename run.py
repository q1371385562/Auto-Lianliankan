# coding: utf-8
"""Main entry of Auto-Lianliankan.
This script detects tiles inside a user-defined ROI and clicks on
identical pairs based on image similarity.
"""
import time
import importlib
from pathlib import Path

import cv2
import numpy as np
import keyboard
try:
    import win32api, win32con
except Exception:  # pragma: no cover
    win32api = win32con = None
import mss

import config

cfg = config
paused = False
running = True


def save_roi_to_config(roi):
    """Write ROI back to config.py if enabled."""
    if not cfg.SAVE_ROI_BACK_TO_CONFIG:
        return
    path = Path(__file__).with_name('config.py')
    text = path.read_text(encoding='utf-8')
    import re
    text = re.sub(r'ROI\s*=\s*\([^\)]*\)', f'ROI = {tuple(map(int, roi))}', text)
    text = re.sub(r'ROI_RESET\s*=\s*True', 'ROI_RESET = False', text)
    path.write_text(text, encoding='utf-8')
    print('ROI 已保存到 config.py')


def select_roi():
    """Show window for user to select ROI."""
    with mss.mss() as sct:
        screenshot = np.array(sct.grab(sct.monitors[0]))[:, :, :3]
    r = cv2.selectROI('请选择棋盘区域', screenshot, False)
    cv2.destroyWindow('请选择棋盘区域')
    if r == (0, 0, 0, 0):
        return None
    save_roi_to_config(r)
    return r


def ensure_roi():
    roi = cfg.ROI
    if cfg.ROI_RESET or roi[2] == 0 or roi[3] == 0:
        print('请框选棋盘区域 (ROI)')
        r = select_roi()
        if not r:
            raise SystemExit('未设置 ROI，程序退出')
        cfg.ROI = tuple(map(int, r))
        cfg.ROI_RESET = False
    return cfg.ROI


def capture_roi(roi):
    x, y, w, h = roi
    with mss.mss() as sct:
        img = np.array(sct.grab({'top': y, 'left': x, 'width': w, 'height': h}))
    return img[:, :, :3]


def detect_tiles(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    _, th = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    contours, _ = cv2.findContours(th, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    tiles = []
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        area = w * h
        if area < cfg.MIN_AREA or area > cfg.MAX_AREA:
            continue
        aspect = abs(w - h) / max(w, h)
        if aspect > cfg.ASPECT_TOL:
            continue
        cx, cy = x + w // 2, y + h // 2
        keep = True
        for t in tiles:
            if abs(cx - t['cx']) < cfg.NMS_DIST and abs(cy - t['cy']) < cfg.NMS_DIST:
                keep = False
                break
        if not keep:
            continue
        pad = int(min(w, h) * cfg.CROP_RATIO)
        crop = img[y + pad:y + h - pad, x + pad:x + w - pad]
        tiles.append({'box': (x, y, w, h), 'cx': cx, 'cy': cy, 'crop': crop})
    return tiles


def _norm_img(img):
    r = cv2.cvtColor(cv2.resize(img, (32, 32)), cv2.COLOR_BGR2GRAY)
    r = r.astype('float32') / 255.0
    return r


def compare(img1, img2):
    a = _norm_img(img1)
    b = _norm_img(img2)
    mean1, mean2 = a.mean(), b.mean()
    num = np.sum((a - mean1) * (b - mean2))
    den = np.sqrt(np.sum((a - mean1) ** 2) * np.sum((b - mean2) ** 2))
    if den == 0:
        return 0
    return num / den


def group_tiles(tiles):
    groups = []
    for t in tiles:
        placed = False
        for g in groups:
            if compare(t['crop'], g[0]['crop']) >= cfg.SSIM_THR:
                g.append(t)
                placed = True
                break
        if not placed:
            groups.append([t])
    return groups


def click(x, y):
    if win32api is None:
        print('未检测到 pywin32，无法发送鼠标事件')
        return False
    try:
        win32api.SetCursorPos((x, y))
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
        time.sleep(cfg.CLICK_DELAY_MS / 1000)
        return True
    except Exception:
        print('鼠标点击失败，请以管理员身份运行')
        return False


def process_once(roi):
    img = capture_roi(roi)
    tiles = detect_tiles(img)
    if cfg.DEBUG:
        dbg = img.copy()
        for t in tiles:
            x, y, w, h = t['box']
            cv2.rectangle(dbg, (x, y), (x + w, y + h), (0, 255, 0), 1)
        cv2.imshow('debug', dbg)
        cv2.waitKey(1)
    if not tiles:
        print('没有检测到方块，请调整参数')
        return
    groups = group_tiles(tiles)
    for g in groups:
        if len(g) >= 2:
            t1, t2 = g[0], g[1]
            x1 = roi[0] + t1['cx'] + cfg.CLICK_OFFSET_X
            y1 = roi[1] + t1['cy'] + cfg.CLICK_OFFSET_Y
            x2 = roi[0] + t2['cx'] + cfg.CLICK_OFFSET_X
            y2 = roi[1] + t2['cy'] + cfg.CLICK_OFFSET_Y
            if cfg.DEBUG:
                cv2.rectangle(dbg, (t1['box'][0], t1['box'][1]),
                              (t1['box'][0] + t1['box'][2], t1['box'][1] + t1['box'][3]), (0, 0, 255), 2)
            if cfg.DEBUG:
                cv2.rectangle(dbg, (t2['box'][0], t2['box'][1]),
                              (t2['box'][0] + t2['box'][2], t2['box'][1] + t2['box'][3]), (0, 0, 255), 2)
                cv2.imshow('debug', dbg)
                cv2.waitKey(1)
            click(x1, y1)
            click(x2, y2)
            return
    print('未找到可点击的配对')


def toggle_pause():
    global paused
    paused = not paused
    print('已暂停' if paused else '继续运行')


def stop():
    global running
    running = False
    print('收到退出命令')
    cv2.destroyAllWindows()


def reload_cfg():
    global cfg
    print('重新加载配置...')
    try:
        cfg = importlib.reload(config)
        register_hotkeys()
        print('配置已重新加载')
    except Exception as e:
        print('重新加载失败:', e)


def register_hotkeys():
    keyboard.clear_all_hotkeys()
    keyboard.add_hotkey(cfg.PAUSE_HOTKEY, toggle_pause)
    keyboard.add_hotkey(cfg.EXIT_HOTKEY, stop)
    keyboard.add_hotkey(cfg.RELOAD_HOTKEY, reload_cfg)


def main():
    register_hotkeys()
    roi = ensure_roi()
    while running:
        if not paused:
            try:
                process_once(roi)
            except Exception as e:
                print('处理过程出错:', e)
        time.sleep(cfg.LOOP_SLEEP_MS / 1000)


if __name__ == '__main__':
    main()
