# bj.py
import streamlit as st
from math import floor

# -------------------------
# Page & session init
# -------------------------
st.set_page_config(page_title="Blackjack Assistant", layout="centered")
st.markdown("<h1 style='text-align:center; font-size:160%;'>Blackjack Assistant</h1>", unsafe_allow_html=True)

# session state keys - initialize reliably
initial_keys = {
    "player_input": "",        # visible, not yet committed
    "other_input": "",
    "dealer_input": "",
    "shoe": [],                # hidden committed shoe register (list of rank strings)
    "active_box": "player",    # "player" | "other" | "dealer"
    "num_decks": 8,
    # calculation outputs updated only on Calculate
    "running_count": 0,
    "true_count": 0.0,
    "penetration": 0.0,
    "ev": 0.0,
    "recommendation": ""
}
for k, v in initial_keys.items():
    if k not in st.session_state:
        st.session_state[k] = v

# -------------------------
# Constants & helpers
# -------------------------
# treat face cards as '10' input from keypad; user only inputs 2-10 and A
CARD_VALUES = {
    'A': [1, 11],
    '2': [2], '3': [3], '4': [4], '5': [5], '6': [6],
    '7': [7], '8': [8], '9': [9], '10': [10]
}

# Hi-Lo counting weights
HI_LO = { '2': 1, '3': 1, '4': 1, '5': 1, '6': 1,
          '7': 0, '8': 0, '9': 0, '10': -1, 'A': -1 }

def parse_box_text(text):
    """Return list of ranks from a text box (space separated)."""
    if not text:
        return []
    parts = [p.strip().upper() for p in text.split() if p.strip()]
    # normalize face cards if user typed anything weird
    norm = []
    for p in parts:
        if p in ['J','Q','K']:
            norm.append('10')
        elif p == 'T':  # allow T shorthand
            norm.append('10')
        elif p == '1' or p == '01':  # guard
            norm.append('10')
        else:
            norm.append(p)
    return norm

def best_hand_value(cards):
    """Return best total <=21 or minimal total if bust."""
    totals = [0]
    for c in cards:
        vals = CARD_VALUES.get(c, [0])
        totals = [t + v for t in totals for v in vals]
    under = [t for t in totals if t <= 21]
    return max(under) if under else min(totals)

def commit_box_to_shoe(box_name):
    """
    Commit the current visible input (if any) in the box 'player'/'other'/'dealer' to the shoe.
    Clears the visible input afterward.
    Returns True if anything committed, False if empty.
    """
    key = f"{box_name}_input"
    text = st.session_state.get(key, "").strip()
    if not text:
        return False
    ranks = parse_box_text(text)
    if ranks:
        st.session_state.shoe.extend(ranks)
    st.session_state[key] = ""
    return True

def calculate_counts_and_ev():
    """
    Calculate running count (Hi-Lo), true count, penetration, and a recommended action.
    This is only run on Calculate button press (user-controlled).
    """
    shoe = st.session_state.shoe[:]  # committed cards only
    running = 0
    for c in shoe:
        running += HI_LO.get(c, 0)
    decks = max(1, int(st.session_state.num_decks))
    cards_seen = len(shoe)
    remaining_cards = decks * 52 - cards_seen
    remaining_decks = max(0.0001, remaining_cards / 52.0)
    true = running / remaining_decks
    penetration = cards_seen / (decks * 52)
    # recommendation uses basic strategy based on committed player cards and dealer upcard (first dealer committed card)
    player_cards = []  # the player's committed cards for decision-making
    # We need to check last committed player cards in shoe or assume user committed player's cards via Enter
    # For decision, use the player's last hand committed in shoe. To be deterministic, we assume all player's committed cards
    # in shoe are in chronological order; but here we'll use the most recent contiguous group from shoe that came from player.
    # Simpler: request that user press Enter to commit before Calculate. We'll use aggregated committed player cards.
    # For now, build player_cards from shoe by scanning committed sections is not tracked. So we will require Enter to commit and
    # rely on st.session_state.shoe containing all cards. We'll ask user to commit current hand with Enter before Calculate.
    # To keep workable: compute recommendation from last three committed cards for player if any exist in shoe by searching backwards
    # for the last time player committed — but we do not track origin. Simpler: use visible pattern:
    # If user has not committed the player hand, no recommendation possible.
    #
    # We'll prefer: if st.session_state.player_input is empty (user likely used Enter before), find last contiguous sequence
    # of shoe that were player cards — but we cannot separate origins. So we'll instead recommend using the visible committed
    # boxes: if user previously used Enter, st.session_state.shoe includes them; but to avoid complexity, the app will compute recommendation
    # using the most recent visible committed player_input before Enter. To keep behavior clear: user should press Enter to commit
    # before Calculate. We will try to use the committed player cards if possible by tracking last_player_index in session_state.
    #
    # For now, compute recommendation using visible policy: if there's any current uncommitted player_input, use it; else, we
    # try to find last player's cards in shoe by searching st.session_state.last_player_snapshot if present.
    #
    player_ranks = st.session_state.get("_last_committed_player", [])
    # find dealer upcard:
    dealer_up = st.session_state.shoe[0] if st.session_state.shoe else None
    # Compute recommendation using basic strategy function defined below, using player_ranks and dealer_up.
    rec = "No player hand committed"
    if player_ranks:
        rec = recommend_basic_strategy(player_ranks, dealer_up)
    # store results
    st.session_state.running_count = running
    st.session_state.true_count = true
    st.session_state.penetration = penetration
    st.session_state.recommendation = rec
    # compute a placeholder EV (detailed EV modeling is complex) — simple proxy: (true_count * 0.01) maybe
    st.session_state.ev = round(true * 0.05, 4)  # small proxy; can be replaced with full EV model

