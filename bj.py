# blackjack_assistant.py
import streamlit as st
import random

# ----------------------
# Core blackjack logic
# ----------------------
CARD_VALUES = {
    "A": [1, 11],
    "2": [2], "3": [3], "4": [4], "5": [5],
    "6": [6], "7": [7], "8": [8], "9": [9],
    "10": [10],
}

HI_LO_VALUES = {
    "2": +1, "3": +1, "4": +1, "5": +1, "6": +1,
    "7": 0, "8": 0, "9": 0, "10": -1, "A": -1,
}

VALID_CARDS = set(CARD_VALUES.keys())

def build_shoe(num_decks=8):
    cards = list(CARD_VALUES.keys())
    shoe = cards * 4 * num_decks
    random.shuffle(shoe)
    return shoe

def parse_cards_from_string(s: str):
    """Expect space-separated tokens like '10 A 5' or 'A 10'."""
    raw = [t.strip().upper() for t in s.split() if t.strip()]
    out = []
    for token in raw:
        # accept only 2-10 or A; treat J/Q/K as 10 if they appear
        if token in ("J","Q","K"):
            out.append("10")
        elif token == "A":
            out.append("A")
        elif token.isdigit() and token in CARD_VALUES:
            out.append(token)
        else:
            raise ValueError(f"Invalid card token: '{token}'. Use 2-10 or A.")
    return out

def best_hand_value(cards):
    """Return best value <=21 or minimal bust value."""
    totals = [0]
    for c in cards:
        new = []
        for v in CARD_VALUES[c]:
            for t in totals:
                new.append(t + v)
        totals = new
    valid = [t for t in totals if t <= 21]
    return max(valid) if valid else min(totals)

def card_value(card):
    return CARD_VALUES[card][0]

def recommend_action(player_cards, dealer_up):
    total = best_hand_value(player_cards)
    if total > 21:
        return "Bust"
    # Pair / split checks (10-values considered 10)
    if len(player_cards) == 2 and card_value(player_cards[0]) == card_value(player_cards[1]):
        if player_cards[0] == "A" or player_cards[0] == "8":
            return "Split"
        if card_value(player_cards[0]) == 10:
            return "Stand"
        # other splits simplified
    # Soft totals
    if "A" in player_cards and total <= 21:
        if total <= 17:
            return "Hit"
        if total == 18:
            return "Stand" if dealer_up in ["2","7","8"] else "Hit"
        return "Stand"
    # Hard totals
    if total >= 17:
        return "Stand"
    if 13 <= total <= 16:
        return "Stand" if dealer_up in ["2","3","4","5","6"] else "Hit"
    if total == 12:
        return "Stand" if dealer_up in ["4","5","6"] else "Hit"
    if total == 11:
        return "Double if allowed, otherwise Hit"
    if total == 10:
        return "Double if allowed vs dealer 2–9, otherwise Hit"
    if total == 9:
        return "Double if allowed vs dealer 3–6, otherwise Hit"
    return "Hit"

def running_count(cards):
    return sum(HI_LO_VALUES.get(c,0) for c in cards)

# ----------------------
# Streamlit UI & state
# ----------------------
st.set_page_config(page_title="Blackjack Assistant", layout="centered")
st.markdown("<h1 style='font-size:30px;margin-bottom:6px;'>Blackjack Assistant</h1>", unsafe_allow_html=True)

# Initialize forced state keys
if "shoe" not in st.session_state:
    st.session_state.shoe = build_shoe(8)
if "seen_cards" not in st.session_state:
    st.session_state.seen_cards = []

# fields that hold visible input (space-separated tokens)
FIELD_KEYS = [
    "player_field",        # player's cards
    "others_field",        # other players' cards
    "dealer_field",        # all dealer cards in sequence: first = upcard, rest are down/drawn
]

for k in FIELD_KEYS:
    if k not in st.session_state:
        st.session_state[k] = ""  # e.g. "10 A 5 "

# Utility helpers for safe update (avoid += in-place issues)
def append_to_field(field_key: str, token: str):
    cur = st.session_state.get(field_key, "")
    if cur and not cur.endswith(" "):
        cur = cur + " "
    st.session_state[field_key] = (cur + token + " ").strip() + " "

def delete_from_field(field_key: str):
    cur = st.session_state.get(field_key, "").strip()
    if not cur:
        st.session_state[field_key] = ""
        return
    parts = cur.split()
    parts = parts[:-1]
    st.session_state[field_key] = (" ".join(parts) + " ") if parts else ""

