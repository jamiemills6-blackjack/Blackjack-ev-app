# File: bj.py
import streamlit as st

# ---------------------------
# Initialize session state
# ---------------------------
def init_session():
    fields = [
        "player", "others", "dealer", "shoe", "num_decks",
        "running_count", "true_count", "penetration", "ev"
    ]
    for f in fields:
        if f not in st.session_state:
            st.session_state[f] = "" if f in ["player", "others", "dealer"] else 0

init_session()

# ---------------------------
# Blackjack logic constants
# ---------------------------
CARD_VALUES = {
    "2": [2], "3": [3], "4": [4], "5": [5], "6": [6],
    "7": [7], "8": [8], "9": [9], "10": [10], "A": [1, 11]
}

# ---------------------------
# Helper functions
# ---------------------------
def best_hand_value(cards):
    values = [0]
    for c in cards.split():
        if c not in CARD_VALUES:
            continue
        new_values = []
        for v in CARD_VALUES[c]:
            for total in values:
                new_values.append(total + v)
        values = new_values
    under = [v for v in values if v <= 21]
    return max(under) if under else min(values)

def recommend_action(player_cards, dealer_card):
    total = best_hand_value(player_cards)
    if total > 21:
        return "Bust"
    # Placeholder: Replace with actual perfect strategy logic
    if total >= 17:
        return "Stand"
    return "Hit"

# ---------------------------
# CSS for keypad and layout
# ---------------------------
st.markdown("""
<style>
.grid-container {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1.5mm;
  margin-bottom: 3mm;
}
.grid-button {
  width: 100%;
  height: 50px;
  font-size: 16px;
}
.display-box {
  border: 1px solid white;
  padding: 4px;
  margin-bottom: 3mm;
  min-height: 35px;
}
.action-btn {
  width: 100%;
  height: 40px;
  margin-bottom: 5px;
  font-size: 16px;
}
</style>
""", unsafe_allow_html=True)

# ---------------------------
# Card keypad helper
# ---------------------------
def render_keypad(field_name):
    container = st.container()
    display_text = st.text_area("", value=st.session_state[field_name], key=f"{field_name}_display",
                                height=50)
    st.session_state[field_name] = display_text.strip()
    with container:
        grid_html = "<div class='grid-container'>"
        for c in list(map(str, range(2, 11))) + ["A", "Delete", "Enter"]:
            grid_html += f"""
            <button class='grid-button' onclick="document.getElementById('{field_name}_display').value='{c if c not in ['Enter','Delete'] else ''}';console.log('{c}');">{c}</button>
            """
        grid_html += "</div>"
        st.markdown(grid_html, unsafe_allow_html=True)

# ---------------------------
# Header
# ---------------------------
st.markdown("<h1 style='font-size:200%'>Blackjack Assistant</h1>", unsafe_allow_html=True)

# ---------------------------
# Input sections
# ---------------------------
st.markdown("### Your cards")
render_keypad("player")

st.markdown("### Other players' cards")
render_keypad("others")

st.markdown("### Dealer cards (up, down, drawn)")
render_keypad("dealer")

# ---------------------------
# Action buttons
# ---------------------------
if st.button("Calculate", key="calc"):
    player_cards = st.session_state["player"]
    dealer_card = st.session_state["dealer"].split()[0] if st.session_state["dealer"] else "10"
    action = recommend_action(player_cards, dealer_card)
    st.session_state["ev"] = 0  # Placeholder EV
    st.session_state["running_count"] += 0  # Placeholder
    st.session_state["true_count"] = st.session_state["running_count"] / max(1, int(st.session_state["num_decks"]))
    st.success(f"Action: {action}")

if st.button("Next Hand", key="next"):
    st.session_state["player"] = ""
    st.session_state["others"] = ""
    st.session_state["dealer"] = ""

if st.button("New Shoe", key="newshoe"):
    st.session_state["player"] = ""
    st.session_state["others"] = ""
    st.session_state["dealer"] = ""
    st.session_state["shoe"] = ""
    st.session_state["running_count"] = 0
    st.session_state["true_count"] = 0
    st.session_state["penetration"] = 0
    st.session_state["ev"] = 0

# ---------------------------
# Count Info
# ---------------------------
with st.expander("Count Info"):
    st.number_input("Number of Decks", min_value=1, max_value=12, value=8, key="num_decks")
    st.write(f"EV: {st.session_state.get('ev',0)}")
    st.write(f"True Count: {st.session_state.get('true_count',0):.2f}")
    st.write(f"Running Count: {st.session_state.get('running_count',0)}")
    st.write(f"Penetration: {st.session_state.get('penetration',0):.2f}")
