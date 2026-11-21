"""
ui.py - Interactive Text-Based Console Interface
CSC200 Data Structures & Algorithms | Mid Term Project
Author: @Muhammad Hamza

Requirements Covered:
- UI-1, UI-2, UI-3: Board layout, [##] face-down cards, rank/suit labels, colored suits.
- UI-4, NFR-3, NFR-6: Friendly one-line reason for rejected actions, crash-proof parsing.
- Section 6.3: Command set (d, m, f, u, r, h, n, ?, q).
- FR-9.4: Formatted Help screen with pile notations and commands.
- FR-9.5: Safe confirmation before quitting or restarting game in progress.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from typing import Optional
from game import KlondikeGame
from card import SUIT_SYMBOLS


class ConsoleUI:
    """Manages console rendering and interactive command loop for Klondike Solitaire."""

    def __init__(self, game: Optional[KlondikeGame] = None):
        self.game: KlondikeGame = game if game is not None else KlondikeGame()
        self.last_message: str = "Welcome to Klondike Solitaire! Enter '?' for help."
        self.last_message_is_error: bool = False

    def clear_screen(self) -> None:
        """Prints ANSI escape code to clear terminal screen."""
        sys.stdout.write("\033[2J\033[H")
        sys.stdout.flush()

    def render_board(self) -> None:
        """Renders board state strictly matching SRS Section 6.4 format."""
        g = self.game

        # Top row: Stock & Waste
        stock_str = f"Stock: {g.stock.size():<2}"
        waste_top = g.waste.peek()
        waste_str = f"Waste: {waste_top.ansi_str() if waste_top else '-- ':<4}"

        # Foundations F1 (Spades), F2 (Hearts), F3 (Clubs), F4 (Diamonds)
        f_strs = []
        for i, f in enumerate(g.foundations):
            top = f.peek_top()
            suit_sym = SUIT_SYMBOLS[f.suit]
            if top:
                f_strs.append(f"F{i+1}({suit_sym}): {top.ansi_str()}")
            else:
                f_strs.append(f"F{i+1}({suit_sym}): -- ")
        foundations_str = "Foundations: " + "  ".join(f_strs)

        # Header bar
        print("=" * 76)
        print(f" KLONDIKE SOLITAIRE (CSC200 DSA Edition) | Mode: Draw-{g.draw_mode}")
        print(f" Score: {g.score:<5}  Moves: {g.moves_count:<4}  Time: {g.elapsed_seconds}s  Undo: {g.undo_stack.size()}")
        print("=" * 76)
        print(f" {stock_str}    {waste_str}       {foundations_str}")
        print("-" * 76)

        # Tableau header columns: T1 .. T7
        tableau_cols = [t.to_list() for t in g.tableau]
        max_height = max((len(col) for col in tableau_cols), default=0)

        header_row = "  " + "     ".join(f"T{i+1}" for i in range(7))
        print(header_row)

        if max_height == 0:
            print("  (All tableau piles empty)")
        else:
            for row in range(max_height):
                row_items = []
                for col in range(7):
                    if row < len(tableau_cols[col]):
                        card = tableau_cols[col][row]
                        row_items.append(card.ansi_str())
                    else:
                        row_items.append("    ")
                print("  " + "   ".join(row_items))

        print("-" * 76)

        # Status / Feedback line
        if self.last_message:
            prefix = "\033[91m[!]\033[0m " if self.last_message_is_error else "\033[92m[*]\033[0m "
            print(f"{prefix}{self.last_message}")

        if g.is_game_won:
            print("\n\033[93m" + "*" * 76)
            print("  ★ ★ ★ CONGRATULATIONS! YOU HAVE WON THE GAME! ★ ★ ★")
            print(f"  Final Score: {g.score} | Total Moves: {g.moves_count} | Elapsed Time: {g.elapsed_seconds}s")
            print("*" * 76 + "\033[0m")

    def show_help(self) -> None:
        """Displays command syntax and pile notation (FR-9.4)."""
        help_text = """
