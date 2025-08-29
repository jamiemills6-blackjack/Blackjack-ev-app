# blackjack_streamlit_app.py
import streamlit as st

try:
    from blackjack_ev import build_shoe, parse_seen_cards, Rules, recommend_action, default_cashout_policy
except Exception as e:
    st.error(
        f"Could not import blackjack_ev.py. Make sure it's in the same folder. Error:\n{e}"
    )
    st.stop()

# ---------- Page setup ----------
st.set_page_config(page_title="Blackjack EV Advisor (Mobile)", layout="centered")
st.title("♠ Blackjack EV Advisor — Mobile")
st.markdown("Enter ranks only (e.g. `3 10 A Q`).")

# ---------- Session state ----------
if "seen_cards" not in st.session_state:
    st.session_state["seen_cards"] = []

if "player_hand_input" not in st.session_state:
    st.session_state["player_hand_input"] = ""
if "dealer_up_input" not in st.session_state:
    st.session_state["dealer_up_input"] = ""
if "extra_seen_input" not in st.session_state:
    st.session_state["extra_seen_input"] = ""

# ---------- Inputs ----------
st.markdown("**Your hand** (e.g. `8 8` or `A 7`)")
player_hand_input = st.text_input("Your hand", key="player_hand_input")

st.markdown("**Dealer upcard** (e.g. `6`)")
dealer_up_input = st.text_input("Dealer upcard", key="dealer_up_input")

st.markdown("**Other cards seen this hand** (hits/dealer outcome). Example: `3 10 A`")
extra_seen = st.text_input("Other seen cards", key="extra_seen_input")

# ---------- Buttons ----------
col1, col2, col3 = st.columns(3)
with col1:
    calculate_pressed = st.button("Calculate")
with col2:
    next_hand_pressed = st.button("Next hand")
with col3:
    newshoe_pressed = st.button("New shoe")

# ---------- Helpers ----------
def normalize_cards(s: str):
    """Parse input string into card ranks list."""
    if not s:
        return []
    try:
        return parse_seen_cards(s)
    except Exception:
        return [p.upper() for p in s.replace(",", " ").split()]

def hand_is_splittable(hand):
    """Splittable if same rank OR both 10-value (10,J,Q,K)."""
    if len(hand) != 2:
        return False
    r1, r2 = hand[0].upper(), hand[1].upper()
    tens = {"10", "J", "Q", "K"}
    return (r1 == r2) or (r1 in tens and r2 in tens)

# ---------- New shoe ----------
if newshoe_pressed:
    st.session_state["seen_cards"] = []
    st.session_state["player_hand_input"] = ""
    st.session_state["dealer_up_input"] = ""
    st.session_state["extra_seen_input"] = ""
    st.success("✅ New shoe created (8 decks reset).")
    st.stop()

# ---------- Next hand ----------
if next_hand_pressed:
    # Commit all current inputs to the hidden shoe register
    st.session_state["seen_cards"].extend(normalize_cards(player_hand_input))
    st.session_state["seen_cards"].extend(normalize_cards(dealer_up_input))
    st.session_state["seen_cards"].extend(normalize_cards(extra_seen))
    # Clear input boxes
    st.session_state["player_hand_input"] = ""
    st.session_state["dealer_up_input"] = ""
    st.session_state["extra_seen_input"] = ""
    st.success("➡️ Hand committed to shoe. Ready for next hand.")
    st.stop()

# ---------- Calculate EV ----------
if calculate_pressed:
    if not player_hand_input or not dealer_up_input:
        st.warning("Enter your hand and dealer upcard first.")
    else:
        # Temporary shoe: base + hidden seen cards + current inputs
        temp_seen = []
        temp_seen.extend(st.session_state["seen_cards"])
        temp_seen.extend(normalize_cards(player_hand_input))
        temp_seen.extend(normalize_cards(dealer_up_input))
        temp_seen.extend(normalize_cards(extra_seen))

        shoe = build_shoe(decks=8, seen_cards=temp_seen)
        player_hand = normalize_cards(player_hand_input)
        dealer_up = dealer_up_input.strip().upper()

        rules = Rules(
            hit_soft_17=False,
            double_any_two=True,
            double_after_split=True,
            max_splits=3,
            resplit_aces=False,
            hit_split_aces=False,
            blackjack_pays_3_to_2=True,
            dealer_peeks_for_blackjack=True,
        )

        reco = recommend_action(
            shoe, dealer_up, player_hand,
            rules=rules, cashout_policy=default_cashout_policy
        )
        evs = dict(reco.get("ev_by_action", {}))

        # remove split if not splittable
        if not hand_is_splittable(player_hand) and "split" in evs:
            evs.pop("split")

        st.markdown("### EV by action (per 1 unit bet)")
        order = ["stand", "hit", "double", "split", "cashout"]
        for act in order:
            if act in evs:
                st.write(f"**{act.title():7}** : {evs[act]: .4f}")

        if evs:
            best = max(evs.items(), key=lambda kv: kv[1])
            st.markdown(f"### ✅ Best action: **{best[0].upper()}** (EV = {best[1]:.4f})")

        st.markdown("---")
        st.write(f"Running count: **{shoe.hi_lo_running()}**")
        st.write(f"True count: **{shoe.true_count():.2f}**")
        st.write(f"Cards remaining: **{shoe.total_cards()}**")
        st.write(f"Cards stored in shoe: **{len(st.session_state['seen_cards'])}**")
