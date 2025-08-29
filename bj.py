# bj.py  -- single-file Blackjack Assistant (mobile-friendly single keypad)
import streamlit as st
from math import floor

# ---------------------------
#  Session init
# ---------------------------
st.set_page_config(page_title="Blackjack Assistant", layout="centered")
st.markdown("<h1 style='text-align:center; font-size:150%;'>Blackjack Assistant</h1>", unsafe_allow_html=True)

# Persistent state (committed shoe and pending entries)
if "shoe" not in st.session_state:
    st.session_state.shoe = []                 # committed cards across hands (strings like '2','10','A')
if "pending_player" not in st.session_state:
    st.session_state.pending_player = []       # pending entries not yet committed
if "pending_others" not in st.session_state:
    st.session_state.pending_others = []
if "pending_dealer" not in st.session_state:
    st.session_state.pending_dealer = []
if "active_box" not in st.session_state:
    st.session_state.active_box = "player"     # 'player' | 'other' | 'dealer'

# Calculation outputs (updated only by Calculate)
if "running_count" not in st.session_state:
    st.session_state.running_count = 0
if "true_count" not in st.session_state:
    st.session_state.true_count = 0.0
if "penetration" not in st.session_state:
    st.session_state.penetration = 0.0
if "ev" not in st.session_state:
    st.session_state.ev = 0.0
if "recommendation" not in st.session_state:
    st.session_state.recommendation = ""

# last committed player snapshot (used by basic-strategy recommendation)
if "_last_committed_player" not in st.session_state:
    st.session_state._last_committed_player = []

# default decks (widget will set this value when changed)
if "num_decks" not in st.session_state:
    st.session_state.num_decks = 8

# ---------------------------
#  Helpers: parsing & values
# ---------------------------
CARD_VALUES = {
    'A': [1, 11],
    '2': [2], '3': [3], '4': [4], '5': [5], '6': [6],
    '7': [7], '8': [8], '9': [9], '10': [10]
}

HI_LO = {'2': 1, '3': 1, '4': 1, '5': 1, '6': 1,
         '7': 0, '8': 0, '9': 0, '10': -1, 'A': -1}

def best_hand_value(cards):
    """Return best value <=21 else minimal value"""
    totals = [0]
    for c in cards:
        vals = CARD_VALUES.get(c, [0])
        totals = [t + v for t in totals for v in vals]
    under = [t for t in totals if t <= 21]
    return max(under) if under else min(totals)

def is_soft(cards):
    """Detect whether hand is soft (ace counted as 11)"""
    if 'A' not in cards:
        return False
    totals = [0]
    for c in cards:
        vals = CARD_VALUES.get(c, [0])
        totals = [t + v for t in totals for v in vals]
    # if any total <=21 and differs from min, it's soft
    return any(t <= 21 and t != min(totals) for t in totals)

def compute_running_count_from_cards(card_list):
    return sum(HI_LO.get(c, 0) for c in card_list)

# ---------------------------
#  UI: Show pending boxes (display only)
# ---------------------------
def box_display(title, cards, is_active=False):
    """Styled display for pending cards"""
    active_style = "border:2px solid #444; padding:8px; border-radius:6px;" if is_active else "border:1px solid #aaa; padding:8px; border-radius:6px;"
    st.markdown(f"**{title}**")
    st.markdown(f"<div style='{active_style}; min-height:28px;'>{' '.join(cards) if cards else '<span style=color:#777>None</span>'}</div>", unsafe_allow_html=True)

st.markdown("<div style='display:flex; gap:8px; flex-direction:column;'>", unsafe_allow_html=True)
box_display("Your cards (pending)", st.session_state.pending_player, st.session_state.active_box == "player")
box_display("Other players' cards (pending)", st.session_state.pending_others, st.session_state.active_box == "other")
box_display("Dealer cards (up/down/drawn) (pending)", st.session_state.pending_dealer, st.session_state.active_box == "dealer")
st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

# ---------------------------
#  Keypad (single, unique keys) - 4x4 grid with placeholders
# ---------------------------
# Keys we need
key_list = ['2','3','4','5','6','7','8','9','10','A','Delete','Enter']
# pad to 16 for a 4x4 visual
pad_len = 16 - len(key_list)
key_list_extended = key_list + [''] * pad_len

st.markdown("""
<style>
.keypad-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap:6px; }
.keypad-grid button { padding:10px 6px; font-size:18px; border-radius:8px; }
.keypad-enter { background:#222;color:white; }
.keypad-delete { background:#ddd;color:black; }
</style>
""", unsafe_allow_html=True)

