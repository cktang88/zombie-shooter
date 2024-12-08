# Zombie Defense Shooter

A fast-paced 2D top-down shooter where you defend against waves of zombies while upgrading your arsenal and fortifying your position.

## Features

### Combat System

- **Multiple Weapon Types:**

  - Pistol: Balanced starter weapon
  - Assault Rifle: Rapid-fire automatic weapon
  - SMG: Very fast firing but lower damage
  - Battle Rifle: High damage semi-automatic
  - Shotgun: Close range spread damage
  - Knife: Melee weapon for emergencies
  - Grenades: Area damage explosives

- **Weapon Mechanics:**
  - Unique fire rates and damage values
  - Automatic and semi-automatic firing modes
  - Ammunition management and reloading
  - Screen shake feedback based on weapon type
  - Bullet physics and range limits

### Enemy System

- **Zombie Types:**

  - Normal: Balanced stats
  - Fast: Quick but fragile
  - Tank: Slow but high health
  - Boss zombies on special waves

- **AI Behavior:**
  - Active pursuit of player
  - Attack when in range
  - Health bars and damage feedback
  - Death animations and rewards

### Progression System

- **Wave-Based Gameplay:**

  - Increasingly difficult waves
  - More zombies per wave
  - Special boss waves
  - Wave completion rewards

- **Shop System:**
  - Available between waves
  - Weapon upgrades and new weapons
  - Defensive structures
  - Health and ammo refills

### Defensive Structures

- **Buildable Defenses:**
  - Walls: Block zombie movement
  - Turrets: Automatic defense
  - Traps: Damage or slow enemies
  - Strategic placement options

### Game Mechanics

- **Movement:**

  - WASD/Arrow keys for movement
  - Mouse aim and shooting
  - Smooth camera following
  - Screen shake effects

- **Resource Management:**
  - Health system
  - Ammo management
  - Cash economy
  - Grenade inventory

### User Interface

- **HUD Elements:**
  - Health bar
  - Ammo counter
  - Wave information
  - Cash display
  - Weapon selector
  - Shop interface

## Controls

- **Movement:** WASD or Arrow Keys
- **Combat:**
  - Left Click: Shoot
  - Right Click: Throw Grenade
  - R: Reload
  - Q: Switch Weapons
- **Game Flow:**
  - Space: Start Next Wave (in shop)
  - ESC: Pause Game
  - E: Buy/Interact in Shop

## Installation

1. Install Python 3.8 or higher
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run the game:

```bash
python main.py
```

## Game Flow

1. **Start Game:**

   - Begin with basic loadout
   - Initial cash allocation
   - Tutorial messages

2. **Combat Phase:**

   - Fight waves of zombies
   - Collect cash from kills
   - Manage resources
   - Use defensive structures

3. **Shop Phase:**

   - Appears after each wave
   - Buy new weapons
   - Upgrade existing gear
   - Place defensive structures
   - Replenish supplies

4. **Progression:**
   - Harder waves
   - More zombie types
   - Better upgrade options
   - Boss fights

## Development

The game is built with:

- Python 3.8+
- Pygame for graphics and input
- Object-oriented design
- Component-based architecture

### Project Structure

```
shooter-game/
├── src/
│   ├── entities/       # Game objects (player, zombies)
│   ├── weapons/        # Weapon system
│   ├── managers/       # Game state management
│   ├── structures/     # Defensive buildings
│   └── utils/         # Helper functions
├── assets/            # Graphics and sounds
├── requirements.txt   # Dependencies
└── main.py           # Entry point
```