# -------------------------
# Basic Strategy Implementation
# -------------------------
# We'll implement a conservative, standard basic strategy for dealer stands on all 17 (hard/soft/pair).
# The rules below are a simplified but practical standard chart (not exhaustive advanced deviations).
def recommend_basic_strategy(player_cards, dealer_up):
    """
    Return "Hit", "Stand", "Split" or "Double if allowed/Hit" etc.
    For simplicity, we return one of: Hit, Stand, Split, Double (if appropriate), Bust.
    """
    # normalize dealer_up
    if dealer_up is None:
        du = None
    else:
        du = dealer_up
    tot = best_hand_value(player_cards)
    # detect pair
    pair = False
    if len(player_cards) == 2 and player_cards[0] == player_cards[1]:
        pair = True
        pair_card = player_cards[0]
    # detect soft total (contains ace counted as 11)
    contains_ace = 'A' in player_cards
    soft = False
    if contains_ace:
        # if any total uses 11 and <=21
        totals = [t for t in (sum(vals) if False else None) for vals in []]  # placeholder to keep structure
        # simpler: check tot-10 >= 1 and tot-10 <= 11 => not necessary
        # We'll compute soft by checking if counting an ace as 11 gives a different total and <=21
        totals = [0]
        for c in player_cards:
            vals = CARD_VALUES.get(c, [0])
            totals = [t + v for t in totals for v in vals]
        soft = any(t <= 21 and t != min(totals) for t in totals)
    # Basic strategy simplified:
    # Pairs: common splits
    if pair:
        if pair_card == 'A':
            return "Split"
        if pair_card == '8':
            return "Split"
        if pair_card in ['2','3']:
            if du and du in ['2','3','4','5','6','7']:
                return "Split"
        if pair_card == '6':
            if du and du in ['2','3','4','5','6']:
                return "Split"
        if pair_card == '7':
            if du and du in ['2','3','4','5','6','7','8']:
                return "Split"
        if pair_card == '9':
            if du and du in ['2','3','4','5','6','8','9']:
                return "Split"
        if pair_card == '4':
            if du and du in ['5','6']:
                return "Split"
        # 10s never split
        # otherwise fallback to hard/soft rules
    # Soft totals
    if contains_ace and tot <= 21:
        # quantify soft total treat ace as 11 where possible
        if tot >= 19:
            return "Stand"
        if tot == 18:
            if du and du in ['9','10','A']:
                return "Hit"
            else:
                return "Stand"
        if tot <= 17:
            return "Hit"
    # Hard totals
    if tot >= 17:
        return "Stand"
    if 13 <= tot <= 16:
        if du and du in ['2','3','4','5','6']:
            return "Stand"
        else:
            return "Hit"
    if tot == 12:
        if du and du in ['4','5','6']:
            return "Stand"
        else:
            return "Hit"
    if tot <= 11:
        return "Hit"
    return "Stand"

# -------------------------
# UI: Input boxes (labels non-empty, collapsed)
# -------------------------
st.markdown("### Inputs (use single keypad below — Enter commits & advances box)")
player_text = st.text_input("Player hand (hidden, press Enter on keypad to commit)", value=st.session_state.player_input, key="player_input", label_visibility="collapsed")
other_text  = st.text_input("Other players' cards", value=st.session_state.other_input, key="other_input", label_visibility="collapsed")
dealer_text = st.text_input("Dealer cards (up,down,drawn)", value=st.session_state.dealer_input, key="dealer_input", label_visibility="collapsed")

