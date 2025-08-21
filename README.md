# Auto-Lianliankan

基于屏幕截图和图像相似度的连连看辅助脚本。

## 安装
```bash
pip install opencv-python numpy Pillow pywin32 keyboard mss
```

## 使用步骤
1. 打开游戏后运行 `python run.py`。
2. 首次运行会弹出截图，使用鼠标拖动框选棋盘区域 (ROI)。
3. ROI 会保存到 `config.py`，下次启动可直接复用。若需重新框选，将 `config.py` 中 `ROI_RESET` 设为 `True`。
4. 脚本会在 ROI 内检测方块，相似的图标会自动两两点击。

## 参数调整与热加载
- 所有参数位于 `config.py`，例如检测阈值、点击偏移、热键等。
- 修改 `config.py` 后，在终端按 `Enter`(默认) 即可热加载，无需重启脚本。

主要参数：
- `ROI`、`ROI_RESET`、`SAVE_ROI_BACK_TO_CONFIG`
- 目标检测：`MIN_AREA`、`MAX_AREA`、`ASPECT_TOL`、`NMS_DIST`、`CROP_RATIO`、`SSIM_THR`
- 点击控制：`CLICK_OFFSET_X`、`CLICK_OFFSET_Y`、`CLICK_DELAY_MS`、`LOOP_SLEEP_MS`
- 热键：`PAUSE_HOTKEY`、`EXIT_HOTKEY`、`RELOAD_HOTKEY`

## 可视化调试
`config.DEBUG` 为 `True` 时，会显示调试窗口：
- 绿色框表示检测到的所有方块。
- 红色框表示即将点击的两块。

## 常见问题
- **定位不到窗口/ROI**：确保游戏窗口位于主屏幕内，必要时重新框选 ROI。
- **无法发送鼠标事件**：请安装 `pywin32` 并以管理员身份运行脚本。
- **点击偏移**：调整 `CLICK_OFFSET_X/Y`，默认 Y 方向向上偏移以避开阴影。
- **相似度阈值过高/过低**：调节 `SSIM_THR`，值越高越严格。

仅供学习交流，请勿用于商业用途。
