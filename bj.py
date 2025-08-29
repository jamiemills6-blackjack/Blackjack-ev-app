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
    raw = [t.strip().upper() for t in s.split() if t.strip()]
    out = []
    for token in raw:
        if token in ("J", "Q", "K"):
            out.append("10")
        elif token == "A":
            out.append("A")
        elif token.isdigit() and token in CARD_VALUES:
            out.append(token)
        else:
            raise ValueError(f"Invalid card token: '{token}'. Use 2-10 or A.")
    return out

def best_hand_value(cards):
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
    # Splits (simplified)
    if len(player_cards) == 2 and card_value(player_cards[0]) == card_value(player_cards[1]):
        if player_cards[0] == "A" or player_cards[0] == "8":
            return "Split"
        if card_value(player_cards[0]) == 10:
            return "Stand"
    # Soft/hard totals simplified logic (keeps previous behaviour)
    if "A" in player_cards and total <= 21:
        if total <= 17:
            return "Hit"
        if total == 18:
            return "Stand" if dealer_up in ["2","7","8"] else "Hit"
        return "Stand"
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
    return sum(HI_LO_VALUES.get(c, 0) for c in cards)

# ----------------------
# Streamlit UI & state
# ----------------------
st.set_page_config(page_title="Blackjack Assistant", layout="centered")
# header 25% bigger from earlier baseline (now ~30px)
st.markdown("<h1 style='font-size:30px;margin-bottom:6px;'>Blackjack Assistant</h1>", unsafe_allow_html=True)

# CSS: thin white border around input display + compact keypad buttons with small gap (~1.5mm)
st.markdown("""
<style>
/* input display thin white border */
.field-display input[type="text"] {
  border: 1px solid #ffffff !important;
  border-radius: 6px !important;
  background-color: transparent !important;
  color: inherit !important;
  padding: 6px 8px !important;
}

/* make st buttons used for keypad smaller and tightly spaced */
div.stButton > button {
  padding: 6px 8px !important;
  margin: 3px !important; /* ~1.5mm approx on many screens */
  font-size: 16px !important;
  min-width: 48px !important;
  min-height: 42px !important;
}

/* keep big action buttons a bit more visible */
div.stButton > button.action { padding: 8px 10px !important; }

/* force narrow-layout friendliness */
@media (max-width: 480px) {
  div.stButton > button { font-size:15px !important; min-width:44px !important; min-height:40px !important; margin:3px !important; }
}
</style>
""", unsafe_allow_html=True)

# Init session state safely
if "shoe" not in st.session_state:
    st.session_state.shoe = build_shoe(8)
if "seen_cards" not in st.session_state:
    st.session_state.seen_cards = []

FIELD_KEYS = ["player_field", "others_field", "dealer_field"]
for fk in FIELD_KEYS:
    if fk not in st.session_state:
        st.session_state[fk] = ""  # visible, space-separated tokens (e.g. "10 A 5 ")

# safe append and delete
def append_token_to_field(field_key: str, token: str):
    cur = st.session_state.get(field_key, "")
    cur = cur.strip()
    if cur:
        new = cur + " " + token
    else:
        new = token
    st.session_state[field_key] = (new + " ").strip() + " "

def delete_last_token(field_key: str):
    cur = st.session_state.get(field_key, "").strip()
    if not cur:
        st.session_state[field_key] = ""
        return
    parts = cur.split()
    parts.pop()
    st.session_state[field_key] = (" ".join(parts) + " ") if parts else ""