# Create the grid using st.columns per row (ensures unique keys)
for row in range(4):
    cols = st.columns(4, gap="small")
    for col_idx in range(4):
        idx = row * 4 + col_idx
        label = key_list_extended[idx]
        if label == "":
            cols[col_idx].markdown("&nbsp;")  # placeholder cell (keeps grid shape)
            continue
        # unique key per button (index + label)
        btn_key = f"kp_{idx}_{label}"
        # style class is not directly attachable; we leave native buttons but keys are unique
        if cols[col_idx].button(label, key=btn_key):
            # handle the keypress
            active = st.session_state.active_box
            # map to appropriate pending list
            pending_map = {
                "player": st.session_state.pending_player,
                "other": st.session_state.pending_others,
                "dealer": st.session_state.pending_dealer
            }
            pending = pending_map[active]
            if label == "Delete":
                if pending:
                    pending.pop()
            elif label == "Enter":
                # commit only if pending non-empty:
                if pending:
                    # append pending to shoe
                    st.session_state.shoe.extend(pending)
                    # if committing player's pending, snapshot it for recommendation use
                    if active == "player":
                        st.session_state._last_committed_player = pending.copy()
                    # clear that pending list
                    pending.clear()
                # move active box on Enter
                if active == "player":
                    st.session_state.active_box = "other"
                elif active == "other":
                    st.session_state.active_box = "dealer"
                else:
                    st.session_state.active_box = "player"
            else:
                # normal card pressed -> append to pending
                # normalize faces: user only has keypad '10' and 'A' so OK
                pending.append(label)

st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

# ---------------------------
#  Action Buttons: Calculate, Next Hand, New Shoe
# ---------------------------
c1, c2, c3 = st.columns(3)
# Calculate: computes counts/ev/recommendation (user-controlled)
if c1.button("Calculate", key="btn_calculate"):
    # For calculation, include committed shoe + current pending across boxes (so you can enter current hand and press Calculate)
    combined_cards = st.session_state.shoe + st.session_state.pending_player + st.session_state.pending_others + st.session_state.pending_dealer
    running = compute_running_count_from_cards(combined_cards)
    decks = max(1, int(st.session_state.num_decks))
    cards_seen = len(combined_cards)
    rem_cards = max(0, decks * 52 - cards_seen)
    rem_decks = max(0.0001, rem_cards / 52.0)
    true = running / rem_decks if rem_decks > 0 else 0.0
    pen = cards_seen / (decks * 52)
    # Obtain the player hand to base recommendation on:
    # Prefer pending player if present, otherwise last committed snapshot
    if st.session_state.pending_player:
        player_hand = st.session_state.pending_player.copy()
    else:
        player_hand = st.session_state._last_committed_player.copy()
    # dealer upcard (prefer pending dealer first if present, else look into shoe)
    if st.session_state.pending_dealer:
        dealer_up = st.session_state.pending_dealer[0] if st.session_state.pending_dealer else None
    else:
        # find first dealer card in shoe? we can't tell origin—use shoe[0] as a fallback if present
        dealer_up = st.session_state.shoe[0] if st.session_state.shoe else None

    # Determine recommendation
    if not player_hand:
        rec = "No player hand entered"
    else:
        rec = recommend_basic_strategy(player_hand, dealer_up)

    # EV proxy calculation (simple approximation): advantage per true count * 0.5% per TC -> EV% = TC * 0.5%
    ev_proxy = true * 0.005
    st.session_state.running_count = running
    st.session_state.true_count = true
    st.session_state.penetration = pen
    st.session_state.ev = round(ev_proxy, 5)
    st.session_state.recommendation = rec

# Next Hand: commit any pending (player/other/dealer) to shoe and clear pending (keeps shoe)
if c2.button("Next Hand", key="btn_next_hand"):
    # commit pending if any
    if st.session_state.pending_player:
        st.session_state.shoe.extend(st.session_state.pending_player)
        st.session_state._last_committed_player = st.session_state.pending_player.copy()
        st.session_state.pending_player.clear()
    if st.session_state.pending_others:
        st.session_state.shoe.extend(st.session_state.pending_others)
        st.session_state.pending_others.clear()
    if st.session_state.pending_dealer:
        st.session_state.shoe.extend(st.session_state.pending_dealer)
        st.session_state.pending_dealer.clear()
    # active box back to player
    st.session_state.active_box = "player"

