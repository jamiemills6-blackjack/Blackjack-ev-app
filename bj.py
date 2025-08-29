import streamlit as st

st.set_page_config(page_title="Blackjack Assistant", layout="centered")

# --- Initialize session state ---
for key in ["player", "others", "dealer", "action"]:
    if key not in st.session_state:
        st.session_state[key] = ""

# --- Helper function to calculate hand value ---
def calculate_hand(cards):
    values = []
    for c in cards.split():
        if c in ["J", "Q", "K"]:  # face cards count as 10
            values.append(10)
        elif c == "A":
            values.append(11)
        else:
            values.append(int(c))
    total = sum(values)
    # adjust for aces
    ace_count = cards.split().count("A")
    while total > 21 and ace_count > 0:
        total -= 10
        ace_count -= 1
    return total

# --- Render custom keypad for each box ---
def card_keypad(field_name, label):
    st.markdown(f"### {label}")
    st.markdown(
        f"<div style='border:1px solid white; padding:6px; border-radius:6px; min-height:40px;'>"
        f"{st.session_state[field_name]}</div>",
        unsafe_allow_html=True
    )

    cols = st.columns(4, gap="small")
    buttons = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "A", "Delete", "Enter"]

    for i, b in enumerate(buttons):
        if cols[i % 4].button(b, key=f"{field_name}_{b}", use_container_width=True):
            if b == "Delete":
                st.session_state[field_name] = " ".join(st.session_state[field_name].split()[:-1])
            elif b == "Enter":
                pass  # future: move cursor logic
            else:
                st.session_state[field_name] += f"{b} "

# --- Layout ---
st.markdown("<h1 style='text-align:center; font-size:200%;'>Blackjack Assistant</h1>", unsafe_allow_html=True)

card_keypad("player", "Your cards")
card_keypad("others", "Other players' cards")
card_keypad("dealer", "Dealer cards (up, down, drawn)")

# --- Action logic ---
if st.button("Calculate", key="calc", use_container_width=True):
    player_total = calculate_hand(st.session_state["player"])
    dealer_up = st.session_state["dealer"].split()[0] if st.session_state["dealer"] else None

    if player_total > 21:
        st.session_state["action"] = "Bust"
    elif dealer_up:
        st.session_state["action"] = "Hit" if player_total < 17 else "Stand"
    else:
        st.session_state["action"] = "Need dealer up card"

if st.button("Next Hand", key="next", use_container_width=True):
    st.session_state["player"] = ""
    st.session_state["dealer"] = ""
    st.session_state["action"] = ""

if st.button("New Shoe", key="shoe", use_container_width=True):
    for k in ["player", "others", "dealer", "action"]:
        st.session_state[k] = ""

# --- Display results ---
if st.session_state["action"]:
    if st.session_state["action"] == "Bust":
        st.markdown("<p style='text-align:center; font-size:150%; color:black;'>Bust</p>", unsafe_allow_html=True)
    else:
        st.markdown(f"<p style='text-align:center; font-size:150%; color:black;'>Action: {st.session_state['action']}</p>", unsafe_allow_html=True)

# --- Style buttons white with black text ---
st.markdown("""
<style>
    .stButton > button {
        background-color: white !important;
        color: black !important;
        border: 1px solid black !important;
        border-radius: 8px;
        padding: 6px 0px;
        font-size: 16px;
    }
</style>
""", unsafe_allow_html=True)