# ------------------------------------------------------------------
# Compact keypad grid UI generator (small buttons), per active field
# ------------------------------------------------------------------
def render_field_ui(field_key: str, label: str):
    st.markdown(f"**{label}**")
    # display current value (readonly)
    display = st.session_state.get(field_key, "").strip()
    if display == "":
        st.markdown("_(empty)_")
    else:
        st.markdown(f"`{display}`")

    # keypad: small grid (5 columns)
    card_buttons = ["2","3","4","5","6","7","8","9","10","A"]
    cols_per_row = 5
    for i in range(0, len(card_buttons), cols_per_row):
        cols = st.columns(cols_per_row)
        row = card_buttons[i:i+cols_per_row]
        for j, card in enumerate(row):
            # unique key for each button per field
            bkey = f"{field_key}_btn_{card}"
            if cols[j].button(card, key=bkey):
                # safe append
                append_to_field(field_key, card)

    # Delete and Enter small buttons
    dcol, ecol = st.columns([1,1])
    if dcol.button("Delete", key=f"{field_key}_del"):
        delete_from_field(field_key)
    if ecol.button("Enter", key=f"{field_key}_enter"):
        # Move logical focus to next field by setting a flag in session_state
        cur_index = FIELD_KEYS.index(field_key)
        next_index = (cur_index + 1) % len(FIELD_KEYS)
        st.session_state["_focus_next"] = FIELD_KEYS[next_index]
        # no direct DOM focus; we show the target field at top and a tiny hint
        st.experimental_rerun()

# Render fields in order; if a focus was requested, show a small hint
focus_next = st.session_state.pop("_focus_next", None)

# Render each field UI (compact)
for fk, label in zip(FIELD_KEYS, ["Player cards", "Other players' cards", "Dealer cards (first = upcard)"]):
    render_field_ui(fk, label)
    if focus_next == fk:
        st.markdown(f"_: Now focused — press keypad to add cards to **{label}**._")

st.markdown("---")

# -------------------
# Action buttons row
# -------------------
col1, col2, col3 = st.columns([1,1,1])
with col1:
    calc_clicked = st.button("Calculate", key="calc_button")
with col2:
    next_clicked = st.button("Next Hand", key="next_button")
with col3:
    newshoe_clicked = st.button("New Shoe", key="newshoe_button")

# Button colours (attempt; also keep buttons accessible)
st.markdown("""
<style>
div.stButton > button[title="Calculate"] {background-color: white; color: black;}
div.stButton > button[title="Next Hand"] {background-color: #cccccc; color: black;}
div.stButton > button[title="New Shoe"] {background-color: black; color: white;}
/* fallback selectors */
div.stButton > button:first-child {background-color: white; color: black;}
div.stButton > button:nth-of-type(2) {background-color: #cccccc; color: black;}
div.stButton > button:nth-of-type(3) {background-color: black; color: white;}
</style>
""", unsafe_allow_html=True)

# -------------------
# Actions for Calculate / Next / New Shoe
# -------------------
if calc_clicked:
    # Parse fields safely and update seen_cards (hidden register)
    try:
        player_tokens = parse_cards_from_string(st.session_state.get("player_field",""))
        others_tokens = parse_cards_from_string(st.session_state.get("others_field","")) if st.session_state.get("others_field","").strip() else []
        dealer_tokens_all = parse_cards_from_string(st.session_state.get("dealer_field","")) if st.session_state.get("dealer_field","").strip() else []
        # Dealer upcard is first token if present
        if not dealer_tokens_all:
            st.error("Please enter at least the dealer upcard (first dealer card).")
        else:
            dealer_up = dealer_tokens_all[0]
            # Add everything to seen_cards for counting (players, dealer all, others)
            st.session_state.seen_cards.extend(player_tokens + others_tokens + dealer_tokens_all)
            # Recommendation uses dealer_up only
            advice = recommend_action(player_tokens, dealer_up)
            total = best_hand_value(player_tokens)
            # Colouring: bust -> subtle black, others colour-coded
            if advice == "Bust":
                color = "black"
                bg_style = "background-color: white; color: black;"
            elif "Hit" in advice:
                color = "green"
                bg_style = ""
            elif "Stand" in advice:
                color = "red"
                bg_style = ""
            else:
                color = "orange"
                bg_style = ""
            # show result
            if advice == "Bust":
                st.markdown(f"<div style='{bg_style}padding:8px;border-radius:4px;'><strong>Hand total: {total} → Recommended: {advice}</strong></div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<h3 style='color:{color}'>Hand total: {total} → Recommended: {advice}</h3>", unsafe_allow_html=True)
    except ValueError as e:
        st.error(str(e))

if next_clicked:
    # Clear visible inputs only; keep st.session_state.seen_cards
    for k in FIELD_KEYS:
        st.session_state[k] = ""
    # no need to rerun but we do to refresh UI
    st.experimental_rerun()

if newshoe_clicked:
    st.session_state.shoe = build_shoe(8)
    st.session_state.seen_cards = []
    for k in FIELD_KEYS:
        st.session_state[k] = ""
    st.success("🔄 New shoe created and seen cards cleared.")

# -------------------
# Count info (expander)
# -------------------
with st.expander("📊 Count info"):
    num_decks = st.number_input("Number of decks in shoe", min_value=1, max_value=12, value=8, step=1)
    seen = st.session_state.get("seen_cards", [])
    total_cards = 52 * num_decks
    remaining_cards = total_cards - len(seen)
    rc = running_count(seen)
    decks_remaining = max(1, remaining_cards / 52)
    tc = round(rc / decks_remaining, 2)
    penetration = round(len(seen) / total_cards * 100, 1)

    st.write("Seen cards so far:", seen)
    st.write("Cards remaining in shoe:", remaining_cards)
    st.write(f"Running count: {rc}")
    st.write(f"True count: {tc}")
    st.write(f"Shoe penetration: {penetration}%")
