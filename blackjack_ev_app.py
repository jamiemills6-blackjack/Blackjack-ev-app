import streamlit as st
import random

# =========================
# Blackjack Core Logic
# =========================

# Card values
CARD_VALUES = {
    "A": [1, 11],
    "2": [2],
    "3": [3],
    "4": [4],
    "5": [5],
    "6": [6],
    "7": [7],
    "8": [8],
    "9": [9],
    "10": [10],
    "J": [10],
    "Q": [10],
    "K": [10],
}

# Hi-Lo count values
HI_LO_VALUES = {
    "2": +1,
    "3": +1,
    "4": +1,
    "5": +1,
    "6": +1,
    "7": 0,
    "8": 0,
    "9": 0,
    "10": -1,
    "J": -1,
    "Q": -1,
    "K": -1,
    "A": -1,
}

# Build full shoe (8 decks by default)
def build_shoe(num_decks=8):
    cards = list(CARD_VALUES.keys())
    shoe = cards * 4 * num_decks  # 4 suits per deck
    random.shuffle(shoe)
    return shoe

# Parse input string into cards
def parse_cards(input_str):
    return [c.strip().upper() for c in input_str.split(",") if c.strip()]

# Perfect basic strategy rule engine (simplified)
def recommend_action(player_cards, dealer_up):
    # Handle splitting rules (any pair of 10-value cards included)
    if len(player_cards) == 2 and card_value(player_cards[0]) == card_value(player_cards[1]):
        if player_cards[0] in ["A", "8"]:
            return "Split"
        if card_value(player_cards[0]) == 10:
            return "Stand"  # Do not split 10s per perfect strategy
        if card_value(player_cards[0]) == 9:
            if dealer_up in ["7", "10", "A"]:
                return "Stand"
            else:
                return "Split"
        if card_value(player_cards[0]) in [2, 3]:
            return "Split" if dealer_up in ["4", "5", "6", "7"] else "Hit"
        if card_value(player_cards[0]) == 6:
            return "Split" if dealer_up in ["2", "3", "4", "5", "6"] else "Hit"
        if card_value(player_cards[0]) == 7:
            return "Split" if dealer_up in ["2", "3", "4", "5", "6", "7"] else "Hit"
        if card_value(player_cards[0]) == 4:
            return "Split" if dealer_up in ["5", "6"] else "Hit"
        if card_value(player_cards[0]) == 5:
            return "Double if allowed, otherwise Hit"
    
    # Soft totals (hand contains Ace counted as 11)
    total = best_hand_value(player_cards)
    if "A" in player_cards and total <= 21:
        if total <= 17:
            return "Hit"
        elif total == 18:
            return "Stand" if dealer_up in ["2", "7", "8"] else "Hit"
        else:
            return "Stand"

    # Hard totals
    if total >= 17:
        return "Stand"
    if 13 <= total <= 16:
        return "Stand" if dealer_up in ["2", "3", "4", "5", "6"] else "Hit"
    if total == 12:
        return "Stand" if dealer_up in ["4", "5", "6"] else "Hit"
    if total == 11:
        return "Double if allowed, otherwise Hit"
    if total == 10:
        return "Double if allowed vs dealer 2–9, otherwise Hit"
    if total == 9:
        return "Double if allowed vs dealer 3–6, otherwise Hit"
    return "Hit"

def card_value(card):
    return CARD_VALUES[card][0]

def best_hand_value(cards):
    values = [0]
    for c in cards:
        new_values = []
        for v in CARD_VALUES[c]:
            for base in values:
                new_values.append(base + v)
        values = new_values
    return max([v for v in values if v <= 21] or values)

# Hi-Lo running count
def running_count(cards):
    return sum(HI_LO_VALUES.get(c, 0) for c in cards)

# =========================
# Streamlit UI
# =========================

st.set_page_config(page_title="Blackjack EV Helper", layout="centered")

st.markdown(
    "<h2 style='font-size:18px;'>♠️ Blackjack EV Helper (Mobile)</h2>",
    unsafe_allow_html=True,
)

# Init session state
if "shoe" not in st.session_state:
    st.session_state.shoe = build_shoe()
if "seen_cards" not in st.session_state:
    st.session_state.seen_cards = []

# --- Inputs ---
player_input = st.text_input("Your cards", key="player", help="E.g. 10, 7 or A, 8")
dealer_input = st.text_input("Dealer upcard", key="dealer", help="E.g. 6")
others_input = st.text_input("Other players' cards", key="others", help="E.g. 9, 4, K")

# --- Button layout (mobile optimised) ---
calc_btn = st.button("Calculate")
next_btn = st.button("Next Hand")
new_btn = st.button("New Shoe")

# --- Actions ---
if calc_btn:
    player_cards = parse_cards(player_input)
    dealer_card = dealer_input.strip().upper()
    others_cards = parse_cards(others_input)

    if not player_cards or not dealer_card:
        st.error("Please enter both your cards and the dealer's upcard.")
    else:
        st.session_state.seen_cards.extend(player_cards + [dealer_card] + others_cards)
        advice = recommend_action(player_cards, dealer_card)
        total = best_hand_value(player_cards)

        st.success(f"Hand total: {total} → Recommended action: **{advice}**")

if next_btn:
    # Just clear inputs, keep seen cards
    st.session_state.player = ""
    st.session_state.dealer = ""
    st.session_state.others = ""

if new_btn:
    # Full reset
    st.session_state.shoe = build_shoe()
    st.session_state.seen_cards = []
    st.session_state.player = ""
    st.session_state.dealer = ""
    st.session_state.others = ""
    st.success("🔄 New shoe created (8 decks).")

# --- Debug info ---
with st.expander("📊 Debug info"):
    seen = st.session_state.seen_cards
    st.write("Seen cards so far:", seen)
    st.write("Cards remaining in shoe:", len(st.session_state.shoe) - len(seen))

    rc = running_count(seen)
    decks_remaining = max(1, (len(st.session_state.shoe) - len(seen)) / 52)
    tc = round(rc / decks_remaining, 2)

    st.write(f"Running count: {rc}")
    st.write(f"True count: {tc}")