# New Shoe: clear committed shoe and pending entirely and reset counts
if c3.button("New Shoe", key="btn_new_shoe"):
    st.session_state.shoe = []
    st.session_state.pending_player = []
    st.session_state.pending_others = []
    st.session_state.pending_dealer = []
    st.session_state.running_count = 0
    st.session_state.true_count = 0.0
    st.session_state.penetration = 0.0
    st.session_state.ev = 0.0
    st.session_state.recommendation = ""
    st.session_state._last_committed_player = []
    st.session_state.active_box = "player"

st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

# ---------------------------
#  Count Info expander (drop-down)
# ---------------------------
with st.expander("Count Info"):
    # number of decks (widget key: num_decks) -> we *do not* overwrite st.session_state.num_decks afterwards
    st.session_state.num_decks = st.number_input("Number of decks", min_value=1, max_value=16, value=int(st.session_state.num_decks), key="num_decks")
    st.markdown(f"**EV (proxy):** {st.session_state.ev}")
    st.markdown(f"**True Count:** {st.session_state.true_count:.2f}")
    st.markdown(f"**Running Count:** {st.session_state.running_count}")
    st.markdown(f"**Penetration:** {st.session_state.penetration:.3f}")
    st.markdown(f"**Recommendation:** {st.session_state.recommendation}")
    st.markdown(f"**Committed cards in shoe:** {len(st.session_state.shoe)}")

# ---------------------------
#  Recommendation display (color-coded)
# ---------------------------
rec = st.session_state.get("recommendation", "")
if rec:
    color = "black"
    if rec.lower().startswith("hit"):
        color = "crimson"
    elif rec.lower().startswith("stand"):
        color = "green"
    elif rec.lower().startswith("split"):
        color = "navy"
    elif rec.lower().startswith("double"):
        color = "orange"
    elif rec.lower().startswith("bust"):
        color = "black"
    st.markdown(f"<div style='font-weight:600; padding:8px; border-radius:6px; text-align:center; color:{color};'>{rec}</div>", unsafe_allow_html=True)

# ---------------------------
#  Basic Strategy helper (conservative practical chart)
# ---------------------------
def recommend_basic_strategy(player_cards, dealer_up):
    """Return 'Hit'/'Stand'/'Split'/'Double' etc. (practical conservative basic strategy for S17)."""
    # normalize dealer
    du = dealer_up
    if du is None:
        du_val = None
    else:
        du_val = du

    # Convert ranks to numeric values (A stays 'A')
    # Pair?
    pair = False
    if len(player_cards) == 2:
        a, b = player_cards[0], player_cards[1]
        # consider 10 and face all as '10' already
        if a == b:
            pair = True
            pair_card = a

    # soft?
    soft = is_soft(player_cards)
    total = best_hand_value(player_cards)

    # Pairs first
    if pair:
        pc = pair_card
        # A,A or 8,8 always split
        if pc == 'A' or pc == '8':
            return "Split"
        if pc in ['2','3']:
            if du_val in ['2','3','4','5','6','7']:
                return "Split"
            else:
                return "Hit"
        if pc == '6':
            if du_val in ['2','3','4','5','6']:
                return "Split"
            else:
                return "Hit"
        if pc == '7':
            if du_val in ['2','3','4','5','6','7','8']:
                return "Split"
            else:
                return "Hit"
        if pc == '9':
            if du_val in ['2','3','4','5','6','8','9']:
                return "Split"
            else:
                return "Stand"
        if pc == '4':
            if du_val in ['5','6']:
                return "Split"
            else:
                return "Hit"
        if pc == '5':
            # treat as hard 10
            pass
        if pc == '10':
            # standard basic strategy: never split tens -> Stand
            return "Stand"

    # Soft totals
    if soft:
        # typical simplified rules:
        if total >= 19:
            return "Stand"
        if total == 18:
            # Stand vs 2-8, else Hit
            if du_val in ['9','10','A']:
                return "Hit"
            else:
                return "Stand"
        # soft 17 or less -> Hit (doubling options omitted)
        return "Hit"

    # Hard totals
    if total >= 17:
        return "Stand"
    if 13 <= total <= 16:
        if du_val in ['2','3','4','5','6']:
            return "Stand"
        else:
            return "Hit"
    if total == 12:
        if du_val in ['4','5','6']:
            return "Stand"
        else:
            return "Hit"
    if total <= 11:
        return "Hit"

    return "Stand"
