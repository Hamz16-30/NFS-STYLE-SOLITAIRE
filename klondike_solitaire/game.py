"""
game.py - Klondike Solitaire Core Engine & Logic
CSC200 Data Structures & Algorithms | Mid Term Project
Author: @Muhammad Hamza

Requirements Covered:
- FR-2.1 to 2.6: Game setup, tableau dealing (1..7), stock, waste, foundations, draw mode.
- FR-3.1 to 3.6: Stock queue FIFO, Draw-1/Draw-3, Waste recycle via temporary stack (DS-7).
- FR-4.1 to 4.6: Tableau linked list, run moving, descending opposite colors, King on empty.
- FR-5.1 to 5.5: Foundation stacks A->K by suit, waste/tableau to foundation, foundation to tableau.
- FR-6.1 to 6.5: Move validation, automatic exposed card flipping, card location HashMap (DS-5, DS-9).
- FR-7.1 to 7.6: Complete Undo/Redo stack with un-flipping and state restoration.
- FR-8.1 to 8.4: Win condition detection (52 cards in foundations), auto-complete bonus.
- FR-10.1 to 10.6: Hint system (priority ordered), Scoring system, elapsed time tracking.
"""

import time
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from typing import List, Optional, Dict, Any, Tuple
from card import Card, SUITS, SUIT_LETTERS
from dsa import (
    CustomStack,
    CustomQueue,
    CustomDoublyLinkedList,
    CustomHashMap,
    Deck,
    DLNode
)


class MoveRecord:
    """Stores full metadata for an action to enable exact undo/redo (DS-8, FR-7.1)."""
    def __init__(
        self,
        action_type: str,
        source: str,
        dest: str,
        cards: List[Card],
        card_flipped: Optional[Card] = None,
        draw_count: int = 0,
        score_delta: int = 0,
        recycle_count: int = 0
    ):
        self.action_type = action_type  # 'TABLEAU', 'TO_FOUNDATION', 'FROM_FOUNDATION', 'DRAW', 'RECYCLE'
        self.source = source
        self.dest = dest
        self.cards = list(cards)
        self.card_flipped = card_flipped  # Card that was auto-flipped face-up by this action
        self.draw_count = draw_count
        self.score_delta = score_delta
        self.recycle_count = recycle_count


class TableauPile:
    """Encapsulates a Tableau pile modeled as a CustomDoublyLinkedList (DS-4, FR-4.1)."""
    def __init__(self, index: int):
        self.index: int = index  # 0 to 6 (corresponds to T1 to T7)
        self.cards: CustomDoublyLinkedList = CustomDoublyLinkedList()

    def append(self, card: Card) -> DLNode:
        return self.cards.append(card)

    def peek_top(self) -> Optional[Card]:
        return self.cards.peek_tail()

    def pop_top(self) -> Optional[Card]:
        return self.cards.pop_tail()

    def size(self) -> int:
        return self.cards.size()

    def is_empty(self) -> bool:
        return self.cards.is_empty()

    def to_list(self) -> List[Card]:
        return self.cards.to_list()

    def clear(self) -> None:
        self.cards.clear()


class FoundationPile:
    """Encapsulates a Foundation pile modeled as a CustomStack (DS-2, FR-5.1)."""
    def __init__(self, index: int, suit: str):
        self.index: int = index  # 0 to 3 (F1 to F4)
        self.suit: str = suit    # 'spades', 'hearts', 'clubs', 'diamonds'
        self.cards: CustomStack = CustomStack()

    def push(self, card: Card) -> None:
        self.cards.push(card)

    def pop(self) -> Optional[Card]:
        return self.cards.pop()

    def peek_top(self) -> Optional[Card]:
        return self.cards.peek()

    def size(self) -> int:
        return self.cards.size()

    def is_empty(self) -> bool:
        return self.cards.is_empty()

    def to_list(self) -> List[Card]:
        return self.cards.to_list()

    def clear(self) -> None:
        self.cards.clear()


