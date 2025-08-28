import streamlit as st
from blackjack_ev import build_shoe, parse_seen_cards, Rules, guidance_for_all_hands

# Page setup
st.set_page_config(page_title="Blackjack EV Advisor", layout="centered")
st.title("Blackjack EV Advisor (8-Deck, Card Counting)")
st.markdown("Simplified input: ranks only, e.g., '3 10 A Q'")

# -----------------------------
# Session state initialization
# -----------------------------
if 'seen_cards' not in st.session_state:
    st.session_state['seen_cards'] = []

# Input fields with session keys
raw_seen = st.text_input("Cards dealt so far (ranks only, e.g., '3 10 A Q')", key='raw_seen_input')
player_hand_input = st.text_input("Your hand (ranks only, e.g., '8 8')", key='player_hand_input')
dealer_up = st.text_input("Dealer upcard (rank only, e.g., '6')", key='dealer_up_input')

# -----------------------------
# Reset shoe button
# -----------------------------
if st.button("Reset Shoe"):
    st.session_state['seen_cards'] = []
    st.session_state['raw_seen_input'] = ""
    st.session_state['player_hand_input'] = ""
    st.session_state['dealer_up_input'] = ""
    st.success("Shoe has been reset to a full 8 decks.")

# -----------------------------
# Calculate EV and guidance
# -----------------------------
if st.button("Calculate"):
    if not player_hand_input or not dealer_up:
        st.warning("Please enter at least your hand and dealer upcard!")
    else:
        # Parse newly entered seen cards and update session state
        if raw_seen:
            new_seen = parse_seen_cards(raw_seen)
            st.session_state['seen_cards'].extend(new_seen)

        # Build shoe from session state
        shoe = build_shoe(decks=8, seen_cards=st.session_state['seen_cards'])
        player_hand = parse_seen_cards(player_hand_input)
        dealer_up_rank = dealer_up.upper()

        rules = Rules(
            hit_soft_17=False,
            double_any_two=True,
            double_after_split=True,
            max_splits=3,
            resplit_aces=False,
            hit_split_aces=False,
            blackjack_pays_3_to_2=True,
            dealer_peeks_for_blackjack=True
        )

        import io
        from contextlib import redirect_stdout

        f = io.StringIO()
        with redirect_stdout(f):
            guidance_for_all_hands(shoe, dealer_up_rank, [player_hand], rules)
        output = f.getvalue()

        # Display output with best action highlighted
        for line in output.split('\n'):
            if line.strip().lower().startswith('best action'):
                st.markdown(f"<span style='color:red;font-weight:bold'>{line}</span>", unsafe_allow_html=True)
            else:
                st.text(line)
