# bj.py
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
    return sum(HI_LO_VALUES.get(c, 0) for c in cards)

# ----------------------
# Streamlit UI & state
# ----------------------
st.set_page_config(page_title="Blackjack Assistant", layout="centered")
st.markdown("<h1 style='font-size:30px;margin-bottom:6px;'>Blackjack Assistant</h1>", unsafe_allow_html=True)

# CSS: white thin border around the display fields, small keypad buttons, tight spacing (~1.5mm)
st.markdown("""
<style>
/* thin white border for the readonly displays */
.field-display input[type="text"] {
  border: 1px solid #ffffff !important;
  border-radius: 6px !important;
  padding: 6px 8px !important;
  background-color: transparent !important;
  color: inherit !important;
}

/* keypad buttons compact, tight spacing */
div.stButton > button {
  padding: 6px 6px !important;
  margin: 3px !important; /* ~1.5mm approximation */
  font-size: 16px !important;
  min-width: 46px !important;
  min-height: 40px !important;
  border-radius: 6px !important;
}

/* force all main action buttons to white with black text */
div.stButton > button {
  background-color: white !important;
  color: black !important;
  border: 1px solid #000000 !important;
}

/* slightly smaller on tiny screens */
@media (max-width: 420px) {
  div.stButton > button { font-size:15px !important; min-width:40px !important; min-height:36px !important; margin:2px !important; }
}
</style>
""", unsafe_allow_html=True)

# Initialize session state safely
if "shoe" not in st.session_state:
    st.session_state.shoe = build_shoe(8)
if "seen_cards" not in st.session_state:
    st.session_state.seen_cards = []

FIELD_KEYS = ["player_field", "others_field", "dealer_field"]
for fk in FIELD_KEYS:
    if fk not in st.session_state:
        st.session_state[fk] = ""  # visible fields (space-separated tokens)

# safe append and delete helpers
def append_token_to_field(field_key: str, token: str):
    cur = st.session_state.get(field_key, "").strip()
    new = (cur + " " + token).strip() if cur else token
    # store with a trailing space for consistent display logic
    st.session_state[field_key] = (new + " ").strip() + " "

def delete_last_token(field_key: str):
    cur = st.session_state.get(field_key, "").strip()
    if not cur:
        st.session_state[field_key] = ""
        return
    parts = cur.split()
    parts.pop()
    st.session_state[field_key] = (" ".join(parts) + " ") if parts else ""

# Render one compact field with strict 4x4 keypad (placeholders keep grid)
def render_compact_4x4_field(field_key: str, label: str):
    st.markdown(f"**{label}**")
    display_val = st.session_state.get(field_key, "").strip()
    # wrapper so CSS applies
    st.markdown(f"<div class='field-display'></div>", unsafe_allow_html=True)
    st.text_input("", value=display_val, key=f"{field_key}_display", disabled=True)

    # tokens we need (2-10, A, Delete, Enter) -> total 12 tokens
    core_tokens = ["2","3","4","5","6","7","8","9","10","A","Delete","Enter"]
    # We must lay out in strict 4x4 grid (16 cells) — create 4 placeholders to fill
    grid_tokens = core_tokens + [""] * (16 - len(core_tokens))  # empties are placeholders
    # draw rows of 4
    for i in range(0, 16, 4):
        row = grid_tokens[i:i+4]
        cols = st.columns(4, gap="small")
        for j, token in enumerate(row):
            col = cols[j]
            if token == "":
                # placeholder: small invisible block to keep layout
                col.markdown("<div style='width:46px;height:40px;display:inline-block;'></div>", unsafe_allow_html=True)
            else:
                # unique key per token+field
                btn_key = f"{field_key}_btn_{token}_{i}_{j}"
                if col.button(token, key=btn_key):
                    if token == "Delete":
                        delete_last_token(field_key)
                    elif token == "Enter":
                        # move logical focus (store flag)
                        idx = FIELD_KEYS.index(field_key)
                        next_idx = (idx + 1) % len(FIELD_KEYS)
                        st.session_state["_focus_next"] = FIELD_KEYS[next_idx]
                        # short-circuit: rerun to show hint
                        st.experimental_rerun()
                    else:
                        append_token_to_field(field_key, token)

# Render fields (portrait friendly)
focus_next = st.session_state.pop("_focus_next", None)

render_compact_4x4_field("player_field", "Player cards")
if focus_next == "player_field":
    st.markdown("_Now focused: Player cards_")

render_compact_4x4_field("others_field", "Other players' cards")
if focus_next == "others_field":
    st.markdown("_Now focused: Other players' cards_")

render_compact_4x4_field("dealer_field", "Dealer cards (enter UP card first; others count only)")
if focus_next == "dealer_field":
    st.markdown("_Now focused: Dealer cards_")

st.markdown("---")

# Actions: Calculate / Next Hand / New Shoe (all will be white text-black per CSS above)
c1, c2, c3 = st.columns([1,1,1], gap="small")
with c1:
    calc_clicked = st.button("Calculate", key="calc_button")
with c2:
    next_clicked = st.button("Next Hand", key="next_button")
with c3:
    newshoe_clicked = st.button("New Shoe", key="newshoe_button")

# Calculate logic (safe parsing + commit to seen_cards)
if calc_clicked:
    try:
        player_tokens = parse_cards_from_string(st.session_state.get("player_field","")) if st.session_state.get("player_field","").strip() else []
        others_tokens = parse_cards_from_string(st.session_state.get("others_field","")) if st.session_state.get("others_field","").strip() else []
        dealer_tokens = parse_cards_from_string(st.session_state.get("dealer_field","")) if st.session_state.get("dealer_field","").strip() else []
        if not player_tokens:
            st.error("Please enter your player cards before calculating.")
        elif not dealer_tokens:
            st.error("Please enter at least the dealer upcard (first dealer card).")
        else:
            dealer_up = dealer_tokens[0]
            # commit to seen_cards for count (hidden register)
            st.session_state.seen_cards.extend(player_tokens + others_tokens + dealer_tokens)
            # get action
            action = recommend_action(player_tokens, dealer_up)
            total = best_hand_value(player_tokens)
            if action == "Bust":
                # show exactly "Bust" in subtle black & white
                st.markdown("<div style='background:white;color:black;padding:8px;border-radius:6px;display:inline-block;'><strong>Bust</strong></div>", unsafe_allow_html=True)
            else:
                # color-code (Hit green, Stand red, others orange)
                if "Hit" in action:
                    color = "green"
                elif "Stand" in action:
                    color = "red"
                else:
                    color = "orange"
                st.markdown(f"<h3 style='color:{color}'>Hand total: {total} → Recommended: {action}</h3>", unsafe_allow_html=True)
    except ValueError as e:
        st.error(str(e))

# Next Hand: clear visible fields only, keep seen_cards
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

# Count info in expander (decks input placed here)
with st.expander("📊 Count info"):
    num_decks = st.number_input("Number of decks in shoe", min_value=1, max_value=12, value=8, step=1)
    seen = st.session_state.get("seen_cards", [])
    total_cards = 52 * num_decks
    remaining_cards = max(0, total_cards - len(seen))
    rc = running_count(seen)
    decks_remaining = max(1, remaining_cards / 52)
    tc = round(rc / decks_remaining, 2) if decks_remaining > 0 else 0.0
    penetration = round(len(seen) / total_cards * 100, 1) if total_cards > 0 else 0.0

    st.write("Seen cards so far:", seen)
    st.write("Cards remaining in shoe:", remaining_cards)
    st.write(f"Running count: {rc}")
    st.write(f"True count: {tc}")
    st.write(f"Shoe penetration: {penetration}%")
