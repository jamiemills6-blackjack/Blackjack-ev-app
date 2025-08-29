# bj.py -- Blackjack Assistant with real-time mobile-ready keypad
import streamlit as st
import streamlit.components.v1 as components

# ---------------------------
# Session state initialization
# ---------------------------
defaults = {
    "shoe": [], "pending_player": [], "pending_others": [], "pending_dealer": [],
    "active_box": "player", "running_count":0, "true_count":0.0,
    "penetration":0.0, "ev":0.0, "recommendation":"", "_last_committed_player":[],
    "num_decks":8, "last_key":""
}
for key, val in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = val

st.set_page_config(page_title="Blackjack Assistant", layout="centered")
st.markdown("<h1 style='text-align:center; font-size:150%;'>Blackjack Assistant</h1>", unsafe_allow_html=True)

# ---------------------------
# Card values and Hi-Lo
# ---------------------------
CARD_VALUES = {'A':[1,11],'2':[2],'3':[3],'4':[4],'5':[5],'6':[6],'7':[7],'8':[8],'9':[9],'10':[10]}
HI_LO = {'2':1,'3':1,'4':1,'5':1,'6':1,'7':0,'8':0,'9':0,'10':-1,'A':-1}

def best_hand_value(cards):
    totals = [0]
    for c in cards:
        vals = CARD_VALUES.get(c,[0])
        totals = [t+v for t in totals for v in vals]
    under = [t for t in totals if t<=21]
    return max(under) if under else min(totals)

def is_soft(cards):
    if 'A' not in cards: return False
    totals = [0]
    for c in cards:
        vals = CARD_VALUES.get(c,[0])
        totals = [t+v for t in totals for v in vals]
    return any(t<=21 and t!=min(totals) for t in totals)

def compute_running_count_from_cards(card_list):
    return sum(HI_LO.get(c,0) for c in card_list)

# ---------------------------
# Display pending boxes
# ---------------------------
def box_display(title, cards, active=False):
    style = "border:2px solid #444; padding:8px; border-radius:6px;" if active else "border:1px solid #aaa; padding:8px; border-radius:6px;"
    st.markdown(f"**{title}**")
    st.markdown(f"<div style='{style}; min-height:28px;'>{' '.join(cards) if cards else '<span style=color:#777>None</span>'}</div>", unsafe_allow_html=True)

st.markdown("<div style='display:flex; gap:8px; flex-direction:column;'>", unsafe_allow_html=True)
box_display("Your cards", st.session_state.pending_player, st.session_state.active_box=="player")
box_display("Other players' cards", st.session_state.pending_others, st.session_state.active_box=="other")
box_display("Dealer cards", st.session_state.pending_dealer, st.session_state.active_box=="dealer")
st.markdown("</div>", unsafe_allow_html=True)
st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

# ---------------------------
# Hidden input for JS keypad
# ---------------------------
st.text_input("hidden_key_capture", value=st.session_state.last_key, key="hidden_input", label_visibility="collapsed")

# ---------------------------
# HTML/JS Keypad (centered, smaller Enter/Delete font)
# ---------------------------
keys = ['2','3','4','5','6','7','8','9','10','A','Delete','Enter']
keypad_html = """
<div style='display:flex; justify-content:center; margin-bottom:6px;'>
<div style='display:grid; grid-template-columns: repeat(4, 60px); gap:6px;'>
"""
for k in keys + ['','','','']:  # pad to 16 cells
    if k:
        size = '14px' if k in ['Delete','Enter'] else '18px'
        keypad_html += f"""<button onclick="document.getElementById('hidden_input').value='{k}';
document.getElementById('hidden_input').dispatchEvent(new Event('change'))" 
style='padding:10px; font-size:{size}; border-radius:8px; width:60px;'>{k}</button>"""
    else:
        keypad_html += "<div>&nbsp;</div>"
keypad_html += "</div></div>"
components.html(keypad_html, height=300)

