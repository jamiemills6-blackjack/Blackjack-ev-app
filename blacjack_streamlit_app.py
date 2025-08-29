import streamlit as st
from blackjack_ev import (
    build_shoe,
    parse_seen_cards,
    Rules,
    default_cashout_policy,
    recommend_action,
)

# ------------------------------
# App State
# ------------------------------

if "shoe" not in st.session_state:
    st.session_state.shoe = build_shoe(decks=6)

if "seen_cards" not in st.session_state:
    st.session_state.seen_cards = []

# ------------------------------
# Helper Functions
# ------------------------------

def reset_shoe():
    st.session_state.shoe = build_shoe(decks=6)
    st.session_state.seen_cards = []


def next_hand():
    st.session_state.player_input = ""
    st.session_state.dealer_input = ""


# ------------------------------
# Layout
# ------------------------------

st.title("♠️ Blackjack EV Helper (Mobile Optimised)")

# Text inputs
player_hand_str = st.text_input("Your Hand (e.g. `10 A`)", key="player_input")
dealer_up_str = st.text_input("Dealer Upcard (e.g. `6`)", key="dealer_input")

# Buttons
col1, col2 = st.columns([1, 1])
with col1:
    calc_btn = st.button("✅ Calculate")
with col2:
    new_shoe_btn = st.button("♻️ New Shoe")

# Next hand button full width below
next_hand_btn = st.button("➡️ Next Hand")

# ------------------------------
# Logic
# ------------------------------

rules = Rules()

if calc_btn:
    player_hand = parse_seen_cards(player_hand_str)
    dealer_up = parse_seen_cards(dealer_up_str)

    if not player_hand or not dealer_up:
        st.error("Please enter both player hand and dealer upcard.")
    else:
        # Add dealt cards to seen register
        st.session_state.seen_cards.extend(player_hand + dealer_up)

        result = recommend_action(
            st.session_state.shoe,
            dealer_up[0],
            player_hand,
            rules,
            default_cashout_policy,
        )

        st.subheader("📊 Recommendation")
        st.write(f"**Best Action:** {result['best_action']}")
        st.write("EV by action:")
        for act, ev in result["ev_by_action"].items():
            st.write(f"- {act}: {ev:.3f}")

if new_shoe_btn:
    reset_shoe()
    st.success("🔄 New shoe started. Seen cards cleared.")

if next_hand_btn:
    next_hand()
    st.info("➡️ Ready for next hand. Shoe memory preserved.")
