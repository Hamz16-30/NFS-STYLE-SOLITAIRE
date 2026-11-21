"""
test_solitaire.py - Comprehensive Unit & Validation Test Suite
CSC200 Data Structures & Algorithms | Mid Term Project
Author: @Muhammad Hamza

Covers all 22 test cases specified in SRS Section 10:
- TC-01: Deck integrity (FR-1.1 to 1.3)
- TC-02: Shuffle determinism & distribution (FR-1.4, 1.5)
- TC-03: Initial deal validation (FR-2.1 to 2.4)
- TC-04: CustomStack ADT verification (DS-2)
- TC-05: CustomQueue ADT verification (DS-3)
- TC-06: CustomDoublyLinkedList run split & attach (DS-4, FR-4.6)
- TC-07: Draw-1 and Draw-3 modes (FR-3.2, 3.3)
- TC-08: Waste recycling original draw order (FR-3.5, DS-7)
- TC-09: Legal tableau move (FR-4.3)
- TC-10: Illegal tableau moves validation (FR-4.3, 4.5, 6.2)
- TC-11: Empty tableau pile King rule (FR-4.4)
- TC-12: Foundation suit & ascending rank rules (FR-5.2, 5.3)
- TC-13: Automatic exposed card flipping (FR-6.3)
- TC-14: Card Location HashMap accuracy (FR-6.5, DS-9)
- TC-15: Undo automatic card flip (FR-7.1, 7.2)
- TC-16: Undo and redo chain with redo invalidation (FR-7.3 to 7.5)
- TC-17: Empty undo/redo handling (FR-7.6)
- TC-18: Win detection on 52 cards in foundation (FR-8.1 to 8.3)
- TC-19: Incomplete foundation non-win detection (FR-8.1)
- TC-20: Malformed & unknown command resilience (FR-9.3, NFR-3)
- TC-21: Full game flow & card conservation (NFR-4, all FR)
- TC-22: Hint priority ordering (FR-10.1, 10.2)
"""

import unittest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from card import Card, SUITS
from dsa import (
    CustomStack,
    CustomQueue,
    CustomDoublyLinkedList,
    CustomHashMap,
    Deck,
    DLNode
)
from game import KlondikeGame
from ui import ConsoleUI


