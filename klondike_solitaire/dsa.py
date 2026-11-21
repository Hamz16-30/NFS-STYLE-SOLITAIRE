"""
dsa.py - Custom Hand-Written Data Structures
CSC200 Data Structures & Algorithms | Mid Term Project
Author: @Muhammad Hamza

Requirements Covered:
- DS-1: Array / list for 52-card deck with Fisher-Yates shuffle and seedable PRNG.
- DS-2: Custom Stack ADT (LIFO) for Foundation piles (4), waste pile, undo stack, redo stack.
- DS-3: Custom Queue ADT (FIFO) for Stock pile.
- DS-4, DS-6: Custom Doubly Linked List for Tableau piles (head at bottom, tail at top, run split/attach in O(1)).
- DS-5, DS-9: Custom HashMap with separate chaining for Card Location Index.
- DS-10: Independent data structure classes decoupled from game logic for unit testing.
"""

from typing import Any, List, Optional, Callable, Tuple
from card import Card, SUITS


class Node:
    """Singly-linked node for CustomStack and CustomQueue."""
    def __init__(self, value: Any):
        self.value: Any = value
        self.next: Optional['Node'] = None


class DLNode:
    """Doubly-linked node for CustomDoublyLinkedList (Tableau piles)."""
    def __init__(self, card: Card):
        self.card: Card = card
        self.prev: Optional['DLNode'] = None
        self.next: Optional['DLNode'] = None


# ==============================================================================
# DS-2: Custom Stack ADT (LIFO)
# ==============================================================================
class CustomStack:
    """
    Hand-written LIFO Stack ADT backed by singly-linked nodes.
    Used for: Foundation piles (4), Waste pile, Undo stack, Redo stack.
    Time Complexity:
      push: O(1)
      pop: O(1)
      peek: O(1)
      size: O(1)
      is_empty: O(1)
    """
    def __init__(self):
        self._top: Optional[Node] = None
        self._size: int = 0

    def push(self, value: Any) -> None:
        """Pushes an element onto the top of the stack."""
        new_node = Node(value)
        new_node.next = self._top
        self._top = new_node
        self._size += 1

    def pop(self) -> Optional[Any]:
        """Removes and returns the top element of the stack, or None if empty."""
        if self._top is None:
            return None
        popped = self._top.value
        self._top = self._top.next
        self._size -= 1
        return popped

    def peek(self) -> Optional[Any]:
        """Returns the top element without removing it, or None if empty."""
        if self._top is None:
            return None
        return self._top.value

    def is_empty(self) -> bool:
        """Returns True if the stack has 0 elements."""
        return self._size == 0

    def size(self) -> int:
        """Returns the current number of elements in the stack."""
        return self._size

    def to_list(self) -> List[Any]:
        """Returns elements as a list from top to bottom."""
        result = []
        curr = self._top
        while curr is not None:
            result.append(curr.value)
            curr = curr.next
        return result

    def clear(self) -> None:
        """Clears all elements from the stack."""
        self._top = None
        self._size = 0

    def __len__(self) -> int:
        return self._size

    def __iter__(self):
        curr = self._top
        while curr is not None:
            yield curr.value
            curr = curr.next


# ==============================================================================
# DS-3: Custom Queue ADT (FIFO)
# ==============================================================================
class CustomQueue:
    """
    Hand-written FIFO Queue ADT backed by singly-linked nodes with head and tail.
    Used for: Stock draw pile.
    Time Complexity:
      enqueue: O(1)
      dequeue: O(1)
      peek: O(1)
      size: O(1)
      is_empty: O(1)
    """
    def __init__(self):
        self._head: Optional[Node] = None
        self._tail: Optional[Node] = None
        self._size: int = 0

    def enqueue(self, value: Any) -> None:
        """Adds an element to the rear of the queue."""
        new_node = Node(value)
        if self._tail is None:
            self._head = new_node
            self._tail = new_node
        else:
            self._tail.next = new_node
            self._tail = new_node
        self._size += 1

    def dequeue(self) -> Optional[Any]:
        """Removes and returns the front element from the queue, or None if empty."""
        if self._head is None:
            return None
        val = self._head.value
        self._head = self._head.next
        if self._head is None:
            self._tail = None
        self._size -= 1
        return val

    def peek(self) -> Optional[Any]:
        """Returns the front element without removing it, or None if empty."""
        if self._head is None:
            return None
        return self._head.value

    def is_empty(self) -> bool:
        """Returns True if the queue has 0 elements."""
        return self._size == 0

    def size(self) -> int:
        """Returns the current count of elements in the queue."""
        return self._size

    def to_list(self) -> List[Any]:
        """Returns elements as a list from front to rear."""
        result = []
        curr = self._head
        while curr is not None:
            result.append(curr.value)
            curr = curr.next
        return result

    def clear(self) -> None:
        """Clears all elements from the queue."""
        self._head = None
        self._tail = None
        self._size = 0

    def __len__(self) -> int:
        return self._size

    def __iter__(self):
        curr = self._head
        while curr is not None:
            yield curr.value
            curr = curr.next


