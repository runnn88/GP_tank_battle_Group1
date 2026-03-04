# Tank Battle: Chaos Maze

A local **2-player PvP tank game** built with **Python + Pygame**. Players duel inside a maze, using movement, turret control, and ricochet shots to destroy the opponent first.

---

## Table of Contents
- [1) Project Overview](#1-project-overview)
- [2) Tech Stack](#2-tech-stack)
- [3) Requirements](#3-requirements)
- [4) Setup and Run](#4-setup-and-run)
- [5) Controls (Default)](#5-controls-default)
- [6) Gameplay Summary](#6-gameplay-summary)
- [7) Physics Implementation (Reflection Included)](#7-physics-implementation-reflection-included)
- [8) Map Format](#8-map-format)
- [9) Asset Sources](#9-asset-sources)
- [10) Project Structure](#10-project-structure)

---

## 1) Project Overview

Tank Battle: Chaos Maze is designed for same-keyboard multiplayer. Each player controls one tank, navigates walls, and times shots to hit the enemy directly or via wall bounces.

### Main features
- Local 1v1 combat (same keyboard)
- Bullet ricochet with bounce limits
- Mix of destructible and indestructible wall tiles
- Menu/state system (`start`, `gameplay`, `pause`, `settings`, `game_over`)
- Settings for fullscreen, resolution, audio volume, keybinds, and independent turret mode

---

## 2) Tech Stack
- Python
- Pygame

---

## 3) Requirements
- Python 3.10+ recommended
- `pygame` package

---

## 4) Setup and Run

### Install dependency
```bash
pip install pygame
```

### Run game
```bash
python main.py
```

If the game window does not open, verify Python/Pygame installation and run from the repository root.

---

## 5) Controls (Default)

> Note: Turret controls can be changed in **Settings → Keybinds**.

### Player 1
- Move forward/backward: `W` / `S`
- Rotate tank body: `A` / `D`
- Shoot: `Space` or `F`
- Turret left/right (when **Independent Turret** is ON): `R` / `T`

### Player 2
- Move forward/backward: `Up` / `Down`
- Rotate tank body: `Left` / `Right`
- Shoot: `Enter` or `M`
- Turret left/right (when **Independent Turret** is ON): `N` / `M`

### Global
- Pause during gameplay: `Esc`
- Menu/Settings navigation: Arrow keys + `Enter` (or mouse)

---

## 6) Gameplay Summary
- Tanks have health and are destroyed after enough hits.
- Bullets are limited per player and have cooldown between shots.
- Indestructible walls reflect bullets.
- Destructible walls can be broken by bullet hits.
- Win condition: be the last surviving tank.

---

## 7) Physics Implementation (Reflection Included)

This section explains exactly what the game code does each frame for movement, collision, and bullet ricochet.

### 7.1 Frame update model (`dt`)
- The game updates using delta time (`dt`) from the main loop.
- All movement uses `speed * dt`, so behavior stays consistent across different FPS.

### 7.2 Tank movement (body direction)
- The tank body has an angle.
- A forward direction vector is computed from that angle.
- Pressing forward/backward adds/subtracts velocity along that direction.
- Position update is time-based:
  - `tank_position += tank_velocity * dt`

### 7.3 Tank vs wall collision (how clipping is prevented)
The tank uses **axis-separated collision resolution** against wall rectangles:
1. Move on **X** only.
2. If overlapping a wall, push tank out on X (to wall edge).
3. Move on **Y** only.
4. If overlapping a wall, push tank out on Y.

Why this is used:
- Prevents tanks from passing through corners.
- Avoids jitter from solving X and Y at the same time.
- Gives stable movement in narrow maze corridors.

### 7.4 Bullet movement
- Bullets store position and velocity vectors.
- Each frame:
  - `bullet_position += bullet_velocity * dt`
- Before moving, the previous bullet position is saved (`old_position`) for safe rollback during collision handling.

### 7.5 Bullet reflection on indestructible walls (what is actually done)
When a bullet collides with an indestructible wall tile:
1. **Rollback:** set bullet position back to `old_position` (prevents bullet getting stuck inside wall).
2. **Find impact side:** compare distances to the wall rectangle edges (left/right/top/bottom) and take the smallest one.
3. **Choose normal vector `n`:**
   - Left edge -> `(-1, 0)`
   - Right edge -> `(1, 0)`
   - Top edge -> `(0, -1)`
   - Bottom edge -> `(0, 1)`
4. **Reflect velocity:**
   - `v' = v - 2 * (v · n) * n`
5. **Count bounce:** increase bounce counter.
6. **Destroy if limit exceeded:** bullet is removed after passing the configured max bounce count.

### 7.6 Destructible wall handling (different from reflection)
- If the collided wall is destructible, the wall takes damage.
- If wall HP reaches 0, the wall is removed from the level.
- This interaction is damage/destruction logic, not a normal ricochet bounce.

### 7.7 Practical result in gameplay
- You can bank shots off solid walls to hit opponents indirectly.
- You cannot infinitely bounce unless bounce limit is configured that way.
- Destructible walls gradually open new paths as they are destroyed.

---

## 8) Map Format
Maps in `data/maps/` are plain text grids.

Symbols:
- `W` = solid wall
- `D` = destructible wall
- `P1` = player 1 spawn
- `P2` = player 2 spawn
- `.` = empty floor

---

## 9) Asset Sources
This repository ships required runtime assets inside `assets/`.

- **Visual assets**: tank sprites, wall/floor textures, effects, and backgrounds in `assets/` and `assets/BG/`
- **Fonts**: bundled in `assets/fonts/`
- **Audio**: bundled in `assets/sounds/`
  - Includes files named with `freesound_community-*`, indicating Freesound community sourced sound effects

If you redistribute this project, keep original attribution/license information for third-party assets where required.

---

## 10) Project Structure
- `main.py` — entry point and state-machine initialization
- `states/` — game states (menus, gameplay, pause, settings, game over)
- `game/` — gameplay systems (`tank`, `bullet`, `level`, `wall`, settings)
- `ui/` — HUD and interface rendering
- `data/maps/` — text-based level definitions
- `assets/` — images, fonts, audio
