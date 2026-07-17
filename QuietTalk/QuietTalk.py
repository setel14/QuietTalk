import streamlit as st
import sqlite3
import random
from datetime import datetime

conn = sqlite3.connect("baza_czatu.db", check_same_thread=False)
c = conn.cursor()
c.execute("""
    CREATE TABLE IF NOT EXISTS uzytkownicy (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE,
        telefon TEXT,
        nick TEXT UNIQUE,
        haslo TEXT
    )
""")
c.execute("""
    CREATE TABLE IF NOT EXISTS znajomi (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_od TEXT,
        user_do TEXT,
        status TEXT
    )
""")
c.execute("""
    CREATE TABLE IF NOT EXISTS wiadomosci_dm (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nadawca TEXT,
        odbiorca TEXT,
        tresc TEXT,
        data TEXT
    )
""")
conn.commit()

st.set_page_config(page_title="QuietTalk", page_icon="🔒", layout="wide")

st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    .stApp {
        background: radial-gradient(circle at center, #0052d4 0%, #4364f7 50%, #6fb1fc 100%);
        background-attachment: fixed;
        color: #ffffff;
    }
    .login-box {
        background-color: rgba(10, 25, 47, 0.9);
        padding: 40px;
        border-radius: 15px;
        border: 2px solid #00f2fe;
        box-shadow: 0px 0px 25px rgba(0, 242, 254, 0.6);
        max-width: 400px;
        margin: 50px auto;
        color: white;
    }
    div[data-testid="stSidebar"] {
        background-color: rgba(10, 25, 47, 0.95);
        border-right: 2px solid #00f2fe;
    }
    div[data-testid="stSidebar"] * {
        color: white !important;
    }
    .stButton>button {
        background-color: transparent !important;
        color: #00f2fe !important;
        border: 1px solid #00f2fe !important;
        box-shadow: 0px 0px 10px rgba(0, 242, 254, 0.2);
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #00f2fe !important;
        color: #0a192f !important;
        box-shadow: 0px 0px 20px rgba(0, 242, 254, 0.6);
    }
    </style>
""", unsafe_allow_html=True)

if "user" not in st.session_state:
    st.session_state.user = ""
if "view" not in st.session_state:
    st.session_state.view = "login"
if "active_dm" not in st.session_state:
    st.session_state.active_dm = ""

if st.session_state.user:
    st.fragment(run_every=3)(lambda: None)()

if not st.session_state.user:
    st.markdown("<h1 style='text-align: center; color: #00f2fe; font-family: sans-serif; font-weight: bold; text-shadow: 0 0 15px rgba(0,242,254,0.6);'>🛸 QuietTalk</h1>", unsafe_allow_html=True)
    
    if st.session_state.view == "login":
        st.markdown("<div class='login-box'>", unsafe_allow_html=True)
        login_nick = st.text_input("Nick:")
        login_haslo = st.text_input("Hasło:", type="password")
        
        if st.button("Zaloguj się", use_container_width=True):
            c.execute("SELECT nick FROM uzytkownicy WHERE nick=? AND haslo=?", (login_nick.strip(), login_haslo.strip()))
            user_exists = c.fetchone()
            if user_exists:
                st.session_state.user = str(user_exists[0])
                st.rerun()
            else:
                st.error("Nieprawidłowy nick lub hasło!")
                
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Rejestracja", use_container_width=True):
                st.session_state.view = "register"
                st.rerun()
        with col2:
            if st.button("Reset hasła", use_container_width=True):
                st.session_state.view = "reset"
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    elif st.session_state.view == "register":
        st.markdown("<div class='login-box'>", unsafe_allow_html=True)
        st.subheader("Zarejestruj się")
        reg_email = st.text_input("E-mail:")
        reg_telefon = st.text_input("Numer telefonu:")
        reg_nick = st.text_input("Twój Nick:")
        reg_haslo = st.text_input("Hasło:", type="password")
        
        if st.button("Załóż konto", use_container_width=True):
            if reg_email and reg_nick and reg_haslo:
                try:
                    c.execute("INSERT INTO uzytkownicy (email, telefon, nick, haslo) VALUES (?, ?, ?, ?)",
                              (reg_email.strip(), reg_telefon.strip(), reg_nick.strip(), reg_haslo.strip()))
                    conn.commit()
                    st.success("Konto założone!")
                    st.session_state.view = "login"
                    st.rerun()
                except sqlite3.IntegrityError:
                    st.error("Nick lub Email jest już zajęty!")
            else:
                st.error("Uzupełnij wymagane pola!")
        if st.button("Powrót", use_container_width=True):
            st.session_state.view = "login"
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    elif st.session_state.view == "reset":
        st.markdown("<div class='login-box'>", unsafe_allow_html=True)
        st.subheader("Odzyskiwanie hasła")
        reset_input = st.text_input("E-mail lub Telefon:")
        if st.button("Wyślij kod", use_container_width=True):
            if reset_input.strip():
                st.info(f"🔒 Kod (symulacja): {random.randint(100000, 999999)}")
            else:
                st.error("Wpisz dane!")
        if st.button("Powrót", use_container_width=True):
            st.session_state.view = "login"
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

else:
    with st.sidebar:
        st.markdown(f"### 👤 **{st.session_state.user}**")
        if st.button("🔒 Wyloguj", use_container_width=True):
            st.session_state.user = ""
            st.rerun()
        st.divider()
        
        st.markdown("📩 **Zaproszenia do znajomych**")
        c.execute("SELECT user_od FROM znajomi WHERE user_do=? AND status='oczekujace'", (st.session_state.user,))
        zaproszenia = c.fetchall()
        if zaproszenia:
            for zap in zaproszenia:
                osoba = str(zap[0])
                col_z1, col_z2 = st.columns(2)
                with col_z1:
                    if st.button(f"✅ {osoba}", key=f"acc_{osoba}", use_container_width=True):
                        c.execute("UPDATE znajomi SET status='zaakceptowane' WHERE user_od=? AND user_do=?", (osoba, st.session_state.user))
                        conn.commit()
                        st.rerun()
                with col_z2:
                    if st.button(f"❌ {osoba}", key=f"dec_{osoba}", use_container_width=True):
                        c.execute("DELETE FROM znajomi WHERE user_od=? AND user_do=?", (osoba, st.session_state.user))
                        conn.commit()
                        st.rerun()
        else:
            st.write("Brak nowych zaproszeń.")
        
        st.divider()
        
        st.markdown("🔍 **Szukaj znajomych**")
        szukaj = st.text_input("Wpisz nick:", label_visibility="collapsed")
        if szukaj.strip():
            c.execute("SELECT nick FROM uzytkownicy WHERE nick LIKE ? AND nick != ?", (f"%{szukaj.strip()}%", st.session_state.user))
            znalezieni = c.fetchall()
            for z in znalezieni:
                osoba = str(z[0])
                c.execute("SELECT status FROM znajomi WHERE (user_od=? AND user_do=?) OR (user_od=? AND user_do=?)",
                          (st.session_state.user, osoba, osoba, st.session_state.user))
                relacja = c.fetchone()
                if not relacja:
                    if st.button(f"➕ Zaproś {osoba}", key=f"inv_{osoba}", use_container_width=True):
                        c.execute("INSERT INTO znajomi (user_od, user_do, status) VALUES (?, ?, 'oczekujace')", (st.session_state.user, osoba))
                        conn.commit()
                        st.success(f"Wysłano do {osoba}!")
                        st.rerun()
                else:
                    st.write(f"👥 {osoba} ({relacja[0]})")
                    
        st.divider()
        
        st.markdown("💬 **Bezpośrednie wiadomości (DM)**")
        c.execute("""
            SELECT user_do FROM znajomi WHERE user_od=? AND status='zaakceptowane'
            UNION
            SELECT user_od FROM znajomi WHERE user_do=? AND status='zaakceptowane'
        """, (st.session_state.user, st.session_state.user))
        lista_znajomych = c.fetchall()
        
        if lista_znajomych:
            for zn in lista_znajomych:
                przyjaciel = str(zn[0])
                style_btn = f"📥 {przyjaciel}"
                if st.session_state.active_dm == przyjaciel:
                    style_btn = f"🔥 {przyjaciel}"
                if st.button(style_btn, key=f"dm_{przyjaciel}", use_container_width=True):
                    st.session_state.active_dm = przyjaciel
                    st.rerun()
        else:
            st.write("Dodaj znajomych, aby zacząć DM.")

    if st.session_state.active_dm:
        st.markdown(f"## 💬 Czat z: **{st.session_state.active_dm}**")
        st.divider()
        
        c.execute("""
            SELECT nadawca, tresc FROM wiadomosci_dm 
            WHERE (nadawca=? AND odbiorca=?) OR (nadawca=? AND odbiorca=?) 
            ORDER BY id ASC
        """, (st.session_state.user, st.session_state.active_dm, st.session_state.active_dm, st.session_state.user))
        rozmowa = c.fetchall()
        
        for nadawca, tresc in rozmowa:
            rola = "user" if nadawca == st.session_state.user else "assistant"
            with st.chat_message(rola):
                st.write(f"**{nadawca}**: {tresc}")
                
        if prompt := st.chat_input(f"Napisz do {st.session_state.active_dm}..."):
            teraz = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            c.execute("INSERT INTO wiadomosci_dm (nadawca, odbiorca, tresc, data) VALUES (?, ?, ?, ?)",
