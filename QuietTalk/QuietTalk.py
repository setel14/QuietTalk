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
    CREATE TABLE IF NOT EXISTS wiadomosci (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        autor TEXT,
        tresc TEXT,
        data TEXT
    )
""")
conn.commit()

st.set_page_config(page_title="QuietTalk", page_icon="🔒", layout="centered")

st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    .stApp {
        background: radial-gradient(circle at center, #0052d4 0%, #4364f7 50%, #6fb1fc 100%);
        background-attachment: fixed;
    }
    
    .login-box {
        background-color: rgba(10, 25, 47, 0.85);
        padding: 30px;
        border-radius: 15px;
        border: 2px solid #00f2fe;
        box-shadow: 0px 0px 20px rgba(0, 242, 254, 0.5);
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

if "user" not in st.session_state:
    st.session_state.user = st.query_params.get("u", "")

if "view" not in st.session_state:
    st.session_state.view = "login"

if st.session_state.user:
    st.fragment(run_every=3)(lambda: None)()

if not st.session_state.user:
    st.markdown("<h1 style='text-align: center; color: #00f2fe; font-family: sans-serif;'>🛸 QuietTalk</h1>", unsafe_allow_html=True)
    
    if st.session_state.view == "login":
        st.markdown("<div class='login-box'>", unsafe_allow_html=True)
        st.subheader("Zaloguj się")
        
        login_nick = st.text_input("Nick:")
        login_haslo = st.text_input("Hasło:", type="password")
        
        if st.button("Zaloguj się", use_container_width=True):
            c.execute("SELECT nick FROM uzytkownicy WHERE nick=? AND haslo=?", (login_nick.strip(), login_haslo.strip()))
            user_exists = c.fetchone()
            if user_exists:
                st.session_state.user = str(user_exists[0])
                st.query_params["u"] = str(user_exists[0])
                st.rerun()
            else:
                st.error("Nieprawidłowy nick lub hasło!")
                
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Stwórz konto (Rejestracja)", use_container_width=True):
                st.session_state.view = "register"
                st.rerun()
        with col2:
            if st.button("Nie pamiętam hasła", use_container_width=True):
                st.session_state.view = "reset"
                st.rerun()
        st.markdown("</div>", unsafe_hidden_html=True)

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
                    st.success("Konto założone! Możesz się zalogować.")
                    st.session_state.view = "login"
                    st.rerun()
                except sqlite3.IntegrityError:
                    st.error("Ten Nick lub Email jest już zajęty!")
            else:
                st.error("Uzupełnij wymagane pola (Email, Nick, Hasło)!")
                
        if st.button("Powrót do logowania", use_container_width=True):
            st.session_state.view = "login"
            st.rerun()
        st.markdown("</div>", unsafe_hidden_html=True)

    elif st.session_state.view == "reset":
        st.markdown("<div class='login-box'>", unsafe_allow_html=True)
        st.subheader("Odzyskiwanie hasła")
        
        reset_input = st.text_input("Wpisz swój E-mail lub Numer telefonu:")
        
        if st.button("Wyślij kod weryfikacyjny", use_container_width=True):
            if reset_input.strip():
                losowy_kod = random.randint(100000, 999999)
                st.info(f"🔒 Twój kod resetujący (symulacja): {losowy_kod}")
                st.success("Kod został wysłany!")
            else:
                st.error("Wpisz dane!")
                
        if st.button("Powrót do logowania", use_container_width=True):
            st.session_state.view = "login"
            st.rerun()
        st.markdown("</div>", unsafe_hidden_html=True)

else:
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"🛸 Rozmawiasz jako: **{st.session_state.user}**")
    with col2:
        if st.button("Wyloguj", use_container_width=True):
            st.session_state.user = ""
            st.query_params.clear()
            st.rerun()
    
    st.divider()

    c.execute("SELECT autor, tresc FROM wiadomosci ORDER BY id ASC")
    wszystkie_wiadomosci = c.fetchall()

    for autor, tresc in wszystkie_wiadomosci:
        rola = "user" if autor == st.session_state.user else "assistant"
        with st.chat_message(rola):
            st.write(f"**{autor}**: {tresc}")

    if prompt := st.chat_input("Napisz cichą wiadomość..."):
        teraz = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        c.execute("INSERT INTO wiadomosci (autor, tresc, data) VALUES (?, ?, ?)", 
                  (st.session_state.user, prompt, teraz))
        conn.commit()
        st.rerun()
