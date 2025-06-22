# 🚀 Cannon Battle - Python Pygame Tank War Game

Welcome to **Cannon Battle**, an action-packed, turn-based tank shooting game built with **Python** and **Pygame**! 💣

Compete against a smart AI, earn points, unlock powerful tanks, and dominate the battlefield. Whether you're a casual gamer or a Python developer, Cannon Battle offers fun gameplay with solid logic, creative graphics, and strategic challenges.

---

## 📜 Game Story

> The world is at war. You're the last commander of your nation’s artillery force.  
> Your mission? **Defend your base**, **eliminate the AI tanks**, and **conquer with strategy** and precision.  
> **Win rounds, earn points, and unlock futuristic tanks** to upgrade your might and win the war.

---

## 🎮 Features

- 🧠 **Turn-Based Gameplay** – Take turns to attack the enemy tank.
- 🎯 **Mouse-Aiming Cannon System** – Click anywhere to fire at that angle.
- 🌍 **Physics-based Trajectories** – Realistic gravity and motion.
- 💥 **Explosions & Sounds** – Audio feedback for every hit and shot.
- 🧱 **Health System** – Tanks start with 100 HP. Manage it wisely!
- 💰 **Points & Rewards** – Win rounds to earn coins and upgrade tanks.
- 🔐 **Tank Unlock System** – Buy stronger tanks with points.
- 🤖 **AI Opponent with Dynamic Skins** – Random AI tank each game.
- 🔁 **Rounds & Match Scoring** – First to 3 wins ends the match.
- 💾 **Persistent Data Storage** – Unlocks and scores saved in `player_data.json`.

---

## 📁 Project Structure
cannon-battle/
├── main.py # Main game script
├── player_data.json # Points & unlocked tank data
├── assets/
│ ├── fire.wav # Cannon fire sound
│ ├── explosion.wav # Explosion sound
│ └── tanks/
│ ├── blue.png # Default tank
│ ├── red.png # AI tank 1
│ ├── red1.png # AI tank 2
│ ├── best1.png # Unlockable tank
│ ├── sifi.png # Unlockable tank
│ ├── sifi2.png # Unlockable tank
│ └── sifi3.png # Unlockable tank


🕹️ Controls
Action	Control
Move Player Tank	Left / Right Arrow
Fire Cannon	Mouse Left Click
Select Tank	Mouse Click
Exit Game	Window Close (X)

🏆 Match System
Each game is divided into rounds.

Win 3 rounds to win the match.

Earn:

+20 points per round win

+50 bonus points for match victory

Use points to unlock new tanks with stronger damage multipliers.

🛒 Tank Shop
Tank	Damage Multiplier	Price (Points)
blue	0.8	Free (Default)
best1	1.0	20
sifi	1.2	40
sifi2	1.4	60
sifi3	1.6	80

Tanks are unlocked permanently and saved to your data file.

The AI randomly selects from its set of red-themed tanks.

🧪 Troubleshooting
Issue: Game crashes with KeyError: 'red'
Fix: Ensure 'red' and 'red1' tank images are present in assets/tanks/.

Issue: No sound plays
Fix: Ensure fire.wav and explosion.wav are present in assets/.

Issue: Points not saving
Fix: Make sure player_data.json is writable (not read-only).

🛠️ Built With
💻 Python

🎮 Pygame

🖌️ Custom-designed tank images


🙏 Credits
Developed with 💖 by Yash Vaghasiya
Special thanks to the Pygame community for documentation and support.


📬 Contact
For questions, feedback, or collaboration:

Email: vaghasiyash2607@gmail.com

GitHub: github.com/v1yash
