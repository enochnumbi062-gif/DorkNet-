#DorkNet Xchange - main.py
import streamlit as st
import streamlit_authenticator as stauth
import sqlite3
import backtrader as bt
import pandas as pd
import matplotlib.pyplot as plt
import yfinance as yf
import ta

# --- Configuration ---
names = ['admin']
usernames = ['dorknet']
passwords = ['dorknet123']
hashed_passwords = stauth.utils.hash_passwords(passwords)

# --- Authentification ---
authenticator = stauth.Authenticate(names, usernames, hashed_passwords,
                                    'dorknet_cookie', 'dorknet_secret', cookie_expiry_days=30)
name, authentication_status, username = authenticator.login('Login', 'main')

if authentication_status:
    # --- Connexion DB ---
    conn = sqlite3.connect('dorknet.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS trades
                 (id INTEGER PRIMARY KEY, devise TEXT, type TEXT, prix REAL, date TEXT)''')
    conn.commit()

    # --- Fonctions ---
    def save_trade(devise, type, prix):
        c.execute("INSERT INTO trades (devise, type, prix, date) VALUES (?, ?, ?, datetime('now'))",
                  (devise, type, prix))
        conn.commit()

    def get_trades():
        return c.execute("SELECT * FROM trades").fetchall()

    # --- Interface ---
    st.title('DorkNet Xchange')
    st.sidebar.subheader('Filtres')
    filtre_devise = st.sidebar.multiselect('Devises', ['USD/EUR', 'USD/GBP', 'USD/JPY'])
    filtre_periode = st.sidebar.selectbox('Période', ['1 mois', '3 mois', '6 mois', '1 an'])

    # Données exemple
    data = yf.download('EURUSD=X', period='1y')

    # Indicateurs techniques
    data['RSI'] = ta.momentum.rsi(data['Close'])
    data['MACD'] = ta.trend.macd(data['Close'])

    # Affichage
    st.subheader('Données EUR/USD')
    st.write(data)

    st.subheader('Indicateurs techniques')
    col1, col2 = st.columns(2)
    with col1:
        st.write('**RSI**')
        st.line_chart(data['RSI'])
    with col2:
        st.write('**MACD**')
        st.line_chart(data['MACD'])

    # Trades
    trades = get_trades()
    st.subheader('Historique des trades')
    st.write(trades)

    col1, col2, col3 = st.columns(3)
    with col1:
        devise = st.selectbox('Devise', ['USD/EUR', 'USD/GBP', 'USD/JPY'])
    with col2:
        type_trade = st.selectbox('Type', ['Achat', 'Vente'])
    with col3:
        prix = st.number_input('Prix', value=1.20)

    if st.button('Sauvegarder trade'):
        save_trade(devise, type_trade, prix)
        st.success('Trade sauvegardé !')

    #Graphique
    st.subheader('Évolution du portefeuille')
    plt.figure(figsize=(10,3))
    plt.plot(data['Close'], label='Prix')
    plt.legend()
    st.pyplot(plt)

    # Simulateur de portefeuille
    st.subheader('Simulateur de portefeuille')
    portefeuille = 1000  # Exemple
    st.write(f'Valeur initiale : **{portefeuille} €**')
    if st.button('Calculer gains'):
        gains = (data['Close'].iloc[-1] - data['Close'].iloc[0]) * 100
        st.write(f'Gains : **{gains:.2f} €**')

    # Alerte prix
    st.sidebar.subheader('Alerte prix')
    seuil = st.sidebar.number_input('Seuil (EUR/USD)', value=1.20)
    if data['Close'].iloc[-1] > seuil:
        st.sidebar.warning(f'Prix > {seuil} !')

elif authentication_status == False:
    st.error('Nom d\'utilisateur/mot de passe incorrect')
elif authentication_status == None:
    st.warning('Veuillez vous connecter')