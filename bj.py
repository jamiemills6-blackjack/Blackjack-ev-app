import streamlit as st

# ---------------------------
# Initialize session state
# ---------------------------
if "active_box" not in st.session_state:
    st.session_state.active_box = "player"

if "player_cards" not in st.session_state:
    st.session_state.player_cards = []

if "others_cards" not in st.session_state:
    st.session_state.others_cards = []

if "dealer_cards" not in st.session_state:
    st.session_state.dealer_cards = []

# ---------------------------
# Utility Functions
# ---------------------------
def commit_card(value):
    """Commit a card to the currently active input box."""
    if st.session_state.active_box == "player":
        if value == "Delete":
            if st.session_state.player_cards:
                st.session_state.player_cards.pop()
        elif value == "Enter":
            st.session_state.active_box = "others"
        else:
            st.session_state.player_cards.append(value)

    elif st.session_state.active_box == "others":
        if value == "Delete":
            if st.session_state.others_cards:
                st.session_state.others_cards.pop()
        elif value == "Enter":
            st.session_state.active_box = "dealer"
        else:
            st.session_state.others_cards.append(value)

    elif st.session_state.active_box == "dealer":
        if value == "Delete":
            if st.session_state.dealer_cards:
                st.session_state.dealer_cards.pop()
        elif value == "Enter":
            st.session_state.active_box = "player"  # loop back
        else:
            st.session_state.dealer_cards.append(value)

def calculate_counts():
    """Dummy calculation logic — replace with real EV/counting formulas."""
    num_decks = st.session_state.get("num_decks", 0) or 0
    running_count = len(st.session_state.player_cards) + \
                    len(st.session_state.others_cards) + \
                    len(st.session_state.dealer_cards)
    true_count = running_count / num_decks if num_decks > 0 else 0
    ev = true_count * 0.1
    penetration = running_count / (num_decks * 52) if num_decks > 0 else 0
    return ev, true_count, running_count, penetration

# ---------------------------
# UI Layout
# ---------------------------
st.title("Blackjack Assistant")

# Player / Others / Dealer input displays
st.subheader("Your cards")
st.write(" ".join(st.session_state.player_cards) or "No cards yet")

st.subheader("Other players' cards")
st.write(" ".join(st.session_state.others_cards) or "No cards yet")

st.subheader("Dealer cards (up, down, drawn)")
st.write(" ".join(st.session_state.dealer_cards) or "No cards yet")

# ---------------------------
# Keypad (robust grid)
# ---------------------------
st.markdown("---")
st.markdown("### Keypad")

# Define keypad layout
buttons = ["2", "3", "4", "5",
           "6", "7", "8", "9",
           "10", "A", "Delete", "Enter"]

# Render keypad in grid
rows = [buttons[i:i+4] for i in range(0, len(buttons), 4)]
for row in rows:
    cols = st.columns(len(row), gap="small")
    for col, val in zip(cols, row):
        if col.button(val, use_container_width=True):
            commit_card(val)

st.markdown("---")

# ---------------------------
# Count Info
# ---------------------------
with st.expander("Count Info"):
    st.number_input("Number of Decks", min_value=0, key="num_decks", step=1)
    if st.button("Calculate"):
        ev, true_count, running_count, penetration = calculate_counts()
        st.write(f"**EV:** {ev:.2f}")
        st.write(f"**True Count:** {true_count:.2f}")
        st.write(f"**Running Count:** {running_count}")
        st.write(f"**Penetration:** {penetration:.2%}")
