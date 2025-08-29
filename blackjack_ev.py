import random
from collections import Counter

# ------------------------------
# Rules and Policies
# ------------------------------

class Rules:
    def __init__(self, decks=6, hit_soft_17=True, double_after_split=True):
        self.decks = decks
        self.hit_soft_17 = hit_soft_17
        self.double_after_split = double_after_split


def default_cashout_policy(action, ev):
    """Placeholder policy: just return the EV."""
    return ev


# ------------------------------
# Shoe Management
# ------------------------------

def build_shoe(decks=6):
    """Return a fresh shoe with N decks."""
    ranks = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
    shoe = []
    for _ in range(decks):
        for r in ranks:
            shoe.extend([r] * 4)  # 4 of each rank per deck
    random.shuffle(shoe)
    return shoe


def parse_seen_cards(seen_cards_str):
    """Convert input string 'A 7 10 J' into a list of cards."""
    if not seen_cards_str.strip():
        return []
    return [c.strip().upper() for c in seen_cards_str.split()]


# ------------------------------
# EV & Action Guidance
# ------------------------------

def hand_value(cards):
    """Compute blackjack hand value with Aces flexible."""
    value, aces = 0, 0
    for c in cards:
        if c in ["J", "Q", "K", "10"]:
            value += 10
        elif c == "A":
            aces += 1
            value += 11
        else:
            value += int(c)

    while value > 21 and aces:
        value -= 10
        aces -= 1
    return value


def is_pair(cards):
    """Check if two cards form a splittable pair (any two 10-value cards count)."""
    if len(cards) != 2:
        return False
    tens = {"10", "J", "Q", "K"}
    return (cards[0] == cards[1]) or (cards[0] in tens and cards[1] in tens)


def guidance_for_all_hands(shoe, dealer_up, player_hand, rules, cashout_policy):
    """
    Return dummy EVs for all legal actions.
    (In reality you'd calculate via simulation / lookup tables.)
    """
    evs = {}

    # Example placeholders
    evs["hit"] = -0.1
    evs["stand"] = 0.05
    if len(player_hand) == 2:
        evs["double"] = 0.02
        if is_pair(player_hand):
            evs["split"] = -0.05

    return evs


def recommend_action(shoe, dealer_up, player_hand, rules, cashout_policy):
    """Return recommended action + EVs for all legal actions."""
    evs = guidance_for_all_hands(
        shoe=shoe,
        dealer_up=dealer_up,
        player_hand=player_hand,
        rules=rules,
        cashout_policy=cashout_policy,
    )

    if not evs:
        return {"best_action": None, "ev_by_action": {}}

    best_action = max(evs.items(), key=lambda kv: kv[1])[0]
    return {"best_action": best_action, "ev_by_action": evs}
