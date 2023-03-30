"""
Created on Wed Mar 15 22:51:15 2023

@author: jonas, inspiré par http://adilmoujahid.com/posts/2020/05/streamlit-python-schelling/
Final version

Use package https://docs.streamlit.io/library/get-started/installation

Dans le terminal de anaconda (sur un nouvel espace) :
pip install streamlit
streamlit hello #pour vérifier la bonne installation

#execute the program with the command...
streamlit run crime4.py
... and see!

Model with uniform proba
"""

import random
from random import randrange, choices
import numpy as np
import streamlit as st
from math import sqrt

import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap


class Schelling:
    
    def __init__(self, size, ini_delinquant, nv_delinquant):
        self.size = size #nb de maisons dans la ville
        #dans notre modèle il mesure la proportion de maison avec forte proba d'être cambriolée
        
        
        #création de la ville
        p = [0.2, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1] #définition des proba de chaque état
        city_size = int(np.sqrt(self.size))**2 #pour bien obetnir un carré
        self.city = np.random.choice([0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9], size=city_size, p=p) #on définit 3 seuils selon les proba précédentes
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
            
            k= np.random.binomial(1, self.city[a][b])
            if k == 1 : 
                if self.city[a][b]<0.9 : self.city[a][b]=self.city[a][b]+0.1
                supp.append(i)
            else :
                if self.city[a][b]>0.1 : self.city[a][b]=self.city[a][b]-0.1
                
                #on fait un déplacement semi-aléatoire pour les personnes au bord
                if a==0 or b==0 or a<int(sqrt(self.size)) or b<int(sqrt(self.size)) :
                    l=randrange(self.city_col)
                    c=random.choices(range(self.city_col), weights=([k for k in self.city[l]])) 
                    self.delinquant[i]=[l,c[0]]
                #déplacement pondéré pour les autres :
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


st.title("Spatial crime (9 states and uniform probability)")

population_size = st.sidebar.slider("Taille de la population", 500, 10000, 2500)

#on ajoute les nouveaux paramètres
ini_delinquant=st.sidebar.slider("Délinquants au départ", 10, 1000, 250)
nv_delinquant=st.sidebar.slider("Nouveaux délinquants ajoutés à chaque fin de 'tour'", 50, 1000, 250)

n_iterations = st.sidebar.number_input("Number of Iterations", 30)


schelling = Schelling(population_size, ini_delinquant, nv_delinquant)

#Plot the graphs at initial stage
plt.style.use("ggplot")
plt.figure(figsize=(8, 4))

# Left hand side graph with Schelling simulation plot
cmap = ListedColormap(['w', 'paleturquoise', 'darkturquoise', 'deepskyblue', 'blue', 'orange', 'coral', 'indianred', 'orangered', 'r'])
plt.subplot(121)
plt.axis('off')
plt.pcolor(schelling.city, cmap=cmap, edgecolors='w', linewidths=1)

#Right hand side graph with Mean Similarity Ratio graph
plt.subplot(122)
plt.xlim([0, n_iterations])
plt.ylim([0.4, 1])

city_plot = st.pyplot(plt)

progress_bar = st.progress(0)

if st.sidebar.button('Run Simulation'):

    for i in range(n_iterations):
        schelling.run()
        plt.figure(figsize=(8, 4))
    
        plt.subplot(121)
        plt.axis('off')
        plt.pcolor(schelling.city, cmap=cmap, edgecolors='w', linewidths=1)

        plt.subplot(122)
        plt.xlim([0, n_iterations])
        plt.ylim([0.4, 1])

        city_plot.pyplot(plt)
        plt.close("all")
        progress_bar.progress((i+1.)/n_iterations)
