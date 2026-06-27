import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Cocktail Party", page_icon="🍹", layout="wide")

# BIJELA POZADINA, CRNI I CRVENI DETALJI
st.markdown("""
<style>
    .stApp { background-color: #ffffff !important; color: #1a202c !important; }
    h1, h2, h3 { color: #d69e2e !important; font-family: sans-serif; font-weight: 700; }
    .stButton>button { background-color: #e53e3e; color: white; border-radius: 8px; font-weight: 600; width: 100%; border: none; padding: 12px; }
    .stButton>button:hover { background-color: #c53030; }
    .notification { background-color: #c6f6d5; border-left: 5px solid #38a169; padding: 15px; border-radius: 8px; color: #22543d; font-weight: bold; }
    p, label, .stCheckbox, span { color: #1a202c !important; font-size: 16px; font-weight: 600; }
</style>
""", unsafe_allow_html=True)

if 'orders' not in st.session_state: st.session_state.orders = []
if 'users' not in st.session_state: st.session_state.users = {"ADMIN": "0000"}
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'user' not in st.session_state: st.session_state.user = None

csv_name = 'cocktails_za_claudea.csv'
df = pd.read_csv(csv_name, sep=';') if os.path.exists(csv_name) else None
if df is not None:
    df.columns = [c.strip().title() for c in df.columns]
    for c in df.columns:
        if 'ing' in c.lower() or 'sas' in c.lower(): df.rename(columns={c: 'Ingredients'}, inplace=True)
        if 'nam' in c.lower() or 'naz' in c.lower() or 'ime' in c.lower(): df.rename(columns={c: 'Cocktail Name'}, inplace=True)

if not st.session_state.logged_in:
    st.title("🍹 Welcome to the Cocktail Party!")
    u_in = st.text_input("Username (Your Name):").strip()
    p_in = st.text_input("4-digit PIN (Password):", type="password", max_chars=4)
    if st.button("Enter Party 🚀") and u_in and len(p_in) == 4:
        if u_in in st.session_state.users and st.session_state.users[u_in] != p_in: st.error("❌ Incorrect PIN!")
        else: st.session_state.users[u_in] = p_in; st.session_state.logged_in = True; st.session_state.user = u_in; st.rerun()
