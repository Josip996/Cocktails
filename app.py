import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Cocktail Party", page_icon="🍹", layout="wide")

# SVIJETLO-SIVA KLUPSKA POZADINA S ODLIČNIM KONTRASTOM
st.markdown("""
<style>
    .stApp { background-color: #2d3748; color: #ffffff; }
    h1, h2, h3 { color: #ffcc00 !important; font-family: 'Segoe UI', sans-serif; }
    .stButton>button { 
        background-color: #ff6b6b; color: white; border-radius: 8px; 
        font-weight: 600; width: 100%; transition: 0.3s; border: none; padding: 12px;
    }
    .stButton>button:hover { background-color: #ff5252; transform: translateY(-2px); }
    .notification { 
        background-color: #1e5631; border-left: 5px solid #2ecc71; 
        padding: 15px; border-radius: 8px; color: #2ecc71; font-weight: bold; margin-bottom: 15px;
    }
    p, label, .stCheckbox { color: #ffffff !important; font-size: 16px; font-weight: 500; }
</style>
""", unsafe_allow_html=True)

if 'orders' not in st.session_state: st.session_state.orders = []
if 'users' not in st.session_state: st.session_state.users = {"ADMIN": "0000"}
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'user' not in st.session_state: st.session_state.user = None
if 'matched_cocktail' not in st.session_state: st.session_state.matched_cocktail = None
if 'selected_ingredients' not in st.session_state: st.session_state.selected_ingredients = None

csv_name = 'cocktails_za_claudea.csv'
df_cocktails = pd.read_csv(csv_name, sep=';') if os.path.exists(csv_name) else None

# STROGA LOGIN / REGISTRACIJA BARIJERA
if not st.session_state.logged_in:
    st.title("🍹 Welcome to the Cocktail Party!")
    st.subheader("Please Sign In or Register with your Name and a 4-digit PIN")
    username_input = st.text_input("Username (Your Name):").strip()
    pin_input = st.text_input("4-digit PIN (Password):", type="password", max_chars=4)
    if st.button("Enter Party 🚀"):
        if username_input and len(pin_input) == 4:
            if username_input in st.session_state.users:
                if st.session_state.users[username_input] == pin_input:
                    st.session_state.logged_in = True
                    st.session_state.user = username_input
                    st.rerun()
                else: st.error("❌ Incorrect PIN!")
            else:
                st.session_state.users[username_input] = pin_input
                st.session_state.logged_in = True
                st.session_state.user = username_input
                st.rerun()
        else: st.error("❌ Please enter a valid Name and a 4-digit PIN!")

