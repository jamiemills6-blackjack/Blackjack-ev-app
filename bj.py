import streamlit as st
import random
import streamlit.components.v1 as components

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
    raw_cards = input_str.strip().split()
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
    total = best_hand_value(player_cards)
    if total > 21:
        return "Bust"
    if len(player_cards) == 2 and card_value(player_cards[0]) == card_value(player_cards[1]):
        if player_cards[0] == "A" or player_cards[0] == "8":
            return "Split"
        if card_value(player_cards[0]) == 10:
            return "Stand"
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

def card_value(card):
    return CARD_VALUES[card][0]

# =========================
# Streamlit UI
# =========================

st.set_page_config(page_title="Blackjack Assistant", layout="centered")
st.markdown("<h1 style='font-size:22.5px;'>Blackjack Assistant</h1>", unsafe_allow_html=True)  # 25% bigger

# Session state init
if "shoe" not in st.session_state: st.session_state.shoe = build_shoe(8)
if "seen_cards" not in st.session_state: st.session_state.seen_cards = []

fields = ["player_input","others_input","dealer_up_input","dealer_down_input","dealer_drawn_input"]
for f in fields:
    if f not in st.session_state: st.session_state[f] = ""

# =========================
# Custom keypad function
# =========================
def card_keypad_input(field_name):
    st.text_input(f"{field_name.replace('_',' ').title()}", value=st.session_state[field_name], key=field_name, disabled=True)
    cols = st.columns([1]*6)
    card_buttons = ["2","3","4","5","6","7","8","9","10","A"]
    for i, card in enumerate(card_buttons):
        col = cols[i % 6]
        if col.button(card + f" ({field_name})"):
            st.session_state[field_name] += f"{card} "
    if st.button(f"Delete ({field_name})"):
        lst = st.session_state[field_name].strip().split()
        if lst:
            lst.pop()
            st.session_state[field_name] = " ".join(lst) + (" " if lst else "")
    if st.button(f"Enter ({field_name})"):
        # Move focus to next field
        idx = fields.index(field_name)
        next_idx = (idx + 1) % len(fields)
        components.html(f"<script>document.getElementById('{fields[next_idx]}').focus();</script>", height=0)

# Draw keypads
for f in fields:
    card_keypad_input(f)

# -------------------
# Buttons
# -------------------
col1, col2, col3 = st.columns(3)
with col1:
    calc_btn = st.button("Calculate", key="calc")
with col2:
    next_btn = st.button("Next Hand", key="next")
with col3:
    new_btn = st.button("New Shoe", key="newshoe")

# Button colors
st.markdown("""
<style>
div.stButton > button:nth-child(1) {background-color: white; color: black;}
div.stButton > button:nth-child(2) {background-color: #cccccc; color: black;}
div.stButton > button:nth-child(3) {background-color: black; color: white;}
</style>
""", unsafe_allow_html=True)

# -------------------
# Button actions
# -------------------
if calc_btn:
    try:
        player_cards = parse_cards(st.session_state.player_input)
        dealer_up = st.session_state.dealer_up_input.strip().upper()
        dealer_down = st.session_state.dealer_down_input.strip().upper()
        dealer_drawn = parse_cards(st.session_state.dealer_drawn_input)
        others_cards = parse_cards(st.session_state.others_input)
        
        for d in [dealer_up, dealer_down]:
            if d in ["J","Q","K"]: 
                if d == dealer_up: dealer_up = "10"
                else: dealer_down = "10"
        if dealer_up not in VALID_CARDS:
            st.error(f"Invalid dealer upcard: {dealer_up}. Use 2-10 or A")
        else:
            st.session_state.seen_cards.extend(player_cards + [dealer_up, dealer_down] + dealer_drawn + others_cards)
            advice = recommend_action(player_cards, dealer_up)
            total = best_hand_value(player_cards)
            if advice == "Bust":
                color = "black"
            elif "Hit" in advice:
                color = "green"
            elif "Stand" in advice:
                color = "red"
            else:
                color = "orange"
            st.markdown(f"<h3 style='color:{color}'>Hand total: {total} → Recommended action: {advice}</h3>", unsafe_allow_html=True)
    except ValueError as e:
        st.error(str(e))

if next_btn:
    for f in fields:
        st.session_state[f] = ""
    st.experimental_rerun()

if new_btn:
    st.session_state.shoe = build_shoe(8)
    st.session_state.seen_cards = []
    for f in fields:
        st.session_state[f] = ""
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
