#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 13 12:01:52 2023
COMMANDE: python3 Extraction_chaînes.py $NOM DU FICHIER .CONLL
"""
import sys
import re
import glob


fichier=sys.argv[1]

try:
    entree=open(fichier,"r")
#IOError : exception lancée lorsqu'il s'avère impossible d'ouvrir un fichier 
except IOError:
    print("Erreur lors de l'ouverture du fichier : "+fichier)
    exit()

    #Liste qui se réinitialisent à chaque nouveau texte. 
text_id=[]
pos=[]
lemme=[]
maillon=[]
chaine0=[]
chaine1=[]
chaine2=[]

#Création d'une sortie, un csv.
sortie = open('chaines_Resolco.csv', 'w')
sortie.write("CT"+"\t"+"ID TEXT"+"\t"+"NB CHAINE"+"\t"+"LONGUEUR"+"\t"+(("Maillon"+"\t")*63)+"\n")
 
#Fonction qui remplit le fichier csv 
def tocsv(chaine,nb,liste_id,x): 
    sortie.write("CT_"+str(nb)+"\t"+str(liste_id[0])+"\t"+str(x)+"\t"+str(len(chaine))+"\t") 
    for element in chaine:
        sortie.write(str(element)+"\t")
    sortie.write("\n")     


# Fonction qui remplace le postag avec son lemme si c'est un DET
def remplaceDET(tag, y, lemma):
    if tag[y]=="DET":
        tag[y]=lemma[y]

"""A FAIRE:
    créer une fonction qui permet de transformer les pos et les tranches de listes de pos (pos[i:fin+1]) en différentes étiquettes:
        P.ex if 'NOUN' in pos[i:fin+1]:
            if "le" in pos[i:fin+1]:
                syntagme="SN_def"
        """

"""Proposition de Maria"""

def type_multiword(tag, y, end): #Fonction pour traiter les maillons contenant plrs mots
    syntagme=""
    if 'NOUN' in tag[y:end+1]:
            if "le" in tag[y:end+1][0]: #Pour déterminer quel type de syntagme c'est, on commence par voir quel est le mot qu'on a au début 
                syntagme="SN_def"
            elif "un" or 'NUM' in tag[y:end+1][0]:  
                syntagme="SN_ind"
            elif "son" in tag[y:end+1][0]:
                syntagme="pos"
            elif "ce" in tag[y:end+1][0]:
                syntagme="SN_dem"
            elif "PRON" in tag[y:end+1][0]:
                syntagme="Pro"
            elif 'NOUN' in tag[y:end+1][0]:
                syntagme="SN_sansDET"
            else:
                syntagme="Autre"
    else:
        if 'VERB' in tag[y]:
            syntagme="Sujet zéro"
        else:
            syntagme="Autre"
        
    return syntagme
                
def type_motseul(tag, y): #Fonction pour traiter les maillons contenant un seul mot
    syntagme=""
    if 'NOUN' in tag[y]:
        syntagme="SN_sansDET"
    elif 'PRON' in tag[y]:
        syntagme="Pro"
    elif 'PROPN' in tag[y]:
        syntagme="NPP"  
    elif 'son' in tag[y]:
        syntagme="Pos"
    elif 'VERB' in tag[y]:
        syntagme="Sujet zéro"
    else:
        syntagme="Autre"
    
    return syntagme

#Compteur qui commence par 1 et augmente par 1 à chaque nouvelle chaîne
Nb=1 
            
for ligne in entree:
    ligne=ligne.rstrip("\n")
    if len(ligne)>0: #On saute les lignes vides entre les phrases
        x=ligne.split("\t") 
        
        #Si la ligne contient 13 colonnes
        if len(x)==13:
            text_id.append(x[0])
            pos.append(x[4])
            lemme.append(x[6])
            maillon.append(x[12])

        elif x[0]=="#end document": #Le texte est fini, on commence à stocker

            #print(text_id[0])
            for i in range(0, len(text_id)):
                if re.search(r'\|?\(0\)\|?', maillon[i]): #si la chiffre en entourée par parenthèses, alors on stocke le pos dans la liste
                    remplaceDET(pos,i, lemme)
                    chaine0.append(type_motseul(pos,i))

                elif re.search(r'\(0', maillon[i]):
                    remplaceDET(pos,i, lemme)
                    
                    fin=i+1
                    while fin<len(text_id) and not '0)' in maillon[fin]: #S'il n'ya qu'une parenthèse ouvrante, alors on stocke 
                        remplaceDET(pos,fin, lemme)
                        fin=fin+1
                    chaine0.append(type_multiword(pos, i, fin))  
#            print("chaine 0", len(chaine0), chaine0)
            if len(chaine0)>1: #On ne prend pas en compte les chaînes avec 1 seul maillon
                tocsv(chaine0, Nb,text_id, "0")
                Nb=Nb+1
            
            for i in range(0, len(text_id)):
  
                if re.search(r'\|?\(1\)\|?', maillon[i]):
                    remplaceDET(pos,i, lemme)
                    chaine1.append(type_motseul(pos,i))

                elif re.search(r'\(1', maillon[i]):
                    remplaceDET(pos,i, lemme)
                    #print(maillon[i])
                    fin=i+1
                    while fin<len(text_id) and not '1)' in maillon[fin]:
                        remplaceDET(pos,fin, lemme)    
                        fin=fin+1   
                    chaine1.append(type_multiword(pos, i, fin))
#            print("chaine 1", len(chaine1), chaine1)
            if len(chaine1)>1:#On ne prend pas en compte les chaînes avec 1 seul maillon
                tocsv(chaine1,Nb, text_id, "1")
                Nb=Nb+1

            for i in range(0, len(text_id)):
                if re.search(r'\|?\(2\)\|?', maillon[i]):
                    remplaceDET(pos,i, lemme)
                    chaine2.append(type_motseul(pos,i))
#
                elif re.search(r'\(2', maillon[i]):
                    remplaceDET(pos,i, lemme)
                    fin=i+1
                    while fin<len(text_id) and not '2)' in maillon[fin]:
                        remplaceDET(pos,fin, lemme)    
                        fin=fin+1
                    chaine2.append(type_multiword(pos, i, fin)) 
                    
#            print("chaine 2", len(chaine2), chaine2)
            if len(chaine2)>1: #On ne prend pas en compte les chaînes avec 1 seul maillon
                tocsv(chaine2,Nb, text_id, "2")
                Nb=Nb+1
           
            #On vide les listes pour traiter le texte suivant ensuite    
            text_id=[]
            pos=[]
            lemme=[]
            maillon=[]
            chaine0=[]
            chaine1=[]
            chaine2=[]

    