class KlondikeGame:
    """
    Central Klondike Solitaire Game Engine.
    Coordinates all data structures, move validation, actions, undo/redo, and win detection.
    """
    def __init__(self, seed: Optional[int] = None, draw_mode: int = 1):
        self.draw_mode: int = draw_mode  # 1 or 3 (FR-2.5)
        self.seed: Optional[int] = seed
        self.score: int = 0
        self.moves_count: int = 0
        self.start_time: float = time.time()
        self.is_game_won: bool = False

        # Required Data Structures
        self.deck: Deck = Deck(seed=seed)
        self.stock: CustomQueue = CustomQueue()          # DS-3: FIFO queue
        self.waste: CustomStack = CustomStack()          # DS-2: LIFO stack
        self.foundations: List[FoundationPile] = [       # DS-2: 4 LIFO stacks
            FoundationPile(0, 'spades'),
            FoundationPile(1, 'hearts'),
            FoundationPile(2, 'clubs'),
            FoundationPile(3, 'diamonds')
        ]
        self.tableau: List[TableauPile] = [              # DS-4: 7 DoublyLinkedLists
            TableauPile(i) for i in range(7)
        ]
        self.undo_stack: CustomStack = CustomStack()     # DS-2: LIFO stack of MoveRecord
        self.redo_stack: CustomStack = CustomStack()     # DS-2: LIFO stack of MoveRecord
        self.card_map: CustomHashMap = CustomHashMap(128) # DS-5: HashMap card_id -> location record

        self.new_game(seed=seed, draw_mode=draw_mode)

    # ==========================================================================
    # FR-2.x: Game Setup & Initialization
    # ==========================================================================
    def new_game(self, seed: Optional[int] = None, draw_mode: Optional[int] = None) -> None:
        """Starts a new game, dealing tableau, stock, and resetting state (FR-2.1 - 2.6)."""
        if seed is not None:
            self.seed = seed
        if draw_mode is not None:
            self.draw_mode = draw_mode

        self.score = 0
        self.moves_count = 0
        self.start_time = time.time()
        self.is_game_won = False

        # Clear all structures
        self.stock.clear()
        self.waste.clear()
        for f in self.foundations:
            f.clear()
        for t in self.tableau:
            t.clear()
        self.undo_stack.clear()
        self.redo_stack.clear()
        self.card_map.clear()

        # Create and shuffle 52 cards (FR-1.3, FR-1.4, FR-1.5)
        self.deck.reset()
        self.deck.shuffle(seed=self.seed)

        # Deal 7 tableau piles: pile i gets i+1 cards (1 to 7) (FR-2.1)
        for i in range(7):
            for j in range(i + 1):
                card = self.deck.deal_one()
                if card is None:
                    break
                # Only the top (last) card of each pile is face-up (FR-2.2)
                card.face_up = (j == i)
                self.tableau[i].append(card)

        # Place remaining 24 cards in the stock queue face-down in dealt order (FR-2.3)
        while not self.deck.is_empty():
            card = self.deck.deal_one()
            if card:
                card.face_up = False
                self.stock.enqueue(card)

        # Update card location map (FR-6.5, DS-5)
        self.update_card_map()

    # ==========================================================================
    # FR-6.5, DS-5, DS-9: Card Location HashMap Management
    # ==========================================================================
    def update_card_map(self) -> None:
        """
        Updates the CustomHashMap storing location and face state for every card.
        Key: card.id (e.g. 'AS', '10H')
        Value: dict {'pile': str, 'pile_index': int, 'position': int, 'face_up': bool}
        """
        # Stock
        for pos, card in enumerate(self.stock.to_list()):
            self.card_map.put(card.id, {
                'pile': 'stock', 'pile_index': 0, 'position': pos, 'face_up': card.face_up
            })
        # Waste
        for pos, card in enumerate(self.waste.to_list()):
            self.card_map.put(card.id, {
                'pile': 'waste', 'pile_index': 0, 'position': pos, 'face_up': card.face_up
            })
        # Foundations
        for f_idx, f in enumerate(self.foundations):
            for pos, card in enumerate(f.to_list()):
                self.card_map.put(card.id, {
                    'pile': 'foundation', 'pile_index': f_idx, 'position': pos, 'face_up': card.face_up
                })
        # Tableau
        for t_idx, t in enumerate(self.tableau):
            for pos, card in enumerate(t.to_list()):
                self.card_map.put(card.id, {
                    'pile': 'tableau', 'pile_index': t_idx, 'position': pos, 'face_up': card.face_up
                })

    # ==========================================================================
    # FR-3.x: Stock & Waste Operations
    # ==========================================================================
    def draw(self) -> Dict[str, Any]:
        """
        Draws 1 or up to 3 cards from stock queue to waste stack.
        If stock is empty, recycles waste into stock using temporary stack (DS-7).
        """
        if self.is_game_won:
            return {'ok': False, 'reason': 'Game is already won.'}

        # Case 1: Stock has cards
        if not self.stock.is_empty():
            drawn_cards: List[Card] = []
            count = min(self.draw_mode, self.stock.size())
            for _ in range(count):
                card = self.stock.dequeue()
                if card:
                    card.face_up = True
                    self.waste.push(card)
                    drawn_cards.append(card)

            # Record action in undo stack (FR-7.1)
            record = MoveRecord(
                action_type='DRAW',
                source='stock',
                dest='waste',
                cards=drawn_cards,
                draw_count=len(drawn_cards),
                score_delta=0
            )
            self.undo_stack.push(record)
            self.redo_stack.clear()
            self.moves_count += 1
            self.update_card_map()
            return {'ok': True, 'drawn': len(drawn_cards), 'action': 'draw'}

        # Case 2: Stock is empty, but waste has cards -> Recycle (FR-3.5, DS-7)
        elif not self.waste.is_empty():
            # DS-7: Empty waste through temporary stack to restore original FIFO queue draw order
            temp_stack = CustomStack()
            recycle_cards: List[Card] = []

            # 1. Pop all cards from waste into temp stack
            while not self.waste.is_empty():
                c = self.waste.pop()
                if c:
                    temp_stack.push(c)

            # 2. Pop all cards from temp stack and enqueue into stock
            while not temp_stack.is_empty():
                c = temp_stack.pop()
                if c:
                    c.face_up = False
                    self.stock.enqueue(c)
                    recycle_cards.append(c)

            # Scoring: default -100 for waste recycle in draw-1
            score_delta = -100 if self.draw_mode == 1 else -20
            self.score = max(0, self.score + score_delta)

            record = MoveRecord(
                action_type='RECYCLE',
                source='waste',
                dest='stock',
                cards=recycle_cards,
                recycle_count=len(recycle_cards),
                score_delta=score_delta
            )
            self.undo_stack.push(record)
            self.redo_stack.clear()
            self.moves_count += 1
            self.update_card_map()
            return {'ok': True, 'recycled': len(recycle_cards), 'action': 'recycle'}

        # Case 3: Both stock and waste are empty (FR-3.6)
        else:
            return {'ok': False, 'reason': 'Stock and waste are both empty; nothing to draw.'}

    # ==========================================================================
    # FR-4.x & FR-6.x: Tableau to Tableau Moves
    # ==========================================================================
    def move_tableau_to_tableau(self, src_idx: int, dst_idx: int, count: int = 1) -> Dict[str, Any]:
        """
        Moves `count` cards from tableau[src_idx] to tableau[dst_idx].
        Validates descending rank and alternating color (FR-4.3), King to empty pile (FR-4.4).
        """
        if self.is_game_won:
            return {'ok': False, 'reason': 'Game is already won.'}

        if not (0 <= src_idx < 7) or not (0 <= dst_idx < 7):
            return {'ok': False, 'reason': f'Invalid tableau index. Expected 0..6 (T1..T7).'}

        if src_idx == dst_idx:
            return {'ok': False, 'reason': 'Source and destination tableau piles cannot be the same.'}

        src_pile = self.tableau[src_idx]
        dst_pile = self.tableau[dst_idx]

        if src_pile.is_empty():
            return {'ok': False, 'reason': f'Tableau pile T{src_idx+1} is empty.'}

        if count < 1 or count > src_pile.size():
            return {'ok': False, 'reason': f'Cannot move {count} cards; T{src_idx+1} only has {src_pile.size()} cards.'}

        # Find the start node of the run (count cards from the tail)
        start_node = src_pile.cards.get_node_at_offset_from_tail(count)
        if start_node is None:
            return {'ok': False, 'reason': f'Could not locate run of {count} cards in T{src_idx+1}.'}

        # Check all cards in run are face-up (FR-4.5)
        curr = start_node
        while curr is not None:
            if not curr.card.face_up:
                return {'ok': False, 'reason': 'Cannot move a run containing face-down cards.'}
            curr = curr.next

        base_card = start_node.card
        dst_top = dst_pile.peek_top()

        # Validation logic (FR-4.3, FR-4.4)
        if dst_top is None:
            # Empty destination requires a King (rank 13)
            if base_card.rank != 13:
                return {'ok': False, 'reason': f'Only a King can be placed on an empty tableau pile (tried {base_card.short_label}).'}
        else:
            # Non-empty destination requires rank = dst_top.rank - 1 and opposite color
            if base_card.color == dst_top.color:
                return {'ok': False, 'reason': f'Color mismatch: cannot place {base_card.color} {base_card.short_label} on {dst_top.color} {dst_top.short_label}. Must alternate colors.'}
            if base_card.rank != dst_top.rank - 1:
                return {'ok': False, 'reason': f'Rank mismatch: {base_card.short_label} is not one rank lower than {dst_top.short_label}.'}

        # Execution: Split run from source DLL and attach to destination DLL (O(1))
        detached_run = src_pile.cards.split_from(start_node)
        moved_cards = detached_run.to_list()
        dst_pile.cards.attach(detached_run)

        # Automatic card flipping for newly exposed card (FR-6.3)
        flipped_card: Optional[Card] = None
        new_top = src_pile.peek_top()
        score_delta = 0
        if new_top is not None and not new_top.face_up:
            new_top.face_up = True
            flipped_card = new_top
            score_delta += 5  # Turn over a tableau card: +5

        self.score += score_delta
        record = MoveRecord(
            action_type='TABLEAU',
            source=f'T{src_idx+1}',
            dest=f'T{dst_idx+1}',
            cards=moved_cards,
            card_flipped=flipped_card,
            score_delta=score_delta
        )
        self.undo_stack.push(record)
        self.redo_stack.clear()
        self.moves_count += 1
        self.update_card_map()
        self.check_win()
        return {'ok': True, 'moved': len(moved_cards), 'action': 'move_tableau'}

    # ==========================================================================
    # FR-5.x: Foundation Moves
    # ==========================================================================
    def move_to_foundation(self, source_code: str) -> Dict[str, Any]:
        """
        Moves the top card of source ('W' or 'T1'..'T7') to its appropriate foundation pile.
        Validation: Ace on empty, next rank of same suit on non-empty (FR-5.2, FR-5.3).
        """
        if self.is_game_won:
            return {'ok': False, 'reason': 'Game is already won.'}

        source_code = source_code.upper().strip()
        card_to_move: Optional[Card] = None
        src_pile_obj: Any = None
        is_tableau = False
        t_idx = -1

        if source_code == 'W':
            if self.waste.is_empty():
                return {'ok': False, 'reason': 'Waste pile is empty.'}
            card_to_move = self.waste.peek()
            src_pile_obj = self.waste
        elif source_code.startswith('T') and len(source_code) == 2 and source_code[1].isdigit():
            t_idx = int(source_code[1]) - 1
            if not (0 <= t_idx < 7):
                return {'ok': False, 'reason': f'Invalid tableau pile: {source_code}.'}
            src_pile_obj = self.tableau[t_idx]
            if src_pile_obj.is_empty():
                return {'ok': False, 'reason': f'Tableau pile {source_code} is empty.'}
            card_to_move = src_pile_obj.peek_top()
            is_tableau = True
        else:
            return {'ok': False, 'reason': f'Invalid source: {source_code}. Expected W or T1..T7.'}

        if card_to_move is None or not card_to_move.face_up:
            return {'ok': False, 'reason': 'No visible card available to move.'}

        # Find foundation matching card's suit
        suit_idx = SUITS.index(card_to_move.suit)
        foundation = self.foundations[suit_idx]
        f_top = foundation.peek_top()

        # Validation (FR-5.2, FR-5.3)
        if f_top is None:
            if card_to_move.rank != 1:
                return {'ok': False, 'reason': f'Empty foundation accepts only an Ace (tried {card_to_move.short_label}).'}
        else:
            if card_to_move.suit != f_top.suit:
                return {'ok': False, 'reason': f'Suit mismatch: cannot place {card_to_move.suit} on {f_top.suit}.'}
            if card_to_move.rank != f_top.rank + 1:
                return {'ok': False, 'reason': f'Rank mismatch: {card_to_move.short_label} must be exactly one rank higher than {f_top.short_label}.'}

        # Execute move
        if is_tableau:
            popped_card = src_pile_obj.pop_top()
        else:
            popped_card = src_pile_obj.pop()

        foundation.push(popped_card)

        # Check auto flip on tableau (FR-6.3)
        flipped_card: Optional[Card] = None
        score_delta = 10  # Waste or tableau to foundation: +10
        if is_tableau:
            new_top = src_pile_obj.peek_top()
            if new_top is not None and not new_top.face_up:
                new_top.face_up = True
                flipped_card = new_top
                score_delta += 5  # Turn over tableau card: +5

        self.score += score_delta
        record = MoveRecord(
            action_type='TO_FOUNDATION',
            source=source_code,
            dest=f'F{suit_idx+1}',
            cards=[popped_card],
            card_flipped=flipped_card,
            score_delta=score_delta
        )
        self.undo_stack.push(record)
        self.redo_stack.clear()
        self.moves_count += 1
        self.update_card_map()
        self.check_win()
        return {'ok': True, 'card': popped_card.short_label, 'dest': f'F{suit_idx+1}', 'action': 'to_foundation'}

    def move_foundation_to_tableau(self, f_idx: int, t_idx: int) -> Dict[str, Any]:
        """
        Moves the top card of foundation[f_idx] back to tableau[t_idx] (FR-5.5).
        """
        if self.is_game_won:
            return {'ok': False, 'reason': 'Game is already won.'}

        if not (0 <= f_idx < 4) or not (0 <= t_idx < 7):
            return {'ok': False, 'reason': 'Invalid foundation or tableau index.'}

        foundation = self.foundations[f_idx]
        tableau_pile = self.tableau[t_idx]

        if foundation.is_empty():
            return {'ok': False, 'reason': f'Foundation F{f_idx+1} is empty.'}

        card = foundation.peek_top()
        t_top = tableau_pile.peek_top()

        if t_top is None:
            if card.rank != 13:
                return {'ok': False, 'reason': f'Only a King can be placed on an empty tableau pile.'}
        else:
            if card.color == t_top.color or card.rank != t_top.rank - 1:
                return {'ok': False, 'reason': f'Cannot place {card.short_label} on {t_top.short_label}.'}

        # Execute
        popped = foundation.pop()
        tableau_pile.append(popped)

        score_delta = -15  # Foundation to tableau: -15
        self.score = max(0, self.score + score_delta)

        record = MoveRecord(
            action_type='FROM_FOUNDATION',
            source=f'F{f_idx+1}',
            dest=f'T{t_idx+1}',
            cards=[popped],
            score_delta=score_delta
        )
        self.undo_stack.push(record)
        self.redo_stack.clear()
        self.moves_count += 1
        self.update_card_map()
        return {'ok': True, 'card': popped.short_label, 'action': 'from_foundation'}

    def move_waste_to_tableau(self, dst_idx: int) -> Dict[str, Any]:
        """Moves the top card of waste stack to tableau[dst_idx] (FR-3.4, FR-4.3)."""
        if self.is_game_won:
            return {'ok': False, 'reason': 'Game is already won.'}

        if not (0 <= dst_idx < 7):
            return {'ok': False, 'reason': 'Invalid tableau pile index.'}

        if self.waste.is_empty():
            return {'ok': False, 'reason': 'Waste pile is empty.'}

        card = self.waste.peek()
        dst_pile = self.tableau[dst_idx]
        dst_top = dst_pile.peek_top()

        if dst_top is None:
            if card.rank != 13:
                return {'ok': False, 'reason': f'Only a King can be placed on an empty tableau pile (tried {card.short_label}).'}
        else:
            if card.color == dst_top.color:
                return {'ok': False, 'reason': f'Color mismatch: cannot place {card.color} {card.short_label} on {dst_top.color} {dst_top.short_label}.'}
            if card.rank != dst_top.rank - 1:
                return {'ok': False, 'reason': f'Rank mismatch: {card.short_label} must be one rank lower than {dst_top.short_label}.'}

        popped = self.waste.pop()
        dst_pile.append(popped)

        score_delta = 5  # Waste to tableau: +5
        self.score += score_delta

        record = MoveRecord(
            action_type='WASTE_TO_TABLEAU',
            source='W',
            dest=f'T{dst_idx+1}',
            cards=[popped],
            score_delta=score_delta
        )
        self.undo_stack.push(record)
        self.redo_stack.clear()
        self.moves_count += 1
        self.update_card_map()
        self.check_win()
        return {'ok': True, 'card': popped.short_label, 'dest': f'T{dst_idx+1}', 'action': 'waste_to_tableau'}

    # ==========================================================================
    # FR-7.x: Undo and Redo System
    # ==========================================================================
    def undo(self) -> Dict[str, Any]:
        """Restores exact previous state including un-flipping cards (FR-7.1, FR-7.2)."""
        if self.undo_stack.is_empty():
            return {'ok': False, 'reason': 'Undo stack is empty; nothing to undo.'}

        record: MoveRecord = self.undo_stack.pop()

        # Reverse score
        self.score = max(0, self.score - record.score_delta)

        # Un-flip card if one was flipped during this action (FR-7.2)
        if record.card_flipped is not None:
            record.card_flipped.face_up = False

        # Reverse action
        if record.action_type == 'TABLEAU':
            # Run moved from src to dest. Detach run from dest and attach back to src.
            src_idx = int(record.source[1]) - 1
            dst_idx = int(record.dest[1]) - 1
            dst_pile = self.tableau[dst_idx]
            src_pile = self.tableau[src_idx]

            count = len(record.cards)
            start_node = dst_pile.cards.get_node_at_offset_from_tail(count)
            detached = dst_pile.cards.split_from(start_node)
            src_pile.cards.attach(detached)

        elif record.action_type == 'TO_FOUNDATION':
            # Card moved to foundation. Pop from foundation and push back to source.
            f_idx = int(record.dest[1]) - 1
            card = self.foundations[f_idx].pop()
            if record.source == 'W':
                self.waste.push(card)
            else:
                t_idx = int(record.source[1]) - 1
                self.tableau[t_idx].append(card)

        elif record.action_type == 'WASTE_TO_TABLEAU':
            dst_idx = int(record.dest[1]) - 1
            card = self.tableau[dst_idx].pop_top()
            self.waste.push(card)

        elif record.action_type == 'FROM_FOUNDATION':
            t_idx = int(record.dest[1]) - 1
            f_idx = int(record.source[1]) - 1
            card = self.tableau[t_idx].pop_top()
            self.foundations[f_idx].push(card)

        elif record.action_type == 'DRAW':
            # Cards were drawn from stock to waste. Pop from waste, flip face-down, put back to stock.
            # To restore stock queue: the drawn cards were at the FRONT of stock.
            # Pop each card from waste and reconstruct stock queue with these cards at front.
            restored_cards = []
            for _ in range(record.draw_count):
                c = self.waste.pop()
                if c:
                    c.face_up = False
                    restored_cards.append(c)

            # Reconstruct queue: restored_cards in reverse of pop order (so original head is first)
            new_stock = CustomQueue()
            for c in reversed(restored_cards):
                new_stock.enqueue(c)
            while not self.stock.is_empty():
                new_stock.enqueue(self.stock.dequeue())
            self.stock = new_stock

        elif record.action_type == 'RECYCLE':
            # Waste was recycled into stock. Move cards back from stock to waste face-up.
            # Clear stock and push all cards back to waste in reverse order
            recycled_cards = []
            while not self.stock.is_empty():
                c = self.stock.dequeue()
                if c:
                    recycled_cards.append(c)
            for c in recycled_cards:
                c.face_up = True
                self.waste.push(c)

        self.redo_stack.push(record)
        self.update_card_map()
        return {'ok': True, 'action': 'undo', 'undone': record.action_type}

    def redo(self) -> Dict[str, Any]:
        """Re-applies the most recently undone action (FR-7.3, FR-7.4)."""
        if self.redo_stack.is_empty():
            return {'ok': False, 'reason': 'Redo stack is empty; nothing to redo.'}

        record: MoveRecord = self.redo_stack.pop()

        # Re-apply action
        if record.action_type == 'TABLEAU':
            src_idx = int(record.source[1]) - 1
            dst_idx = int(record.dest[1]) - 1
            count = len(record.cards)
            start_node = self.tableau[src_idx].cards.get_node_at_offset_from_tail(count)
            detached = self.tableau[src_idx].cards.split_from(start_node)
            self.tableau[dst_idx].cards.attach(detached)
            if record.card_flipped is not None:
                record.card_flipped.face_up = True

        elif record.action_type == 'TO_FOUNDATION':
            f_idx = int(record.dest[1]) - 1
            if record.source == 'W':
                card = self.waste.pop()
            else:
                t_idx = int(record.source[1]) - 1
                card = self.tableau[t_idx].pop_top()
            self.foundations[f_idx].push(card)
            if record.card_flipped is not None:
                record.card_flipped.face_up = True

        elif record.action_type == 'WASTE_TO_TABLEAU':
            dst_idx = int(record.dest[1]) - 1
            card = self.waste.pop()
            self.tableau[dst_idx].append(card)

        elif record.action_type == 'FROM_FOUNDATION':
            f_idx = int(record.source[1]) - 1
            t_idx = int(record.dest[1]) - 1
            card = self.foundations[f_idx].pop()
            self.tableau[t_idx].append(card)

        elif record.action_type == 'DRAW':
            for _ in range(record.draw_count):
                c = self.stock.dequeue()
                if c:
                    c.face_up = True
                    self.waste.push(c)

        elif record.action_type == 'RECYCLE':
            temp_stack = CustomStack()
            while not self.waste.is_empty():
                c = self.waste.pop()
                if c:
                    temp_stack.push(c)
            while not temp_stack.is_empty():
                c = temp_stack.pop()
                if c:
                    c.face_up = False
                    self.stock.enqueue(c)

        self.score += record.score_delta
        self.undo_stack.push(record)
        self.update_card_map()
        self.check_win()
        return {'ok': True, 'action': 'redo', 'redone': record.action_type}

    # ==========================================================================
    # FR-8.x: Win Detection & Auto-Complete
    # ==========================================================================
    def check_win(self) -> bool:
        """Checks if all 4 foundations hold 13 cards each (52 total) (FR-8.1)."""
        won = all(f.size() == 13 for f in self.foundations)
        if won and not self.is_game_won:
            self.is_game_won = True
        return self.is_game_won

    def can_auto_complete(self) -> bool:
        """Checks if all tableau cards are face-up and stock/waste are empty (FR-8.4)."""
        if not self.stock.is_empty() or not self.waste.is_empty():
            return False
        for t in self.tableau:
            for card in t.to_list():
                if not card.face_up:
                    return False
        return True

    def auto_complete(self) -> int:
        """Repeatedly moves cards to foundation until win is reached or no move exists."""
        if not self.can_auto_complete():
            return 0

        moves_made = 0
        progress = True
        while progress and not self.check_win():
            progress = False
            for t_idx in range(7):
                if not self.tableau[t_idx].is_empty():
                    res = self.move_to_foundation(f'T{t_idx+1}')
                    if res['ok']:
                        moves_made += 1
                        progress = True
                        break
        return moves_made

    # ==========================================================================
    # FR-10.x: Hint System (Priority Ordered)
    # ==========================================================================
    def get_hint(self) -> Dict[str, Any]:
        """
        Suggests one legal move according to priority order (FR-10.1, FR-10.2):
          1. Foundation move (waste or tableau to foundation)
          2. Tableau move that reveals a face-down card
          3. Waste to tableau
          4. Tableau-to-tableau run move
          5. Draw from stock
        """
        if self.is_game_won:
            return {'available': False, 'message': 'Game is already won!'}

        # Priority 1: Move to foundation
        # Check waste top
        if not self.waste.is_empty():
            w_top = self.waste.peek()
            f_idx = SUITS.index(w_top.suit)
            f_top = self.foundations[f_idx].peek_top()
            if (f_top is None and w_top.rank == 1) or (f_top and w_top.rank == f_top.rank + 1):
                return {
                    'available': True,
                    'priority': 1,
                    'message': f'Move {w_top.short_label} from Waste to Foundation F{f_idx+1}',
                    'cmd': 'f W'
                }

        # Check tableau tops to foundation
        for t_idx in range(7):
            t_top = self.tableau[t_idx].peek_top()
            if t_top and t_top.face_up:
                f_idx = SUITS.index(t_top.suit)
                f_top = self.foundations[f_idx].peek_top()
                if (f_top is None and t_top.rank == 1) or (f_top and t_top.rank == f_top.rank + 1):
                    return {
                        'available': True,
                        'priority': 1,
                        'message': f'Move {t_top.short_label} from T{t_idx+1} to Foundation F{f_idx+1}',
                        'cmd': f'f T{t_idx+1}'
                    }

        # Priority 2: Tableau move that reveals a face-down card
        for src_idx in range(7):
            src_pile = self.tableau[src_idx]
            cards = src_pile.to_list()
            # Find face-up run length
            face_up_cards = [c for c in cards if c.face_up]
            face_down_cards = [c for c in cards if not c.face_up]

            if face_down_cards and face_up_cards:
                # Moving all face_up_cards exposes the face-down card underneath!
                base_card = face_up_cards[0]
                run_len = len(face_up_cards)
                for dst_idx in range(7):
                    if dst_idx == src_idx:
                        continue
                    dst_pile = self.tableau[dst_idx]
                    dst_top = dst_pile.peek_top()
                    if dst_top is None:
                        if base_card.rank == 13:
                            return {
                                'available': True,
                                'priority': 2,
                                'message': f'Move run of {run_len} starting with {base_card.short_label} from T{src_idx+1} to empty T{dst_idx+1} to reveal a card',
                                'cmd': f'm T{src_idx+1} T{dst_idx+1} {run_len}'
                            }
                    else:
                        if base_card.color != dst_top.color and base_card.rank == dst_top.rank - 1:
                            return {
                                'available': True,
                                'priority': 2,
                                'message': f'Move run of {run_len} starting with {base_card.short_label} from T{src_idx+1} onto {dst_top.short_label} in T{dst_idx+1} to reveal a card',
                                'cmd': f'm T{src_idx+1} T{dst_idx+1} {run_len}'
                            }

        # Priority 3: Waste to tableau
        if not self.waste.is_empty():
            w_card = self.waste.peek()
            for dst_idx in range(7):
                dst_top = self.tableau[dst_idx].peek_top()
                if dst_top is None:
                    if w_card.rank == 13:
                        return {
                            'available': True,
                            'priority': 3,
                            'message': f'Move {w_card.short_label} from Waste to empty T{dst_idx+1}',
                            'cmd': f'm W T{dst_idx+1}'
                        }
                else:
                    if w_card.color != dst_top.color and w_card.rank == dst_top.rank - 1:
                        return {
                            'available': True,
                            'priority': 3,
                            'message': f'Move {w_card.short_label} from Waste onto {dst_top.short_label} in T{dst_idx+1}',
                            'cmd': f'm W T{dst_idx+1}'
                        }

        # Priority 4: Other legal tableau-to-tableau moves (not moving King to empty if already at base)
        for src_idx in range(7):
            src_pile = self.tableau[src_idx]
            cards = src_pile.to_list()
            face_up_indices = [i for i, c in enumerate(cards) if c.face_up]
            for start_idx in face_up_indices:
                base_card = cards[start_idx]
                run_len = len(cards) - start_idx
                # Avoid moving a King that's already the bottom-most card to another empty pile
                if start_idx == 0 and base_card.rank == 13:
                    continue

                for dst_idx in range(7):
                    if dst_idx == src_idx:
                        continue
                    dst_top = self.tableau[dst_idx].peek_top()
                    if dst_top is None:
                        if base_card.rank == 13 and start_idx > 0:
                            return {
                                'available': True,
                                'priority': 4,
                                'message': f'Move King run starting with {base_card.short_label} from T{src_idx+1} to empty T{dst_idx+1}',
                                'cmd': f'm T{src_idx+1} T{dst_idx+1} {run_len}'
                            }
                    else:
                        if base_card.color != dst_top.color and base_card.rank == dst_top.rank - 1:
                            return {
                                'available': True,
                                'priority': 4,
                                'message': f'Move {base_card.short_label} from T{src_idx+1} onto {dst_top.short_label} in T{dst_idx+1}',
                                'cmd': f'm T{src_idx+1} T{dst_idx+1} {run_len}'
                            }

        # Priority 5: Draw from stock
        if not self.stock.is_empty():
            return {
                'available': True,
                'priority': 5,
                'message': 'Draw cards from the stock pile',
                'cmd': 'd'
            }
        elif not self.waste.is_empty():
            return {
                'available': True,
                'priority': 5,
                'message': 'Recycle waste back into stock pile',
                'cmd': 'd'
            }

        # Stuck (FR-10.3)
        return {
            'available': False,
            'message': 'No legal moves available. The game may be stuck.'
        }

    @property
    def elapsed_seconds(self) -> int:
        """Returns elapsed time in seconds (FR-10.4)."""
        return int(time.time() - self.start_time)

    def to_dict(self) -> Dict[str, Any]:
        """Serializes full game state to dictionary for JSON API and GUI."""
        return {
            'seed': self.seed,
            'draw_mode': self.draw_mode,
            'score': self.score,
            'moves': self.moves_count,
            'elapsed_seconds': self.elapsed_seconds,
            'is_won': self.is_game_won,
            'can_auto_complete': self.can_auto_complete(),
            'stock_count': self.stock.size(),
            'waste_top': self.waste.peek().to_dict() if self.waste.peek() else None,
            'waste_count': self.waste.size(),
            'foundations': [
                {
                    'index': f.index,
                    'suit': f.suit,
                    'size': f.size(),
                    'top': f.peek_top().to_dict() if f.peek_top() else None
                }
                for f in self.foundations
            ],
            'tableau': [
                {
                    'index': t.index,
                    'size': t.size(),
                    'cards': [c.to_dict() for c in t.to_list()]
                }
                for t in self.tableau
            ],
            'undo_count': self.undo_stack.size(),
            'redo_count': self.redo_stack.size()
        }
