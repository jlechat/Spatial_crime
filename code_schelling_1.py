"""
Created on Wed Mar 15 22:51:15 2023

@author: jonas, inspiré par http://adilmoujahid.com/posts/2020/05/streamlit-python-schelling/
Final version

Use package https://docs.streamlit.io/library/get-started/installation

Dans le terminal de anaconda (sur un nouvel espace) :
pip install streamlit
streamlit hello #pour vérifier la bonne installation

#execute the program with the command...
streamlit run crime3_vf.py
... and see!

This is the basic Schelling model (3 states)
"""
import random
from random import randrange, choices
import numpy as np
import streamlit as st

import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from math import sqrt


class Schelling:
    
    def __init__(self, size, ini_delinquant, nv_delinquant, ratio_haut):
        self.size = size #nb de maisons dans la ville
        self.ratio_haut = ratio_haut #ration de maison avec haute probabilité de se faire cambrioler
        self.ratio_mid = (1-ratio_haut)/2 #calcul des ratio restant
        self.ratio_bas = (1-(ratio_haut))/2
        #dans notre modèle il mesure la proportion de maison avec forte proba d'être cambriolée
        
        
        #création de la ville sous forme d'une matrice carré
        p = [self.ratio_bas, self.ratio_mid, self.ratio_haut] #définition des proba de chaque état
        city_size = int(np.sqrt(self.size))**2 #pour bien obetnir un carré
        self.city = np.random.choice([0.2, 0.5, 0.8], size=city_size, p=p) #on définit 3 seuils selon les proba précédentes
        self.city = np.reshape(self.city, (int(np.sqrt(city_size)), int(np.sqrt(city_size))))
        
        #nouvelles données
        self.ini_delinquant=ini_delinquant #nb de délinquants au début
        self.nv_delinquant=int(nv_delinquant) #taux de nouveaux délinquants à chaque nouvelle periode
        self.city_col=int(np.sqrt(self.size)) #nb de colonnes ou de lignes
        self.delinquant=[]
        for i in range(ini_delinquant) :
            a=randrange(self.city_col)
            b=randrange(self.city_col)
            self.delinquant.append([a,b])
        #la liste contient la position de tous les délinquants au départ
        
    
    def run(self):
        """
        Permet de retourner la simulation pour 1 pas :
            -On parcourt les délinquants
            -On regarde si la proba est assez élevée pour le cambriollage
                -Si oui : on augmente la proba de la maison et on retire le délinquant
                -Si non : on baisse la proba de la maison et le délinquant se déplace d'une case aléatoire (avec pondération partielle)
            -On rajoute la proportion de délinquant
        """
        for i in range(len(self.delinquant)) :
            a,b=self.delinquant[i]
            supp=[] #liste qui contiendra l'indice des délinquants à supprimer
            
            k = np.random.binomial(1, self.city[a][b]) #a l'aide d'une génération bernoulli on regarde si le camnrioleur passe à l'action (1) ou non (0).
            if k == 1 : 
                #on change les états : les maisons sont plus attractives
                if self.city[a][b]==0.2 : self.city[a][b]=0.5
                elif self.city[a][b]==0.5 : self.city[a][b]=0.8
                supp.append(i) #on ajoute l'indice du délinquant à supprimer

            else :
                #on réduit les proba si le délinquant n'attaque pas la maison
                if self.city[a][b]==0.8 : self.city[a][b]=0.5
                elif self.city[a][b]==0.5 : self.city[a][b]=0.2
                
                #on fait un déplacement semi-aléatoire pour les personnes au bord (choix de la ligne au hasard et déplacement au hasard sur la colone avec pondération par l'attarctivité)
                if a==0 or b==0 or a<int(sqrt(self.size)) or b<int(sqrt(self.size)) :
                    l=randrange(self.city_col)
                    c=random.choices(range(self.city_col), weights=([k for k in self.city[l]])) 
                    self.delinquant[i]=[l,c[0]]

                #déplacement pondéré selon l'attractivité des maisons dans les cases autour pour les autres :
                else :
                    liste=[[a-1, b-1], [a, b-1], [a+1, b-1], [a-1, b], [a+1, b], [a-1, b+1], [a, b+1], [a+1, b+1]]
                    indice=random.choices(liste, weights=([self.city[k[0]][k[1]] for k in liste]))
                    lig, col=indice[0]
                    self.delinquant[i]=[lig, col]

        #on supprime les délinquants qui ont cambriollé
        supp=supp[::-1] 
        #il faut prendre la liste à l'envers pour ne pas avoir de problème d'indexe
        for i in supp : del self.delinquant[i]
        
        #la boucle est presque finie : il faut ajouter le renouvellement des délinquants
        for i in range(self.nv_delinquant) :
            a=randrange(self.city_col)
            b=randrange(self.city_col)
            self.delinquant.append([a,b])


st.title("Spatial crime (basic schelling model)") #titre de la page web de simulation

population_size = st.sidebar.slider("Taille de la population", 500, 10000, 2500) #choix de la taille de la population par l'utilisateur

ini_delinquant=st.sidebar.slider("Délinquants au départ", 10, 1000, 250) #choix du nombre de délinquants
nv_delinquant=st.sidebar.slider("Nouveaux délinquants ajoutés à chaque fin de 'tour'", 50, 1000, 250) #choix du renouvellement délinquants
r_haut=st.sidebar.slider("Proportion de maisons avec fort risque de cambriolage", 0., 1., .5)

n_iterations = st.sidebar.number_input("Number of Iterations", 30)


schelling = Schelling(population_size, ini_delinquant, nv_delinquant, r_haut) #on créé la "ville"

#On affiche le graph initial
plt.style.use("ggplot")
plt.figure(figsize=(8, 4))

cmap = ListedColormap(['royalblue', 'orange', 'red'])
plt.subplot(121)
plt.axis('off')
plt.pcolor(schelling.city, cmap=cmap, edgecolors='w', linewidths=1)

# Ce graph pourrait servir a calculer la concentration des hotspots
plt.subplot(122)
plt.xlabel("Iterations")
plt.xlim([0, n_iterations])
plt.ylim([0.4, 1])

city_plot = st.pyplot(plt)

progress_bar = st.progress(0)

if st.sidebar.button('Run Simulation'): #lorsque run est pressé, la boucle se lance

    for i in range(n_iterations):
        schelling.run()
        plt.figure(figsize=(8, 4))
    
        plt.subplot(121)
        plt.axis('off')
        plt.pcolor(schelling.city, cmap=cmap, edgecolors='w', linewidths=1)

        plt.subplot(122)
        plt.xlabel("Iterations")
        plt.xlim([0, n_iterations])
        plt.ylim([0.4, 1])

        city_plot.pyplot(plt)
        plt.close("all")
        progress_bar.progress((i+1.)/n_iterations)
