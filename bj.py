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

def best_hand_value(cards_str):
    cards = cards_str.split()
    total = sum(card_value(c) for c in cards)
    aces = cards.count("A")
    while total > 21 and aces:
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
            count -= 1
    return count

def true_count(running, decks):
    return running / decks if decks else running

def expected_value(player_total, dealer_up):
    if player_total > 21:
        return -1.0
    if player_total >= 17:
        return 0.5
    if dealer_up:
        return 0.2
    return 0.0

# --- Keypad Function ---
def card_keypad(field_name, label):
    st.markdown(f"### {label}")
    st.markdown(f"<div style='border:1px solid white; padding:6px; border-radius:6px; min-height:40px;'>{st.session_state[field_name]}</div>", unsafe_allow_html=True)

    keys = ["2","3","4","5","6","7","8","9","10","A","Delete","Enter"]
    cols = st.columns(4)
    i=0
    for k in keys:
        if cols[i%4].button(k, key=f"{field_name}_{k}"):
            if k=="Delete":
                st.session_state[field_name] = " ".join(st.session_state[field_name].split()[:-1])
            elif k=="Enter":
                commit_cards(st.session_state[field_name])
            else:
                st.session_state[field_name] += f"{k} "
        i+=1

# --- Header ---
st.markdown("<h1 style='text-align:center; font-size:125%;'>Blackjack Assistant</h1>", unsafe_allow_html=True)

# --- Inputs ---
card_keypad("player", "Your cards")
card_keypad("others", "Other players' cards")
card_keypad("dealer", "Dealer cards (up, down, drawn)")

# --- Action Buttons ---
cols_action = st.columns(3)
if cols_action[0].button("Calculate"):
    player_total = best_hand_value(st.session_state["player"])
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
    rc = running_count()
    tc = true_count(rc, decks)
    player_total = best_hand_value(st.session_state["player"])
    dealer_up = st.session_state["dealer"].split()[0] if st.session_state["dealer"] else None
    ev = expected_value(player_total, dealer_up)
    st.markdown(f"**Expected Value (EV):** {ev:.2f}")
    st.markdown(f"**True Count:** {tc:.2f}")
    st.markdown(f"**Running Count:** {rc}")
    penetration = len(st.session_state.shoe_cards)/(decks*52)
    st.markdown(f"**Penetration:** {penetration:.2%}")

# --- Display Action ---
if st.session_state["action"]:
    color = "black" if st.session_state["action"]=="Bust" else "green"
    st.markdown(f"<p style='text-align:center; font-size:150%; color:{color};'>Action: {st.session_state['action']}</p>", unsafe_allow_html=True)