else:
    user = st.session_state.user
    if user.upper() == "ADMIN":
        st.title("👑 Master Bartender Dashboard")
        if st.sidebar.button("Logout 🚪"): st.session_state.logged_in = False; st.rerun()
        active = [o for o in st.session_state.orders if o['status'] == "In preparation"]
        st.subheader(f"Active Orders ({len(active)})")
        for idx, o in enumerate(active):
            st.write(f"👤 **{o['guest']}** ordered **{o['name']}** ({o['strength']})"); st.caption(f"Ingredients: {o['ingredients']}")
            if st.button(f"Serve {o['guest']}", key=f"srv_{idx}"): o['status'] = "Served"; st.rerun()
    else:
        served = [o for o in st.session_state.orders if o['guest'] == user and o['status'] == "Served" and not o.get('notified', False)]
        if served: st.markdown('<div class="notification">🔔 Your cocktail is ready! Come and get it! 🍹</div>', unsafe_allow_html=True); served[0]['notified'] = True
        st.title(f"🍹 Welcome, {user}!")
        if st.sidebar.button("Logout 🚪"): st.session_state.logged_in = False; st.rerun()
        
        if 'chk_state' not in st.session_state: st.session_state.chk_state = {i: False for i in ["Gin", "Vodka", "Rum", "Orange Juice", "Cranberry Juice", "Blueberry Juice", "Pineapple Juice", "Grenadine", "Blue Curacao", "Coca-Cola", "Jamnica", "Lemonade"]}
        c1, c2, c3, c4, c5 = st.columns(5)
        cur_alk = sum([st.session_state.chk_state[x] for x in ["Gin", "Vodka", "Rum"]])
        cur_juc = sum([st.session_state.chk_state[x] for x in ["Orange Juice", "Cranberry Juice", "Blueberry Juice", "Pineapple Juice"]])
        tot = sum(st.session_state.chk_state.values())
        
        with c1: st.markdown("**Alcohol**"); g1 = st.checkbox("Gin", value=st.session_state.chk_state["Gin"], disabled=not st.session_state.chk_state["Gin"] and (cur_alk >= 2 or tot >= 7)); g2 = st.checkbox("Vodka", value=st.session_state.chk_state["Vodka"], disabled=not st.session_state.chk_state["Vodka"] and (cur_alk >= 2 or tot >= 7)); g3 = st.checkbox("Rum", value=st.session_state.chk_state["Rum"], disabled=not st.session_state.chk_state["Rum"] and (cur_alk >= 2 or tot >= 7))
        with c2: st.markdown("**Juices**"); s1 = st.checkbox("Orange Juice", value=st.session_state.chk_state["Orange Juice"], disabled=not st.session_state.chk_state["Orange Juice"] and (cur_juc >= 2 or tot >= 7)); s2 = st.checkbox("Cranberry Juice", value=st.session_state.chk_state["Cranberry Juice"], disabled=not st.session_state.chk_state["Cranberry Juice"] and (cur_juc >= 2 or tot >= 7)); s3 = st.checkbox("Blueberry Juice", value=st.session_state.chk_state["Blueberry Juice"], disabled=not st.session_state.chk_state["Blueberry Juice"] and (cur_juc >= 2 or tot >= 7)); s4 = st.checkbox("Pineapple Juice", value=st.session_state.chk_state["Pineapple Juice"], disabled=not st.session_state.chk_state["Pineapple Juice"] and (cur_juc >= 2 or tot >= 7))
        with c3: st.markdown("**Syrups**"); si1 = st.checkbox("Grenadine", value=st.session_state.chk_state["Grenadine"], disabled=not st.session_state.chk_state["Grenadine"] and tot >= 7); si2 = st.checkbox("Blue Curacao", value=st.session_state.chk_state["Blue Curacao"], disabled=not st.session_state.chk_state["Blue Curacao"] and tot >= 7)
        with c4: st.markdown("**Carbonated**"); gz1 = st.checkbox("Coca-Cola", value=st.session_state.chk_state["Coca-Cola"], disabled=not st.session_state.chk_state["Coca-Cola"] and tot >= 7); gz2 = st.checkbox("Jamnica", value=st.session_state.chk_state["Jamnica"], disabled=not st.session_state.chk_state["Jamnica"] and tot >= 7)
        with c5: st.markdown("**Sour**"); k1 = st.checkbox("Lemonade", value=st.session_state.chk_state["Lemonade"], disabled=not st.session_state.chk_state["Lemonade"] and tot >= 7)
        
        st.session_state.chk_state = {"Gin":g1,"Vodka":g2,"Rum":g3,"Orange Juice":s1,"Cranberry Juice":s2,"Blueberry Juice":s3,"Pineapple Juice":s4,"Grenadine":si1,"Blue Curacao":si2,"Coca-Cola":gz1,"Jamnica":gz2,"Lemonade":k1}
        if sum(st.session_state.chk_state.values()) != tot: st.rerun()
        
        odb = [k for k, v in st.session_state.chk_state.items() if v]
        if st.button("Done 🔮") and odb:
            st.session_state['m_c'] = "Custom Tranquillo Mix"; st.session_state['m_i'] = ", ".join(odb)
            if df is not None:
                for _, r in df.iterrows():
                    b_l = [i.strip() for i in str(r['Ingredients']).replace('+', ',').split(',')]
                    if set(b_l) == set(odb): st.session_state['m_c'] = r['Cocktail Name']; break
        if st.session_state.get('m_c'):
            st.success(f"🔮 Created: **{st.session_state['m_c']}**")
            jac = st.radio("Strength:", ["Light", "Strong"], horizontal=True)
            if st.button("Order Cocktail 🚀"):
                st.session_state.orders.append({'guest': user, 'name': st.session_state['m_c'], 'ingredients': st.session_state['m_i'], 'strength': jac, 'status': "In preparation", 'rating': None, 'notified': False})
                st.session_state['m_c'] = None; st.rerun()
