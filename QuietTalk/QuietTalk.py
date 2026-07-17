import streamlit as st
import sqlite3
import random
from datetime import datetime
import re

DB_NAME = "baza_czatu.db"

def init_db():
    with sqlite3.connect(DB_NAME, check_same_thread=False) as conn:
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

def run_query(query, params=(), commit=False, fetchone=False, fetchall=False):
    with sqlite3.connect(DB_NAME, check_same_thread=False) as conn:
        c = conn.cursor()
        c.execute(query, params)
        if commit:
            conn.commit()
        if fetchone:
            return c.fetchone()
        if fetchall:
            return c.fetchall()
    return None

init_db()

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

if not st.session_state.user:
    st.markdown("<h1 style='text-align: center; color: #00f2fe; font-family: sans-serif; font-weight: bold; text-shadow: 0 0 15px rgba(0,242,254,0.6);'>🛸 QuietTalk</h1>", unsafe_allow_html=True)
    
    if st.session_state.view == "login":
        st.markdown("<div class='login-box'>", unsafe_allow_html=True)
        login_nick = st.text_input("Nick:")
        login_haslo = st.text_input("Hasło:", type="password")
        
        if st.button("Zaloguj się", use_container_width=True):
            user_exists = run_query("SELECT nick FROM uzytkownicy WHERE nick=? AND haslo=?", (login_nick.strip(), login_haslo.strip()), fetchone=True)
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
            if reg_email and reg_telefon and reg_nick and reg_haslo:
                if not re.match(r"[^@]+@[^@]+\.[^@]+", reg_email):
                    st.error("Wpisz poprawny adres e-mail (np. ktos@domena.pl)!")
                elif not reg_telefon.isdigit() or len(reg_telefon) < 9:
                    st.error("Numer telefonu musi składać się z samych cyfr i mieć min. 9 znaków!")
                else:
                    try:
                        run_query("INSERT INTO uzytkownicy (email, telefon, nick, haslo) VALUES (?, ?, ?, ?)",
                                  (reg_email.strip(), reg_telefon.strip(), reg_nick.strip(), reg_haslo.strip()), commit=True)
                        st.success("Konto założone!")
                        st.session_state.view = "login"
                        st.rerun()
                    except sqlite3.IntegrityError:
                        st.error("Nick lub Email jest już zajęty!")
            else:
                st.error("Uzupełnij wszystkie pola!")
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
            st.session_state.active_dm = ""
            st.rerun()
        st.divider()
        
        @st.fragment(run_every=5)
        def sprawdz_zaproszenia():
            st.markdown("📩 **Zaproszenia do znajomych**")
            zaproszenia = run_query("SELECT user_od FROM znajomi WHERE user_do=? AND status='oczekujace'", (st.session_state.user,), fetchall=True)
            if zaproszenia:
                for zap in zaproszenia:
                    osoba = str(zap[0])
                    col_z1, col_z2 = st.columns(2)
                    with col_z1:
                        if st.button(f"✅ {osoba}", key=f"acc_{osoba}", use_container_width=True):
                            run_query("UPDATE znajomi SET status='zaakceptowane' WHERE user_od=? AND user_do=?", (osoba, st.session_state.user), commit=True)
                            st.rerun()
                    with col_z2:
                        if st.button(f"❌ {osoba}", key=f"dec_{osoba}", use_container_width=True):
                            run_query("DELETE FROM znajomi WHERE user_od=? AND user_do=?", (osoba, st.session_state.user), commit=True)
                            st.rerun()
            else:
                st.write("Brak nowych zaproszeń.")
                
        sprawdz_zaproszenia()
        
        st.divider()
        
        st.markdown("🔍 **Szukaj znajomych**")
        szukaj = st.text_input("Wpisz nick:", label_visibility="collapsed")
        if szukaj.strip():
            znalezieni = run_query("SELECT nick FROM uzytkownicy WHERE nick LIKE ? AND nick != ?", (f"%{szukaj.strip()}%", st.session_state.user), fetchall=True)
            for z in znalezieni:
                osoba = str(z[0])
                relacja = run_query("SELECT status FROM znajomi WHERE (user_od=? AND user_do=?) OR (user_od=? AND user_do=?)",
                                    (st.session_state.user, osoba, osoba, st.session_state.user), fetchone=True)
                if not relacja:
                    if st.button(f"➕ Zaproś {osoba}", key=f"inv_{osoba}", use_container_width=True):
                        run_query("INSERT INTO znajomi (user_od, user_do, status) VALUES (?, ?, 'oczekujace')", (st.session_state.user, osoba), commit=True)
                        st.success(f"Wysłano do {osoba}!")
                        st.rerun()
                else:
                    st.write(f"👥 {osoba} ({relacja[0]})")
                    
        st.divider()
        
        st.markdown("💬 **Bezpośrednie wiadomości (DM)**")
        lista_znajomych = run_query("""
            SELECT user_do FROM znajomi WHERE user_od=? AND status='zaakceptowane'
            UNION
            SELECT user_od FROM znajomi WHERE user_do=? AND status='zaakceptowane'
        """, (st.session_state.user, st.session_state.user), fetchall=True)
        
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
        
        @st.fragment(run_every=3)
        def wyswietl_czat():
            rozmowa = run_query("""
                SELECT nadawca, tresc FROM wiadomosci_dm 
                WHERE (nadawca=? AND odbiorca=?) OR (nadawca=? AND odbiorca=?) 
                ORDER BY id ASC
            """, (st.session_state.user, st.session_state.active_dm, st.session_state.active_dm, st.session_state.user), fetchall=True)
            
            for nadawca, tresc in rozmowa:
                rola = "user" if nadawca == st.session_state.user else "assistant"
                with st.chat_message(rola):
                    st.write(f"**{nadawca}**: {tresc}")

        wyswietl_czat()
                
        if prompt := st.chat_input(f"Napisz do {st.session_state.active_dm}..."):
            teraz = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            run_query("INSERT INTO wiadomosci_dm (nadawca, odbiorca, tresc, data) VALUES (?, ?, ?, ?)",
                      (st.session_state.user, st.session_state.active_dm, prompt, teraz), commit=True)
            st.rerun()