===========================================================================
 KLONDIKE SOLITAIRE - COMMAND REFERENCE & PILE NOTATION (SRS Section 6.3)
===========================================================================
 PILE CODES:
   S         Stock draw pile
   W         Waste pile (drawn cards)
   T1 - T7   Tableau piles (1 to 7 from left to right)
   F1 - F4   Foundation piles:
             F1: Spades ♠    F2: Hearts ♥    F3: Clubs ♣    F4: Diamonds ♦

 COMMANDS:
   d                  Draw card(s) from stock (or recycle waste if stock is empty)
   m SRC DST [N]      Move N cards (default 1) from SRC to DST
                      Examples:
                        m T3 T5 2    (Move top 2 cards from T3 to T5)
                        m W T2       (Move top waste card to T2)
                        m T4 T1      (Move top card from T4 to T1)
                        m F1 T3      (Move card from Foundation 1 back to T3)
   f SRC              Send top card of SRC (W or T1..T7) to its matching foundation
                      Examples:
                        f W          (Send top waste card to its foundation)
                        f T4         (Send top card of T4 to its foundation)
   u                  Undo previous move (reverses card flip & score)
   r                  Redo previously undone move
   h                  Get an intelligent hint for the next best move
   n                  Start a new game (will ask for confirmation)
   ?                  Show this help screen
   q                  Quit the game (will ask for confirmation)
