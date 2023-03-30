###Importation des librairies et fonctions utiles
import numpy as np
import numpy.random as rd
import matplotlib.pyplot as plt
from numpy import exp
from matplotlib.pyplot import axis , plot , show

###Programme auxiliaire
#Programmme qui renvoie la liste des coordonnées des points voisins d'un point de la grille (i,j)
def voisins(n,i,j):
    #Cas d'un point sur la première ligne
    if i ==0:
        if j==0 :
            return [(0,1),(1,0)]
        elif j==n-1:
            return [(0,n-2),(1,n-1)]
        return [(0,j-1),(0,j+1),(1,j)]
    #Cas d'un point sur la dernière ligne
    elif i==n-1:
        if j==0 :
            return [(n-2,0),(n-1,1)]
        elif j==n-1:
            return [(n-1,n-2),(n-2,n-1)]
        return [(n-1,j-1),(n-1,j+1),(n-2,j)]
    #Cas d'un point sur la première colonne (les deux coins ont déjà été traités)
    elif j==0 :
        return [(i-1,0),(i+1,0),(i,1)]
    #Cas d'un point sur la dernière colonne (les deux coins ont déjà été traités)
    elif j==n-1 :
        return [(i-1,n-1),(i+1,n-1),(i,n-1)]
    #Cas d'un point intérieur
    else :
        return [(i+1,j),(i-1,j),(i,j-1),(i,j+1)]

###Paramètres et les valeurs prises dans l'article


###Modèle de l'article
#Une seule grande fonction qui prend en entrée les paramètres, et ressort la carte du crime après 730 itérations

def Short(A_0, Gamma, l, taille, Omega, Eta, dt, Theta):

    rd.seed(10)

    ##Formation de la grille et des matrices importantes
    #Bbar : Valeur moyenne de l'attractivité dynamique à l'état stationnaire
    Bbar=(Gamma*Theta)/Omega
    #nbar : Valeur moyenne du nombre de cambrioleurs par maison à l'état stationnaire
    nbar=(Gamma*dt)/(1-exp(-(A_0+Bbar)*dt))
    #Criminel : Matrice du nombre de criminels à chaque point. Au départ, en chaque point la moyenne de criminels par maison doit être de nbar
    Criminel=np.zeros((taille,taille),dtype=np.int32)
    nombre=int(nbar*taille**2)
    if nombre >1:
        alea=rd.randint(0,taille,2*nombre)
        for p in range(nombre):
            Criminel[alea[2*p],alea[2*p+1]]+=1
    #A : Matrice des attractivités
    A=A_0*np.ones((taille,taille))
    #B : Matrice des attractivités dynamiques
    B=Bbar*np.ones((taille,taille))

    ##Simulation
    for t in range(730):
        #Blame : Matrice qui permet simplement de ne pas compter deux fois un criminel au cours d'une période dt, sachant qu'il peut avoir bougé
        Blame=np.zeros((taille,taille),dtype=np.int32)

        for i in range(taille) :
            for j in range(taille):
                #E : Compteur du nombre de crime qui a lieu au point (i,j) au cours de l'intervalle de temps dt. L'intervalle de temps vient de commencer, donc aucun crime n'a encore été commis au noeud s pendant l'intervalle
                E=0

                #Introduction d'un criminel au noeud s avec la probabilité Gamma
                r =rd.random()
                if r<=Gamma:
                    Criminel[i,j]+=1

                ##Début de la boucle criminelle
                #Criminels_actifs : Donne le nombre de criminels sur place, en enlevant les criminels déjà comptés dans ce tour
                Criminels_actifs=Criminel[i,j]-Blame[i,j]
                #Cas où il y a des criminels présents sur place
                if Criminels_actifs>0:
                    #Une action par criminel présent sur place
                    for q in range(Criminels_actifs):
                        #Cambriolage avec une probabilité p
                        p=1-exp(-A[i,j]*dt)
                        v=rd.random()

                        #Cas où la maison est effectivement cambriolée
                        if v<=p:
                            E+=1 #On augmente le compteur de crimes commis

                        #Cas où la maison n'est pas cambriolée
                        else :
                            #Liste des voisins de la maison
                            vois=voisins(taille,i,j)
                            #Liste des probabilités d'aller chez un voisin
                            L=[]
                            #Compteur qui donne l'indice du voisin choisi
                            somme=-1
                            #Liste des indices des voisins, sert à faire le choix
                            cho=[]

                            #Calcul du dénominateur
                            S=0
                            for l in vois:
                                S+=A[l[0],l[1]]

                            #Choix du voisin à visiter (le cambrioleur est obligé de partir)
                            for k in vois:
                                L.append(A[k[0],k[1]]/S)
                                somme+=1
                                cho.append(somme)
                            #Choix dans l'indice du voisin, pondéré avec les probabilités de L associées
                            choix=rd.choice(cho,1,p=L)[0]
                            #On ajoute un criminel dans la maison d'arrivée
                            Criminel[vois[choix][0],vois[choix][1]]+=1
                            #On retient que ce criminel a déjà été compté pendant cette période, et donc qu'en passant au voisin il ne faudra pas le recompter à nouveau
                            Blame[vois[choix][0],vois[choix][1]]+=1

                        #Dans les deux cas (cambriolage ou non), le criminel sera parti
                        Criminel[i,j]-=1

                ##Recalcul de B[i,j]
                D=B[i,j]*(1-Omega*dt)+Theta*E
                B[i,j]=D
                A[i,j]=A_0+B[i,j]

    ##Interface graphique
    x=[]
    y=[]
    colors=[]
    marque=[]
    for m in range(taille):
        for n in range(taille):
            x.append(m)
            y.append(n)
            colors.append(B[m,n])
            marque.append(1)

    plt.scatter(x,y,s=marque, c=colors,marker="s",vmax=2*Bbar)
    axis([0,128,0,128]) ; show()