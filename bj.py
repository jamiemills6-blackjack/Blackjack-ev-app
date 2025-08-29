import streamlit as st

# ----------------------------
# Blackjack Helper Functions
# ----------------------------

CARD_VALUES = {
    "2": [2], "3": [3], "4": [4], "5": [5], "6": [6],
    "7": [7], "8": [8], "9": [9], "10": [10],
    "A": [1, 11]
}

def hand_value(cards):
    """Calculate best hand value (handle Aces)."""
    values = [0]
    for c in cards:
        new_values = []
        if c not in CARD_VALUES:
            continue
        for v in CARD_VALUES[c]:
            for total in values:
                new_values.append(total + v)
        values = new_values
    best = max([v for v in values if v <= 21], default=min(values))
    return best

def recommend_action(player_cards, dealer_card):
    """Very basic blackjack strategy (demo)."""
    total = hand_value(player_cards)
    if total > 21:
        return "Bust"
    if total >= 17:
        return "Stand"
    if total <= 11:
        return "Hit"
    if dealer_card in ["7", "8", "9", "10", "A"] and total < 17:
        return "Hit"
    return "Stand"

# ----------------------------
# Custom Keypad Input
# ----------------------------

FIELD_KEYS = ["player", "others", "dealer"]

def append_token_to_field(field_name, token):
    st.session_state[field_name] = st.session_state.get(field_name, "") + token + " "

def delete_last_token(field_name):
    current = st.session_state.get(field_name, "").strip().split()
    if current:
        current.pop()
    st.session_state[field_name] = " ".join(current) + " "

def render_compact_4x4_field(field_key: str, label: str):
    st.markdown(f"<div style='margin-bottom:4px;'><b>{label}</b></div>", unsafe_allow_html=True)
    display_val = st.session_state.get(field_key, "").strip()
    st.text_input("", value=display_val, key=f"{field_key}_display", disabled=True,
                  label_visibility="collapsed")

    core_tokens = ["2","3","4","5","6","7","8","9","10","A","Delete","Enter"]
    grid_tokens = core_tokens + [""] * (16 - len(core_tokens))

    html = """
    <style>
    .grid-container {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 6px;
        justify-items: center;
        margin: 6px 0;
    }
    .grid-container button {
        width: 100%;
        min-height: 50px;
        font-size: 18px;
        border-radius: 6px;
        background: white;
        color: black;
        border: 1px solid #000;
    }
    </style>
    <div class="grid-container">
    """
    for token in grid_tokens:
        if token == "":
            html += "<div></div>"
        else:
            form_key = f"{field_key}_{token}"
            html += f"""
            <form action="" method="post">
                <button name="{form_key}" type="submit">{token}</button>
            </form>
            """
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)

# ----------------------------
# Streamlit App
# ----------------------------

st.markdown(
    "<h1 style='font-size:225%; text-align:center;'>Blackjack Assistant</h1>",
    unsafe_allow_html=True
)

# Thin white border around text boxes
st.markdown(
    """
    <style>
    .stTextInput > div > div > input {
        border: 1px solid white;
    }
    </style>
    """, unsafe_allow_html=True
)

# Input fields
render_compact_4x4_field("player", "Your cards")
render_compact_4x4_field("others", "Other players' cards")
render_compact_4x4_field("dealer", "Dealer cards (up, down, drawn)")

# Calculate button
if st.button("Calculate", key="calc", type="secondary"):
    player_cards = st.session_state.get("player", "").strip().split()
    dealer_cards = st.session_state.get("dealer", "").strip().split()
    dealer_up = dealer_cards[0] if dealer_cards else None

    if not player_cards or not dealer_up:
        st.warning("Enter at least your cards and dealer’s upcard.")
    else:
        action = recommend_action(player_cards, dealer_up)
        if action == "Bust":
            st.markdown("<div style='color:black; font-weight:bold;'>Bust</div>", unsafe_allow_html=True)
        elif action == "Hit":
            st.markdown("<div style='color:red; font-weight:bold;'>Hit</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div style='color:green; font-weight:bold;'>Stand</div>", unsafe_allow_html=True)

# Next hand button
if st.button("Next Hand", key="next", type="secondary"):
    for k in FIELD_KEYS:
        st.session_state[k] = ""

# New shoe button
if st.button("New Shoe", key="shoe", type="secondary"):
    for k in FIELD_KEYS:
        st.session_state[k] = ""