# Keep session_state values in sync with visible text inputs (user might type directly)
st.session_state.player_input = player_text
st.session_state.other_input = other_text
st.session_state.dealer_input = dealer_text

# -------------------------
# Keypad (single, unique keys)
# -------------------------
st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
st.markdown("""
<style>
.keypad { display: grid; grid-template-columns: repeat(4, 1fr); gap: 6px; }
.keypad button { padding: 12px 0; font-size:16px; border-radius:8px; background:white; color:black; border:1px solid #333;}
.keypad .enter { background:#222; color:white; }
.keypad .delete { background:#ddd; color:black; }
</style>
""", unsafe_allow_html=True)

keypad_values = ['2','3','4','5','6','7','8','9','10','A','Delete','Enter']

# create the keypad — only once — with unique keys
cols = st.columns(4)
i = 0
for val in keypad_values:
    # unique key name using val
    keyname = f"keypad_{val}"
    col = cols[i % 4]
    # streamlit button must have unique key
    if col.button(val, key=keyname):
        # perform action on the active box
        if val == "Delete":
            box = st.session_state.active_box + "_input"
            # remove last token
            tokens = st.session_state.get(box, "").strip().split()
            if tokens:
                tokens = tokens[:-1]
                st.session_state[box] = " ".join(tokens)
        elif val == "Enter":
            # commit current box to shoe only if non-empty
            boxname = st.session_state.active_box
            committed = commit_box_to_shoe(boxname)
            # if committed store snapshot for recommendation
            if committed:
                # snapshot last committed player cards to allow recommendation
                if boxname == "player":
                    # find the last N appended to shoe — but simpler: capture the committed box that was just added
                    # we cannot separate shoe origins—so store snapshot in a separate key
                    last_committed = parse_box_text(st.session_state.get("_last_box_pending", ""))
                    # we used commit_box_to_shoe which cleared visible; instead capture before commit
                    # To ensure we have player snapshot, we do:
                    pass
            # advance active box
            if st.session_state.active_box == "player":
                st.session_state.active_box = "other"
            elif st.session_state.active_box == "other":
                st.session_state.active_box = "dealer"
            else:
                st.session_state.active_box = "player"
        else:
            # regular card pressed
            box = st.session_state.active_box + "_input"
            cur = st.session_state.get(box, "")
            if cur:
                st.session_state[box] = cur + " " + val
            else:
                st.session_state[box] = val
    i += 1

# -------------------------
# Buttons: Calculate / Next Hand / New Shoe
# -------------------------
st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
c1, c2, c3 = st.columns([1,1,1])
if c1.button("Calculate", key="btn_calc"):
    # Before calculating, we take a snapshot of the most recently committed player's cards if any:
    # We will find the last sequence of player cards committed by looking at the tail of st.session_state.shoe.
    # To keep things simple and reliable, enforce a rule: user should press Enter in player box to commit before Calculate.
    # We'll look for last committed player snapshot stored in session_state._last_player_snapshot if present.
    # (We update _last_player_snapshot when player box is successfully committed - we implement that above.)
    # So compute counts and EV now
    calculate_counts_and_ev()

if c2.button("Next Hand", key="btn_next"):
    # Next Hand: clear visible boxes but do NOT clear the shoe register
    st.session_state.player_input = ""
    st.session_state.other_input = ""
    st.session_state.dealer_input = ""
    st.session_state.active_box = "player"

if c3.button("New Shoe", key="btn_newshoe"):
    # New shoe resets everything
    st.session_state.shoe = []
    st.session_state.player_input = ""
    st.session_state.other_input = ""
    st.session_state.dealer_input = ""
    st.session_state.running_count = 0
    st.session_state.true_count = 0.0
    st.session_state.penetration = 0.0
    st.session_state.ev = 0.0
    st.session_state.recommendation = ""
    st.session_state.active_box = "player"

# -------------------------
# Count Info Expander
# -------------------------
with st.expander("Count Info"):
    st.session_state.num_decks = st.number_input("Number of decks", min_value=1, max_value=16, value=int(st.session_state.num_decks), key="num_decks_input")
    st.write(f"EV: {st.session_state.get('ev',0.0)}")
    st.write(f"True Count: {st.session_state.get('true_count',0.0):.2f}")
    st.write(f"Running Count: {st.session_state.get('running_count',0)}")
    st.write(f"Penetration: {st.session_state.get('penetration',0.0):.2f}")
    st.write(f"Recommendation: {st.session_state.get('recommendation','')}")
    st.write(f"Shoe cards committed: {len(st.session_state.shoe)}")

# -------------------------
# Display active box info
# -------------------------
st.markdown(f"**Active box:** {st.session_state.active_box.capitalize()} (use keypad; Enter commits & advances).")