===========================================================================
"""
        print(help_text)
        input("Press Enter to return to the game...")

    def prompt_confirmation(self, action_name: str) -> bool:
        """Prompts player for confirmation before discarding game state (FR-9.5)."""
        choice = input(f"Are you sure you want to {action_name}? (y/N): ").strip().lower()
        return choice in ('y', 'yes')

    def run_command(self, raw_cmd: str) -> bool:
        """
        Parses and executes a player command.
        Returns True to continue loop, False to exit.
        Crash-proof per NFR-3.
        """
        parts = raw_cmd.strip().split()
        if not parts:
            self.last_message = ""
            return True

        cmd = parts[0].lower()

        try:
            # Command: Help
            if cmd in ('?', 'help'):
                self.show_help()
                self.last_message = "Help displayed."
                self.last_message_is_error = False
                return True

            # Command: Quit
            elif cmd in ('q', 'quit', 'exit'):
                if self.prompt_confirmation("quit"):
                    print("\nThanks for playing Klondike Solitaire!")
                    return False
                self.last_message = "Quit canceled."
                self.last_message_is_error = False
                return True

            # Command: New Game
            elif cmd in ('n', 'new'):
                if self.prompt_confirmation("start a new game"):
                    draw_choice = input("Select Draw Mode (1 or 3, default 1): ").strip()
                    mode = 3 if draw_choice == '3' else 1
                    self.game.new_game(draw_mode=mode)
                    self.last_message = f"New game started in Draw-{mode} mode."
                    self.last_message_is_error = False
                else:
                    self.last_message = "New game canceled."
                    self.last_message_is_error = False
                return True

            # Command: Draw
            elif cmd in ('d', 'draw'):
                res = self.game.draw()
                if res['ok']:
                    if res.get('action') == 'recycle':
                        self.last_message = f"Recycled {res['recycled']} cards from waste to stock."
                    else:
                        self.last_message = f"Drew {res['drawn']} card(s) to waste."
                    self.last_message_is_error = False
                else:
                    self.last_message = res['reason']
                    self.last_message_is_error = True
                return True

            # Command: Undo
            elif cmd in ('u', 'undo'):
                res = self.game.undo()
                if res['ok']:
                    self.last_message = f"Undone: {res['undone']}."
                    self.last_message_is_error = False
                else:
                    self.last_message = res['reason']
                    self.last_message_is_error = True
                return True

            # Command: Redo
            elif cmd in ('r', 'redo'):
                res = self.game.redo()
                if res['ok']:
                    self.last_message = f"Redone: {res['redone']}."
                    self.last_message_is_error = False
                else:
                    self.last_message = res['reason']
                    self.last_message_is_error = True
                return True

            # Command: Hint
            elif cmd in ('h', 'hint'):
                hint = self.game.get_hint()
                self.last_message = f"Hint: {hint['message']}"
                self.last_message_is_error = not hint.get('available', False)
                return True

            # Command: Move to Foundation (f SRC)
            elif cmd in ('f', 'foundation'):
                if len(parts) < 2:
                    self.last_message = "Usage: f <SRC>  (e.g. f W, f T3)"
                    self.last_message_is_error = True
                    return True
                src = parts[1].upper()
                res = self.game.move_to_foundation(src)
                if res['ok']:
                    self.last_message = f"Moved {res['card']} to Foundation {res['dest']} (+10 points)."
                    self.last_message_is_error = False
                else:
                    self.last_message = res['reason']
                    self.last_message_is_error = True
                return True

            # Command: Move (m SRC DST [N])
            elif cmd in ('m', 'move'):
                if len(parts) < 3:
                    self.last_message = "Usage: m <SRC> <DST> [N]  (e.g. m T3 T5 2, m W T1)"
                    self.last_message_is_error = True
                    return True

                src = parts[1].upper()
                dst = parts[2].upper()
                count = int(parts[3]) if len(parts) >= 4 and parts[3].isdigit() else 1

                # Subcase A: Waste to Tableau
                if src == 'W' and dst.startswith('T') and len(dst) == 2 and dst[1].isdigit():
                    t_idx = int(dst[1]) - 1
                    res = self.game.move_waste_to_tableau(t_idx)
                    if res['ok']:
                        self.last_message = f"Moved {res['card']} from Waste to {dst}."
                        self.last_message_is_error = False
                    else:
                        self.last_message = res['reason']
                        self.last_message_is_error = True
                    return True

                # Subcase B: Tableau to Tableau
                elif src.startswith('T') and dst.startswith('T') and len(src) == 2 and len(dst) == 2:
                    s_idx = int(src[1]) - 1
                    d_idx = int(dst[1]) - 1
                    res = self.game.move_tableau_to_tableau(s_idx, d_idx, count)
                    if res['ok']:
                        self.last_message = f"Moved {res['moved']} card(s) from {src} to {dst}."
                        self.last_message_is_error = False
                    else:
                        self.last_message = res['reason']
                        self.last_message_is_error = True
                    return True

                # Subcase C: Move to Foundation (m SRC Fx)
                elif dst.startswith('F') and len(dst) == 2:
                    res = self.game.move_to_foundation(src)
                    if res['ok']:
                        self.last_message = f"Moved {res['card']} from {src} to {res['dest']}."
                        self.last_message_is_error = False
                    else:
                        self.last_message = res['reason']
                        self.last_message_is_error = True
                    return True

                # Subcase D: Foundation to Tableau (m Fx Ty)
                elif src.startswith('F') and dst.startswith('T') and len(src) == 2 and len(dst) == 2:
                    f_idx = int(src[1]) - 1
                    t_idx = int(dst[1]) - 1
                    res = self.game.move_foundation_to_tableau(f_idx, t_idx)
                    if res['ok']:
                        self.last_message = f"Moved {res['card']} from {src} back to {dst}."
                        self.last_message_is_error = False
                    else:
                        self.last_message = res['reason']
                        self.last_message_is_error = True
                    return True

                else:
                    self.last_message = f"Invalid move syntax or unsupported pile combination: {src} -> {dst}."
                    self.last_message_is_error = True
                    return True

            else:
                self.last_message = f"Unknown command: '{cmd}'. Enter '?' for help."
                self.last_message_is_error = True
                return True

        except Exception as e:
            # Crash prevention (NFR-3)
            self.last_message = f"Error processing command: {str(e)}"
            self.last_message_is_error = True
            return True

    def start_loop(self) -> None:
        """Main game loop for the interactive console."""
        while True:
            self.render_board()
            try:
                cmd = input("\nEnter command (d, m, f, u, r, h, n, ?, q) > ").strip()
            except (KeyboardInterrupt, EOFError):
                print("\nExiting Klondike Solitaire. Goodbye!")
                break

            if not self.run_command(cmd):
                break
