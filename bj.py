import streamlit as st

# -------------------------------
# Basic setup
# -------------------------------
st.set_page_config(page_title="Blackjack Assistant", layout="centered")

# Styling
st.markdown(
    """
    <style>
    h1 {
        font-size: 200%; 
        text-align: center;
    }
    .stTextInput > div > div > input {
        border: 1px solid white !important;
        border-radius: 6px;
        padding: 6px;
        background-color: black;
        color: white;
    }
    .keypad button {
        margin: 2px;
        min-width: 60px;
        min-height: 45px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# -------------------------------
# Card values and helpers
# -------------------------------
CARD_VALUES = {
    "A": [1, 11],
    "2": [2], "3": [3], "4": [4], "5": [5],
    "6": [6], "7": [7], "8": [8], "9": [9],
    "10": [10]
}

def best_hand_value(cards):
    """Return best blackjack value (<=21 if possible)."""
    total = 0
    aces = 0
    for c in cards:
        if c == "A":
            aces += 1
            total += 11
        else:
            total += int(c)
    while total > 21 and aces:
        total -= 10
        aces -= 1
    return total

def recommend_action(player_cards, dealer_card):
    """Return blackjack action based on basic strategy (simplified)."""
    total = best_hand_value(player_cards)
    if total > 21:
        return "Bust"
    if total >= 17:
        return "Stand"
    elif total <= 11:
        return "Hit"
    else:  # 12–16
        return "Stand" if dealer_card in ["2","3","4","5","6"] else "Hit"

# -------------------------------
# Session State
# -------------------------------
if "player" not in st.session_state: st.session_state.player = []
if "others" not in st.session_state: st.session_state.others = []
if "dealer" not in st.session_state: st.session_state.dealer = []

# -------------------------------
# UI Header
# -------------------------------
st.title("Blackjack Assistant")

st.write("Player Input")

# -------------------------------
# Input field (shows current cards)
# -------------------------------
player_str = " ".join(st.session_state.player)
player_input = st.text_input("Your cards", value=player_str, key="player_display")

# -------------------------------
# Card input keypad (grid)
# -------------------------------
def keypad_handler(field, card):
    if card == "⌫":  # delete
        if st.session_state[field]:
            st.session_state[field].pop()
    elif card == "⏎":  # enter does nothing special now
        pass
    else:
        st.session_state[field].append(card)

st.markdown("### Keypad")

rows = [
    ["2", "3", "4"],
    ["5", "6", "7"],
    ["8", "9", "10"],
    ["A", "⌫", "⏎"]
]

for row in rows:
    cols = st.columns(3, gap="small")
    for i, card in enumerate(row):
        with cols[i]:
            if st.button(card, key=f"btn_{card}_player"):
                keypad_handler("player", card)

# -------------------------------
# Dealer input
# -------------------------------
dealer_str = " ".join(st.session_state.dealer)
st.text_input("Dealer cards (Up, Down, Drawn)", value=dealer_str, key="dealer_display")

rows_dealer = [
    ["2", "3", "4"],
    ["5", "6", "7"],
    ["8", "9", "10"],
    ["A", "⌫", "⏎"]
]
st.markdown("### Dealer Keypad")
for row in rows_dealer:
    cols = st.columns(3, gap="small")
    for i, card in enumerate(row):
        with cols[i]:
            if st.button(card, key=f"btn_{card}_dealer"):
                keypad_handler("dealer", card)

# -------------------------------
# Calculate button
# -------------------------------
if st.button("Calculate", type="primary"):
    if st.session_state.player and st.session_state.dealer:
        action = recommend_action(
            st.session_state.player,
            st.session_state.dealer[0]  # only up card for calc
        )
        if action == "Bust":
            st.markdown("### **Bust**", unsafe_allow_html=True)
        else:
            color = "green" if action == "Stand" else "red"
            st.markdown(f"<h3 style='color:{color};'>Recommend: {action}</h3>", unsafe_allow_html=True)

# -------------------------------
# Buttons (Next Hand, New Shoe)
# -------------------------------
col1, col2, col3 = st.columns(3, gap="small")
with col1:
    if st.button("Next Hand"):
        st.session_state.player = []
        st.session_state.dealer = []
with col2:
    if st.button("New Shoe", type="primary"):
        st.session_state.player = []
        st.session_state.dealer = []
        st.session_state.others = []