# ==============================================================================
# DS-4 & DS-6: Custom Doubly Linked List for Tableau Piles
# ==============================================================================
class CustomDoublyLinkedList:
    """
    Doubly Linked List for Tableau piles.
    Head is at the bottom (deepest card), Tail is at the top (exposed/playable card).
    Direct access to tail allows O(1) stack-like operations (peek, pop_tail),
    while double links allow detaching and attaching runs of cards in O(1).
    """
    def __init__(self):
        self.head: Optional[DLNode] = None
        self.tail: Optional[DLNode] = None
        self._size: int = 0

    def append(self, card: Card) -> DLNode:
        """Appends a card to the tail (top of the pile). O(1)."""
        node = DLNode(card)
        if self.head is None:
            self.head = node
            self.tail = node
        else:
            self.tail.next = node
            node.prev = self.tail
            self.tail = node
        self._size += 1
        return node

    def pop_tail(self) -> Optional[Card]:
        """Removes and returns the top card (tail). O(1)."""
        if self.tail is None:
            return None
        removed_card = self.tail.card
        if self.head == self.tail:
            self.head = None
            self.tail = None
        else:
            self.tail = self.tail.prev
            self.tail.next = None
        self._size -= 1
        return removed_card

    def peek_tail(self) -> Optional[Card]:
        """Returns the top card without removing it. O(1)."""
        if self.tail is None:
            return None
        return self.tail.card

    def find_node(self, predicate: Callable[[Card], bool]) -> Optional[DLNode]:
        """Finds the first node matching predicate, walking from head to tail."""
        curr = self.head
        while curr is not None:
            if predicate(curr.card):
                return curr
            curr = curr.next
        return None

    def get_node_at_offset_from_tail(self, count: int) -> Optional[DLNode]:
        """
        Gets the start node of a run of `count` cards from the top.
        Example: count=1 returns tail. count=2 returns tail.prev.
        """
        if count < 1 or count > self._size:
            return None
        curr = self.tail
        for _ in range(count - 1):
            if curr is None:
                return None
            curr = curr.prev
        return curr

    def split_from(self, node: DLNode) -> 'CustomDoublyLinkedList':
        """
        Splits list from `node` onward.
        Returns a new CustomDoublyLinkedList containing [node .. tail].
        The original list retains [head .. node.prev].
        Time Complexity: O(1) pointer updates + O(k) counting detached nodes.
        """
        if node is None:
            raise ValueError("Cannot split from None node")

        detached = CustomDoublyLinkedList()
        detached.head = node
        detached.tail = self.tail

        # Count nodes in the detached run
        count = 0
        curr = node
        while curr is not None:
            count += 1
            curr = curr.next
        detached._size = count

        if node == self.head:
            self.head = None
            self.tail = None
            self._size = 0
        else:
            self.tail = node.prev
            self.tail.next = None
            node.prev = None
            self._size -= count

        return detached

    def attach(self, run_list: 'CustomDoublyLinkedList') -> None:
        """
        Attaches an entire sub-run CustomDoublyLinkedList to the tail.
        Time Complexity: O(1).
        """
        if run_list is None or run_list.is_empty():
            return

        if self.head is None:
            self.head = run_list.head
            self.tail = run_list.tail
            self._size = run_list._size
        else:
            self.tail.next = run_list.head
            run_list.head.prev = self.tail
            self.tail = run_list.tail
            self._size += run_list._size

    def is_empty(self) -> bool:
        """Returns True if pile is empty."""
        return self._size == 0

    def size(self) -> int:
        """Returns the number of cards in the pile."""
        return self._size

    def to_list(self) -> List[Card]:
        """Returns cards from head (bottom) to tail (top)."""
        result = []
        curr = self.head
        while curr is not None:
            result.append(curr.card)
            curr = curr.next
        return result

    def clear(self) -> None:
        """Clears all cards from the pile."""
        self.head = None
        self.tail = None
        self._size = 0

    def __len__(self) -> int:
        return self._size

    def __iter__(self):
        curr = self.head
        while curr is not None:
            yield curr.card
            curr = curr.next


