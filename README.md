# OrchestraWebsite

Welcome to our repository! 

This project is a collaborative effort between university students living in the same household, known as the **Orchestrakot**. The goal of this repository is to explore and develop small tools that aim to simplify some of the everyday logistical or organizational challenges we face. What might seem like minor annoyances can end up consuming a lot of time and energy — so we’re trying to automate what we can!

## First feature: A rehearsal planner

As a music band, we often need to plan rehearsals during some days of the week or even big ones during weekends for bigger concerts. Our first idea was: _could we design a program that solves this kind of **Constraint Satisfaction Problem (CSP)** for us_, saving both time and mental load?

Eventually, we realized that just finding _a_ solution wasn't always enough, so we transitioned from pure CSP to **Constraint Optimization Problem (COP)** to allow for more flexibility and to model preferences.

We designed several constraints and preferences that reflect the real-life decisions we encounter when planning rehearsals.

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone <https://github.com/mat-bau/OrchestraWebsite.git>
cd OrchestraWebsite
```

### 2. Create and activate a virtual environment (recommended)
```bash
python3 -m venv venv
source venv/bin/activate      # On Linux/macOS
venv\Scripts\activate         # On Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### Execution

#### 1. Website
Launch the website

```bash
python3 start.py
```

```

#### 3. Access the interface at http://localhost:5050

---

## Bug fixes & contributions

This is an evolving project! If you find any bug, weird behavior, or simply have an idea that could improve the planner or add other features for shared living, **please open an issue or contribute directly** — we’d love your help.

---
## Next step

- Customize songs' rehearsal duration
- Clean the html
