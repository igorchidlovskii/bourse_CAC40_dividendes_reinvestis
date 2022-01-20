# -*- coding: utf-8 -*-
"""
Created on Mon Nov  8 12:43:28 2021

@author: ichid
"""

#librairies
import pandas as pd
import matplotlib.pyplot as plt
import os
import datetime as dt


#location
os.chdir('D:/Documents/Travail perso/Exercices/bourse/bourse_Paris')

#liste des actions. On a la plupart 
list_actions = [x[0:len(x)-4] for x in os.listdir("data/input/cours_actions_CAC40_2001_2021")]
list_actions


#fonction calcul dividende reinvesti dans le temps
def fonction_reinvest_dividende(date_cours, cours, table_dividendes):
    
    #filtre sur les dividendes precedent la date du cours
    table_dividendes_filtree = table_dividendes[table_dividendes.date_versement <= date_cours]
    
    #si aucun dividende present avant la date (vraisemblablement on est sur fin 2001 ou debut 20212)
    if (table_dividendes_filtree.shape[0] == 0):
        cours_avec_dividende = cours
        
    #autres cas : on calcule le cours avec dividende reinvesti, pour cela la formule est :
    #soit t la date ou l'on veut connaitre le cours avec dividende reinvesti
    #soit n le nombre de dividendes sur la periode [07/11/2001 ; t ]
    #cours avec div reinvesti(t) = cours(t)*((cours(t0)+dividende0)/cours(t0))*...*((cours(tn)+dividenden)/cours(tn))
    else:
        cours_avec_dividende = cours
        for i in table_dividendes_filtree.index:
            cours_jour_versement_i = table_dividendes_filtree.loc[i, ['cours']].item()
            div_i = table_dividendes_filtree.loc[i, ['dividende_brut']].item()
            cours_avec_dividende = cours_avec_dividende*(cours_jour_versement_i + div_i)/cours_jour_versement_i
    
    return cours_avec_dividende






for action in list_actions:
    
    #lecture cours action 2001-2021
    cours_action =  pd.read_csv("data/input/cours_actions_CAC40_2001_2021/" + action + ".txt", sep = "\t")
    
    #correction date
    cours_action.date = pd.to_datetime(arg = cours_action.date, dayfirst = True, yearfirst = False).dt.date

    
    #lecture dividendes historique 2001-2021
    div = pd.read_excel("data/input/dividendes/" + action + ".xlsx")
    
    #renommage colonnes
    div.columns = ['date_annonce', 'date_detachement_brut', 'date_versement_brut', 'annee_ref', 'type', 
                      'dividende_brut_brut', 'dividende_normalise_brut', 'rendement_annuel', 'commentaire']

    #suppression premiere ligne (inutile) et mauvaises valeurs
    div = div.drop(0)
    div = div[div.date_versement_brut != '-']
    div = div[div.date_versement_brut.notna()]

    #correction date versement
    div['date_versement'] = pd.to_datetime(arg = div['date_versement_brut'], dayfirst = True, yearfirst = False).dt.date

    #conversion dividende de string avec € en float
    div['dividende_brut'] = div.dividende_brut_brut.apply(lambda x: float(x[0: len(x)-2]))
    
    #filtre sur les dividendes de la periode 7/11/2001 - 8/11/2021
    div = div[div.date_versement > dt.date(2001, 11, 7)]
    div = div[div.date_versement < dt.date(2021, 11, 8)]

    #merge du cours de cloture sur l'historique de dividendes
    div = div.merge(right = cours_action[['date', 'clot']], how = 'left', left_on = 'date_versement', right_on = 'date')

    #reindex dans le sens inverse, filtre sur les colonnes importantes, renommage colonne
    div = div.reindex(index = div.index[::-1]).reset_index(drop = True)
    div = div[['date_versement', 'dividende_brut', 'clot']]
    div = div.rename(columns = {'clot': 'cours'})

    #application fonction de calcul du cours avec dividende reinvesti en fonction de la date
    cours_action['cours_dividende_reinvesti'] = cours_action.\
         apply(lambda x: fonction_reinvest_dividende(date_cours = x['date'], cours = x['clot'], table_dividendes = div), 
                                              axis = 1)


    #figure pyplot + enregistrement
    plt.figure(figsize = (20, 10))
    plt.plot(cours_action.date, cours_action.clot, label = 'cours action')
    plt.plot(cours_action.date, cours_action.cours_dividende_reinvesti, 
                    label = 'cours action avec dividende reinvesti depuis novembre 2001')
    plt.title(action)
    plt.legend()
    plt.savefig("figures/" + action + ".png")
    plt.show()
    
    #enregistrement Excel cours avec en plus le cours avec dividende reinvesti
    cours_action[['date', 'clot', 'cours_dividende_reinvesti']].to_excel("data/output/" + action + "_avec_dividende_reinvesti.xlsx")
    
    #enregistrement Excel dividende avec le cours a la date de versement en plus
    div.to_excel("data/output/" + action + "_dividende.xlsx")
    
    #pour dire si ca a bien tout fonctionne
    print(action + " ok")




