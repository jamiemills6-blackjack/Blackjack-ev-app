import streamlit as st

# --- Page setup ---
st.set_page_config(page_title="Blackjack Assistant", layout="centered")

# --- Initialize session state ---
for key in ["player", "others", "dealer", "action", "shoe_cards"]:
    if key not in st.session_state:
        st.session_state[key] = "" if key != "shoe_cards" else []

# --- Helper functions ---

# Card values
def card_value(c):
    if c == "A":
        return 11
    return int(c)

# Calculate hand value
def calculate_hand(cards_str):
    cards = cards_str.split()
    total = sum(card_value(c) for c in cards)
    # Adjust for Aces
    aces = cards.count("A")
    while total > 21 and aces > 0:
        total -= 10
        aces -= 1
    return total

# Update hidden shoe for counting
def commit_cards(cards_str):
    for c in cards_str.split():
        st.session_state.shoe_cards.append(c)

# Calculate running count (Hi-Lo)
def running_count():
    count = 0
    for c in st.session_state.shoe_cards:
        if c in ["2","3","4","5","6"]:
            count += 1
        elif c in ["10","A"]:
            count -=1
    return count

# --- Custom keypad ---
def card_keypad(field_name, label):
    st.markdown(f"### {label}")
    st.markdown(f"<div style='border:1px solid white; padding:6px; border-radius:6px; min-height:40px;'>"
                f"{st.session_state[field_name]}</div>", unsafe_allow_html=True)

    # Grid buttons
    buttons = ["2","3","4","5","6","7","8","9","10","A","Delete","Enter"]
    button_html = "<div style='display:grid; grid-template-columns: repeat(4, 1fr); gap:5px;'>"
    for b in buttons:
        button_html += f"<button onclick='window.streamlitSendMessage({b})'>{b}</button>"
    button_html += "</div>"
    # Use Streamlit buttons
    cols = st.columns(4, gap="small")
    for i, b in enumerate(buttons):
        if cols[i%4].button(b, key=f"{field_name}_{b}", use_container_width=True):
            if b == "Delete":
                st.session_state[field_name] = " ".join(st.session_state[field_name].split()[:-1])
            elif b == "Enter":
                commit_cards(st.session_state[field_name])
            else:
                st.session_state[field_name] += f"{b} "

# --- Header ---
st.markdown("<h1 style='text-align:center; font-size:125%;'>Blackjack Assistant</h1>", unsafe_allow_html=True)

# --- Input Keypads ---
card_keypad("player", "Your cards")
card_keypad("others", "Other players' cards")
card_keypad("dealer", "Dealer cards (up, down, drawn)")

# --- Count Info ---
with st.expander("Count Info"):
    decks = st.number_input("Number of decks", min_value=1, value=8, step=1)
    st.markdown(f"**Running Count:** {running_count()}")
    # Penetration calculation
    total_cards = decks * 52
    penetration = len(st.session_state.shoe_cards) / total_cards
    st.markdown(f"**Penetration:** {penetration:.2%}")

# --- Actions ---
st.markdown("---")
cols_action = st.columns(3)
if cols_action[0].button("Calculate", use_container_width=True):
    player_total = calculate_hand(st.session_state["player"])
    dealer_up = st.session_state["dealer"].split()[0] if st.session_state["dealer"] else None
    if player_total > 21:
        st.session_state["action"] = "Bust"
    elif dealer_up:
        st.session_state["action"] = "Hit" if player_total < 17 else "Stand"
    else:
        st.session_state["action"] = "Need dealer up card"

if cols_action[1].button("Next Hand", use_container_width=True):
    commit_cards(st.session_state["player"])
    commit_cards(st.session_state["others"])
    commit_cards(st.session_state["dealer"])
    st.session_state["player"] = ""
    st.session_state["others"] = ""
    st.session_state["dealer"] = ""
    st.session_state["action"] = ""

if cols_action[2].button("New Shoe", use_container_width=True):
    st.session_state["player"] = ""
    st.session_state["others"] = ""
    st.session_state["dealer"] = ""
    st.session_state["action"] = ""
    st.session_state["shoe_cards"] = []

# --- Display action ---
if st.session_state["action"]:
    color = "black" if st.session_state["action"]=="Bust" else "green"
    st.markdown(f"<p style='text-align:center; font-size:150%; color:{color};'>Action: {st.session_state['action']}</p>", unsafe_allow_html=True)

# --- Button styling ---
st.markdown("""
<style>
    .stButton>button {
        background-color: white !important;
        color: black !important;
        border: 1px solid black !important;
        border-radius: 6px;
        padding: 6px 0px;
        font-size:16px;
    }
</style>
""", unsafe_allow_html=True)
