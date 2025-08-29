# File: bj.py
import streamlit as st

# -----------------------
# Initialize session
# -----------------------
def init_state():
    keys = ["player", "others", "dealer", "shoe", "num_decks",
            "running_count", "true_count", "penetration", "ev"]
    for k in keys:
        if k not in st.session_state:
            if k in ["player", "others", "dealer"]:
                st.session_state[k] = []
            elif k == "num_decks":
                st.session_state[k] = 8
            else:
                st.session_state[k] = 0

init_state()

# -----------------------
# Blackjack logic
# -----------------------
CARD_VALUES = {"2":2,"3":3,"4":4,"5":5,"6":6,"7":7,"8":8,"9":9,"10":10,"A":[1,11]}

def best_hand_value(cards):
    values = [0]
    for c in cards:
        if c not in CARD_VALUES:
            continue
        new_values = []
        card_vals = CARD_VALUES[c] if isinstance(CARD_VALUES[c], list) else [CARD_VALUES[c]]
        for v in card_vals:
            for total in values:
                new_values.append(total+v)
        values = new_values
    under = [v for v in values if v <= 21]
    return max(under) if under else min(values)

def recommend_action(player_cards, dealer_up):
    total = best_hand_value(player_cards)
    if total > 21:
        return "Bust"
    # Simple perfect strategy placeholder
    if total >= 17:
        return "Stand"
    return "Hit"

# -----------------------
# UI
# -----------------------
st.markdown("<h1 style='font-size:250%'>Blackjack Assistant</h1>", unsafe_allow_html=True)

def render_keypad(field):
    st.text(" ".join(st.session_state[field]))
    keypad = [str(i) for i in range(2,11)] + ["A"]
    col_count = 4
    for i in range(0, len(keypad), col_count):
        cols = st.columns(col_count)
        for j, key in enumerate(keypad[i:i+col_count]):
            if cols[j].button(key):
                st.session_state[field].append(key)
    # Delete and Enter row
    cols = st.columns(2)
    if cols[0].button("Delete"):
        if st.session_state[field]:
            st.session_state[field].pop()
    if cols[1].button("Enter"):
        # Do nothing here; just confirms current hand
        pass

# -----------------------
# Input sections
# -----------------------
st.subheader("Your cards")
render_keypad("player")

st.subheader("Other players' cards")
render_keypad("others")

st.subheader("Dealer cards (up, down, drawn)")
render_keypad("dealer")

# -----------------------
# Action buttons
# -----------------------
if st.button("Calculate"):
    player_cards = st.session_state["player"]
    dealer_up = st.session_state["dealer"][0] if st.session_state["dealer"] else "10"
    action = recommend_action(player_cards, dealer_up)
    st.session_state["ev"] = 0  # placeholder
    st.session_state["running_count"] += 0  # placeholder
    st.session_state["true_count"] = st.session_state["running_count"]/max(1, st.session_state["num_decks"])
    st.success(f"Action: {action}")

if st.button("Next Hand"):
    st.session_state["player"] = []
    st.session_state["others"] = []
    st.session_state["dealer"] = []

if st.button("New Shoe"):
    st.session_state["player"] = []
    st.session_state["others"] = []
    st.session_state["dealer"] = []
    st.session_state["shoe"] = ""
    st.session_state["running_count"] = 0
    st.session_state["true_count"] = 0
    st.session_state["penetration"] = 0
    st.session_state["ev"] = 0

# -----------------------
# Count info
# -----------------------
with st.expander("Count Info"):
    st.number_input("Number of Decks", min_value=1, max_value=12, value=st.session_state["num_decks"], key="num_decks")
    st.write(f"EV: {st.session_state['ev']}")
    st.write(f"True Count: {st.session_state['true_count']:.2f}")
    st.write(f"Running Count: {st.session_state['running_count']}")
    st.write(f"Penetration: {st.session_state['penetration']:.2f}")
