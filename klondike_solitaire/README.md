# Klondike Solitaire - CSC200 Data Structures & Algorithms Mid Term Project

**Author:** @Muhammad Hamza  
**Course:** CSC200 Data Structures & Algorithms  
**Project:** Mid Term Project — Klondike Solitaire  
**Date:** November 21, 2026  
**Implementation Technology:** Python 3 (Pure standard library, zero external pip dependencies)

---

## 1. Project Overview

This software implements a complete, single-player **Klondike Solitaire** game engineered specifically to demonstrate the practical, real-world application of core computer science data structures:
1. **Arrays / Lists** (`DS-1`): Deck creation, index access, swap, and unbiased Fisher-Yates shuffle in $O(n)$ with seedable PRNG.
2. **Custom Stacks (LIFO)** (`DS-2`): Hand-written singly linked node stack used for the 4 Foundation piles, the Waste pile, the Undo stack, and the Redo stack.
3. **Custom Queue (FIFO)** (`DS-3`): Hand-written linked queue with direct head and tail pointers used for the Stock draw pile.
4. **Custom Doubly Linked List** (`DS-4`, `DS-6`): Hand-written doubly linked list with direct tail access used for the 7 Tableau piles, enabling $O(1)$ stack-like top access and $O(1)$ pointer-based detachment/attachment of card runs.
5. **Custom Hash Map** (`DS-5`, `DS-9`): Hand-written separate chaining hash map tracking every card's unique ID (`card.id`) to its real-time location record (`pile`, `index`, `position`, `face_up`).

The project provides **two external interfaces**:
- **Interactive Terminal Console UI** (compliant with SRS Section 6.3 & 6.4)
- **"Midnight Run" Street-Racing Graphical User Interface (GUI)** with Web Audio sounds, speedometer/odometer dashboard HUD, nitro combo meter, and theme switching.

---

## 2. Architecture & File Structure

```
klondike_solitaire/
├── card.py              # Card model, suits, ranks, colors, and ANSI short labels
├── dsa.py               # Hand-written Stack, Queue, DoublyLinkedList, HashMap, Deck
├── game.py              # Klondike Solitaire game engine, rules, validation, undo/redo, hints
├── ui.py                # Text-based interactive terminal console interface (SRS Sec 6)
├── test_solitaire.py    # Automated test suite covering all 22 test cases (TC-01 to TC-22)
├── server.py            # Python HTTP server & REST API serving the GUI and endpoints
├── main.py              # Unified CLI launcher (--cli, --gui, --test)
├── run_game.bat         # Windows 1-click batch launcher for GUI
├── run_cli.bat          # Windows 1-click batch launcher for CLI
├── run_tests.bat        # Windows 1-click batch launcher for Test Suite
├── README.md            # Comprehensive documentation & traceability matrix
└── web/
    └── index.html       # "Midnight Run" street-racing web GUI + DSA X-Ray Inspector
```

---

## 3. Data Structures Mapping & Complexity

| SRS ID | Data Structure | Used For | Key Operations | Time Complexity |
|---|---|---|---|---|
| **DS-1** | Array / List | 52-card Deck before & during deal | Fisher-Yates shuffle, indexed deal | $O(n)$ shuffle, $O(1)$ deal |
| **DS-2** | Stack (LIFO) | 4 Foundation piles, Waste pile, Undo stack, Redo stack | `push()`, `pop()`, `peek()`, `size()` | $O(1)$ each |
| **DS-3** | Queue (FIFO) | Stock draw pile | `enqueue()`, `dequeue()`, `peek()`, `size()` | $O(1)$ each |
| **DS-4** | Doubly Linked List | 7 Tableau piles (head at bottom, tail at top) | `append()`, `pop_tail()`, `split_from()`, `attach()` | $O(1)$ top, $O(1)$ attach/detach |
| **DS-5** | Hash Map | Card Location & State Index (`card.id` &rarr; record) | `put()`, `get()`, `remove()`, `entries()` | $O(1)$ average |
| **DS-7** | Temporary Stack | Stock recycling from Waste pile | Pop waste &rarr; push temp &rarr; pop temp &rarr; enqueue stock | $O(n)$ restoring original draw order |

---

## 4. How to Run

### Option A: Using Windows Batch Scripts
- Double click **`run_game.bat`** to launch the **Midnight Run** GUI in your default browser.
- Double click **`run_cli.bat`** to start the interactive **Terminal Console UI**.
- Double click **`run_tests.bat`** to execute the **Automated Validation Suite**.

### Option B: Using Python Command Line
```powershell
# 1. Interactive Menu
python main.py

# 2. Text Console Interface (CLI)
python main.py --cli

# 3. Graphical Interface (GUI)
python main.py --gui

# 4. Automated Test Suite (All 22 Test Cases)
python main.py --test
```

*(Note: If using the included portable Python runtime in `.python`, run `..\.python\python.exe main.py`)*

---

## 5. Console Commands & Notation (SRS Section 6.3)

| Command | Action | Example |
|---|---|---|
| `d` | Draw from Stock queue (or recycle waste if empty) | `d` |
| `m SRC DST [N]` | Move $N$ cards (default 1) from `SRC` to `DST` | `m T3 T5 2`, `m W T1`, `m F1 T2` |
| `f SRC` | Send top card of `SRC` (`W` or `T1`..`T7`) to its Foundation | `f W`, `f T4` |
| `u` | Undo previous move (reverses card flips and points) | `u` |
| `r` | Redo previously undone move | `r` |
| `h` | Suggest intelligent hint for next best move | `h` |
| `n` | Start a new game (confirms with player) | `n` |
| `?` | Show command reference & pile notation | `?` |
| `q` | Quit game (confirms with player) | `q` |

