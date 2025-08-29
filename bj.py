import streamlit as st
import random

# =========================
# Blackjack Core Logic
# =========================

CARD_VALUES = {
    "A": [1, 11], "2": [2], "3": [3], "4": [4], "5": [5],
    "6": [6], "7": [7], "8": [8], "9": [9], "10": [10],
}

HI_LO_VALUES = {
    "2": +1, "3": +1, "4": +1, "5": +1, "6": +1, "7": 0,
    "8": 0, "9": 0, "10": -1, "A": -1,
}

VALID_CARDS = set(CARD_VALUES.keys())

def build_shoe(num_decks=8):
    cards = list(CARD_VALUES.keys())
    shoe = cards * 4 * num_decks
    random.shuffle(shoe)
    return shoe

def parse_cards(input_str):
    input_str = input_str.replace(",", " ")
    raw_cards = [c.strip().upper() for c in input_str.split() if c.strip()]
    cards = []
    for c in raw_cards:
        if c in ["J","Q","K"]:
            cards.append("10")
        elif c == "A":
            cards.append("A")
        elif c.isdigit() and c in CARD_VALUES:
            cards.append(c)
        else:
            raise ValueError(f"Invalid card entered: {c}. Use 2-10 or A")
    return cards

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

def recommend_action(player_cards, dealer_up):
    if len(player_cards) == 2 and card_value(player_cards[0]) == card_value(player_cards[1]):
        if player_cards[0] == "A" or player_cards[0] == "8":
            return "Split"
        if card_value(player_cards[0]) == 10:
            return "Stand"
        if card_value(player_cards[0]) == 9:
            if dealer_up in ["7", "10", "A"]:
                return "Stand"
            else:
                return "Split"
        if card_value(player_cards[0]) in [2, 3]:
            return "Split" if dealer_up in ["4","5","6","7"] else "Hit"
        if card_value(player_cards[0]) == 6:
            return "Split" if dealer_up in ["2","3","4","5","6"] else "Hit"
        if card_value(player_cards[0]) == 7:
            return "Split" if dealer_up in ["2","3","4","5","6","7"] else "Hit"
        if card_value(player_cards[0]) == 4:
            return "Split" if dealer_up in ["5","6"] else "Hit"
        if card_value(player_cards[0]) == 5:
            return "Double if allowed, otherwise Hit"
    
    total = best_hand_value(player_cards)
    if "A" in player_cards and total <= 21:
        if total <= 17:
            return "Hit"
        elif total == 18:
            return "Stand" if dealer_up in ["2","7","8"] else "Hit"
        else:
            return "Stand"
    
    if total >= 17: return "Stand"
    if 13 <= total <= 16: return "Stand" if dealer_up in ["2","3","4","5","6"] else "Hit"
    if total == 12: return "Stand" if dealer_up in ["4","5","6"] else "Hit"
    if total == 11: return "Double if allowed, otherwise Hit"
    if total == 10: return "Double if allowed vs dealer 2–9, otherwise Hit"
    if total == 9: return "Double if allowed vs dealer 3–6, otherwise Hit"
    return "Hit"

def running_count(cards):
    return sum(HI_LO_VALUES.get(c,0) for c in cards)

# =========================
# Streamlit UI
# =========================

st.set_page_config(page_title="Blackjack Assistant", layout="centered")

st.markdown("<h1 style='font-size:24px;'>Blackjack Assistant</h1>", unsafe_allow_html=True)

# Session state init
if "shoe" not in st.session_state:
    st.session_state.shoe = build_shoe(8)
if "seen_cards" not in st.session_state:
    st.session_state.seen_cards = []
if "player" not in st.session_state:
    st.session_state.player = ""
if "dealer" not in st.session_state:
    st.session_state.dealer = ""
if "others" not in st.session_state:
    st.session_state.others = ""

# Inputs
player_input = st.text_input("Your cards", key="player", help="E.g. 10 7 or A 8")
others_input = st.text_input("Other players' cards", key="others", help="E.g. 9 4 10")
dealer_input = st.text_input("Dealer upcard", key="dealer", help="E.g. 6")

# -------------------
# Buttons using HTML for styling
# -------------------
col1, col2, col3 = st.columns(3)

with col1:
    calc_btn = st.button("Calculate", key="calc")
with col2:
    next_btn = st.button("Next Hand", key="next")
with col3:
    new_btn = st.button("New Shoe", key="newshoe")

st.markdown("""
    <style>
    div.stButton > button:first-child {background-color: white; color: black;}
    div.stButton > button:nth-child(2) {background-color: #cccccc; color: black;}
    div.stButton > button:nth-child(3) {background-color: black; color: white;}
    </style>
""", unsafe_allow_html=True)

# -------------------
# Button actions
# -------------------
if calc_btn:
    try:
        player_cards = parse_cards(player_input)
        dealer_card = dealer_input.strip().upper()
        if dealer_card in ["J","Q","K"]:
            dealer_card = "10"
        if dealer_card not in VALID_CARDS:
            st.error(f"Invalid dealer card: {dealer_card}. Use 2-10 or A")
        else:
            others_cards = parse_cards(others_input)
            st.session_state.seen_cards.extend(player_cards + [dealer_card] + others_cards)
            advice = recommend_action(player_cards, dealer_card)
            total = best_hand_value(player_cards)

            color = "green" if "Hit" in advice else "red" if "Stand" in advice else "orange"
            st.markdown(f"<h3 style='color:{color}'>Hand total: {total} → Recommended action: {advice}</h3>", unsafe_allow_html=True)

    except ValueError as e:
        st.error(str(e))

if next_btn:
    st.session_state.player = ""
    st.session_state.others = ""
    st.session_state.dealer = ""

if new_btn:
    st.session_state.shoe = build_shoe(8)
    st.session_state.seen_cards = []
    st.session_state.player = ""
    st.session_state.dealer = ""
    st.session_state.others = ""
    st.success("🔄 New shoe created (8 decks).")

# -------------------
# Count info
# -------------------
with st.expander("📊 Count info"):
    num_decks = st.number_input("Number of decks in shoe", min_value=1, max_value=12, value=8, step=1)
    seen = st.session_state.seen_cards
    total_cards = 52 * num_decks
    remaining_cards = total_cards - len(seen)
    st.write("Seen cards so far:", seen)
    st.write("Cards remaining in shoe:", remaining_cards)

    rc = running_count(seen)
    decks_remaining = max(1, remaining_cards / 52)
    tc = round(rc / decks_remaining, 2)
    penetration = round(len(seen) / total_cards * 100, 1)

    st.write(f"Running count: {rc}")
    st.write(f"True count: {tc}")
    st.write(f"Shoe penetration: {penetration}%")
