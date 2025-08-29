import streamlit as st
from blackjack_ev import (
    build_shoe,
    parse_seen_cards,
    Rules,
    default_cashout_policy,
    recommend_action,
    running_and_true_count,
)

# ------------------------------
# App State
# ------------------------------

if "shoe" not in st.session_state:
    st.session_state.shoe = build_shoe(decks=8)

if "seen_cards" not in st.session_state:
    st.session_state.seen_cards = []

# ------------------------------
# Helper Functions
# ------------------------------

def reset_shoe():
    st.session_state.shoe = build_shoe(decks=8)
    st.session_state.seen_cards = []
    st.session_state.player_input = ""
    st.session_state.dealer_input = ""
    st.session_state.others_input = ""


def next_hand():
    st.session_state.player_input = ""
    st.session_state.dealer_input = ""
    st.session_state.others_input = ""


# ------------------------------
# Layout
# ------------------------------

st.markdown("<h4 style='font-size:14px'>♠️ Blackjack EV Helper (Mobile Optimised)</h4>", unsafe_allow_html=True)

# Text inputs
player_hand_str = st.text_input("Your Hand", key="player_input", placeholder="10 A")
dealer_up_str = st.text_input("Dealer Upcard", key="dealer_input", placeholder="6")
others_str = st.text_input("Other Players' Cards", key="others_input", placeholder="9 K 5 8")

# Buttons stacked (Calculate → Next Hand → New Shoe)
calc_btn = st.button("✅ Calculate")
next_hand_btn = st.button("➡️ Next Hand")
new_shoe_btn = st.button("♻️ New Shoe")

# ------------------------------
# Logic
# ------------------------------

rules = Rules()

if calc_btn:
    player_hand = parse_seen_cards(player_hand_str)
    dealer_up = parse_seen_cards(dealer_up_str)
    other_cards = parse_seen_cards(others_str)

    if not player_hand or not dealer_up:
        st.error("Please enter your hand and dealer upcard.")
    else:
        # Add dealt cards to seen register
        st.session_state.seen_cards.extend(player_hand + dealer_up + other_cards)

        result = recommend_action(
            st.session_state.shoe,
            dealer_up[0],
            player_hand,
            rules,
            default_cashout_policy,
        )

        # Show recommendation
        st.markdown("<h5 style='font-size:12px'>📊 Recommendation</h5>", unsafe_allow_html=True)
        st.markdown(f"<p style='font-size:12px'><b>Best Action:</b> {result['best_action']}</p>", unsafe_allow_html=True)
        st.markdown("<p style='font-size:12px'>EV by action:</p>", unsafe_allow_html=True)
        for act, ev in result["ev_by_action"].items():
            st.markdown(f"<p style='font-size:12px'>- {act}: {ev:.3f}</p>", unsafe_allow_html=True)

        # Show counts
        running, true, pen = running_and_true_count(st.session_state.seen_cards, decks=8)
        st.markdown("<h5 style='font-size:12px'>📈 Count</h5>", unsafe_allow_html=True)
        st.markdown(f"<p style='font-size:12px'>Running: {running}</p>", unsafe_allow_html=True)
        st.markdown(f"<p style='font-size:12px'>True: {true:.2f}</p>", unsafe_allow_html=True)
        st.markdown(f"<p style='font-size:12px'>Penetration: {pen*100:.1f}%</p>", unsafe_allow_html=True)

if next_hand_btn:
    next_hand()
    st.info("➡️ Ready for next hand. Shoe memory preserved.")

if new_shoe_btn:
    reset_shoe()
    st.success("🔄 New shoe started. Seen cards cleared.")
