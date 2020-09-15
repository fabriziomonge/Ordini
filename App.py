#!/usr/bin/env python
# coding: utf-8

# In[ ]:

import base64
import pandas as pd
import streamlit as st
from ftplib import FTP
import ftplib

st.title("Elaboratore ordini")

#Importo i dati
uploaded_file1 = st.sidebar.file_uploader("Carica il file Excel di AMAZON", type=["xlsx"])
uploaded_file2 = st.sidebar.file_uploader("Carica il file Excel di Bongiovanni", type=["xlsx"])

if uploaded_file1 is not None and uploaded_file2 is not None:

    df=pd.read_excel(uploaded_file1, header=4)

    #creo univoco etichette

    lista_etichette_univoci = list(df['Codice di riferimento corriere'].unique())
    df_etichette_univoci = pd.DataFrame(lista_etichette_univoci, index=range(1,len(lista_etichette_univoci)+1), columns=['Etichetta'])


    #Creo univoco prodotti
    lista_prodotti_univoci = list(df['Titolo'].unique())
    lista_prodotti_univoci = pd.DataFrame(lista_prodotti_univoci, columns=['prodotto'])
    lista_prodotti_univoci['progressivo']=lista_prodotti_univoci.index
    lista_prodotti_univoci = lista_prodotti_univoci.set_index('prodotto', drop=True)

    #Importo il file di Bongiovanni

    df1 = pd.read_excel(uploaded_file2)

    # elimino i non confermati
    df1 = df1.loc[df1['Quantita confermata']>0]
    df1 = df1.reset_index(drop=True)

    #Aggiungo delle righe per ogni scatola nel range

    df1['colli_nel_range']=df1['collo a']-df1['collo da']+1
    df_lavorato = pd.DataFrame(columns=df1.columns)
    for i in range(len(df1)):
        df_riga = df1.loc[df1.index==i]
        ncolli = df_riga['colli_nel_range'][i]

        for i2 in range(int(ncolli)):
            riga_aggiunta = df_riga
            df_lavorato = df_lavorato.append(riga_aggiunta)


    # Modifico le quantità confermate nelle righe multicollo 

    df_lavorato = df_lavorato.reset_index(drop=True)
    lista_Q2 = []

    i = 0
    while i < (len(df_lavorato)):
        Q = int(df_lavorato['Quantita confermata'][i])
        C = int(df_lavorato['colli_nel_range'][i])
        if C > 1:
            div = Q/C
            divint = Q//C

            if div == divint:
                for i2 in range(C):
                    Q2 = Q/C
                    lista_Q2.append(Q2)
                    i = i+1
            else:
                for i2 in range(C-1):
                    Q2 = Q//(C-1)
                    lista_Q2.append(Q2)
                    i = i+1
                Q2 = Q%(C-1)
                lista_Q2.append(Q2)
                i=i+1

        else:
            lista_Q2.append(Q)
            i = i+1


    df_lavorato['Quantita spedita'] = lista_Q2    

    # creo una colonna collo univoca

    aggiunta = 0
    lista_somme = []
    passaggio = 0

    for i in df_lavorato['collo da']:
            if passaggio == 0:
                lista_somme.append(int(i))
                aggiunta = 0
            else:
                if df_lavorato['collo da'][passaggio] != df_lavorato['collo da'][passaggio-1] or df_lavorato['colli_nel_range'][passaggio] ==1:
                    aggiunta = 0
                    lista_somme.append(int(i+aggiunta))
                else:
                    aggiunta = aggiunta+1
                    lista_somme.append(int(i+aggiunta))
            passaggio = passaggio+1


    df_lavorato['collo'] = lista_somme

    df_lavorato = df_lavorato.sort_values(by='collo')

    df_lavorato = df_lavorato.reset_index(drop=True)


    # Aggiungo le etichette

    lista_etichetta=[]
    for i in df_lavorato['collo']:
        etichetta = df_etichette_univoci['Etichetta'][i]
        lista_etichetta.append(etichetta)
    df_lavorato['Codice di riferimento corriere']=lista_etichetta

    # Compilo il df definitivo

    df_definitivo = pd.DataFrame(df_lavorato['Codice di riferimento corriere'])
    df_definitivo['Numero OdA'] = df_lavorato['Numero OdA/Ordine']
    df_definitivo['ID esterno'] = df_lavorato['Numero esterno']
    df_definitivo['Numero modello'] = df_lavorato['Numero modello']
    df_definitivo['Titolo'] = df_lavorato['Titolo']
    df_definitivo['ASIN'] = df_lavorato['ASIN']
    df_definitivo['Confermati'] = df_lavorato['Quantita confermata']
    df_definitivo['ASN precedenti'] = df['ASN precedenti']
    df_definitivo['Spediti'] = df_lavorato['Quantita spedita']
    df_definitivo['Data di scadenza (solo per prodotti deperibili)'] = df_lavorato['scadenza']
    df_definitivo['Numero del lotto(se applicabile)'] = df_lavorato['lotto']


    # ricopio il numero esterno e il lotto come stringhe

    lista_n_est = list(df_definitivo['ID esterno'])
    lista_n_est_str = []
    for i in lista_n_est:
        stringa = str(i)
        lista_n_est_str.append(stringa)

    df_definitivo['ID esterno'] = lista_n_est_str

    lista_lotto = list(df_definitivo['Numero del lotto(se applicabile)'])
    lista_lotto_str = []
    for i in lista_lotto:
        stringa = str(i)
        lista_lotto_str.append(stringa)

    df_definitivo['Numero del lotto(se applicabile)'] = lista_lotto_str

    df_definitivo
    
    df_definitivo.to_excel('dati_ordini.xlsx')
    
    # Controllo se ci sono tutti i colli necessari
    
    colli_presenti= list(df_lavorato.collo.unique())
    colli_necessari = list(range(1, df_lavorato.collo.unique().max()+1))
    lista_mancanti = []

    for i in colli_necessari:
        if i not in colli_presenti:
            lista_mancanti.append(i)

    if len(lista_mancanti) >0 :
        st.write("## Eccezione: nella conferma d'ordine mancano i colli: ", lista_mancanti)

    else:
        st.write("## Controllo effettuato: tutti i colli necessari sono presenti nella conferma di ordine")
    
    ftp = FTP('ftp.onstatic-it.setupdns.net')     # connect to host, default port
    ftp.login(user='fabrizio.monge', passwd='Ciuciuska88')
    ftp.cwd('Bongiovanni') 
    file = open('dati_ordini.xlsx', 'rb')
    ftp.storbinary('STOR dati_ordini.xlsx', file)
    file.close()
    ftp.quit()
    print('Ordini caricati sul server')

    
    st.write("""## Puoi scaricare il file a questo link""")
    st.write('http://www.sphereresearch.net/Bongiovanni/dati_ordini.xlsx')
    
    
    