# ---------------------------
# Handle key press
# ---------------------------
key = st.session_state.last_key
if key:
    active = st.session_state.active_box
    pending_map = {"player": st.session_state.pending_player,
                   "other": st.session_state.pending_others,
                   "dealer": st.session_state.pending_dealer}
    pending = pending_map[active]
    if key=="Delete":
        if pending: pending.pop()
    elif key=="Enter":
        if pending:
            st.session_state.shoe.extend(pending)
            if active=="player": st.session_state._last_committed_player = pending.copy()
            pending.clear()
        if active=="player": st.session_state.active_box="other"
        elif active=="other": st.session_state.active_box="dealer"
        else: st.session_state.active_box="player"
    else:
        pending.append(key)
    st.session_state.last_key = ""  # reset

# ---------------------------
# Action Buttons below keypad
# ---------------------------
c1,c2,c3 = st.columns([1,1,1])
if c1.button("Calculate"):
    combined = st.session_state.shoe + st.session_state.pending_player + st.session_state.pending_others + st.session_state.pending_dealer
    running = compute_running_count_from_cards(combined)
    decks = max(1,int(st.session_state.num_decks))
    seen = len(combined)
    rem_cards = max(0,decks*52 - seen)
    rem_decks = max(0.0001, rem_cards/52)
    true = running / rem_decks
    pen = seen/(decks*52)
    player_hand = st.session_state.pending_player.copy() if st.session_state.pending_player else st.session_state._last_committed_player.copy()
    dealer_up = st.session_state.pending_dealer[0] if st.session_state.pending_dealer else (st.session_state.shoe[0] if st.session_state.shoe else None)
    rec = recommend_basic_strategy(player_hand,dealer_up) if player_hand else "No player hand entered"
    st.session_state.running_count = running
    st.session_state.true_count = true
    st.session_state.penetration = pen
    st.session_state.ev = round(true*0.5/100,5)  # simple EV%
    st.session_state.recommendation = rec

if c2.button("Next Hand"):
    for box in ["pending_player","pending_others","pending_dealer"]:
        pending = st.session_state[box]
        if pending:
            st.session_state.shoe.extend(pending)
            if box=="pending_player": st.session_state._last_committed_player = pending.copy()
            pending.clear()
    st.session_state.active_box="player"

if c3.button("New Shoe"):
    for k in ["shoe","pending_player","pending_others","pending_dealer"]:
        st.session_state[k]=[]
    st.session_state.running_count=0
    st.session_state.true_count=0.0
    st.session_state.penetration=0.0
    st.session_state.ev=0.0
    st.session_state.recommendation=""
    st.session_state._last_committed_player=[]
    st.session_state.active_box="player"

# ---------------------------
# Count Info Expander
# ---------------------------
with st.expander("Count Info"):
    st.number_input("Number of decks", min_value=1, max_value=16, key="num_decks")
    st.markdown(f"**EV:** {st.session_state.ev}")
    st.markdown(f"**True Count:** {st.session_state.true_count:.2f}")
    st.markdown(f"**Running Count:** {st.session_state.running_count}")
    st.markdown(f"**Penetration:** {st.session_state.penetration:.3f}")
    st.markdown(f"**Recommendation:** {st.session_state.recommendation}")
    st.markdown(f"**Committed cards in shoe:** {len(st.session_state.shoe)}")

# ---------------------------
# Recommendation Display
# ---------------------------
rec = st.session_state.get("recommendation","")
if rec:
    color = "black"
    rec_lower = rec.lower()
    if rec_lower.startswith("hit"):
        color = "crimson"
    elif rec_lower.startswith("stand"):
        color = "green"
    elif rec_lower.startswith("split"):
        color = "navy"
    elif rec_lower.startswith("double"):
        color = "orange"
    st.markdown(f"<div style='font-weight:600; padding:8px; border-radius:6px; text-align:center; color:{color};'>{rec}</div>", unsafe_allow_html=True)

# ---------------------------
# Basic Strategy Helper
# ---------------------------
def recommend_basic_strategy(player_cards,dealer_up):
    if not player_cards: return "No hand"
    du = dealer_up
    pair=False
    if len(player_cards)==2 and player_cards[0]==player_cards[1]:
        pair=True
        pc = player_cards[0]
    soft = is_soft(player_cards)
    total = best_hand_value(player_cards)
    if pair:
        if pc in ['A','8']: return "Split"
        if pc in ['2','3']: return "Split" if du in ['2','3','4
