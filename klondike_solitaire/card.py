"""
card.py - Klondike Solitaire Card Model
CSC200 Data Structures & Algorithms | Mid Term Project
Author: @Muhammad Hamza

Requirements Covered:
- FR-1.1: Represent card with suit, rank, and face-up/face-down state.
- FR-1.2: Derive card color (red or black) from its suit.
- FR-1.6: Display card as short label (e.g. 10H, QS, AD) or hidden marker [##].
"""

from typing import Dict, Any

SUITS = ['spades', 'hearts', 'clubs', 'diamonds']
SUIT_SYMBOLS = {
    'spades': '♠',
    'hearts': '♥',
    'clubs': '♣',
    'diamonds': '♦'
}
SUIT_LETTERS = {
    'spades': 'S',
    'hearts': 'H',
    'clubs': 'C',
    'diamonds': 'D'
}
LETTER_TO_SUIT = {
    'S': 'spades',
    'H': 'hearts',
    'C': 'clubs',
    'D': 'diamonds'
}

RANK_LABELS = {
    1: 'A', 2: '2', 3: '3', 4: '4', 5: '5', 6: '6', 7: '7',
    8: '8', 9: '9', 10: '10', 11: 'J', 12: 'Q', 13: 'K'
}
LABEL_TO_RANK = {v: k for k, v in RANK_LABELS.items()}


class Card:
    """Represents a standard playing card in Klondike Solitaire."""

    def __init__(self, suit: str, rank: int, face_up: bool = False):
        suit_lower = suit.lower()
        if suit_lower not in SUITS:
            raise ValueError(f"Invalid suit: {suit}. Must be one of {SUITS}")
        if not (1 <= rank <= 13):
            raise ValueError(f"Invalid rank: {rank}. Must be between 1 and 13")

        self.suit: str = suit_lower
        self.rank: int = rank
        self.face_up: bool = face_up

    @property
    def id(self) -> str:
        """Unique card identifier, e.g. 'AS', '10H', 'KD'."""
        return f"{RANK_LABELS[self.rank]}{SUIT_LETTERS[self.suit]}"

    @property
    def color(self) -> str:
        """Derives card color ('red' or 'black') from its suit (FR-1.2)."""
        return 'red' if self.suit in ('hearts', 'diamonds') else 'black'

    @property
    def symbol(self) -> str:
        """Returns unicode suit symbol (♠, ♥, ♣, ♦)."""
        return SUIT_SYMBOLS[self.suit]

    @property
    def rank_label(self) -> str:
        """Returns rank label ('A', '2'-'10', 'J', 'Q', 'K')."""
        return RANK_LABELS[self.rank]

    @property
    def short_label(self) -> str:
        """Returns short label e.g. '10H' if face-up, or '[##]' if face-down (FR-1.6)."""
        if not self.face_up:
            return "[##]"
        return self.id

    def ansi_str(self) -> str:
        """Returns ANSI-colored label for console rendering (UI-2, UI-3)."""
        if not self.face_up:
            return "\033[90m[##]\033[0m"  # Dark gray
        symbol = self.symbol
        label = self.rank_label
        if self.color == 'red':
            # Bright Red
            return f"\033[91m{label:>2}{symbol}\033[0m"
        else:
            # White / Bold Black
            return f"\033[97m{label:>2}{symbol}\033[0m"

    def flip(self) -> None:
        """Toggles face-up state."""
        self.face_up = not self.face_up

    def to_dict(self) -> Dict[str, Any]:
        """Serializes card to dictionary for JSON API and GUI."""
        return {
            'id': self.id,
            'suit': self.suit,
            'rank': self.rank,
            'rank_label': self.rank_label,
            'color': self.color,
            'symbol': self.symbol,
            'face_up': self.face_up,
            'short_label': self.short_label
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Card':
        """Deserializes card from dictionary."""
        return cls(
            suit=data['suit'],
            rank=data['rank'],
            face_up=data.get('face_up', False)
        )

    def __repr__(self) -> str:
        state = "UP" if self.face_up else "DN"
        return f"Card({self.id}:{state})"

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Card):
            return False
        return self.suit == other.suit and self.rank == other.rank

    def __hash__(self) -> int:
        return hash((self.suit, self.rank))