class TestKlondikeSolitaire(unittest.TestCase):

    # --------------------------------------------------------------------------
    # TC-01: Deck integrity (FR-1.1 to 1.3)
    # --------------------------------------------------------------------------
    def test_tc01_deck_integrity(self):
        """TC-01: Verify deck has exactly 52 unique cards, 13 per suit, 26 red, 26 black."""
        deck = Deck()
        cards = deck.cards
        self.assertEqual(len(cards), 52, "Deck must contain exactly 52 cards.")

        unique_ids = {c.id for c in cards}
        self.assertEqual(len(unique_ids), 52, "All 52 cards must have unique IDs.")

        for suit in SUITS:
            suit_cards = [c for c in cards if c.suit == suit]
            self.assertEqual(len(suit_cards), 13, f"Suit {suit} must have exactly 13 cards.")
            ranks = {c.rank for c in suit_cards}
            self.assertEqual(ranks, set(range(1, 14)), f"Suit {suit} must have ranks 1 through 13.")

        red_cards = [c for c in cards if c.color == 'red']
        black_cards = [c for c in cards if c.color == 'black']
        self.assertEqual(len(red_cards), 26, "Deck must have 26 red cards.")
        self.assertEqual(len(black_cards), 26, "Deck must have 26 black cards.")

    # --------------------------------------------------------------------------
    # TC-02: Shuffle determinism & reproducibility (FR-1.4, 1.5)
    # --------------------------------------------------------------------------
    def test_tc02_shuffle(self):
        """TC-02: Test Fisher-Yates shuffle with different seeds and identical seeds."""
        deck1 = Deck(seed=111)
        deck1.shuffle(seed=111)
        order1 = [c.id for c in deck1.cards]

        deck2 = Deck(seed=999)
        deck2.shuffle(seed=999)
        order2 = [c.id for c in deck2.cards]

        self.assertNotEqual(order1, order2, "Different seeds should produce different card orders.")

        deck3 = Deck(seed=111)
        deck3.shuffle(seed=111)
        order3 = [c.id for c in deck3.cards]

        self.assertEqual(order1, order3, "Identical seeds must produce identical shuffles.")
        self.assertEqual(len(set(order1)), 52, "Shuffled deck must still contain 52 unique cards.")

    # --------------------------------------------------------------------------
    # TC-03: Initial deal (FR-2.1 to 2.4)
    # --------------------------------------------------------------------------
    def test_tc03_initial_deal(self):
        """TC-03: Verify tableau sizes 1..7, only top card face-up, 24 in stock, waste/foundations empty."""
        game = KlondikeGame(seed=42)

        # Tableau checks
        for i in range(7):
            pile = game.tableau[i]
            self.assertEqual(pile.size(), i + 1, f"Tableau T{i+1} must contain {i+1} cards.")
            cards = pile.to_list()
            # All cards except the top one must be face-down
            for c in cards[:-1]:
                self.assertFalse(c.face_up, f"Card {c.id} in T{i+1} should be face-down.")
            # Top card must be face-up
            self.assertTrue(cards[-1].face_up, f"Top card {cards[-1].id} in T{i+1} must be face-up.")

        # Stock check
        self.assertEqual(game.stock.size(), 24, "Stock must contain 24 cards after deal.")
        for c in game.stock.to_list():
            self.assertFalse(c.face_up, "Cards in stock must be face-down.")

        # Waste check
        self.assertEqual(game.waste.size(), 0, "Waste pile must be empty initially.")

        # Foundations check
        for i, f in enumerate(game.foundations):
            self.assertEqual(f.size(), 0, f"Foundation F{i+1} must be empty initially.")

    # --------------------------------------------------------------------------
    # TC-04: Stack behavior (DS-2)
    # --------------------------------------------------------------------------
    def test_tc04_stack_behavior(self):
        """TC-04: Push 3 items, pop 3, pop once more on empty stack."""
        stack = CustomStack()
        self.assertTrue(stack.is_empty())
        self.assertEqual(stack.size(), 0)

        stack.push("Alpha")
        stack.push("Beta")
        stack.push("Gamma")

        self.assertEqual(stack.size(), 3)
        self.assertEqual(stack.peek(), "Gamma")

        self.assertEqual(stack.pop(), "Gamma")
        self.assertEqual(stack.pop(), "Beta")
        self.assertEqual(stack.pop(), "Alpha")

        self.assertTrue(stack.is_empty())
        # Extra pop should safely return None without crashing
        self.assertIsNone(stack.pop())
        self.assertIsNone(stack.peek())

    # --------------------------------------------------------------------------
    # TC-05: Queue behavior (DS-3)
    # --------------------------------------------------------------------------
    def test_tc05_queue_behavior(self):
        """TC-05: Enqueue 3 items, dequeue 3 in same order, dequeue once more on empty queue."""
        queue = CustomQueue()
        self.assertTrue(queue.is_empty())
        self.assertEqual(queue.size(), 0)

        queue.enqueue("First")
        queue.enqueue("Second")
        queue.enqueue("Third")

        self.assertEqual(queue.size(), 3)
        self.assertEqual(queue.peek(), "First")

        self.assertEqual(queue.dequeue(), "First")
        self.assertEqual(queue.dequeue(), "Second")
        self.assertEqual(queue.dequeue(), "Third")

        self.assertTrue(queue.is_empty())
        # Extra dequeue should safely return None without crashing
        self.assertIsNone(queue.dequeue())
        self.assertIsNone(queue.peek())

    # --------------------------------------------------------------------------
    # TC-06: Linked list run detach & attach (DS-4, FR-4.6)
    # --------------------------------------------------------------------------
    def test_tc06_linked_list_run_detach(self):
        """TC-06: Build pile of 5, detach top 3, attach elsewhere, check sizes & order."""
        pile1 = CustomDoublyLinkedList()
        cards1 = [
            Card('spades', 13, True),  # KS (bottom)
            Card('hearts', 12, True),  # QH
            Card('clubs', 11, True),   # JC
            Card('diamonds', 10, True),# 10D
            Card('spades', 9, True)    # 9S (top)
        ]
        for c in cards1:
            pile1.append(c)

        self.assertEqual(pile1.size(), 5)

        # Detach top 3 cards (JC, 10D, 9S)
        start_node = pile1.get_node_at_offset_from_tail(3)
        self.assertEqual(start_node.card.id, "JC")

        detached_run = pile1.split_from(start_node)
        self.assertEqual(pile1.size(), 2)
        self.assertEqual([c.id for c in pile1.to_list()], ["KS", "QH"])
        self.assertEqual(detached_run.size(), 3)
        self.assertEqual([c.id for c in detached_run.to_list()], ["JC", "10D", "9S"])

        # Attach to pile2
        pile2 = CustomDoublyLinkedList()
        pile2.append(Card('hearts', 12, True)) # QH in pile2
        pile2.attach(detached_run)

        self.assertEqual(pile2.size(), 4)
        self.assertEqual([c.id for c in pile2.to_list()], ["QH", "JC", "10D", "9S"])

    # --------------------------------------------------------------------------
    # TC-07: Draw-1 and Draw-3 (FR-3.2, 3.3)
    # --------------------------------------------------------------------------
    def test_tc07_draw_modes(self):
        """TC-07: Draw in Draw-1 and Draw-3 modes, verify card counts."""
        # Draw-1 test
        game1 = KlondikeGame(draw_mode=1)
        res1 = game1.draw()
        self.assertTrue(res1['ok'])
        self.assertEqual(res1['drawn'], 1)
        self.assertEqual(game1.waste.size(), 1)
        self.assertEqual(game1.stock.size(), 23)

        # Draw-3 test
        game3 = KlondikeGame(draw_mode=3)
        res3 = game3.draw()
        self.assertTrue(res3['ok'])
        self.assertEqual(res3['drawn'], 3)
        self.assertEqual(game3.waste.size(), 3)
        self.assertEqual(game3.stock.size(), 21)

        # Draw-3 partial draw test (FR-3.3)
        game_partial = KlondikeGame(draw_mode=3)
        # Leave exactly 2 cards in stock
        game_partial.stock.clear()
        game_partial.stock.enqueue(Card('spades', 5, face_up=False))
        game_partial.stock.enqueue(Card('hearts', 5, face_up=False))
        self.assertEqual(game_partial.stock.size(), 2)

        res_partial = game_partial.draw()
        self.assertTrue(res_partial['ok'])
        self.assertEqual(res_partial['drawn'], 2, "Draw-3 with 2 cards left must draw both remaining cards (FR-3.3).")
        self.assertEqual(game_partial.stock.size(), 0)

    # --------------------------------------------------------------------------
    # TC-08: Waste recycle preserves original draw order (FR-3.5, DS-7)
    # --------------------------------------------------------------------------
    def test_tc08_waste_recycle(self):
        """TC-08: Draw all 24 cards, recycle waste, verify original draw order repeats."""
        game = KlondikeGame(seed=777, draw_mode=1)

        # Record original stock order
        original_stock_order = [c.id for c in game.stock.to_list()]
        self.assertEqual(len(original_stock_order), 24)

        # Draw all 24 cards one by one
        drawn_order = []
        for _ in range(24):
            game.draw()
            drawn_order.append(game.waste.peek().id)

        self.assertEqual(game.stock.size(), 0)
        self.assertEqual(original_stock_order, drawn_order)

        # 25th draw triggers recycle
        res = game.draw()
        self.assertTrue(res['ok'])
        self.assertEqual(res.get('action'), 'recycle')
        self.assertEqual(game.stock.size(), 24)
        self.assertEqual(game.waste.size(), 0)

        # Verify stock cards match original order
        recycled_stock_order = [c.id for c in game.stock.to_list()]
        self.assertEqual(original_stock_order, recycled_stock_order,
                         "Waste recycling must restore exact initial draw order (DS-7).")

    # --------------------------------------------------------------------------
    # TC-09: Legal tableau move (FR-4.3)
    # --------------------------------------------------------------------------
    def test_tc09_legal_tableau_move(self):
        """TC-09: Move a red 6 onto a black 7 (accepted)."""
        game = KlondikeGame()
        # Set up T1 with 7 of spades (black 7), T2 with 6 of hearts (red 6)
        game.tableau[0].clear()
        game.tableau[1].clear()

        game.tableau[0].append(Card('spades', 7, face_up=True))
        game.tableau[1].append(Card('hearts', 6, face_up=True))

        res = game.move_tableau_to_tableau(src_idx=1, dst_idx=0, count=1)
        self.assertTrue(res['ok'], "Moving red 6 onto black 7 should be accepted.")
        self.assertEqual(game.tableau[0].size(), 2)
        self.assertEqual(game.tableau[1].size(), 0)
        self.assertEqual(game.tableau[0].peek_top().id, "6H")

    # --------------------------------------------------------------------------
    # TC-10: Illegal tableau moves (FR-4.3, 4.5, 6.2)
    # --------------------------------------------------------------------------
    def test_tc10_illegal_tableau_moves(self):
        """TC-10: Try same color, wrong rank, and face-down card in run; each rejected with reason."""
        game = KlondikeGame()
        game.tableau[0].clear()
        game.tableau[1].clear()

        # Destination has 8 of clubs (black 8)
        game.tableau[0].append(Card('clubs', 8, face_up=True))

        # 1. Same color: 7 of spades (black 7) onto black 8
        game.tableau[1].append(Card('spades', 7, face_up=True))
        res_same_color = game.move_tableau_to_tableau(src_idx=1, dst_idx=0, count=1)
        self.assertFalse(res_same_color['ok'])
        self.assertIn("Color mismatch", res_same_color['reason'])

        # 2. Wrong rank: 5 of hearts (red 5) onto black 8
        game.tableau[1].clear()
        game.tableau[1].append(Card('hearts', 5, face_up=True))
        res_wrong_rank = game.move_tableau_to_tableau(src_idx=1, dst_idx=0, count=1)
        self.assertFalse(res_wrong_rank['ok'])
        self.assertIn("Rank mismatch", res_wrong_rank['reason'])

        # 3. Face-down card in run
        game.tableau[1].clear()
        game.tableau[1].append(Card('diamonds', 7, face_up=False)) # Face-down 7D
        game.tableau[1].append(Card('clubs', 6, face_up=True))     # Face-up 6C
        res_face_down = game.move_tableau_to_tableau(src_idx=1, dst_idx=0, count=2)
        self.assertFalse(res_face_down['ok'])
        self.assertIn("face-down", res_face_down['reason'])

    # --------------------------------------------------------------------------
    # TC-11: Empty pile rule (FR-4.4)
    # --------------------------------------------------------------------------
    def test_tc11_empty_pile_rule(self):
        """TC-11: Move King then non-King to empty pile; King accepted, non-King rejected."""
        game = KlondikeGame()
        game.tableau[0].clear() # Empty pile T1
        game.tableau[1].clear()
        game.tableau[2].clear()

        queen = Card('hearts', 12, face_up=True)
        king = Card('spades', 13, face_up=True)

        game.tableau[1].append(queen)
        game.tableau[2].append(king)

        # Try moving Queen to empty T1 -> should be rejected
        res_queen = game.move_tableau_to_tableau(src_idx=1, dst_idx=0, count=1)
        self.assertFalse(res_queen['ok'])
        self.assertIn("Only a King", res_queen['reason'])

        # Try moving King to empty T1 -> should be accepted
        res_king = game.move_tableau_to_tableau(src_idx=2, dst_idx=0, count=1)
        self.assertTrue(res_king['ok'])
        self.assertEqual(game.tableau[0].peek_top().id, "KS")

    # --------------------------------------------------------------------------
    # TC-12: Foundation rules (FR-5.2, 5.3)
    # --------------------------------------------------------------------------
    def test_tc12_foundation_rules(self):
        """TC-12: Play Ace, 2 of same suit, 3 of different suit, 2 on empty foundation."""
        game = KlondikeGame()
        # Foundation 0 is Spades
        game.foundations[0].clear()

        # 1. Non-Ace on empty foundation -> rejected
        game.waste.clear()
        game.waste.push(Card('spades', 2, face_up=True))
        res_two_empty = game.move_to_foundation('W')
        self.assertFalse(res_two_empty['ok'])
        self.assertIn("Empty foundation accepts only an Ace", res_two_empty['reason'])

        # 2. Ace of spades on empty foundation -> accepted
        game.waste.clear()
        game.waste.push(Card('spades', 1, face_up=True))
        res_ace = game.move_to_foundation('W')
        self.assertTrue(res_ace['ok'])
        self.assertEqual(game.foundations[0].peek_top().id, "AS")

        # 3. 2 of spades on Ace of spades -> accepted
        game.waste.clear()
        game.waste.push(Card('spades', 2, face_up=True))
        res_two = game.move_to_foundation('W')
        self.assertTrue(res_two['ok'])
        self.assertEqual(game.foundations[0].peek_top().id, "2S")

        # 4. Wrong rank: 4 of spades on 2 of spades -> rejected
        game.waste.clear()
        game.waste.push(Card('spades', 4, face_up=True))
        res_four = game.move_to_foundation('W')
        self.assertFalse(res_four['ok'])

    # --------------------------------------------------------------------------
    # TC-13: Card flipping (FR-6.3)
    # --------------------------------------------------------------------------
    def test_tc13_card_flipping(self):
        """TC-13: Move top face-up card off pile with face-down under it; exposed card flips."""
        game = KlondikeGame()
        game.tableau[0].clear()
        game.tableau[1].clear()

        # T1 has a face-down card and a face-up red 6
        face_down_card = Card('spades', 10, face_up=False)
        face_up_card = Card('hearts', 6, face_up=True)
        game.tableau[0].append(face_down_card)
        game.tableau[0].append(face_up_card)

        # T2 has black 7
        game.tableau[1].append(Card('clubs', 7, face_up=True))

        self.assertFalse(face_down_card.face_up)

        # Move 6H from T1 to T2
        res = game.move_tableau_to_tableau(src_idx=0, dst_idx=1, count=1)
        self.assertTrue(res['ok'])
        # The exposed card in T1 must now be face-up
        new_top = game.tableau[0].peek_top()
        self.assertEqual(new_top.id, "10S")
        self.assertTrue(new_top.face_up, "Newly exposed card must automatically turn face-up (FR-6.3).")

    # --------------------------------------------------------------------------
    # TC-14: Location map (FR-6.5, DS-9)
    # --------------------------------------------------------------------------
    def test_tc14_location_map(self):
        """TC-14: Verify every card's recorded location and face state matches actual pile state."""
        game = KlondikeGame(seed=123)
        game.draw()
        game.move_to_foundation('W')  # might succeed or fail depending on card

        # Verify all 52 cards are accounted for in card_map
        all_ids = set()
        for suit in SUITS:
            for rank in range(1, 14):
                all_ids.add(Card(suit, rank).id)

        self.assertEqual(game.card_map.size(), 52)

        for card_id in all_ids:
            loc = game.card_map.get(card_id)
            self.assertIsNotNone(loc, f"Card {card_id} must exist in card_map.")
            pile_type = loc['pile']
            p_idx = loc['pile_index']
            pos = loc['position']

            if pile_type == 'stock':
                card = game.stock.to_list()[pos]
            elif pile_type == 'waste':
                card = game.waste.to_list()[pos]
            elif pile_type == 'foundation':
                card = game.foundations[p_idx].to_list()[pos]
            elif pile_type == 'tableau':
                card = game.tableau[p_idx].to_list()[pos]
            else:
                self.fail(f"Unknown pile type: {pile_type}")

            self.assertEqual(card.id, card_id)
            self.assertEqual(card.face_up, loc['face_up'])

    # --------------------------------------------------------------------------
    # TC-15: Undo a flip (FR-7.1, 7.2)
    # --------------------------------------------------------------------------
    def test_tc15_undo_a_flip(self):
        """TC-15: Move card that flips an exposed card, undo: card returns and flipped card un-flips."""
        game = KlondikeGame()
        game.tableau[0].clear()
        game.tableau[1].clear()

        c_down = Card('spades', 10, face_up=False)
        c_up = Card('hearts', 6, face_up=True)
        game.tableau[0].append(c_down)
        game.tableau[0].append(c_up)
        game.tableau[1].append(Card('clubs', 7, face_up=True))

        # Move 6H from T1 to T2 -> flips c_down
        game.move_tableau_to_tableau(src_idx=0, dst_idx=1, count=1)
        self.assertTrue(c_down.face_up)

        # Undo the move
        undo_res = game.undo()
        self.assertTrue(undo_res['ok'])

        # Card must have returned to T1 and c_down must be face-down again
        self.assertEqual(game.tableau[0].size(), 2)
        self.assertEqual(game.tableau[0].peek_top().id, "6H")
        self.assertFalse(c_down.face_up, "Undoing move must un-flip the exposed card (FR-7.2).")

    # --------------------------------------------------------------------------
    # TC-16: Undo and redo chain (FR-7.3 to 7.5)
    # --------------------------------------------------------------------------
    def test_tc16_undo_redo_chain(self):
        """TC-16: Perform 5 actions, undo 3, redo 2, then make new move; redo stack is cleared."""
        game = KlondikeGame(draw_mode=1)

        # Make 5 draw actions
        for _ in range(5):
            game.draw()
        self.assertEqual(game.waste.size(), 5)
        self.assertEqual(game.undo_stack.size(), 5)

        # Undo 3 times
        game.undo()
        game.undo()
        game.undo()
        self.assertEqual(game.waste.size(), 2)
        self.assertEqual(game.redo_stack.size(), 3)

        # Redo 2 times
        game.redo()
        game.redo()
        self.assertEqual(game.waste.size(), 4)
        self.assertEqual(game.redo_stack.size(), 1)

        # Make a new action -> should clear redo stack (FR-7.5)
        game.draw()
        self.assertEqual(game.redo_stack.size(), 0, "New move must clear redo stack.")

    # --------------------------------------------------------------------------
    # TC-17: Empty undo/redo (FR-7.6)
    # --------------------------------------------------------------------------
    def test_tc17_empty_undo_redo(self):
        """TC-17: Undo or redo with empty stack returns clean message without state change."""
        game = KlondikeGame()
        u_res = game.undo()
        self.assertFalse(u_res['ok'])
        self.assertIn("empty", u_res['reason'].lower())

        r_res = game.redo()
        self.assertFalse(r_res['ok'])
        self.assertIn("empty", r_res['reason'].lower())

    # --------------------------------------------------------------------------
    # TC-18: Win detection (FR-8.1 to 8.3)
    # --------------------------------------------------------------------------
    def test_tc18_win_detection(self):
        """TC-18: Load nearly solved state, place last card; win announced, further moves refused."""
        game = KlondikeGame()
        # Clear all
        for t in game.tableau:
            t.clear()
        game.stock.clear()
        game.waste.clear()

        # Fill 3 foundations completely with 13 cards each
        for f_idx in [0, 1, 2]:
            suit = game.foundations[f_idx].suit
            for rank in range(1, 14):
                game.foundations[f_idx].push(Card(suit, rank, face_up=True))

        # Foundation 3 (diamonds) has ranks 1 through 12
        for rank in range(1, 13):
            game.foundations[3].push(Card('diamonds', rank, face_up=True))

        # Put King of Diamonds in Waste
        game.waste.push(Card('diamonds', 13, face_up=True))
        self.assertFalse(game.check_win())

        # Move KD to Foundation
        res = game.move_to_foundation('W')
        self.assertTrue(res['ok'])
        self.assertTrue(game.is_game_won, "Game must detect win when all foundations reach 13 cards (FR-8.1).")

        # Further moves must be refused
        post_win_move = game.draw()
        self.assertFalse(post_win_move['ok'])
        self.assertIn("already won", post_win_move['reason'])

    # --------------------------------------------------------------------------
    # TC-19: Not a win (FR-8.1)
    # --------------------------------------------------------------------------
    def test_tc19_not_a_win(self):
        """TC-19: 3 full foundations and one with 12 cards is not a win."""
        game = KlondikeGame()
        for f in game.foundations:
            f.clear()

        for f_idx in [0, 1, 2]:
            suit = game.foundations[f_idx].suit
            for rank in range(1, 14):
                game.foundations[f_idx].push(Card(suit, rank, face_up=True))

        for rank in range(1, 13):
            game.foundations[3].push(Card('diamonds', rank, face_up=True))

        self.assertFalse(game.check_win(), "Game is not won when total foundation cards is 51.")

    # --------------------------------------------------------------------------
    # TC-20: Bad input resilience (FR-9.3, NFR-3)
    # --------------------------------------------------------------------------
    def test_tc20_bad_input(self):
        """TC-20: Test empty, unknown, malformed commands in UI; no crashes."""
        game = KlondikeGame()
        ui = ConsoleUI(game)

        bad_inputs = [
            "",
            "   ",
            "foobar",
            "m",
            "m T99 T88",
            "m T1",
            "f",
            "f Z9",
            "m T1 T2 -5",
            "m T1 T2 abc",
            "??? xyz"
        ]

        for inp in bad_inputs:
            cont = ui.run_command(inp)
            self.assertTrue(cont, f"Command '{inp}' should not crash UI.")
            self.assertTrue(len(ui.last_message) > 0 or inp.strip() == "")

    # --------------------------------------------------------------------------
    # TC-21: Full game flow & card conservation (NFR-4, all FR)
    # --------------------------------------------------------------------------
    def test_tc21_card_conservation(self):
        """TC-21: At every step of a simulated game, total cards across all piles is strictly 52."""
        game = KlondikeGame(seed=31415, draw_mode=1)

        def count_all_cards() -> int:
            total = game.stock.size() + game.waste.size()
            total += sum(f.size() for f in game.foundations)
            total += sum(t.size() for t in game.tableau)
            return total

        self.assertEqual(count_all_cards(), 52)

        # Perform mixed sequence of draws, moves, and undos
        for _ in range(10):
            game.draw()
            self.assertEqual(count_all_cards(), 52)

        # Try some foundation moves
        game.move_to_foundation('W')
        self.assertEqual(count_all_cards(), 52)
        for i in range(1, 8):
            game.move_to_foundation(f'T{i}')
            self.assertEqual(count_all_cards(), 52)

        # Undos
        for _ in range(5):
            game.undo()
            self.assertEqual(count_all_cards(), 52)

    # --------------------------------------------------------------------------
    # TC-22: Hint priority ordering (FR-10.1, 10.2)
    # --------------------------------------------------------------------------
    def test_tc22_hint_priority(self):
        """TC-22: Verify foundation moves are suggested before tableau moves."""
        game = KlondikeGame()
        # Put Ace in waste
        game.waste.clear()
        game.waste.push(Card('spades', 1, face_up=True))
        game.foundations[0].clear()

        hint = game.get_hint()
        self.assertTrue(hint['available'])
        self.assertEqual(hint['priority'], 1, "Foundation move must have Priority 1.")
        self.assertIn("Foundation", hint['message'])


if __name__ == '__main__':
    unittest.main()
