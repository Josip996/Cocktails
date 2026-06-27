import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Cocktail Party", page_icon="🍹", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #ffffff !important; color: #1a202c !important; }
    h1, h2, h3 { color: #d69e2e !important; font-family: sans-serif; font-weight: 700; }
    .stButton>button { background-color: #e53e3e; color: white; border-radius: 8px; font-weight: 600; width: 100%; border: none; padding: 12px; }
    .stButton>button:hover { background-color: #c53030; }
    .notification { background-color: #c6f6d5; border-left: 5px solid #38a169; padding: 15px; border-radius: 8px; color: #22543d; font-weight: bold; margin-bottom: 15px; }
    p, label, .stCheckbox, span { color: #1a202c !important; font-size: 16px; font-weight: 600; }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def get_shared_party_db():
    return {"orders": [], "users": {"ADMIN": "0000"}}

shared_data = get_shared_party_db()


if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'user' not in st.session_state: st.session_state.user = None
if 'auth_mode' not in st.session_state: st.session_state.auth_mode = "Sign In"
if 'm_c' not in st.session_state: st.session_state.m_c = None
if 'm_i' not in st.session_state: st.session_state.m_i = None

# 👑 POPRAVAK: Prisilno i pametno njuškanje separatora u bazi podataka
csv_name = 'cocktails_za_claudea.csv'
df = None
if os.path.exists(csv_name):
    try:
        df = pd.read_csv(csv_name, sep=None, engine='python', encoding='utf-8')
    except:
        try:
            df = pd.read_csv(csv_name, sep=';')
        except:
            df = pd.read_csv(csv_name, sep=',')

if df is not None:
    df.columns = [c.strip().title() for c in df.columns]
    for c in df.columns:
        if 'ing' in c.lower() or 'sas' in c.lower(): df.rename(columns={c: 'Ingredients'}, inplace=True)
        if 'nam' in c.lower() or 'naz' in c.lower() or 'ime' in c.lower(): df.rename(columns={c: 'Cocktail Name'}, inplace=True)

if not st.session_state.logged_in:
    if st.session_state.auth_mode == "Sign In":
        st.title("🔑 Sign In to the Party")
        u_in = st.text_input("Username:").strip()
        p_in = st.text_input("4-digit PIN:", type="password", max_chars=4)
        if st.button("Login 🚀") and u_in and len(p_in) == 4:
            if u_in in shared_data["users"] and shared_data["users"][u_in] == p_in:
                st.session_state.logged_in = True; st.session_state.user = u_in; st.rerun()
            else: st.error("❌ Incorrect Username or PIN!")
        if st.button("New here? Register Account ✨"): st.session_state.auth_mode = "Register"; st.rerun()
    else:
        st.title("📝 Register for the Party")
        u_reg = st.text_input("Choose Username:").strip()
        p_reg = st.text_input("Create 4-digit PIN:", type="password", max_chars=4)
        if st.button("Create Account & Enter 🚀") and u_reg and len(p_reg) == 4:
            if u_reg in shared_data["users"]: st.error("❌ Username already taken!")
            else: shared_data["users"][u_reg] = p_reg; st.session_state.logged_in = True; st.session_state.user = u_reg; st.rerun()
        if st.button("Already have an account? Sign In 🔑"): st.session_state.auth_mode = "Sign In"; st.rerun()

else:
    user = st.session_state.user
    if st.sidebar.button("Logout 🚪"):
        st.session_state.logged_in = False
        st.session_state.user = None
        st.session_state.m_c = None
        st.session_state.m_i = None
        st.rerun()

    if user.upper() == "ADMIN":
        st.title("👑 Master Bartender Dashboard")
        active = [o for o in shared_data["orders"] if o['status'] == "In preparation"]
        st.subheader(f"Active Orders Queue ({len(active)})")
        if not active: st.info("No active orders right now. Relax! 🥂")
        for idx, o in enumerate(active):
            st.write(f"👤 **{o['guest']}** ordered **{o['name']}** ({o['strength']})")
            st.caption(f"Ingredients: {o['ingredients']}")
            if st.button(f"Serve {o['guest']}", key=f"srv_{idx}"): o['status'] = "Served"; st.rerun()
            st.markdown("---")
        st.subheader("📊 Leaderboard")
        served = [o for o in shared_data["orders"] if o['status'] == "Served" and o['rating'] is not None]
        if served:
            rdf = pd.DataFrame(served)
            ld = rdf.groupby('name')['rating'].mean().reset_index().rename(columns={'name': 'Cocktail', 'rating': 'Rating'})
            st.dataframe(ld.sort_values(by='Rating', ascending=False))
    else:
        notif = [o for o in shared_data["orders"] if o['guest'] == user and o['status'] == "Served" and not o.get('notified', False)]
        if notif: 
            st.markdown('<div class="notification">🔔 Your cocktail is ready! Come and get it! 🍹</div>', unsafe_allow_html=True)
            for o in notif: o['notified'] = True

        st.title(f"🍹 Welcome, {user}!")
        if df is None: st.error("Missing cocktails_za_claudea.csv file on GitHub!")
        else:
            st.subheader("Mix Your Ingredients")
            if 'chk_state' not in st.session_state: st.session_state.chk_state = {i: False for i in ["Gin", "Vodka", "Rum", "Orange Juice", "Cranberry Juice", "Blueberry Juice", "Pineapple Juice", "Grenadine", "Blue Curacao", "Coca-Cola", "Jamnica", "Lemonade"]}
            c1, c2, c3, c4, c5 = st.columns(5)
            cur_alk = sum([st.session_state.chk_state[x] for x in ["Gin", "Vodka", "Rum"]])
            cur_juc = sum([st.session_state.chk_state[x] for x in ["Orange Juice", "Cranberry Juice", "Blueberry Juice", "Pineapple Juice"]])
            tot = sum(st.session_state.chk_state.values())

            with c1:
                st.markdown("**Alcohol**")
                g1 = st.checkbox("Gin", value=st.session_state.chk_state["Gin"], disabled=not st.session_state.chk_state["Gin"] and (cur_alk >= 2 or tot >= 7))
                g2 = st.checkbox("Vodka", value=st.session_state.chk_state["Vodka"], disabled=not st.session_state.chk_state["Vodka"] and (cur_alk >= 2 or tot >= 7))
                g3 = st.checkbox("Rum", value=st.session_state.chk_state["Rum"], disabled=not st.session_state.chk_state["Rum"] and (cur_alk >= 2 or tot >= 7))
            with c2:
                st.markdown("**Juices**")
                s1 = st.checkbox("Orange Juice", value=st.session_state.chk_state["Orange Juice"], disabled=not st.session_state.chk_state["Orange Juice"] and (cur_juc >= 2 or tot >= 7))
                s2 = st.checkbox("Cranberry Juice", value=st.session_state.chk_state["Cranberry Juice"], disabled=not st.session_state.chk_state["Cranberry Juice"] and (cur_juc >= 2 or tot >= 7))
                s3 = st.checkbox("Blueberry Juice", value=st.session_state.chk_state["Blueberry Juice"], disabled=not st.session_state.chk_state["Blueberry Juice"] and (cur_juc >= 2 or tot >= 7))
                s4 = st.checkbox("Pineapple Juice", value=st.session_state.chk_state["Pineapple Juice"], disabled=not st.session_state.chk_state["Pineapple Juice"] and (cur_juc >= 2 or tot >= 7))
            with c3:
                st.markdown("**Syrups**")
                si1 = st.checkbox("Grenadine", value=st.session_state.chk_state["Grenadine"], disabled=not st.session_state.chk_state["Grenadine"] and tot >= 7)
                si2 = st.checkbox("Blue Curacao", value=st.session_state.chk_state["Blue Curacao"], disabled=not st.session_state.chk_state["Blue Curacao"] and tot >= 7)
            with c4:
                st.markdown("**Carbonated**")
                gz1 = st.checkbox("Coca-Cola", value=st.session_state.chk_state["Coca-Cola"], disabled=not st.session_state.chk_state["Coca-Cola"] and tot >= 7)
                gz2 = st.checkbox("Jamnica", value=st.session_state.chk_state["Jamnica"], disabled=not st.session_state.chk_state["Jamnica"] and tot >= 7)
            with c5:
                st.markdown("**Sour**")
                k1 = st.checkbox("Lemonade", value=st.session_state.chk_state["Lemonade"], disabled=not st.session_state.chk_state["Lemonade"] and tot >= 7)

            st.session_state.chk_state = {"Gin":g1,"Vodka":g2,"Rum":g3,"Orange Juice":s1,"Cranberry Juice":s2,"Blueberry Juice":s3,"Pineapple Juice":s4,"Grenadine":si1,"Blue Curacao":si2,"Coca-Cola":gz1,"Jamnica":gz2,"Lemonade":k1}
            if sum(st.session_state.chk_state.values()) != tot: st.rerun()

            odb = [k for k, v in st.session_state.chk_state.items() if v]
            if st.button("Done 🔮") and odb:
                st.session_state.m_c = "Custom Tranquillo Mix"
                st.session_state.m_i = ", ".join(odb)
                if df is not None:
                    # Radimo strogo čišćenje i pretvaramo odabir gosta u male komadiće teksta
                    set_gosta = {i.strip().lower() for i in odb}
                    for _, r in df.iterrows():
                        # Čistimo cijelu bazu od plusova, zareza i razmaka i pretvaramo u male tekstove
                        raw_ingredients = str(r['Ingredients']).replace(' + ', ',').replace('+', ',')
                        b_l = {i.strip().lower() for i in raw_ingredients.split(',') if i.strip()}

                        # Ako se skupovi savršeno poklapaju u slovo, povuci službeno ime!
                        if b_l == set_gosta:
                            st.session_state.m_c = r['Cocktail Name']
                            break
            if st.session_state.m_c:
                st.success(f"🔮 Created: **{st.session_state.m_c}**")
                st.write(f"Ingredients selected: {st.session_state.m_i}")
                jac = st.radio("Strength:", ["Light", "Strong"], horizontal=True)
                if st.button("Order Cocktail 🚀"):
                    shared_data["orders"].append({
                        'guest': user, 'name': st.session_state.m_c, 
                        'ingredients': st.session_state.m_i, 'strength': jac, 
                        'status': "In preparation", 'rating': None, 'notified': False
                    })
                    st.session_state.m_c = None
                    st.session_state.chk_state = {i: False for i in st.session_state.chk_state.keys()}
                    st.toast("Order sent successfully!")
                    st.rerun()

        st.markdown("---")
        st.subheader("📋 Your Cocktail History & Ratings")
        u_orders = [o for o in shared_data["orders"] if o['guest'] == user]
        if not u_orders: st.write("No orders yet tonight. Start mixing! 🍸")
        for idx, o in enumerate(u_orders):
            col_i, col_r = st.columns(2)
            with col_i:
                st.markdown(f"**{o['name']}** ({o['strength']}) - {o['status']}")
                st.caption(f"Ingredients: {o['ingredients']}")
            with col_r:
                if o['status'] == "Served":
                    if o['rating'] is None:
                        ocj = st.slider("Rate 1-10:", 1, 10, 5, key=f"sld_{idx}")
                        if st.button("Submit Rate", key=f"btn_{idx}"): o['rating'] = ocj; st.rerun()
                    else: st.write(f"⭐ Rating: **{o['rating']}/10**")
            st.markdown("---")
# Pametno osvježavanje Admin šanka koje te NE izbacuje iz profila
if st.session_state.get('logged_in') and st.session_state.get('user', '').upper() == "ADMIN":
    st.empty()
    st.components.v1.html("<script>setTimeout(function(){ window.parent.document.querySelector('.stButton button').click(); }, 5000);</script>", height=0)


