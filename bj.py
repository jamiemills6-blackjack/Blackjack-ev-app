import streamlit as st

# --- Page Setup ---
st.set_page_config(page_title="Blackjack Assistant", layout="centered")

# --- Session State Initialization ---
for key in ["player", "others", "dealer", "action", "shoe_cards"]:
    if key not in st.session_state:
        st.session_state[key] = "" if key != "shoe_cards" else []

# --- Helper Functions ---
def card_value(c):
    if c == "A":
        return 11
    return int(c)

def calculate_hand(cards_str):
    cards = cards_str.split()
    total = sum(card_value(c) for c in cards)
    aces = cards.count("A")
    while total > 21 and aces > 0:
        total -= 10
        aces -= 1
    return total

def commit_cards(cards_str):
    for c in cards_str.split():
        st.session_state.shoe_cards.append(c)

def running_count():
    count = 0
    for c in st.session_state.shoe_cards:
        if c in ["2","3","4","5","6"]:
            count += 1
        elif c in ["10","A"]:
            count -=1
    return count

# --- Keypad HTML/CSS ---
def card_keypad(field_name, label):
    st.markdown(f"### {label}")
    st.markdown(f"<div style='border:1px solid white; padding:6px; border-radius:6px; min-height:40px;'>{st.session_state[field_name]}</div>", unsafe_allow_html=True)

    buttons = ["2","3","4","5","6","7","8","9","10","A","Delete","Enter"]
    html_buttons = "<div style='display:grid; grid-template-columns:repeat(4,1fr); gap:1.5mm;'>"
    for b in buttons:
        html_buttons += f"""<button onclick="fetch('/_stcore', {{method:'POST', body:JSON.stringify({{'button':'{field_name}_{b}'}})}})" 
        style='padding:10px; font-size:16px; border-radius:6px; border:1px solid black; background-color:white; color:black;'>{b}</button>"""
    html_buttons += "</div>"
    st.markdown(html_buttons, unsafe_allow_html=True)

    # Capture button presses
    for b in buttons:
        key = f"{field_name}_{b}"
        if st.button(key, key=key):
            if b=="Delete":
                st.session_state[field_name] = " ".join(st.session_state[field_name].split()[:-1])
            elif b=="Enter":
                commit_cards(st.session_state[field_name])
            else:
                st.session_state[field_name] += f"{b} "

# --- Header ---
st.markdown("<h1 style='text-align:center; font-size:125%;'>Blackjack Assistant</h1>", unsafe_allow_html=True)

# --- Inputs ---
card_keypad("player", "Your cards")
card_keypad("others", "Other players' cards")
card_keypad("dealer", "Dealer cards (up, down, drawn)")

# --- Action Buttons ---
cols_action = st.columns(3)
if cols_action[0].button("Calculate"):
    player_total = calculate_hand(st.session_state["player"])
    dealer_up = st.session_state["dealer"].split()[0] if st.session_state["dealer"] else None
    if player_total > 21:
        st.session_state["action"] = "Bust"
    elif dealer_up:
        st.session_state["action"] = "Hit" if player_total < 17 else "Stand"
    else:
        st.session_state["action"] = "Need dealer up card"

if cols_action[1].button("Next Hand"):
    commit_cards(st.session_state["player"])
    commit_cards(st.session_state["others"])
    commit_cards(st.session_state["dealer"])
    st.session_state["player"] = ""
    st.session_state["others"] = ""
    st.session_state["dealer"] = ""
    st.session_state["action"] = ""

if cols_action[2].button("New Shoe"):
    st.session_state["player"] = ""
    st.session_state["others"] = ""
    st.session_state["dealer"] = ""
    st.session_state["action"] = ""
    st.session_state["shoe_cards"] = []

# --- Count Info ---
with st.expander("Count Info"):
    decks = st.number_input("Number of decks", min_value=1, value=8, step=1)
    st.markdown(f"**Running Count:** {running_count()}")
    total_cards = decks*52
    penetration = len(st.session_state.shoe_cards)/total_cards
    st.markdown(f"**Penetration:** {penetration:.2%}")

# --- Display Action ---
if st.session_state["action"]:
    color = "black" if st.session_state["action"]=="Bust" else "green"
    st.markdown(f"<p style='text-align:center; font-size:150%; color:{color};'>Action: {st.session_state['action']}</p>", unsafe_allow_html=True)