---

## 6. Validation & Test Traceability Matrix (Section 10)

All 22 test cases pass with a **100% success rate**:

| Test ID | Test Name | Expected Result | Requirements Covered | Status |
|---|---|---|---|---|
| **TC-01** | Deck Integrity | Exactly 52 unique cards; 13 per suit; 26 red, 26 black | FR-1.1, FR-1.2, FR-1.3 | **PASS** |
| **TC-02** | Shuffle Determinism | Different seeds yield different orders; same seed identical | FR-1.4, FR-1.5, NFR-10 | **PASS** |
| **TC-03** | Initial Deal | Tableau 1..7 cards; only top card face-up; 24 in stock | FR-2.1, FR-2.2, FR-2.3, FR-2.4 | **PASS** |
| **TC-04** | Stack Behavior | Push 3, pop 3 in reverse order; pop empty reports None | DS-2, NFR-2 | **PASS** |
| **TC-05** | Queue Behavior | Enqueue 3, dequeue 3 in FIFO order; dequeue empty reports None | DS-3, NFR-2 | **PASS** |
| **TC-06** | DLL Run Detach | Detach top 3 cards from pile of 5; attach to new pile | DS-4, DS-6, FR-4.6 | **PASS** |
| **TC-07** | Draw-1 & Draw-3 | 1 or 3 cards dequeued to waste; handles low stock correctly | FR-3.2, FR-3.3 | **PASS** |
| **TC-08** | Waste Recycle | Emptying waste via temp stack preserves original FIFO draw order | FR-3.5, DS-7 | **PASS** |
| **TC-09** | Legal Tableau Move | Red 6 placed on Black 7 accepted | FR-4.3 | **PASS** |
| **TC-10** | Illegal Tableau Moves | Same color, wrong rank, or face-down in run rejected | FR-4.3, FR-4.5, FR-6.2 | **PASS** |
| **TC-11** | Empty Pile Rule | King accepted on empty tableau pile; non-King rejected | FR-4.4 | **PASS** |
| **TC-12** | Foundation Rules | Ace starts pile; same suit rank+1 accepted; wrong rejected | FR-5.2, FR-5.3 | **PASS** |
| **TC-13** | Card Flipping | Exposing face-down card turns it face-up automatically | FR-6.3 | **PASS** |
| **TC-14** | Location Map | Location HashMap matches actual pile positions for all 52 cards | FR-6.5, DS-5, DS-9 | **PASS** |
| **TC-15** | Undo Flip | Undo restores cards and returns auto-flipped card to face-down | FR-7.1, FR-7.2 | **PASS** |
| **TC-16** | Undo/Redo Chain | 5 actions, undo 3, redo 2; new move invalidates redo stack | FR-7.3, FR-7.4, FR-7.5 | **PASS** |
| **TC-17** | Empty Undo/Redo | Undo/redo on empty stack does nothing; returns friendly message | FR-7.6 | **PASS** |
| **TC-18** | Win Detection | Placing 52nd card in foundation announces win & stops moves | FR-8.1, FR-8.2, FR-8.3 | **PASS** |
| **TC-19** | Non-Win State | 3 full foundations and one with 12 cards is not a win | FR-8.1 | **PASS** |
| **TC-20** | Bad Input Resilience | Malformed, empty, and unknown commands never crash program | FR-9.3, NFR-3 | **PASS** |
| **TC-21** | Card Conservation | Total card count across all piles is strictly 52 at every step | NFR-4, all FR | **PASS** |
| **TC-22** | Hint Priority | Foundation moves are prioritized first over tableau moves | FR-10.1, FR-10.2 | **PASS** |

---

## 7. Graphical UI: "Midnight Run" Street-Racing Direction

- **Atmosphere & Table**: Dark asphalt wet-road texture with reflections, night-city skyline silhouette, drifting horizontal speed streaks, and a carbon-fiber textured backing panel for optimal card contrast.
- **Cards**: Matte finish with chrome edge borders, angular corner cut, racing red hearts/diamonds, graphite black spades/clubs, bold sports typography (`Orbitron`), and carbon-fiber weave card back with racing stripes and aerodynamic chevron emblem.
- **Dashboard HUD**:
  - Speedometer-style dial gauge for elapsed time.
  - Digital odometer with rolling numbers for score.
  - Tachometer arc for move counts.
  - Nitro combo bar: consecutive legal actions fill the Nitro cylinder, triggering a screen speed-burst effect!
- **Web Audio Synthesizer**: Zero external audio files required. Uses native HTML5 Web Audio API:
  - Engine rev rise on stock draw.
  - Tire screech sweep on illegal moves.
  - Turbo whoosh on foundation placement.
  - Electronic fanfare arpeggios on win.
  - Mute button toggle (muted by default).
- **Theme Selection**:
  - `Midnight Run` (Default: Street Racing)
  - `Midnight Casino` (Classic Emerald Felt & Gold Trim)
  - `Paper Minimal` (Clean Warm Parchment & Wood)
- **DSA X-Ray Inspector**: Live side-drawer visualizer showing the internal state of all 5 data structures in real-time.
