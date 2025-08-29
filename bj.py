import streamlit as st

# -----------------------
# Blackjack EV Logic
# -----------------------
CARD_VALUES = {
    '2': [2], '3': [3], '4': [4], '5': [5], '6': [6],
    '7': [7], '8': [8], '9': [9], '10': [10], 'A': [1, 11]
}

def hand_values(cards):
    totals = [0]
    for c in cards:
        new_totals = []
        for v in CARD_VALUES[c]:
            for t in totals:
                new_totals.append(t + v)
        totals = new_totals
    return [t for t in set(totals) if t <= 21] or [min(new_totals)]

def recommend_action(player_cards, dealer_upcard):
    totals = hand_values(player_cards)
    if min(totals) > 21:
        return "Bust"
    total = max(totals)
    # Simple perfect strategy placeholder
    if total >= 17:
        return "Stand"
    elif total <= 11:
        return "Hit"
    else:
        return "Hit"

# -----------------------
# Session State Initialization
# -----------------------
if 'shoe' not in st.session_state:
    st.session_state.shoe = []

for field in ['player','others','dealer']:
    if field not in st.session_state:
        st.session_state[field] = []

if 'num_decks' not in st.session_state:
    st.session_state.num_decks = 8

# -----------------------
# UI Layout
# -----------------------
st.markdown("<h1 style='font-size:200%;'>Blackjack Assistant</h1>", unsafe_allow_html=True)

player_input = st.text_area("Your cards", value=" ".join(st.session_state.player), key="player_display", height=40)
others_input = st.text_area("Other players' cards", value=" ".join(st.session_state.others), key="others_display", height=40)
dealer_input = st.text_area("Dealer cards (up, down, drawn)", value=" ".join(st.session_state.dealer), key="dealer_display", height=40)

# Keypad buttons in 4x4 grid
card_buttons = ['2','3','4','5','6','7','8','9','10','A','Delete','Enter']
def render_grid(field):
    cols = st.columns(4)
    for i, card in enumerate(card_buttons):
        if cols[i%4].button(card, key=f"{field}_{card}"):
            if card == "Delete":
                st.session_state[field] = st.session_state[field][:-1]
            elif card == "Enter":
                st.session_state.shoe += st.session_state[field]
                st.session_state[field] = []
            else:
                st.session_state[field].append(card)

render_grid('player')
render_grid('others')
render_grid('dealer')

# -----------------------
# Control Buttons
# -----------------------
col1,col2,col3 = st.columns([1,1,1])
if col1.button("Calculate"):
    action = recommend_action(st.session_state.player, st.session_state.dealer[0] if st.session_state.dealer else None)
    st.session_state.action = action
if col2.button("Next Hand"):
    st.session_state.shoe += st.session_state.player + st.session_state.others + st.session_state.dealer
    st.session_state.player = []
    st.session_state.others = []
    st.session_state.dealer = []
if col3.button("New Shoe"):
    st.session_state.shoe = []
    st.session_state.player = []
    st.session_state.others = []
    st.session_state.dealer = []

# -----------------------
# Count Info Dropdown
# -----------------------
with st.expander("Count Info"):
    st.session_state.num_decks = st.number_input("Number of Decks", min_value=1, max_value=16, value=st.session_state.num_decks)
    running_count = sum([1 if c in ['10','A'] else 0 for c in st.session_state.shoe])  # placeholder
    true_count = running_count / st.session_state.num_decks
    penetration = len(st.session_state.shoe) / (st.session_state.num_decks * 52)
    ev = 0  # placeholder for EV calculation

    st.markdown(f"EV: {ev}")
    st.markdown(f"True Count: {true_count:.2f}")
    st.markdown(f"Running Count: {running_count}")
    st.markdown(f"Penetration: {penetration:.2f}")

# -----------------------
# Action Display
# -----------------------
if 'action' in st.session_state:
    action_color = "black" if st.session_state.action=="Bust" else "green"
    st.markdown(f"<h2 style='color:{action_color}'>{st.session_state.action}</h2>", unsafe_allow_html=True)