# ==============================================================================
# DS-5 & DS-9: Custom HashMap with Separate Chaining
# ==============================================================================
class CustomHashMap:
    """
    Hand-written Hash Map using separate chaining for collision resolution.
    Maps: card_id (str) -> location record dict:
          {'pile': str, 'index': int, 'position': int, 'face_up': bool}
    Time Complexity:
      put: O(1) average
      get: O(1) average
      remove: O(1) average
    """
    def __init__(self, capacity: int = 64):
        self.capacity: int = capacity
        self.buckets: List[List[Tuple[str, Any]]] = [[] for _ in range(capacity)]
        self._size: int = 0

    def _hash(self, key: str) -> int:
        """Polynomial rolling hash code for string keys modulo capacity."""
        h = 0
        for ch in key:
            h = (h * 31 + ord(ch)) % self.capacity
        return h

    def put(self, key: str, value: Any) -> None:
        """Inserts or updates the value associated with key."""
        idx = self._hash(key)
        bucket = self.buckets[idx]
        for i, (k, _) in enumerate(bucket):
            if k == key:
                bucket[i] = (key, value)
                return
        bucket.append((key, value))
        self._size += 1

        # Resize if load factor exceeds 0.75
        if self._size > self.capacity * 0.75:
            self._rehash(self.capacity * 2)

    def get(self, key: str) -> Optional[Any]:
        """Retrieves value for key, or None if not found."""
        idx = self._hash(key)
        bucket = self.buckets[idx]
        for k, v in bucket:
            if k == key:
                return v
        return None

    def remove(self, key: str) -> bool:
        """Removes key from the hash map. Returns True if removed, False otherwise."""
        idx = self._hash(key)
        bucket = self.buckets[idx]
        for i, (k, _) in enumerate(bucket):
            if k == key:
                del bucket[i]
                self._size -= 1
                return True
        return False

    def contains(self, key: str) -> bool:
        """Returns True if key is present in the hash map."""
        return self.get(key) is not None

    def entries(self) -> List[Tuple[str, Any]]:
        """Returns all (key, value) pairs stored in the hash map."""
        all_entries = []
        for bucket in self.buckets:
            for entry in bucket:
                all_entries.append(entry)
        return all_entries

    def size(self) -> int:
        """Returns total number of key-value pairs."""
        return self._size

    def clear(self) -> None:
        """Clears all entries from the hash map."""
        self.buckets = [[] for _ in range(self.capacity)]
        self._size = 0

    def _rehash(self, new_capacity: int) -> None:
        """Rehashes entries into a new bucket array when load factor exceeds threshold."""
        old_entries = self.entries()
        self.capacity = new_capacity
        self.buckets = [[] for _ in range(new_capacity)]
        self._size = 0
        for k, v in old_entries:
            self.put(k, v)

    def __len__(self) -> int:
        return self._size

    def __getitem__(self, key: str) -> Any:
        val = self.get(key)
        if val is None:
            raise KeyError(key)
        return val

    def __setitem__(self, key: str, value: Any) -> None:
        self.put(key, value)

    def __delitem__(self, key: str) -> None:
        if not self.remove(key):
            raise KeyError(key)


# ==============================================================================
# DS-1: Array / List Deck with Fisher-Yates Shuffle & Seedable RNG
# ==============================================================================
class SeededRNG:
    """
    Deterministic 32-bit PRNG (Mulberry32-based) for reproducible testing (FR-1.5, NFR-10).
    """
    def __init__(self, seed: int = 123456):
        self.seed: int = seed & 0xFFFFFFFF
        self._s: int = self.seed

    def next(self) -> float:
        """Generates a pseudorandom float in [0, 1)."""
        self._s = (self._s + 0x6D2B79F5) & 0xFFFFFFFF
        t = self._s
        t = ((t ^ (t >> 15)) * (t | 1)) & 0xFFFFFFFF
        t = (t ^ (t + (((t ^ (t >> 7)) * (t | 61)) & 0xFFFFFFFF))) & 0xFFFFFFFF
        return ((t ^ (t >> 14)) & 0xFFFFFFFF) / 4294967296.0

    def rand_int(self, low: int, high: int) -> int:
        """Generates random integer in [low, high] inclusive."""
        if low > high:
            low, high = high, low
        range_size = high - low + 1
        return low + int(self.next() * range_size)


class Deck:
    """
    Standard 52-card deck stored in an array/list.
    Implements Fisher-Yates shuffle algorithm O(n) (FR-1.3, FR-1.4, FR-1.5).
    """
    def __init__(self, seed: Optional[int] = None):
        self.cards: List[Card] = []
        self.rng: SeededRNG = SeededRNG(seed if seed is not None else 42)
        self.reset()

    def reset(self) -> None:
        """Creates a fresh ordered deck of exactly 52 unique cards (FR-1.3)."""
        self.cards = []
        for suit in SUITS:
            for rank in range(1, 14):
                self.cards.append(Card(suit=suit, rank=rank, face_up=False))

    def shuffle(self, seed: Optional[int] = None) -> None:
        """
        Shuffles the 52 cards in-place using unbiased Fisher-Yates algorithm in O(n) (FR-1.4).
        If seed is provided, ensures deterministic reproducible shuffle (FR-1.5).
        """
        if seed is not None:
            self.rng = SeededRNG(seed)

        n = len(self.cards)
        for i in range(n - 1, 0, -1):
            j = self.rng.rand_int(0, i)
            # Swap cards[i] and cards[j]
            self.cards[i], self.cards[j] = self.cards[j], self.cards[i]

    def deal_one(self) -> Optional[Card]:
        """Deals and removes one card from the deck array."""
        if not self.cards:
            return None
        return self.cards.pop()

    def size(self) -> int:
        """Returns remaining cards in deck."""
        return len(self.cards)

    def is_empty(self) -> bool:
        return len(self.cards) == 0
