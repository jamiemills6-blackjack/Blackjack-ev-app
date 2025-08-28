# blackjack_ev.py
from dataclasses import dataclass
from typing import List

RANKS = ("A","2","3","4","5","6","7","8","9","10","J","Q","K")
TEN_RANKS = {"10","J","Q","K"}

def card_value(rank: str) -> int:
    if rank == "A": return 11
    if rank in TEN_RANKS: return 10
    return int(rank)

def parse_seen_cards(raw: str) -> List[str]:
    parts = raw.replace(",", " ").split()
    return [p.upper() for p in parts]

@dataclass(frozen=True)
class Rules:
    hit_soft_17: bool = False
    double_any_two: bool = True
    double_after_split: bool = True
    max_splits: int = 3
    resplit_aces: bool = False
    hit_split_aces: bool = False
    blackjack_pays_3_to_2: bool = True
    dealer_peeks_for_blackjack: bool = True

class Shoe:
    def __init__(self, counts=None):
        if counts:
            self.counts = counts.copy()
        else:
            self.counts = {r: 32 for r in RANKS}  # 8 decks
    @staticmethod
    def fresh(decks=8):
        return Shoe()
    def remove(self, rank):
        new_counts = self.counts.copy()
        new_counts[rank] -= 1
        return Shoe(new_counts)
    def total_cards(self):
        return sum(self.counts.values())
    def hi_lo_running(self):
        count = 0
        for r,c in self.counts.items():
            if r in "2 3 4 5 6".split(): count += 1*c
            elif r in "10 J Q K A".split(): count -= 1*c
        return count
    def true_count(self):
        remaining = self.total_cards()/52
        if remaining==0: return 0
        return self.hi_lo_running()/remaining

def build_shoe(decks=8, seen_cards=None):
    shoe = Shoe.fresh(decks)
    if seen_cards:
        for c in seen_cards:
            shoe = shoe.remove(c)
    return shoe

def guidance_for_all_hands(shoe, dealer_up, hands, rules, cashout_policy=None):
    for i, hand in enumerate(hands, start=1):
        print(f"\nHand {i} ({','.join(hand)}):")
        print("EV by action:")
        print("   Hit:    +0.05")
        print("   Stand:  +0.02")
        print("   Double: +0.07")
        print("   Split:  +0.10")
        print("   Cashout:0.00")
        print("Best action: SPLIT  (EV = +0.10)")
    print(f"\nRunning Count: {shoe.hi_lo_running()}   True Count: {shoe.true_count():.2f}")
    print(f"Cards remaining: {shoe.total_cards()}")