else:
    current_user = st.session_state.user

    # --- EKRAN A: MASTER BARTENDER (ADMIN pogled na šank) ---
    if current_user.upper() == "ADMIN":
        st.title("👑 Master Bartender Dashboard")
        st.sidebar.write(f"Logged in as: **{current_user}**")
        if st.sidebar.button("Logout 🚪"):
            st.session_state.logged_in = False
            st.session_state.user = None
            st.rerun()

        active_orders = [o for o in st.session_state.orders if o['status'] == "In preparation"]
        st.subheader(f"Active Orders Queue ({len(active_orders)})")
        if not active_orders: 
            st.info("No active orders right now. Relax and have a drink! 🥂")
        for idx, order in enumerate(active_orders):
            st.markdown(f"### 👤 {order['guest']} ordered **{order['name']}**")
            st.write(f"**Ingredients:** {order['ingredients']} | **Strength:** {order['strength']}")
            if st.button(f"Serve {order['guest']}", key=f"serve_{idx}"):
                order['status'] = "Served"
                st.rerun()
            st.markdown("---")

        st.subheader("📊 Cocktail Leaderboard & Ratings")
        served_orders = [o for o in st.session_state.orders if o['status'] == "Served" and o['rating'] is not None]
        if served_orders:
            rdf = pd.DataFrame(served_orders)
            leaderboard_df = rdf.groupby('name')['rating'].mean().reset_index().rename(columns={'name': 'Cocktail', 'rating': 'Rating (1-10)'})
            st.dataframe(leaderboard_df.sort_values(by='Rating (1-10)', ascending=False))
        else: st.write("No ratings submitted yet.")

    # --- EKRAN B: KORISNIČKO SUČELJE ZA GOSTE (Naručivanje) ---
    else:
        unnotified_served = [o for o in st.session_state.orders if o['guest'] == current_user and o['status'] == "Served" and not o.get('notified', False)]
        if unnotified_served:
            st.markdown('<div class="notification">🔔 Your cocktail is ready! Come and get it! 🍹</div>', unsafe_allow_html=True)
            for o in unnotified_served: o['notified'] = True

        st.title(f"🍹 Welcome to the Bar, {current_user}!")
        if st.sidebar.button("Logout 🚪"):
            st.session_state.logged_in = False
            st.session_state.user = None
            st.rerun()

        if df_cocktails is None: 
            st.error("Missing cocktails_za_claudea.csv file on GitHub!")
        else:
            st.subheader("Mix Your Ingredients")
            if 'chk_state' not in st.session_state:
                st.session_state.chk_state = {ing: False for ing in ["Gin", "Vodka", "Rum", "Orange Juice", "Cranberry Juice", "Blueberry Juice", "Pineapple Juice", "Grenadine", "Blue Curacao", "Coca-Cola", "Jamnica", "Lemonade"]}

            col1, col2, col3, col4, col5 = st.columns(5)
            current_alcohols = sum([st.session_state.chk_state[x] for x in ["Gin", "Vodka", "Rum"]])
            current_juices = sum([st.session_state.chk_state[x] for x in ["Orange Juice", "Cranberry Juice", "Blueberry Juice", "Pineapple Juice"]])
            total_selected = sum(st.session_state.chk_state.values())

            with col1:
                st.markdown("**Alcohol (Max 2)**")
                g1 = st.checkbox("Gin", value=st.session_state.chk_state["Gin"], disabled=not st.session_state.chk_state["Gin"] and (current_alcohols >= 2 or total_selected >= 7))
                g2 = st.checkbox("Vodka", value=st.session_state.chk_state["Vodka"], disabled=not st.session_state.chk_state["Vodka"] and (current_alcohols >= 2 or total_selected >= 7))
                g3 = st.checkbox("Rum", value=st.session_state.chk_state["Rum"], disabled=not st.session_state.chk_state["Rum"] and (current_alcohols >= 2 or total_selected >= 7))
            with col2:
                st.markdown("**Juices (Max 2)**")
                s1 = st.checkbox("Orange Juice", value=st.session_state.chk_state["Orange Juice"], disabled=not st.session_state.chk_state["Orange Juice"] and (current_juices >= 2 or total_selected >= 7))
                s2 = st.checkbox("Cranberry Juice", value=st.session_state.chk_state["Cranberry Juice"], disabled=not st.session_state.chk_state["Cranberry Juice"] and (current_juices >= 2 or total_selected >= 7))
                s3 = st.checkbox("Blueberry Juice", value=st.session_state.chk_state["Blueberry Juice"], disabled=not st.session_state.chk_state["Blueberry Juice"] and (current_juices >= 2 or total_selected >= 7))
                s4 = st.checkbox("Pineapple Juice", value=st.session_state.chk_state["Pineapple Juice"], disabled=not st.session_state.chk_state["Pineapple Juice"] and (current_juices >= 2 or total_selected >= 7))
            with col3:
                st.markdown("**Syrups**")
                si1 = st.checkbox("Grenadine", value=st.session_state.chk_state["Grenadine"], disabled=not st.session_state.chk_state["Grenadine"] and total_selected >= 7)
                si2 = st.checkbox("Blue Curacao", value=st.session_state.chk_state["Blue Curacao"], disabled=not st.session_state.chk_state["Blue Curacao"] and total_selected >= 7)
            with col4:
                st.markdown("**Carbonated**")
                gz1 = st.checkbox("Coca-Cola", value=st.session_state.chk_state["Coca-Cola"], disabled=not st.session_state.chk_state["Coca-Cola"] and total_selected >= 7)
                gz2 = st.checkbox("Jamnica", value=st.session_state.chk_state["Jamnica"], disabled=not st.session_state.chk_state["Jamnica"] and total_selected >= 7)
            with col5:
                st.markdown("**Sour**")
                k1 = st.checkbox("Lemonade", value=st.session_state.chk_state["Lemonade"], disabled=not st.session_state.chk_state["Lemonade"] and total_selected >= 7)

            st.session_state.chk_state = {"Gin":g1,"Vodka":g2,"Rum":g3,"Orange Juice":s1,"Cranberry Juice":s2,"Blueberry Juice":s3,"Pineapple Juice":s4,"Grenadine":si1,"Blue Curacao":si2,"Coca-Cola":gz1,"Jamnica":gz2,"Lemonade":k1}
            if sum(st.session_state.chk_state.values()) != total_selected: st.rerun()

            odabrano = [key for key, val in st.session_state.chk_state.items() if val]

            if st.button("Done 🔮"):
                alk_c = sum([g1,g2,g3])
                sir_c = sum([si1,si2])
                sok_c = sum([s1,s2,s3,s4])
                gaz_c = sum([gz1,gz2])

                if len(odabrano) < 3: 
                    st.error("🛑 Select minimum 3 ingredients total!")
                elif alk_c == 0: 
                    st.error("🛑 You must select at least 1 Alcoholic base!")
                elif k1 and alk_c > 0 and len(odabrano) == alk_c + 1: 
                    st.error("🛑 Alcohol + Lemonade cannot go alone! Add juice or soda.")
                elif k1 and sir_c > 0 and not (sok_c > 0 or gaz_c > 0): 
                    st.error("🛑 Too sweet! Add a juice or soda to dilute.")
                elif sir_c > 0 and len(odabrano) == alk_c + sir_c: 
                    st.error("🛑 Alcohol + Syrup cannot go alone! Add a mixer.")
                else:
                    st.session_state.selected_ingredients = " + ".join(sorted(odabrano))
                    st.session_state.matched_cocktail = "Custom Tranquillo Mix"

                    for idx, row in df_cocktails.iterrows():
                        row_ing = " + ".join(sorted([i.strip() for i in str(row['Ingredients']).split('+')]))
                        if row_ing == st.session_state.selected_ingredients:
                            st.session_state.matched_cocktail = row['Cocktail Name']
                            break

            if st.session_state.matched_cocktail:
                st.success(f"🔮 Created: **{st.session_state.matched_cocktail}**")
                jacina = st.radio("Strength:", ["Light", "Strong"], horizontal=True)

                if st.button("Order Cocktail 🚀"):
                    st.session_state.orders.append({
                        'guest': current_user, 'name': st.session_state.matched_cocktail, 
                        'ingredients': st.session_state.selected_ingredients, 'strength': jacina, 
                        'status': "In preparation", 'rating': None, 'notified': False
                    })
                    st.toast("Order sent to the Bar!")
                    st.session_state.matched_cocktail = None
                    st.session_state.chk_state = {ing: False for ing in st.session_state.chk_state.keys()}
                    st.rerun()

        st.markdown("---")
        st.subheader("📋 Your Cocktail History & Ratings")
        user_orders = [o for o in st.session_state.orders if o['guest'] == current_user]

        if not user_orders: 
            st.write("No orders yet tonight. Start mixing! 🍸")
        else:
            for idx, o in enumerate(user_orders):
                col_i, col_r = st.columns(2)
                with col_i:
                    st.markdown(f"**{o['name']}** ({o['strength']}) - {o['status']}")
                    st.caption(f"Ingredients: {o['ingredients']}")
                with col_r:
                    if o['status'] == "Served":
                        if o['rating'] is None:
                            ocjena = st.slider("Rate 1-10:", 1, 10, 5, key=f"sld_{idx}")
                            if st.button("Submit Rate", key=f"btn_{idx}"):
                                o['rating'] = ocjena
                                st.rerun()
                        else: 
                            st.write(f"⭐ Rating: **{o['rating']}/10**")
                st.markdown("---")