# Render one compact field with keypad (4 columns per row)
def render_compact_field(field_key: str, label: str):
    st.markdown(f"**{label}**")
    # display as disabled text (readonly)
    display_val = st.session_state.get(field_key, "").strip()
    # create a small wrapper element to ensure CSS applies
    st.markdown(f"<div class='field-display'></div>", unsafe_allow_html=True)
    st.text_input("", value=display_val, key=f"{field_key}_display", disabled=True)

    # keypad tokens: compact layout (4 columns)
    tokens = ["2","3","4","5","6","7","8","9","10","A"]
    # rows of 4
    cols_per_row = 4
    for i in range(0, len(tokens), cols_per_row):
        row = tokens[i:i+cols_per_row]
        cols = st.columns(len(row), gap="small")
        for j, t in enumerate(row):
            btn_key = f"{field_key}_btn_{t}_{i}_{j}"
            if cols[j].button(t, key=btn_key):
                append_token_to_field(field_key, t)

    # Delete + Enter row (2 buttons)
    dcol, ecol = st.columns([1,1], gap="small")
    if dcol.button("Delete", key=f"{field_key}_del"):
        delete_last_token(field_key)
    if ecol.button("Enter", key=f"{field_key}_enter"):
        # Move logical focus to next field (store flag)
        idx = FIELD_KEYS.index(field_key)
        next_idx = (idx + 1) % len(FIELD_KEYS)
        st.session_state["_focus_next"] = FIELD_KEYS[next_idx]
        st.experimental_rerun()

# show fields; if focus flag exists, display a small hint after the relevant field
focus_next = st.session_state.pop("_focus_next", None)

render_compact_field("player_field", "Player cards")
if focus_next == "player_field":
    st.markdown("_Now focused: Player cards_")

render_compact_field("others_field", "Other players' cards")
if focus_next == "others_field":
    st.markdown("_Now focused: Other players' cards_")

render_compact_field("dealer_field", "Dealer cards (enter upcard first, then down/drawn for count)")
if focus_next == "dealer_field":
    st.markdown("_Now focused: Dealer cards_")

st.markdown("---")

# Actions
c1, c2, c3 = st.columns([1,1,1], gap="small")
with c1:
    calc_clicked = st.button("Calculate", key="calc_button")
with c2:
    next_clicked = st.button("Next Hand", key="next_button")
with c3:
    newshoe_clicked = st.button("New Shoe", key="newshoe_button")

# Mark action buttons with class 'action' where possible (visual)
# (Note: streamlit doesn't support adding classes to button elements directly,
# but the CSS above keeps action buttons readable.)

# Calculate logic
if calc_clicked:
    try:
        player_tokens = parse_cards_from_string(st.session_state.get("player_field","")) if st.session_state.get("player_field","").strip() else []
        others_tokens = parse_cards_from_string(st.session_state.get("others_field","")) if st.session_state.get("others_field","").strip() else []
        dealer_tokens = parse_cards_from_string(st.session_state.get("dealer_field","")) if st.session_state.get("dealer_field","").strip() else []

        if not dealer_tokens:
            st.error("Please enter at least the dealer upcard (first dealer card).")
        else:
            dealer_up = dealer_tokens[0]
            # commit to hidden register for counting
            st.session_state.seen_cards.extend(player_tokens + others_tokens + dealer_tokens)

            # determine advive/action
            action = recommend_action(player_tokens, dealer_up)
            total = best_hand_value(player_tokens)

            if action == "Bust":
                # display exactly "Bust" in subtle black on white box
                st.markdown(f"<div style='background:white;color:black;padding:8px;border-radius:6px;display:inline-block;'><strong>Bust</strong></div>", unsafe_allow_html=True)
            else:
                # color code: Hit green, Stand red, others orange
                color = "green" if "Hit" in action else "red" if "Stand" in action else "orange"
                st.markdown(f"<h3 style='color:{color}'>Hand total: {total} → Recommended: {action}</h3>", unsafe_allow_html=True)

    except ValueError as e:
        st.error(str(e))

# Next Hand: clear visible fields only
if next_clicked:
    for k in FIELD_KEYS:
        st.session_state[k] = ""
    st.experimental_rerun()

# New Shoe: reset shoe and seen_cards and visible fields
if newshoe_clicked:
    st.session_state.shoe = build_shoe(8)
    st.session_state.seen_cards = []
    for k in FIELD_KEYS:
        st.session_state[k] = ""
    st.success("🔄 New shoe created (8 decks).")

# Count info
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
