import streamlit as st

# =========================
# Blackjack Helper Functions
# =========================

CARD_VALUES = {
    'A': [1, 11],
    '2': [2],
    '3': [3],
    '4': [4],
    '5': [5],
    '6': [6],
    '7': [7],
    '8': [8],
    '9': [9],
    '10': [10]
}

def best_hand_value(cards):
    totals = [0]
    for c in cards:
        vals = CARD_VALUES.get(c, [0])
        totals = [t + v for t in totals for v in vals]
    valid_totals = [t for t in totals if t <= 21]
    return max(valid_totals) if valid_totals else min(totals)

def recommend_action(player_cards, dealer_card):
    total = best_hand_value(player_cards)
    if total > 21:
        return "Bust"
    # Simplified placeholder strategy
    if total >= 17:
        return "Stand"
    elif total <= 11:
        return "Hit"
    else:
        return "Hit"

def compute_running_count(cards):
    # Simple Hi-Lo system
    count = 0
    for c in cards:
        if c in ['2','3','4','5','6']:
            count +=1
        elif c in ['10','A']:
            count -=1
    return count

# =========================
# Initialize Session State
# =========================
if "player_cards" not in st.session_state:
    st.session_state.player_cards = []
if "others_cards" not in st.session_state:
    st.session_state.others_cards = []
if "dealer_cards" not in st.session_state:
    st.session_state.dealer_cards = []
if "num_decks" not in st.session_state:
    st.session_state.num_decks = 8
if "action" not in st.session_state:
    st.session_state.action = ""
if "ev" not in st.session_state:
    st.session_state.ev = 0
if "running_count" not in st.session_state:
    st.session_state.running_count = 0
if "true_count" not in st.session_state:
    st.session_state.true_count = 0
if "penetration" not in st.session_state:
    st.session_state.penetration = 0.0

# =========================
# Page Layout
# =========================
st.set_page_config(page_title="Blackjack Assistant", layout="centered")
st.markdown("<h1 style='font-size:150%;'>Blackjack Assistant</h1>", unsafe_allow_html=True)

# =========================
# Input Boxes
# =========================
st.text_input("Your cards", key="player_display", value="")
st.text_input("Other players' cards", key="others_display", value="")
st.text_input("Dealer cards (up, down, drawn)", key="dealer_display", value="")

# =========================
# Helper Function for Keypad Input
# =========================
def keypad_input(box_key, value):
    if value == "Delete":
        st.session_state[box_key] = st.session_state[box_key][:-2]
    elif value == "Enter":
        cards = st.session_state[box_key].strip().split()
        if box_key == "player_display":
            st.session_state.player_cards += cards
        elif box_key == "others_display":
            st.session_state.others_cards += cards
        elif box_key == "dealer_display":
            st.session_state.dealer_cards += cards
        st.session_state[box_key] = ""
    else:
        st.session_state[box_key] += value + " "

# =========================
# Keypad Buttons
# =========================
keypad_values = ["2","3","4","5","6","7","8","9","10","A","Delete","Enter"]

def render_keypad(box_key):
    cols = st.columns(4)
    for i, val in enumerate(keypad_values):
        if cols[i%4].button(val):
            keypad_input(box_key, val)

st.markdown("**Player Input**")
render_keypad("player_display")
st.markdown("**Other Players Input**")
render_keypad("others_display")
st.markdown("**Dealer Input**")
render_keypad("dealer_display")

# =========================
# Action and Buttons
# =========================
cols = st.columns(3)
if cols[0].button("Calculate"):
    st.session_state.action = recommend_action(st.session_state.player_cards, st.session_state.dealer_cards[:1])
    st.session_state.running_count = compute_running_count(
        st.session_state.player_cards + st.session_state.others_cards + st.session_state.dealer_cards
    )
    st.session_state.true_count = st.session_state.running_count / max(st.session_state.num_decks,1)
    st.session_state.ev = round(0.05*best_hand_value(st.session_state.player_cards),2)
    st.session_state.penetration = len(st.session_state.player_cards + st.session_state.others_cards + st.session_state.dealer_cards)/(st.session_state.num_decks*52)

if cols[1].button("Next Hand"):
    st.session_state.player_display = ""
    st.session_state.others_display = ""
    st.session_state.dealer_display = ""
    st.session_state.action = ""

if cols[2].button("New Shoe"):
    st.session_state.player_cards = []
    st.session_state.others_cards = []
    st.session_state.dealer_cards = []
    st.session_state.player_display = ""
    st.session_state.others_display = ""
    st.session_state.dealer_display = ""
    st.session_state.running_count = 0
    st.session_state.true_count = 0
    st.session_state.ev = 0
    st.session_state.penetration = 0.0
    st.session_state.action = ""

# =========================
# Count Info Section
# =========================
with st.expander("Count Info"):
    st.number_input("Number of Decks", key="num_decks", min_value=1, max_value=12)
    st.markdown(f"**EV:** {st.session_state.ev}")
    st.markdown(f"**True Count:** {st.session_state.true_count:.2f}")
    st.markdown(f"**Running Count:** {st.session_state.running_count}")
    st.markdown(f"**Penetration:** {st.session_state.penetration:.2f}")

# =========================
# Display Action
# =========================
st.markdown(f"**Recommended Action:** {st.session_state.action}")
