import streamlit as st
import sqlite3
from datetime import datetime

conn = sqlite3.connect("baza_czatu.db", check_same_thread=False)
c = conn.cursor()
c.execute("""
    CREATE TABLE IF NOT EXISTS wiadomosci (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        autor TEXT,
        tresc TEXT,
        data TEXT
    )
""")
conn.commit()

st.set_page_config(page_title="Prywatny Komunikator", page_icon="🔒")
st.title("🔒 Nasz Prywatny Komunikator")

if "user" not in st.session_state:
    st.session_state.user = ""

if not st.session_state.user:
    st.subheader("Kim jesteś?")
    imie = st.text_input("Wpisz swoje imię lub pseudonim:")
    if st.button("Wejdź do czatu"):
        if imie.strip():
            st.session_state.user = imie.strip()
            st.rerun()
else:
    st.sidebar.write(f"Zalogowany jako: **{st.session_state.user}**")
    if st.sidebar.button("Wyloguj"):
        st.session_state.user = ""
        st.rerun()

    c.execute("SELECT autor, tresc FROM wiadomosci ORDER BY id ASC")
    wszystkie_wiadomosci = c.fetchall()

    for autor, tresc in wszystkie_wiadomosci:
        rola = "user" if autor == st.session_state.user else "assistant"
        with st.chat_message(rola):
            st.write(f"**{autor}**: {tresc}")

    if prompt := st.chat_input("Napisz wiadomość..."):
        teraz = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        c.execute("INSERT INTO wiadomosci (autor, tresc, data) VALUES (?, ?, ?)", 
                  (st.session_state.user, prompt, teraz))
        conn.commit()
        st.rerun()
