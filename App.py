#!/usr/bin/env python
# coding: utf-8

# In[ ]:

import base64
import pandas as pd
import streamlit as st
from ftplib import FTP
import ftplib

st.title("Elaborazione ordini WebApp-2.0")

from PIL import Image
image = Image.open('Tool.png')
st.sidebar.image(image, use_column_width=True)

hide_streamlit_style = """
            <style>
            
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True) 



#Da qua incolla su server
#controllo accessi

url = 'http://www.sphereresearch.net//Bongiovanni/Accessi_Bongiovanni.xlsx'
accessi = pd.read_excel(url)
accessi = accessi.set_index('User', drop = True)
from datetime import datetime
import datetime
A = datetime.date.today()

st.write("""
#### Autenticazione:
""")

Utente = st.text_input("Inserire il nome utente")
Psw = st.text_input("Inserire la password", type='password')


try:
    
    if Psw == accessi['Password'][Utente] and accessi['Statcond'][Utente] == 1 and accessi['Scadenza'][Utente] > A :

        

        #Importo i dati
        uploaded_file1 = st.sidebar.file_uploader("Carica il file Excel di AMAZON", type=["xlsx"])
        uploaded_file2 = st.sidebar.file_uploader("Carica il file Excel di Bongiovanni", type=["xlsx"])

        #Espongo i dettagli utente
        st.sidebar.markdown("Utente:")
        st.sidebar.markdown(Utente)
        st.sidebar.markdown("Ruolo:")
        st.sidebar.markdown(accessi['Tipo'][Utente])

        if uploaded_file1 is not None:

            df=pd.read_excel(uploaded_file1, header=4)
            st.write("""### File Amazon importato""")
            df_show = df.head(3)
            df_show

        if uploaded_file2 is not None:

            df1=pd.read_excel(uploaded_file2)
            st.write("""### File Azienda importato""")
            df1_show = df1.head(3)
            df1_show

            lista_colonne_corretta = ['Numero OdA/Ordine', 'Numero esterno', 'Numero modello', 'ASIN', 'Titolo', 'Prezzo di listino', 'Sconto', 'Costo', 'Quantita confermata', 'scadenza', 'lotto', 'collo da', 'collo a']
            lista_colonne_inserita = list(df1.columns)

            if lista_colonne_inserita[:len(lista_colonne_corretta)] == lista_colonne_corretta:
                st.write("""#### il formato inserito corrisponde al template""")
                st.write("""### Procedo con l'elaborazione dei dati....""")
                controllo = True
            else:
                st.write("""### Il formato del "File azienda" inserito non corrisponde al template""")
                controllo = False
                bottone_aggiusta = st.button("Clicca qui per tentare di sistemare il formato automaticamente")
                if bottone_aggiusta == True:
                    lista_colonne_inserita[:len(lista_colonne_corretta)] = lista_colonne_corretta
                    df1 = pd.DataFrame(df1.values, columns = lista_colonne_inserita)
                    controllo = True
                    st.write("""### Il formato del file è stato sistemato""")
                    st.write("""### Procedo con l'elaborazione dei dati....""")

        if uploaded_file1 is not None and uploaded_file2 is not None and controllo == True:

            if df['Numero OdA'][0] != df1['Numero OdA/Ordine'][0]:
                st.write("""### > Attenzione, i due files corrispondono ad ordini differenti""")

            else:
                st.write("""### > Controllo N° odine superato con esito positivo""")

                # df=pd.read_excel(uploaded_file1, header=4)

                #creo univoco etichette

                lista_etichette_univoci = list(df['Codice di riferimento corriere'].unique())
                
                df_etichette_univoci = pd.DataFrame(lista_etichette_univoci, index=range(1,len(lista_etichette_univoci)+1), columns=['Etichetta'])

                #Creo univoco prodotti
                lista_prodotti_univoci = list(df['Titolo'].unique())
                lista_prodotti_univoci = pd.DataFrame(lista_prodotti_univoci, columns=['prodotto'])
                lista_prodotti_univoci['progressivo']=lista_prodotti_univoci.index
                lista_prodotti_univoci = lista_prodotti_univoci.set_index('prodotto', drop=True)

                #creo un dataframe di prodotti univoci



                #Importo il file di Bongiovanni

                # df1 = pd.read_excel(uploaded_file2)
                df1['collo a'] = df1['collo a'].fillna(df1['collo da'])

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
                while i < (len(df_lavorato)): #len(df_lavorato)
                    Q =int(df_lavorato['Quantita confermata'][i])
                    C =int(df_lavorato['colli_nel_range'][i])
                    if C > 1:
                        div = Q/C
                        divint = Q//C

                        if div == divint:
                            
                            for i2 in range(C):
                                Q2 = Q/C
                                lista_Q2.append(Q2)
                                i = i+1
                        else:
                            
                            somma = 0
                            for i2 in range(C-1):
                                Q2 = round(Q/C,0)
                                lista_Q2.append(Q2)
                                somma = somma+Q2
                                i = i+1
                            Q2 = Q-somma
                            lista_Q2.append(Q2)
                            i=i+1

                    else:
                        lista_Q2.append(Q)
                        i = i+1


                df_lavorato['Quantita spedita'] = lista_Q2    
                

                
                # df_lavorato['quantità_old'] = df.Confermati
                # df_lavorato.loc[df_lavorato['quantità_old'] != df_lavorato['quantità_old']]
                
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


                # faccio in modo da ricopiare i campi [Confermati, ID esterno, NUmero mod, Asin] di Amazon (df)
                lista_confermati = []
                lista_ID = []
                lista_modello = []
                lista_asin =[]

                for i in df_lavorato.Titolo:
                    settore = df.loc[df.Titolo== i].head(1)
                    settore = settore.reset_index(drop=True)

                    quantita = settore['Confermati'][0]
                    id = settore['ID esterno'][0]
                    modello = settore['Numero modello'][0]
                    asin = settore['ASIN'][0]

                    lista_confermati.append(int(quantita))
                    lista_ID.append(id)
                    lista_modello.append(modello)
                    lista_asin.append(asin)
                
                df_lavorato['Quantita confermata'] = lista_confermati
                df_lavorato['Numero esterno'] = lista_ID
                df_lavorato['Numero modello'] = lista_modello
                df_lavorato['ASIN'] = lista_asin

                #Verfico che la quantità confermata ad amazon corrisponda alla somma delle quantità per prodotto
                #creo una lista univoca per prodotto
                lista_prodotto_univoca = list(df_lavorato.Titolo.unique())
                lista_differenti = []
                lista_differenti_dic = []
                lista_differenti_conf = []
                for i in lista_prodotto_univoca:
                    estratto = df_lavorato.loc[df_lavorato.Titolo == i]
                    estratto = estratto.reset_index(drop=True)
                    somma = estratto['Quantita spedita'].sum()
                    if somma != estratto['Quantita confermata'][0]:
                        lista_differenti.append(i)
                        lista_differenti_dic.append(estratto['Quantita confermata'][0])
                        lista_differenti_conf.append(somma)
                df_differenti = pd.DataFrame(lista_differenti, columns=['Titolo'])
                df_differenti['Dichiarati'] = lista_differenti_dic
                df_differenti['In spedizione'] = lista_differenti_conf
                df_differenti = df_differenti.groupby('Titolo').last()
                

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


                st.write("""### Vista del file elaborato""")
                df_definitivo
                
                df_definitivo.to_excel('dati_ordini.xlsx')
                
                # Alcune misure
                colli_presenti= list(df_lavorato.collo.unique())
                colli_necessari = list(range(1, df_lavorato.collo.unique().max()+1))
                lista_mancanti = []
                
                Colli_tot_necessari = len(colli_necessari)
                Colli_totali_presenti = len(colli_presenti)
                Totale_articoli = df_definitivo.Spediti.sum()
                
                st.write("""### > Verifiche sul numero articoli e colli:""" )
                st.write("""#### Sono richiesti""",Colli_tot_necessari,""" Colli""" )
                st.write("""#### Sono in spedizione""",Colli_totali_presenti,""" Colli""" )
                st.write("""#### Stai per inviare""",Totale_articoli,""" Articoli""" )
                
                # Controllo se ci sono tutti i colli necessari
                


                for i in colli_necessari:
                    if i not in colli_presenti:
                        lista_mancanti.append(i)

                if len(lista_mancanti) >0 :
                    st.write(" ")
                    st.write("### > Eccezione: nella conferma d'ordine mancano i colli: ")
                    st.markdown(lista_mancanti)

                else:
                    st.write(" ")
                    st.write("### > Controllo range effettuato: tutti i colli necessari sono presenti nella conferma di ordine")
                
                st.write(""" """)
                if len(df_differenti) > 0:
                    st.write("""### >Attenzione! Stai spedendo una quantità diversa da quella dichiarata per i seguenti prodotti""")
                    
                    df_differenti
                else:
                    st.write("""### > Controllo sulle quantità effettuato: le quantità spedite corrispondono a quelle dichiarate al ricevente""")

                # Verifichiamo una estrazione di tutti i colli che contengono più di un prodotto con le scadenze e i lotti

                lista_colli_univoca = list(df_lavorato['collo'].unique())
                lista_multiprodotto = []
                for i in lista_colli_univoca:
                    df_colli_multiprodotto = df_lavorato.loc[df_lavorato.collo == i]
                    collo = list(df_colli_multiprodotto.collo)
                    prodotto = list(df_colli_multiprodotto.Titolo)
                    lotto = list(df_colli_multiprodotto.lotto)
                    df_colli_multiprodotto_lav = pd.DataFrame(collo, columns=['Collo'])
                    df_colli_multiprodotto_lav['prodotto'] = prodotto
                    df_colli_multiprodotto_lav['lotto'] = lotto

                    if len(df_colli_multiprodotto_lav)>1:
                        lista_multiprodotto.append(df_colli_multiprodotto_lav)

                if len(lista_multiprodotto) >0:
                    st.write("""### > Sono stati rilevati i seguenti colli che contengono prodotti diversi, verifica prima di spedire""")

                    for i in range(len(lista_multiprodotto)):
                        lista_multiprodotto[i]


                st.write(""" """)
                st.write(""" """)

                bottone = True #st.button("Clicca qui per confermare e generare il file")

                if bottone == True:

                    ftp = FTP('ftp.onstatic-it.setupdns.net')     # connect to host, default port
                    ftp.login(user='fabrizio.monge', passwd='Ciuciuska88')
                    ftp.cwd('Bongiovanni') 
                    file = open('dati_ordini.xlsx', 'rb')
                    ftp.storbinary('STOR dati_ordini.xlsx', file)
                    file.close()
                    ftp.quit()
                    print('Ordini caricati sul server')

                    
                    st.write("""### > Assicurati che i controlli siano corretti e scarica il file elaborato a questo link:""", color="red")
                    st.write('http://www.sphereresearch.net/Bongiovanni/dati_ordini.xlsx')

    else:
        st.write("""#### Credenziali non abilitate""")
except:
    st.write("Inserire credenziali valide")
