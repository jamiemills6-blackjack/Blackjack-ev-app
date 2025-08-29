# File: bj.py
import streamlit as st

# -------------------------
# Helper functions
# -------------------------
CARD_VALUES = {
    '2': [2], '3': [3], '4': [4], '5': [5], '6': [6],
    '7': [7], '8': [8], '9': [9], '10': [10], 'A': [1, 11]
}

def calculate_hand_value(cards):
    """Calculate best hand value (for bust detection)"""
    values = [0]
    for c in cards:
        new_values = []
        for val in values:
            for cv in CARD_VALUES.get(c, [0]):
                new_values.append(val + cv)
        values = new_values
    # Filter <=21 and take max, else min
    under_21 = [v for v in values if v <= 21]
    return max(under_21) if under_21 else min(values)

def commit_cards(input_box_key):
    """Commit cards from input box to hidden session storage"""
    if "committed" not in st.session_state:
        st.session_state["committed"] = {
            "player": [], "others": [], "dealer": []
        }
    current_text = st.session_state[input_box_key].strip()
    if not current_text:
        return  # No new cards
    cards = current_text.split()
    if input_box_key == "player_input":
        st.session_state["committed"]["player"].extend(cards)
    elif input_box_key == "others_input":
        st.session_state["committed"]["others"].extend(cards)
    elif input_box_key == "dealer_input":
        st.session_state["committed"]["dealer"].extend(cards)
    st.session_state[input_box_key] = ""  # Clear after commit

def calculate_ev_and_count():
    """Dummy placeholder for EV and count calculation"""
    player_cards = st.session_state.get("committed", {}).get("player", [])
    # Example simple running count: +1 for 2-6, 0 for 7-9, -1 for 10/A
    running_count = sum([1 if c in ['2','3','4','5','6'] else -1 if c in ['10','A'] else 0 for c in player_cards])
    decks = st.session_state.get("num_decks", 8)
    true_count = running_count / decks if decks else running_count
    ev = 0  # placeholder
    return ev, true_count, running_count

def render_keypad(active_box):
    keypad_vals = ['2','3','4','5','6','7','8','9','10','A','Delete','Enter']
    cols = st.columns(4)
    for idx, val in enumerate(keypad_vals):
        col = cols[idx % 4]
        if col.button(val):
            if val == "Delete":
                st.session_state[active_box] = st.session_state[active_box].strip().rsplit(' ', 1)[0]
            elif val == "Enter":
                commit_cards(active_box)
                # Move focus to next box
                if active_box == "player_input":
                    st.session_state["active_box"] = "others_input"
                elif active_box == "others_input":
                    st.session_state["active_box"] = "dealer_input"
                else:
                    st.session_state["active_box"] = "player_input"
            else:
                st.session_state[active_box] += (val + " ")

# -------------------------
# Initialize session state
# -------------------------
if "active_box" not in st.session_state:
    st.session_state["active_box"] = "player_input"
for box in ["player_input", "others_input", "dealer_input"]:
    if box not in st.session_state:
        st.session_state[box] = ""

if "num_decks" not in st.session_state:
    st.session_state["num_decks"] = 8

# -------------------------
# Layout
# -------------------------
st.markdown("<h1 style='font-size:250%'>Blackjack Assistant</h1>", unsafe_allow_html=True)

st.subheader("Your cards")
st.text_input("", key="player_input", placeholder="Enter your cards", label_visibility="collapsed")

st.subheader("Other players' cards")
st.text_input("", key="others_input", placeholder="Enter other players' cards", label_visibility="collapsed")

st.subheader("Dealer cards (up, down, drawn)")
st.text_input("", key="dealer_input", placeholder="Enter dealer cards", label_visibility="collapsed")

# Keypad with spacing
st.markdown("<div style='margin-top:3mm'></div>", unsafe_allow_html=True)
render_keypad(st.session_state["active_box"])

# -------------------------
# Action buttons
# -------------------------
st.markdown("---")
col1, col2, col3 = st.columns([1,1,1])
with col1:
    if st.button("Calculate"):
        ev, true_count, running_count = calculate_ev_and_count()
        st.session_state["ev"] = ev
        st.session_state["true_count"] = true_count
        st.session_state["running_count"] = running_count
with col2:
    if st.button("Next Hand"):
        # Only clear current input boxes
        for box in ["player_input","others_input","dealer_input"]:
            st.session_state[box] = ""
        st.session_state["active_box"] = "player_input"
with col3:
    if st.button("New Shoe"):
        # Clear everything
        st.session_state["player_input"] = ""
        st.session_state["others_input"] = ""
        st.session_state["dealer_input"] = ""
        st.session_state["committed"] = {"player":[],"others":[],"dealer":[]}

# -------------------------
# Count Info
# -------------------------
st.markdown("### Count Info")
st.number_input("Number of Decks", key="num_decks", min_value=1, max_value=16)
st.markdown(f"EV: {st.session_state.get('ev',0)}")
st.markdown(f"True Count: {st.session_state.get('true_count',0.0):.2f}")
st.markdown(f"Running Count: {st.session_state.get('running_count',0)}")
