#!/usr/bin/python
# -*- coding: utf-8 -*-
# Compactage4 : suppression du fichier xyz
# sur la construction de la fenêtre principale : http://python.jpvweb.com/python/mesrecettespython/doku.php?id=barre_de_menu

# protocole final : 
# ply de référence : Projet1-CER-03-11-2017-metric - CloudSegment.ply
# x de -3.5 à 15 = 18.5 m : -3.5< x < 2m : semi compactée ; 2m < x < 8.5 m : compacté ; 8.5m < x < 15m : foisonnée 
# y de 1 à 5.5 = 4.5 m
# 10 590 000 points pour 83 m2 soit 130 000 points au m2 (13 au cm2)

import tkinter
import tkinter.filedialog
import tkinter.simpledialog
import tkinter.messagebox
import tkinter.ttk as ttk                   # amélioration de certains widgets de tkinter : le comportement est géré indépendamment de l'apparence : c'est mieux ! mais différent !
import tkinter.font as font
import time
import statistics
import os
import csv
import struct
from scipy.interpolate import griddata      # Pour l'interpolation
from scipy.stats import ks_2samp            # voir : https://stackoverflow.com/questions/10884668/two-sample-kolmogorov-smirnov-test-in-python-scipy
from scipy.stats import kstest
from scipy.stats import stats
import numpy 
import inspect 
from numpy import transpose
from numpy import loadtxt
from numpy import mgrid
from numpy import savetxt

import matplotlib.pyplot as plt
import pickle                               # pour la persistence
import random
from collections import Counter

# pour obtenir la ligne du scipt : (inspect.stack(context=1)[0][2])
# liste des figure matplotlib : [plt.figure(i) for i in plt.get_fignums()]
############################### CLASSE INTERFACE GRAPHIQUE ##############################################        

class interface(tkinter.Frame):
 
    def __init__(self, master=None):
        tkinter.Frame.__init__(self, master, background="grey")
        self.initialize()

    def initialize(self):
    
       # Initialisation de la fenêtre maitresse du menu principal  (fenetre ou self.master)

        self.master.title(nomApplication+version)               # titre
        self.master.geometry(geometrieFenetre)                  # taille
        icone = tkinter.PhotoImage(data=iconeTexte)             # icone des fenetres, ne pas déplacer       
        fenetre.tk.call('wm', 'iconphoto', fenetre._w, icone)   # Icone
        
        mainMenu = tkinter.Menu()                               # Barre de menu
        menuFichier = tkinter.Menu(mainMenu,tearoff = 0)        # menu Fichier, tearOff = 1, détachable
        menuEdition = tkinter.Menu(mainMenu,tearoff = 0)        # menu Edition
        menuReference = tkinter.Menu(mainMenu,tearoff = 0)      # menu pour ajouter des références        
        menuTraitement = tkinter.Menu(mainMenu,tearoff = 0)     # menu Traitement
        menuSynthese = tkinter.Menu(mainMenu,tearoff = 0)       # menu Synthese
        menuParam = tkinter.Menu(mainMenu,tearoff = 0)          # menu paramètres de traitement
        menuAide = tkinter.Menu(mainMenu,tearoff = 0)           # menu aide

        # Ajout des items du menu principal :

        mainMenu.add_cascade(label="Fichier",menu=menuFichier)
        menuFichier.add_command(label=("Quitter"), command=self.quitter)

        # Menu Edition
        mainMenu.add_cascade(label="Edition",menu=menuEdition)
        menuEdition.add_command(label=("Ménage écran"), command=self.menage)
        menuEdition.add_command(label=("Ouvrir la trace"), command=self.ouvreTrace)
        menuEdition.add_separator()        
        menuEdition.add_command(label=("Effacer la trace"), command=self.supprimeTrace)
        
        # Menu références
        mainMenu.add_cascade(label="Références",menu=menuReference)
        menuReference.add_command(label=("Ajouter une référence"), command=saisieReference)         
        menuReference.add_command(label=("Définir une métrique pour un protocole"), command=saisieMetrique)
        menuReference.add_separator()
        menuReference.add_command(label="Affiche la liste des références enregistrées", command=afficheReferences)
        menuReference.add_separator()
        menuReference.add_command(label=("Effacer des références"), command=supprimeReferences)
        
        # Menu traitement
        mainMenu.add_cascade(label="Traitement",menu=menuTraitement)
        menuTraitement.add_command(label=("Statistiques sur un fichier PLY"), command=statPly)
        menuTraitement.add_separator()
        menuTraitement.add_command(label=("Tester un fichier PLY par rapport aux références"), command=testPly)          
        menuTraitement.add_separator()
        menuTraitement.add_command(label=("fichier PLY vers MNT"), command=PLY2MNT)           
        menuTraitement.add_command(label=("Visualiser un profil"), command=controleMNT)    
        menuTraitement.add_command(label=("Tortuosité d'un MNT"), command=indices)          
        menuTraitement.add_separator()
        menuTraitement.add_command(label=("Effacer des résultats de calcul"), command=supprimeCalculs)
        
        # menu synthése
        mainMenu.add_cascade(label="Synthèse",menu=menuSynthese)       
        menuSynthese.add_command(label=("Affiche les résultats de calculs sur les fichiers PLY"), command=afficheStatPly)
        
        # Menu paramètres
        mainMenu.add_cascade(label="Paramètres",menu=menuParam)
        menuParam.add_command(label=("Affiche les paramètres"), command=afficheParam)        
        menuParam.add_separator()
        menuParam.add_command(label=("Modifier la taille de la maille des MNT"), command=modifMaille)
        menuParam.add_separator()        
        menuParam.add_command(label=("Choisir les colonnes affichées dans le tableau résultats"), command=choisirColonnesResultats)
        menuParam.add_command(label=("Revenir aux colonnes par défaut"), command=choisirColonnesParDefaut)
        
        # Menu aide
        mainMenu.add_cascade(label="Aide",menu=menuAide)
        menuAide.add_command(label=("Aide sur les menus"), command=aide)        
        menuAide.add_command(label=("Documentation sur la tortuosité"), command=aideTortu)
        menuAide.add_command(label=("Aide sur le kurtosis et l'asymétrie"), command=aideMoments)
        menuAide.add_command(label=("A Propos"), command=aPropos)
        
        # Affichage du menu dans la fenêtre maitresse

        self.master.config(menu = mainMenu)

        # le cadre et le label d'encadre pour afficher de courts messages :

        self.resul100=ttk.Frame(self.master,height=50,relief='sunken')
        self.texte101=ttk.Label(self.resul100, text="",justify='center',style="C.TButton")        
        self.texte101.pack(ipadx=5,ipady=5)

        # Le bouton pour afficher les graphiques et son explication
        
        self.aideGraphiquesTest = ("les graphiques représentent les fonctions de répartition des valeurs de Z,\n"+
                                        "et des 200 valeurs de tortuosités calculées sur les références C,SC et F\n "+
                                        "Ces courbes sont superposées aux mêmes valeurs provenant du fichier testé.")
        self.aideGraphiquesStat = ("Les graphiques représentent les histogrammes des Z,\n"+
                                        "et des 200 valeurs de tortuosités transversales et longitudinales")
                                        
        self.aideGraphiques = ttk.Label(self.resul100, justify='center',style="C.TButton")
        self.boutonGraphiques = ttk.Button(self.resul100,
                                  text='Afficher les graphiques',
                                  command= afficheGraphiques)        
        self.boutonGraphiquesHisto = ttk.Button(self.resul100,
                                  text='Afficher les histogrammes',
                                  command= afficheGraphiquesHisto)     

        # Le boutton pour trier les tableaux de résultat
      
        self.boutonTriTableau = ttk.Button(self.resul100,
                                  text='Trier le tableau',
                                  command= choixTri)        

        # Le boutton pour changer les colonnes affichées
      
        self.boutonChangerColonnes = ttk.Button(self.resul100,
                                  text="Choisir d'autres colonnes",
                                  command= changerColonnes)
        
        # Le boutton pour'aide sur le tableau de synthèse
      
        self.boutonAideSynthese = ttk.Button(self.resul100,
                                  text="Aide",
                                  command= aideSynthese)
        
        # la fenetre pour afficher les textes (traces et aides)

        self.resul200 = ttk.Frame(fenetre,height=100,relief='sunken')  # fenêtre texte pour afficher le bilan
        self.scrollbar = ttk.Scrollbar(self.resul200)
        self.scrollbar.pack(side='right',fill='y',expand=1)              
        self.scrollbar.config(command=self.yviewTexte)
        self.texte201 = tkinter.Text(self.resul200,width=200,height=100,yscrollcommand = self.scrollbar.set,wrap='word')
        self.texte201.pack()
        
        # restauration des paramètres ( : nb points dans la maille, protocoleParDefaut, colonnes  du tableau résultats) :

        restaureParam()

        # Message dans la trace

        self.ecrireTrace(   "\n------------ "+heure() +" lancement de Compactage "+version+
                            "\nParamètre : Nombre de mailles par points du nuage : "+str(nbMaillesParPointDuNuage)+"\n")

        # fin par touche windows
        
        self.master.protocol("WM_DELETE_WINDOW", self.quitter)

    def encadrePlus(self,*listeTexte,aligne='center',fonte="TkDefaultFont"):
        liste=[str(e) for e in listeTexte]
        texte = "\n".join(liste)
        self.ecrireTrace(texte)
        try:
            self.texte101Plus+="\n".join(liste)
        except:
            self.texte101Plus="\n".join(liste)
        self.encadre(self.texte101Plus,trace=None,aligne=aligne,fonte=fonte)       
 
    def encadre(self,*listeTexte,trace=1,aligne='center',fonte="TkDefaultFont"):
        self.menage()
        nbLignesmax = 70
        liste=[str(e) for e in listeTexte]
        texte = "\n".join(liste)
        self.texte101Plus = texte        
        if texte.count('\n')>nbLignesmax:                           # limitation à nbLignesmax du nombre de lignes affichées 
            texte='\n'.join(texte.splitlines()[0:nbLignesmax-10]) +'\n.......\n'+'\n'.join(texte.splitlines()[-8:])        
        if texte.__len__()>3000:
            texte=texte[:800]+"\n\n......\n\n"+texte[-800:]
        self.texte101.configure(text=texte,justify=aligne)
        self.texte101.configure(font=fonte)
        self.resul100.pack()              
        if trace==1:
            with open(fichierTrace, 'a',encoding='utf-8') as f:
                f.write("\n------------\n"+heure()+"\n")
                [f.write(e+"\n") for e in texte.split("\n")]
        fenetre.update()
        
    def ecrireTrace(self,texte):
        with open(fichierTrace, 'a',encoding='utf-8') as f:
            f.write(texte)          
        
    def menage(self,ligne=-1):
        if self.resul100.winfo_manager()=="pack":
           self.resul100.pack_forget()
        if self.resul200.winfo_manager()=="pack":
           self.resul200.pack_forget()
        if self.boutonGraphiques.winfo_manager()=="pack":
           self.boutonGraphiques.pack_forget()
        if self.boutonGraphiquesHisto.winfo_manager()=="pack":
           self.boutonGraphiquesHisto.pack_forget()
        if self.aideGraphiques.winfo_manager()=="pack":
           self.aideGraphiques.pack_forget()
        if self.aideGraphiques.winfo_manager()=="pack":
           self.aideGraphiques.pack_forget()
        if self.boutonTriTableau.winfo_manager()=="pack":
           self.boutonTriTableau.pack_forget()
        if self.boutonChangerColonnes.winfo_manager()=="pack":
           self.boutonChangerColonnes.pack_forget()
        if self.boutonAideSynthese.winfo_manager()=="pack":
           self.boutonAideSynthese.pack_forget()           
    def ouvreTrace(self):
        self.menage()
        if os.path.exists(fichierTrace):
            self.cadreVide()            
            with open(fichierTrace,"r",encoding='utf-8') as trace:
                try: contenu=trace.read()
                except:
                    trace.close
                    trace=open(fichierTrace,"r",encoding="latin-1")
                    contenu=trace.read()

            self.texte201.insert('end',str(contenu))                  
            self.texte201.update()
            self.texte201.see('end')             
            self.texte201.see("1.1")            
        else:
            texte = "Pas de trace de la trace !"
            self.encadre(texte,trace=0)

    def supprimeTrace(self):
        self.menage()        
        if os.path.exists(fichierTrace):
            if tkinter.messagebox.askyesno("Suppression de la trace", "Confirmer la suppression de la trace ?"):
                try:
                    supprimeFichier(fichierTraceSauve)
                    os.rename(fichierTrace,fichierTraceSauve)
                    self.encadre("Fichier trace effacé, renommé en "+fichierTraceSauve,trace=0)
                except Exception as e:
                    self.encadre("Problème lors de l'effacement du fichier trace : "+str(e),trace=0)
        else:
                self.encadre("Pas de fichier trace !",trace=0)

        
    ############################### Prépare un cadre pour Afficher une trace dans la fenêtre
        
    def cadreVide(self):
        self.menage()
        fenetre.update()                                  # rafraichissement avant agrandissement
        self.texte201.delete("0.0","end")
        self.resul200.pack()
        
    def yviewTexte(self, *args):
        if args[0] == 'scroll':
            self.texte201.yview_scroll(args[1],args[2])
        elif args[0] == 'moveto':
            self.texte201.yview_moveto(args[1])

    ############################## Quitter l'appli
            
    def quitter(self):
        print("Fin de "+nomApplication+" "+heure())                             # Message dans la consome
        self.ecrireTrace(   "\n------------ "+heure() +" Fin de Compactage ")   # Message dans la trace
        self.master.quit()

############################### FIN DE  LA CLASSE ##############################################        


############################### MENUS
    

########################################### Tester un fichier PLY pour un protocole 

def testPly():

    ################################ Saisie du contexte
    app.menage()
    l=listeProtocoles()
    if not l:
        app.encadre("Aucune référence :\n ajouter des références par le menu 'références/ajout d'une référence")
        return
    # saisie du contexte de la comparaison : 
    titre = ("Protocole utilisé pour effectuer les photos.",
            "Le protocole est relatif aux conditions de prise de vue et de création du ply\n"+
            "L'unité de mesure des x,y et z est unique pour les fichiers issus d'un même protocole\n") 

    protocole = choisirItem(listeItems=l, titre="Choisir un protocole",mode="single").choix  # single ou extended

    if not protocole: return
    if protocole not in l:
        app.encadre("Protocole absent ou inconnu !")
        return
    
    fichierPly = quelFichier(titre="fichier PLY à tester : ",extension=("PLY","*.ply"))
    if not os.path.exists(fichierPly):
        app.encadre("Pas de fichier PLY : Abandon")        
        return

    ################################ tout OK : traitement
    
    # Définir les subplots pour tracer les fonctions de répartition, fait par testKolmogorovSmirnov
    fig = plt.figure()
    ax1 = plt.subplot2grid((3, 2), (0, 0))
    ax2 = plt.subplot2grid((3, 2), (0, 1))
    ax3 = plt.subplot2grid((3, 2), (1, 0), colspan=2)
    ax4 = plt.subplot2grid((3, 2), (2, 0), colspan=2)
    
    fig.suptitle('Fonction de répartition : test en rouge\n compacté en bleu -- Semi-Compacté en vert -- Foisonné en jaune'+
                 '\nProtocole : '+protocole+" ; Fichier :"+fichierPly,fontsize=10)
    
    # calcul des premiers indicateurs et de la listeDesZ sur le fichier choisi :
    
    app.encadre("\nAttention : procédure longue, création d'un maillage à partir du fichier :\n"+fichierPly)
    XYZ = ecrireMNT(fichierPly)
    
    # si erreur dans le fichier ply alors le messages est dans la clé min_x :
    if type(XYZ["min_x"])==str():
        app.encadre("Erreur lors de la lecture du fichier ply :\n\n"+XYZ["min_x"])
        return
    
    # test de la tortuosité de la surface, tient compte des positions relatives des Z, transversales, puis longitudinales
        
    tortu = tortuosity_surfacique(XYZ["fichierMNT"])
    
    # fusion des 3 dictionnaires  en un seul : stat
    
  
    stat = statsBasiques(XYZ["listeDesZ"])
    stat.update(XYZ)     
    stat.update(tortu)              # concaténation des 2 dictionnaires  
    ajoutStatPly(fichierPly,stat)
    
    # tout va bien, test des altitudes sans tenir compte des positions relatives (relief)
    app.menage()
    app.encadre("Test sur les 3 niveaux de compactage du protocole : '"+protocole+"'\n fichier : "+fichierPly+"\n")        
    listeDesZ = XYZ["listeDesZ"]    

    # test de proximité références/sone testée pour les étendues et écarts type des z et des tortuosités H et V
    print("protocole : ",protocole," fichier :",fichierPly)
    retourProxi = testProxi(protocole,stat)
    if retourProxi:
        app.encadrePlus(retourProxi)
        
    # tests d'adéquation des histogrammes du fichier testé aux histogrammes des références : test très sévère !

    retourTestKSZ = testKolmogorovSmirnov(protocole,listeDesZ,cleReference="listeDesZ",titre="sur les altitudes non centrées",axe=ax1)
    
    retourTestKSZ = testKolmogorovSmirnov(protocole,listeDesZ,cleReference="listeDesZ",titre="sur les altitudes centrées",axe=ax2,centrer=True)
    app.encadrePlus(retourTestKSZ)
    
    refH = "tortuosites transversales"
    listeDesTortuositesH = tortu[refH]   
    retourTestKSH = testKolmogorovSmirnov(protocole,listeDesTortuositesH,cleReference=refH,titre="sur les tortuosités transversales",axe=ax3)
    app.encadrePlus(retourTestKSH)

    refV = "tortuosites transversales"
    listeDesTortuositesV = tortu[refV]
    retourTestKSV = testKolmogorovSmirnov(protocole,listeDesTortuositesV,cleReference=refV,titre="sur les tortuosités longitudinales",axe=ax4)

    app.encadrePlus(retourTestKSV)

    ################################ Affichage des graphiques
    
    app.aideGraphiques.config(text=app.aideGraphiquesTest)    
    app.aideGraphiques.pack(ipadx=5,ipady=5,padx=10,pady=10)
    app.boutonGraphiques.pack(ipadx=5,ipady=5,padx=10,pady=10)    
    
def afficheGraphiques(): # affiche la figure courante (les fonctions de répartition créées par testPly ou par statPly)
    # paramètres d'affichage (à vérifier)

    plt.gcf().subplots_adjust(left = 0.1, bottom = 0.1,
                       right = 0.3, top = 0.2, wspace = 0, hspace = 0) # la largeur est définie par right - left    
 
    # affichage en pleine page :
    mng = plt.get_current_fig_manager()
#    mng.window.state('zoomed') # works fine on Windows!
    plt.tight_layout(rect = [0, 0, 1, 0.9])
    plt.show()

def afficheGraphiquesHisto(): # affiche la figure courante (les fonctions de répartition créées par testPly ou par statPly)
    # paramètres d'affichage (à vérifier)
    plt.tight_layout()
    plt.gcf().subplots_adjust(left = 0.1, bottom = 0.1,
                       right = 0.3, top = 0.2, wspace = 0, hspace = 0) # la largeur est définie par right - left    
    plt.tight_layout(rect = [0, 0, 1, 0.9])

    # affichage en pleine page :
    mng = plt.get_current_fig_manager()
    mng.window.state('zoomed') # works fine on Windows!    
    plt.show()

########################################### affiche un profil ##################################

def controleMNT():
    fichierMNT = quelFichier(titre = "MNT à lire",extension=("TXT","*MNT.txt"))
    lePas,nbPointsParMaille = demandeLePas(fichierMNT)
    mailles = lire_fichier_mnt(fichierMNT)  
    n = random.randrange(mailles.__len__())
    unProfil=list(mailles[n])
    moyenne = numpy.mean(unProfil)
    unProfil=[e for e in unProfil if e!=remplissage]
    moyenne = numpy.mean(unProfil)    
    unProfil=[e-moyenne for e in unProfil]
    tortuosite = tortuosity_profil(unProfil,lePas)
    x = [(x*lePas) for x in range(len(unProfil))]       # reconstitue les couples x,y des seuls points valides
    plt.plot(x,unProfil)
    rapport = 'MNT : '+os.path.basename(fichierMNT)+"\n"+'Profil numéro '+str(n)+" tortuosité : "+str(tortuosite)+"\n--------\n"
    app.encadrePlus(rapport)
    plt.xlabel(rapport)    
    plt.show()
    plt.close()

###########################################
    
def ecreterListe(liste): # liste est un array, renvoie un array ecreter à 3 écart type
    if liste.__len__()==0:
        return liste
    moyenne = liste.mean(axis=0)
    ecartType = liste.std(axis=0)
    mini = moyenne - 3*ecartType
    maxi = moyenne + 3*ecartType
    new = [e for e in liste if mini < e < maxi]
    return new

def centrerSurMediane(liste): # garde les nombre, trie, supprime pourCent de marge, centre et renvoie un numpy.apparay
    if liste.__len__()==0:
        return liste    
    l = [e for e in liste if is_number(e)]  # sélection des valeurs numériques :
    if l.__len__()==0: return list()          # pas de valeurs numériue : retour
    l.sort()                                # tri pour trouver la médiane
    moitie = int(l.__len__()/2)        # milieu de la liste
    mediane = l[moitie]                # on retire la médiane pour centrer la liste : (on pourrait utiliser la moyenne)
    l -= mediane   
    return l

########################################### Statistiques sur un PLY

def statPly():
    app.menage() 
    # choix du fichier .ply a traiter
    
    fichierPly = quelFichier(titre="fichier PLY pour la référence",extension=("PLY","*.ply"))
    if not os.path.exists(fichierPly):
        app.encadre("protocole:",protocole,"\nCompactage:",compactage,"\nPas de fichier PLY : Abandon")        
        return

    # toutes les infos sont là pour effecteur les calculs
    
    app.encadre("Calcul des statistiques sur le fichier : ",fichierPly," Patience...")
    
    # Extraction des x y et z, écriture du fichier xyz, listeDesZ
        
    XYZ = ecrireMNT(fichierPly)         # des infos sur la liste des XYZ, dans un dictionnaire
    if type(XYZ["min_x"])==str():       # si erreur dans le fichier ply alors le messages est dans la clé min_x :
        app.encadre("Erreur lors de la lecture du fichier ply :\n\n"+XYZ["min_x"])
        return
    
    # calcul et affichagez des statistiques "basiques"
    
    stat = statsBasiques(XYZ["listeDesZ"])

    # calcul des tortuosités transversales et longitudinales sur 200 lignes aléatoires :
    # clés créé par tortu : "tortuosites transversales" et "tortuosites longitudinales"
    tortu = tortuosity_surfacique(XYZ["fichierMNT"])

    # fusion des 3 dictionnaires  en un seul : stat, enregistrement
    
    stat.update(XYZ)   
    stat.update(tortu)     
    ajoutStatPly(fichierPly,stat)
    
    app.encadre("Statistiques sur les valeurs de Z du fichier ",fichierPly,"\n\n")
    [app.encadrePlus(e+" : "+str(stat[e])+"\n")  for e in stat if e in ["nombre","moyenne","médiane","ecartType","variance","etendue","asymetrie","kurtosis" ] ]  
    app.encadrePlus("---------\nCalcul des tortuosités sur un MNT déduit du semis de points du PLY \n"+
                    "Le MNT comporte "+str(nbMaillesParPointDuNuage)+" maille(s) par point du nuage\n\n")
    [app.encadrePlus(e+" : "+str(stat[e])+"\n")  for e in stat if e in ["tortuosite moyenne transversale","tortuosite moyenne longitudinale" ] ]  
    app.encadrePlus("Voir plus de détails dans le fichier trace")

    # histogrammes :
    fig = plt.figure()
    ax1 = fig.add_subplot(3, 1, 1)
    ax2 = fig.add_subplot(3, 1, 2)
    ax3 = fig.add_subplot(3, 1, 3, sharex = ax2, sharey = ax2)
#
##    fig, (ax1, ax2,ax3) = plt.subplots(3,1,)
    fig.suptitle("fichier "+fichierPly+"\nHistogramme des "+str(stat['nombre'])+" Z et des 200 valeurs de tortuosités transversales et longitudinales",fontsize=10)
    unHistogramme(XYZ["listeDesZ"], ax1, "les Z", 'red')    
    unHistogramme(tortu["tortuosites transversales"], ax2, "Tortuosité transversale", 'red')
    unHistogramme(tortu["tortuosites longitudinales"], ax3, "Tortuosité longitudinale", 'red')
    app.aideGraphiques.config(text=app.aideGraphiquesStat)
    app.aideGraphiques.pack(ipadx=5,ipady=5,padx=10,pady=10)
    app.boutonGraphiquesHisto.pack(ipadx=5,ipady=5,padx=10,pady=10)

########################################### Lire un fichier PLY, écrire un MNT :

def PLY2MNT():
    app.menage()    
    fichierPly = quelFichier(titre="fichier PLY pour MNT",extension=("PLY","*.ply"))
    if not os.path.exists(fichierPly): return
    app.encadre("\nAttention : procédure longue, création d'un maillage à partir du fichier :\n"+fichierPly,trace=0)

    XYZ = ecrireMNT(fichierPly)         # des infos sur la liste des XYZ, dans un dictionnaire
    if type(XYZ["min_x"])==str():       # si erreur dans le fichier ply alors le messages est dans la clé min_x :
        app.encadre("Erreur lors de la lecture du fichier ply :\n\n"+XYZ["min_x"])
        return
    

############################### FONCTIONS STANDARDS ##############################
           
def aPropos():
    app.menage()
    app.encadre(nomApplication+version,
                "\nCalcul de maillages de type MNT (Modèle Numérique de Terrain)\n à partir de fichiers nuages de points 3D de type PLY.",                
                "\nCalculs d'indices surfaciques sur les maillages calculés",
                "\nDans cette version : calcul de la tortuosité",                
                "\nRéalisation Denis Jouin 2019",
                "Laboratoire Régional de Rouen - CEREMA Normandie Centre",trace=None)

def aideTortu():
    app.menage()    
    app.encadre(nomApplication+version,
                "\nCalculs d'indices de tortuosité de surface.",
                "\nLa tortuosité est un bon indicateur de la rugosité de la surface",
                "A partir d'un nuage de points 3D (au format PLY) le traitement constitue un maillage carré régulier,",
                "chaque maille portant une valeur de Z interpolée à partir des points du nuage proches de la maille.",
                "\nCe maillage est appelé modèle numérique de terrain (MNT). La caractéristique essentiel du MNT est le 'PAS' de la maille.",
                "Le PAS est la longueur du coté du carré formant la maille. Un bon maillage comporte plus de mailles",
                "qu'il n'y a de points dans le nuage, sinon il y a perte d'information.",
                "La densité du nuage doit être en rapport avec l'échelle de la tortuosité mesurée.",
                "\nLa définition de la tortuosité sur un profil, transversal ou longitudinal, du maillage est :",
                "         Ls/Ld ",
                "où : Ls est la longueur 'sinueuse' en passant par tous les points du profil",
                "et : Ld est la longueur en ligne droite du point début au point fin du profil",
                "\n Ce programme calcule la tortuosité sur des échantillons de 200 profils horizontaux et 200 profils verticaux.",
                " Les moyennes et médianes de ces séries sont calculées et affichées.",
                "\n Pour fixer les idées une surface plane à une tortuosité de 1 et un escalier : 1 en transversal et 1.36 en longitudinal.",
                "\n La tortuosité décèle ainsi l'anisotropie des surfaces.",                  
                "\n Attention :",
                "    - la tortuosité n'est pas un indice absolu : elle varie suivant le PAS choisi. Elle augmente avec le pas.",
                "    - une moyenne différente de la médiane évoque une surface 'non plane' ou une taille de pixel, ou un pas, trop petit.",
                "\n Les calculs sont indépendants de toute 'métrique' sur le fichier ply en entrée.",                  
                "\n Remarque : dans sa version actuelle ce programme nécessite en entrée un nuage de point au format PLY.",
                " Des outils comme CloudCompare ou Meshlab permettent de convertir tout nuage de points 3D vers le format PLY.",                
                "\nCopyright : 2019 - Laboratoire Régional de Rouen - CEREMA Normandie Centre",
                trace=None,
                aligne='left')

def aideMoments():
    app.menage()    
    app.encadre(nomApplication+version,
                "Aide sur le kurtosis et l'asymétrie.",                
                "\n Le kurtosis est aussi appelé coefficient d'applatissement ou coefficient d'acuité.",
                "\n  Il mesure l'applatissement de la distribution d'une variable aléatoire.",
                "    Sa valeur est supérieure à -2.",
                "    La loi normale à un kurtosis de valeur zéro ",
                "    Une loi uniforme continue, donc applatie, à un kurtosis de -1.2 ",
                "    Une loi plus 'pointue' que la loi normale à un kurtosis positif.",
                "\n Le coefficient d'asymétrie mesure la répartition d'une variable aléatoire.",
                "    Un coefficient d'asymétrie nul indique une distribution symétrique, comme la loi normale.",
                "    Un coefficient négatif indique une queue de distribution étalée vers la gauche.",
                "    Un coefficient positif indique une queue de distribution étalée vers la droite.",
                "\n Remarque métier : ",
                "    Un ballast foisonnée, non modifié, présente des valeurs de Z proches d'une loi normale.",
                "    La distribution des Z est fortement modifiée par le compactage .",
                "\n Remarque statistique : ",
                "    La variance est le moment centré d'ordre 2.",
                "    Le coefficient d'asymétrie est le moment centré d'ordre 3.",
                "    Le kurtosis est le moment centré d'ordre 4.",
                "\nCopyright : 2019 - Laboratoire Régional de Rouen - CEREMA Normandie Centre",
                trace=None,
                aligne='left')

def aideSynthese():
    app.menage()    
    app.encadre(nomApplication+version,
                "Documentation sur le tableau de synthése des résultats.",                
                "\n Ce tableau présente les statistiques sur les valeurs de Z du fichier .ply étudié et sur le fichier MNT déduit.",
                "\n  Il faut noter que ces statistiques portent sur un tableau écrété : ",
                "   Les valeurs extrèmes, susceptibles d'être aberrantes par construction, sont éliminées.",
                "   Les valeurs éliminées sont les 0.5% les plus petites et les 0.5% les plus grandes",
                "\n  Un bouton permet de trier le tableau suivant une colonne.",
                "   Un bouton permet de choisir les colonnes à afficher parmi la liste des statistiques disponibles",
                "\nCopyright : 2019 - Laboratoire Régional de Rouen - CEREMA Normandie Centre",
                trace=None,
                aligne='left')    
def aide():    
    app.menage()    
    app.encadre(nomApplication+version,
                "Documentation sur les items de menus.",                
                "\n2 items dans le menu traitement :",
                "\n  - 'fichier PLY vers MNT' : Cet item transforme un fichier de type .PLY en MNT.",
                "    L'interpolation est de type 'linear'. Le PAS est fonction du nombre de mailles souhaité par point du nuage.",
                "    2 fichiers sont générés :",
                "      1) un MNT, présentant les valeurs de Z suivant une grille de pas régulier.",
                "      2) un PAS, présentant les métadonnées du MNT : valeur du PAS de la grille,",
                "         et nombre de points du nuage par maille de la grille, en moyenne.",
                "\n  - 'Tortuosité d'un MNT' : Cet item calcule la tortuosité du MNT produit par l'item précédent.",
                "     Le programme calcule la tortuosité sur un échantillon de 200 profils horizontaux et verticaux.",
                "     Les moyennes et médianes de ces 2 fois 200 valeurs sont ensuite affichées.",
                "     Ces valeurs peuvent faire apparaître une anisotropie de la surface.",
                "     Les 2 échantillons étant choisis aléatoirement une nouvelle exécution donnera des valeurs légèrement différentes.",                
                "\n     Pour fixer les idées une surface plane à une tortuosité de 1 et un escalier : 1 en transversal et 1.36 en longitudinal..",
                "\n   Voir la doc sur la tortuosité pour documenter le calcul effectué.",                    
                "\n1 item dans le menu paramètres :",
                "\n  - 'modifier la taille de la maille' : modifie le calcul du PAS du maillage.",
                "     Le PAS est calculé pour obtenir un nombre de mailles pour chaque 'point du nuage'.",
                "     La valeur modifiée devient la valeur par défaut (initiallement : 5). ",
                "\n   Voir la doc sur la tortuosité pour documenter le rôle du PAS.",                 
                "\n1 item dans le menu Edition :",
                "\n     - 'ouvrir la trace' : visualise l'ensemble des message générés par les traitements",
                "       Cela permet de retrouver les résultats et les paramètres utilisés. Le copier/coller est possible.",

                "\nCopyright : 2019 - Laboratoire Régional de Rouen - CEREMA Normandie Centre",
                trace=None,
                aligne='left')
########################################### INDICES : en fait un seul, la tortuosité

def indices():
    app.menage()
    tortuosity_surfacique()
    return

########################################### Tortuosité #########################################################################

########################################### tortuosité de profil : longueur réelle du profil / la longeur entre les extrémités

def tortuosity_surfacique(fichierMNT=None):
    if fichierMNT==None: fichierMNT = quelFichier(titre = "MNT à lire",extension=("TXT","*MNT.txt"))
    if not os.path.exists(fichierMNT): return
    lePas,nbPointsParMaille = demandeLePas(fichierMNT)
    if lePas==0 :
        app.encadre("\nFichier incorrect :\n",fichierMNT)
        app.encadrePlus("\n\nLe fichier doit être obtenu par l'item 'fichier PLY vers MNT'")
        return
    app.encadre("\nAttention : procédure longue, calcul de la tortuosité du fichier :\n"+fichierMNT,trace=0)
    # données OK : calcul :
    maillage = lire_fichier_mnt(fichierMNT)
    if type(maillage)==type(None):
        app.encadre("Le fichier :\n"+fichierMNT+"\nne correspond pas à un maillage de type MNT.",trace=0)
        return
    app.encadre("Tortuosité sur le fichier MNT : "+fichierMNT)
    app.encadrePlus("\n\nNombre de points par maille (en moyenne) = "+str(nbPointsParMaille))
    app.encadrePlus("\nValeur du pas de la maille = "+str(lePas))
    app.encadrePlus("\nDimension du maillage = "+str(maillage.shape))        
    app.encadrePlus("\n--------------------------------\nTortuosité sur les transversales : ")    
    tortutransversale,moyenneH,medianeH,tmaxH,tminH = tortuosite_maillage(maillage,lePas)  # liste de 200 valeurs de tortuosité

    app.encadrePlus("\n--------------------------------\nTortuosité sur les longitudinales : ")     
    transmaille = transpose(maillage)
    tortulongitudinale,moyenneV,medianeV,tmaxV,tminV = tortuosite_maillage(transmaille,lePas)

    # clés de stat (sur les Z épurés ) : "marges supprimées","nombre","borneMini","borneMaxi","nombreRetenu",
    # "moyenne","ecartType","maxi","mini","etendue","Nombre de classes","histo","classeModale","mode"
    
    # clés de stat provenant de XYZ : "min_x","max_x","min_x","max_x","lePas",nombreDePointsDansLePly,
    # nombreDeMaillesSansValeur,fichierPly,fichierMNT,listeDesZ
    
    # clés créé par tortu : "tortuosites transversales" et "tortuosites longitudinales"

    # dictionnaire en retour :
    tortu = dict()
    tortu["tortuosites transversales"] = tortutransversale
    tortu["tortuosite moyenne transversale"]= moyenneH
    tortu["tortuosite mediane transversale"] = medianeH
    tortu["tortuosite maximum transversale"] = tmaxH    
    tortu["tortuosite minimum transversale"] = tminH
    tortu["tortuosites longitudinales"] = tortulongitudinale
    tortu["tortuosite moyenne longitudinale"] = moyenneV
    tortu["tortuosite mediane longitudinale"] = medianeV
    tortu["tortuosite maximum longitudinale"] = tmaxV    
    tortu["tortuosite minimum longitudinale"] = tminV    
    return tortu

def tortuosite_maillage(mailles,lePas):
    tortuFinal  = list()
    nbDecimales = 3
    maillage = random.sample([e for e in mailles],min(200,mailles.__len__()))   # choix aléatoire de 200 profils max
    tortu = [tortuosity_profil(profil,lePas) for profil in maillage]            # constitue la liste des tortuosités de chaque ligne
    tortuFinal = [e for e in tortu if e]                                             # suppression des istes vides
    if tortuFinal:
        if (sum(tortuFinal)/tortuFinal.__len__())<=1.03 : nbDecimales = 4 
        moyenne = round(sum(tortuFinal)/tortuFinal.__len__(),nbDecimales)
        mediane = round(statistics.median(tortuFinal),nbDecimales)
        tmax =    round(max(tortuFinal),nbDecimales)
        tmin =    round(min(tortuFinal),nbDecimales)
        variance =statistics.variance(tortuFinal)
        ecarttype=variance**0.5
        app.encadrePlus("\n\nTaille de l'échantillon = "+str(maillage.__len__()))
        app.encadrePlus("\nnombre de points par lignes = "+str(maillage[0].__len__()))
        app.encadrePlus("\n\ntortuosité moyenne = "+str(moyenne))
        app.encadrePlus("\ntortuosité médiane = "+str(mediane))
        app.encadrePlus("\n\ntortuosité maxi = "+str(tmax))
        app.encadrePlus("\ntortuosité mini = "+str(tmin))
        app.encadrePlus("\nvariance = "+str(variance))
        app.encadrePlus("\necart type = "+str(ecarttype))                        
        if abs((moyenne/mediane)-1)>=0.05:
            app.encadrePlus("\n\nRemarque : L'écart entre la moyenne et la médiane suggére que la surface n'est partout plane.")
    else:
        app.encadrePlus("Tortuosité non calculée, la maille du MNT est sans doute trop grande.\nAugmenter la valeur du paramètre 'nombre de maille par points'.")
        return [],0,0,0,0
    return tortuFinal,moyenne,mediane,tmax,tmin    # liste des 200 valeurs de tortuosité sur 200 lignes aléatoires puis les stats

def tortuosity_profil(ligne,lePas): # accepte une ligne de maillage,
                                    # la découpe en plusieurs sous lignes de valeurs effectivement calculées,
                                    # et renvoie la listedes tortuosités pour chaque sous-liste : (t1, t2, t3...)
    # découpe la ligne de points en segments valides (séquence OK séparées par des valeurs de remplissage -9999)
    tortu = None
    sousLigne = list()
    longueurSousLigne=50
    nbRemplissage = 0
    for e in ligne:
        if e != remplissage: sousLigne.append(e)
        if e == remplissage and sousLigne.__len__()>longueurSousLigne: # calcul la tortuosité si le nombre de points consécutifs est au moins de 50
            nbRemplissage+=1
            t = tortuSousLigne(sousLigne,lePas)
            if t>=1:
                tortu = t
                longueurSousLigne=sousLigne.__len__() # on conserve la tortuosité sur la plus longue des sous-lignes valides
    if nbRemplissage==0 and sousLigne.__len__()>longueurSousLigne:
        t = tortuSousLigne(sousLigne,lePas)
        if t>=1:
            tortu = t        
    return tortu            

def tortuSousLigne(unProfil,lePas): # sousLigne : liste des Z successifs, la distance entre 2 Z étant lePas dans la même unité.
    points = [(x*lePas,y) for x,y in enumerate(unProfil)]      # reconstitue les couples x,y des seuls points valides
    nombreDepoints = points.__len__()
    if nombreDepoints<2: return 0                                                                     # si pas au moins 2 points : retour = 0
    longueur_extremit = ((points[-1][1]-points[0][1])**2 + (points[-1][0]-points[0][0])**2)**.5         # Distance euclidienne entre début et fin valides
    longueur_profil = sum([((a[0]-b[0])**2+(a[1]-b[1])**2)**0.5 for a,b in zip(points[:-1],points[1:])])# somme des distances inter points
    t = float(longueur_profil/longueur_extremit)
    return t                                                      # retour : tortuosité du "tableau" (= un profil) et nombre de points

    
########################################### utilitaires métiers

def quelFichier(titre = "MNT à lire", extension=("TXT","*.txt")):
    return tkinter.filedialog.askopenfilename(
                                    filetypes=[extension,("Tous","*")],
                                    multiple=False,
                                    title = titre)

#lecture d'un fichier MNT : de type csv, délimiteur "," (éventuellement " ")de format : 3 lignes de 5 valeurs d'altitude :

def lire_fichier_mnt(fichier):
    try: maillage = loadtxt(fichier,delimiter=',',)
    except: maillage = None
    return maillage

########################################### va chercher le ppas utilisé pour construire le MNT (dans le fichier des métadonnées)

def demandeLePas(fichierMNT):
    fichierPAS = os.path.splitext(fichierMNT)[0][:-4]+"_PAS.txt"         # nom du fichier contenant la métadonnée "lePas" qui sera écrit
    if os.path.exists(fichierPAS):
        try:
            with open(fichierPAS, 'rb') as f:
                param = pickle.load(f)
            lePas = param[0]
            nbPointsParMaille = param[1]
        except: return 0,0
    else: return 0,0
    return lePas,nbPointsParMaille



########################################### Conversion PLY en XYZ puis en MNT

def ecrireMNT(fichierPly):
    erreur = list(range(10))
    if not os.path.exists(fichierPly): return erreur
    
    fichierMNT = os.path.splitext(fichierPly)[0]+"_MNT.txt"         # nom du fichier mnt qui sera écrit   
    fichierPAS = os.path.splitext(fichierPly)[0]+"_PAS.txt"         # nom du fichier contenant la métadonnée "lePas" qui sera écrit   

    endian = "@"                                                    # valeur par défaut : endian du système
    fmt = str()                                                     # format de codage des données dans le ply ce format est utilisé par struct
    i = int()
    with open(fichierPly, 'rb') as infile:                          # lecture du fichier en mode "binaire"
        ligne = infile.read()

    lignes = ligne.splitlines()                                     # coupure du flux binaire en "lignes"
    if lignes[0]!=b'ply':                                           # vérification que le tag "ply" est présent en entête de fichier
        erreur[0] = "erreur : le fichier\n"+fichierPly+"\nn'est pas un fichier de type ply."
        return erreur                                               # Abandon si pas fichier ply

    if b"ascii" in lignes[1]:                                        # pas prévu pour lire les fichiers ply "ASCII" choisir binary lors de l'écriture
        erreur[0] = "erreur : le fichier\n"+fichierPly+"\nest un fichier de type ply au format ASCII.\nUtiliser le format BINARY lors de l'enregistrement du fichier ply."
        return erreur

    for e in lignes:                                                # décodage des lignes d'entête qui indique la structure du fichier
        i+=1
        if e==b'end_header':
            break                                                   # tag de fin d'entête on connait la structure, fin du décodage de la structure
        s=str(e)             
        if "little_endian" in s:                                    # boutisme
            endian="<"
        if "big_endian" in s:
            endian=">"
        if "element vertex" in s:                                   # nombre de points
            nombre_points = int(s.split(" ")[-1][0:-1])
        if "element face" in s:                                     # nombre de faces, cela termine la lecture : on ignore les faces
            nombre_faces = int(s.split(" ")[-1][0:-1])
            break
        if "property" in s:                                         # property : liste les éléments de la structure des données pour chaque point
            cType = s.split(" ")[1]
            if cType=="float":                                      # Micmac n'utilise que les valeurs float et uchar
               fmt += "f"                                           # indique qu'il y a un float à lire
            elif cType=="uchar":
               fmt += "B"                                           # indique qu'il y a un octet à lire
            elif cType=="char":
               fmt += "c"                                           # indique qu'il y a un octet à lire
            elif cType=="short":
               fmt += "h"                                           # indique qu'il y a deux octet à lire 
            elif cType=="ushort":
               fmt += "H"                                           # indique qu'il y a deux octet à lire
            elif cType=="int":
               fmt += "i"                                           # indique qu'il y a 4 octet à lire 
            elif cType=="uint":
               fmt += "I"                                           # indique qu'il y a 4 octet à lire
            elif cType=="double":
               fmt += "d"                                           # indique qu'il y a 8 octet à lire                              
            elif cType!="list":                                     # la valeur list est aussi utilisée, s'il s'agit d'une autre valeur : abandon
                print("format non prévu pour les ply issus de micmac, abandon : ",cType)
                return erreur

    fmt = endian+fmt                                                # le format est complété par le boutisme
    debutData = ligne.find(b"end_header",0,1000)+11                 # on extrait la zone des données utiles dans la varible "ligne" : début = aprés l'entête
    longueurData = nombre_points*struct.calcsize(fmt)               # on prend juste la longueur nécessaire (nombre de point * longueur des données du point)
    finData = debutData + longueurData
    plageData = ligne[debutData:finData]
    
    # extraction des X,Y,Z du ply :
    valeur=tuple([e for e in fmt])
    try:
        app.encadre("\nAttention : procédure longue, création d'un maillage à partir du fichier :\n"+fichierPly)
        lesXYZ = [((valeur[0],valeur[1]),valeur[2]) for [*valeur] in struct.iter_unpack(fmt,plageData).__iter__() ] # list comprehension extrayant les xyz de la structure décodée
    except Exception as e:
        print("Erreur lors du décodage des données, le ply ne provient pas de micmac. Erreur : ",e)
        return erreur

############################### pour test écriture xyz
    
##    # Ecriture fichier points du ply (les z serviront pour le test de kolmogorov-smirnoff)
##    fichierXYZ = os.path.splitext(fichierPly)[0]+".xyz"             # nom du fichier xyz qui sera écrit
##    with open (fichierXYZ,"w") as outfile:                  # ouverture du fichier de sortie, liste des z avec 6 chiffres significatifs
##        app.encadrePlus("\nEcriture fichier XYZ : "+fichierXYZ+"\n")
##        listeDesZ = list()
##        for e in lesXYZ:
##            x=1000*(e[0][0]+100)
##            y=1000*(e[0][1]+100)
##            z=1000*e[1]
##            outfile.write(str(x)+" "+str(y)+" "+str(z)+"\n")# écriture des éléments x y et z séparé par un espace (si on veut une virgule mettre "," au lieu de " "
##            listeDesZ.append(str(e[1])[:6])

############################### fin test
    # liste des Z
    
    listeDesZ = list()
    [listeDesZ.append(str(e[1])) for e in lesXYZ]
    
    # création de la grille régulière :
    
    nombreDePointsDansLePly = lesXYZ.__len__()
    
    points = [xy for xy,z in lesXYZ]        # voir la commande zip peut être utile : https://stackoverflow.com/questions/12142133/how-to-get-first-element-in-a-list-of-tuples
    min_x  = min([x for x,y in points])     # bornes
    max_x  = max([x for x,y in points])
    min_y  = min([y for x,y in points])
    max_y  = max([y for x,y in points])

    # recherche d'un pas de maillage cohérent avec les données du ply :
    # la maille doit être un peu plus fine que la densité de points
    
    surface = (max_x-min_x)*(max_y-min_y)
    if surface>0:
        densite = lesXYZ.__len__()/surface  # densité : nombre de points par unité de surface
        surfaceParPoint = 1/densite         # surface moyenne occupée par un point du nuage
        surfaceMaille = surfaceParPoint / nbMaillesParPointDuNuage # surface de chaque maille
        lePas = surfaceMaille**0.5          # coté moyen du carré autour d'un point du nuage
    else:
        app.encadre("Surface engendrée par les points du ply = 0.")
        return
    
    # générer un maillage avec un pas régulier, création de la grille régulière
    grid_x, grid_y = mgrid[min_x:max_x+lePas:lePas, min_y:max_y+lePas:lePas]

    maillage = griddata( points,
                      [z for xy,z in lesXYZ],
                      (grid_x, grid_y),
                      method=methode,
                      fill_value=remplissage)

    nombreDeMaillesSansValeur = (maillage==remplissage).sum() # maillage est un ndarray

    # Ecriture fichier MNT
    
    savetxt(fichierMNT,
                 maillage,
                 delimiter=',',
                 newline='\r\n',
                 header='')
    
    # écriture du fichier des métadonnées : lePas, nbMaillesParPointDuNuage
    
    with open(fichierPAS, 'wb') as f:
        param=(lePas,nbMaillesParPointDuNuage)
        pickle.dump(param,f)

    if os.path.exists(fichierMNT):
        app.encadre("PLY vers MNT : Fichier PLY traité : ",fichierPly)        
        app.encadrePlus("\n\nFichier MNT écrit sur disque : ",fichierMNT)
        app.encadrePlus("\n\nmini et maxi sur l'axe des x : "+str(round(min_x,4))+"  "+str(round(max_x,4)))
        app.encadrePlus("\nmini et maxi sur l'axe des y : "+str(round(min_y,1))+"  "+str(round(max_y,4)))
        app.encadrePlus("\nDimension du maillage : "+str(int((max_x-min_x)/lePas))+" * "+str(int((max_y-min_y)/lePas)))
        app.encadrePlus("\nNombre de mailles : "+str(int((max_x-min_x)/lePas)*int((max_y-min_y)/lePas)))         
        app.encadrePlus("\n\nnombre de points dans le fichier ply : "+str(nombreDePointsDansLePly))         
        app.encadrePlus("\nnombre de mailles par point du nuage : "+str(nbMaillesParPointDuNuage))      
        app.encadrePlus("\n\nPas retenu pour le maillage : "+str(round(lePas,4)))
        app.encadrePlus("\n\nNombre de mailles sans valeur calculée : "+str(nombreDeMaillesSansValeur)+" soit "+str(int(100*nombreDeMaillesSansValeur/nombreDePointsDansLePly))+" %")
    else:
        app.encadre("Traitement PLY vers MNT (nuage vers maillage) \nErreur lecture du fichier :\n\n ",fichierPly," \n\nCe fichier n'est reconnu comme un fichier PLY valide pour ce traitement.")
    XYZ = dict()
    XYZ["min_x"] = min_x
    XYZ["max_x"] = max_x
    XYZ["min_y"] = min_y
    XYZ["max_y"] = max_y
    XYZ["lePas"] = lePas
    XYZ["nombreDePointsDansLePly"] = nombreDePointsDansLePly    
    XYZ["nombreDeMaillesSansValeur"] = nombreDeMaillesSansValeur
    XYZ["fichierPly"] = fichierPly    
    XYZ["fichierMNT"] = fichierMNT 
    XYZ["listeDesZ"] = listeDesZ
    return dict(XYZ)


########################################### Utilitaires STANDARDS ##############################
    # statsBasiques effectue d'abord un nettoyage des données (numériques, exclut les valeurs extrèmes)

def statsBasiques(liste):   # moyenne, médiane, variance, écart type, mode, étendue, mini, maxi, longueur pour une liste ou un tuple. Seul les nombres sont retenus 
    stat = dict()
    stat["marges supprimées"] = 0.005   # suppression de 1% des valeurs (0.5% en haut et en bas)
    stat["Nombre de classes"] = 10      # Nombre de classes pour l'histogramme
    # sélection des valeurs numériques :
    l = [e for e in liste if is_number(e)]
    stat["nombre"] = l.__len__()
    # conversion en ndArray
    tableauBrut = numpy.array(l,dtype=float) # tableau dimension 1
    # tri sur place pour éliminer les valeurs extrèmes potentiellement aberrantes (0.5% à chaque extrémité)
    tableauBrut.sort()
    stat["borneMini"] = int(stat["nombre"]*stat["marges supprimées"] )      # 0.5%
    stat["borneMaxi"] = stat["nombre"] - stat["borneMini"]                  # 99.5%
    tableau = tableauBrut[stat["borneMini"]:stat["borneMaxi"]]
    stat["nombreRetenu"] = tableau.__len__()
    # alcul des indicateurs statistiques basique    
    stat["moyenne"] = tableau.mean(axis=0)
    stat["ecartType"] = tableau.std(axis=0)
    stat["variance"] = tableau.std(axis=0)*tableau.std(axis=0)   
    stat["maxi"] = tableau.max(axis=0)
    stat["mini"] = tableau.min(axis=0)
    stat["etendue"] = stat["maxi"]-stat["mini"]
    stat["asymetrie"] = stats.skew(tableau,axis=0)
    stat["kurtosis"] = stats.kurtosis(tableau,axis=0) 
    stat["p_value Kolmogoroff Smirnoff pour une loi normale : "] = kstest(tableauBrut,"norm")[1]   
    # calcul histogramme
    stat["histo"] = numpy.histogram(tableau,bins=stat["Nombre de classes"])
    stat["classeModale"] = numpy.argmax(stat["histo"][0])    # classe ayant le plus d'éléments
    stat["médiane"] = tableauBrut[int(tableauBrut.__len__()/2)]
    # recherche le mode (unique) à partir de l'histo : milieu de la classe modale (plus stable que la moyenne avec la classe +1 dont il faudrait tester la présence)
    stat["mode"] = stat["histo"][1][stat["classeModale"]]+(stat["etendue"]/(2*stat["Nombre de classes"])) 
    app.encadre("Statistiques basiques sur les Z\n")
    [app.encadrePlus(e+" : "+str(stat[e])+"\n")  for e in stat] 
    return stat


def testKolmogorovSmirnov(protocole,listeDesValeurs,cleReference,titre,axe,centrer=False,ecreter=True):    
    if type(listeDesValeurs)==type(None):
        return "Pas de données"
    
    # test : distribution de la liste des Z par rapport aux 3 références du protocole :
    # lecture  des références :
    # référence est un dictionnaire la clé étant un tuple 2 éléments : Protocole et le niveau de compactage, la valeur est un dictionnaire
    # si pas sauvegardé, alors création d'un dictionnaire vide references[(protocole,compactage)] = dict()
    # clés de stat (sur les Z épurés ) : "marges supprimées","nombre","borneMini","borneMaxi","nombreRetenu",
    # "moyenne","ecartType","maxi","mini","etendue","Nombre de classes","histo","classeModale","mode"
    # clés de stat provenant de XYZ : "min_x","max_x","min_x","max_x","lePas",nombreDePointsDansLePly,nombreDeMaillesSansValeur,fichierPly,fichierMNT,listeDesZ
    # clés créé par tortu : "tortuosites transversales" et "tortuosites longitudinales"
    # et "tortuosite moyenne transversale" "tortuosite mediane transversale" "tortuosite maxi transversale" "tortuosite mini transversale"

    # valeurs initiales par défaut en cas d'absence d'une référence :
    absence = str()
    listeZReferenceC = list()
    listeZReferenceSC = list()
    listeZReferenceF = list()
    testC = stats.Ks_2sampResult(1,0)
    testSC = stats.Ks_2sampResult(1,0)
    testF = stats.Ks_2sampResult(1,0)
    rapport = str()
                                  
   # On recherche les listes du protocole de référence et on les transforme en array ainsi que la liste test
    aTester           = numpy.asarray(listeDesValeurs,numpy.float32) # liste des Z, ou des tortuosités                                  
    references = restaureReferences()
    if (protocole,"C")  in references.keys():listeZReferenceC  = numpy.asarray(references[(protocole,"C")] [cleReference],numpy.float32)
    if (protocole,"SC") in references.keys():listeZReferenceSC = numpy.asarray(references[(protocole,"SC")][cleReference],numpy.float32)
    if (protocole,"F")  in references.keys():listeZReferenceF  = numpy.asarray(references[(protocole,"F")] [cleReference],numpy.float32)

    # 2 traitements différents des données : les altitudes Z dont la moyenne peut dériver doivent être centrées
    # une fois centrés les fonctions de répartition se coupent en zéro : l'exigence sur l'écart des courbe sera plus grande
    if ecreter:
        listeZReferenceC  = ecreterListe(listeZReferenceC)    # élimine les  valeurs trop loin de la moyenne 
        listeZReferenceSC = ecreterListe(listeZReferenceSC)   
        listeZReferenceF  = ecreterListe(listeZReferenceF)
        aTester           = ecreterListe(aTester)    
 
    if centrer: 
        ecartStatMax=0.2                                                # explication : voir le module de conclusion
        listeZReferenceC  = centrerSurMediane(listeZReferenceC)    # il faut recaler les Z sur sur la médiane ou la moyenne 
        listeZReferenceSC = centrerSurMediane(listeZReferenceSC)   # l'altitude moyenne ne doit pas intervenir dans le calcul
        listeZReferenceF  = centrerSurMediane(listeZReferenceF)
        aTester           = centrerSurMediane(aTester)
    else:                                                               # recalage inutile pour les tortuosités
        ecartStatMax=0.4
   
    if listeZReferenceC.__len__():
        testC = ks_2samp(aTester, listeZReferenceC)
    else :
        absence += "\nZone compactée absente de la référence"
   
    if listeZReferenceSC.__len__():
        testSC = ks_2samp(aTester, listeZReferenceSC)
    else :
        absence += "\nZone Semi-compactée absente de la référence"
    
    if listeZReferenceF.__len__():
        testF = ks_2samp(aTester, listeZReferenceF)
    else :
        absence += "\nZone foisonnée absente de la référence"        

    # examen des résultats des tests de KS et conclusion :

    rapport += conclusionKolmogorov(testC,testSC,testF,titre,ecartStatMax)

    # graphiques :

    # abonde le subplot "axe" avec les 4 courbes test, reférence compactée, semi-compactée et fusionnée, l'affiche est dans un boutn

    uneCourbe(aTester, axe, titre, 'red')
    uneCourbe(listeZReferenceC, axe, titre, 'blue')
    uneCourbe(listeZReferenceSC, axe, titre, 'green')
    uneCourbe(listeZReferenceF, axe, titre, 'yellow')
    
    return rapport+absence
    
def conclusionKolmogorov(c,sc,f,titre=str(),ecartStatMax=0.1):
    rapport = "\n Conclusion du test de Kolmogorov-Smirnov "+titre+" :\n"        
    nb = 0
    assurance = str()    
    # Utilisation des pvalue si une valeur est supérieure à 0.025 : on a trouvé une correspondance au moins probable
    maxPvalue = max (c.pvalue,sc.pvalue,f.pvalue)
    print("KS : c.pvalue,sc.pvalue,f.pvalue = ",c.pvalue,sc.pvalue,f.pvalue)
    if maxPvalue>0.9: assurance = " certaine\n"
    elif maxPvalue>=0.5: assurance = " très probable\n"
    elif maxPvalue>=0.05: assurance = " probable\n"
    elif maxPvalue>=0.025:
        rapport += "\nLa zone testée n'est identifiée avec certitude à aucune des zones de référence.\n"        
        rapport += "\nLa zone la plus ressemblante est la \n" 
    if  maxPvalue>=0.025:
        if c.pvalue==maxPvalue:
            rapport +="zone compactée"+assurance
            nb+=1
        if sc.pvalue==maxPvalue:
            rapport +="zone semi-compactée"+assurance
            nb+=1
        if f.pvalue==maxPvalue:
            rapport +="zone foisonnée"+assurance
            nb+=1
        if nb==2:
            rapport += "Il y a probablement 2 zones de référence identiques\n"
        if nb==3:
            rapport += "Les 3 zones de référence sont probableemnt identiques\n"            
        return rapport
    if maxPvalue==0:  # si pValue est trop faible on ne va pas plus loin
        rapport += "La zone testée n'est proche d'aucune des zones de référence.\n"  
        return rapport
    
    # pas de correspondance flagrante trouvée avec les pvalue (non toutes nulles), exploitation de la valeur statistic :
    
    # Aucune pValue >=0.025, la zone semble n'appartenir à aucun type on recherche le minimum de l'écart normé
    # utilisation de "statistic" qui mesure l'écart max entre les distributions,
    # Pour les Z qui sont centrés sur zéro l'écart et nul pour zéro, l'écart max acceptable est fixé à 0.20
    # pour les tortuosités qui peuvent être très variable l'écart max est fixé à 0.4
    #ce paramète est passé lors de l'appel de la fonction
    minEcart = min(c.statistic,sc.statistic,f.statistic)
    if minEcart<=ecartStatMax:
        rapport += "\nLa zone testée n'est identifiée avec certitude à aucune des zones de référence.\n"        
        rapport += "\nLa zone la plus ressemblante est la \n"         
        if c.statistic==minEcart:
            rapport +="zone compactée\n"
            nb+=1            
        if sc.statistic==minEcart:
            rapport +="zone semi-compactée\n"
            nb+=1
        if f.statistic==minEcart:
            rapport +="zone foisonnée\n"
            nb+=1
        if nb==2:
            rapport += "Il y a probablement 2 zones de référence identiques\n"
        if nb==3:
            rapport += "Les 3 zones de référence sont probableemnt identiques\n"  
        return rapport
    rapport += "La zone testée n'est proche d'aucune des zones de référence.\n"  
    return rapport

def testProxi(protocole,stat):
    def proxi(attribut):
        # proximité : attribut
        try:
            attributC = references[(protocole,"C")][attribut]
            attributSC = references[(protocole,"SC")][attribut]
            attributF = references[(protocole,"F")][attribut]
            valAttribut = stat[attribut]
            dC = abs(attributC-valAttribut)
            dSC = abs(attributSC-valAttribut)
            dF = abs(attributF-valAttribut)
            plusProche = min(dC,dSC,dF)
            print("plus proche=",attribut,"=",valAttribut," ref : ",attributC,attributSC,attributF," dist mini = ",plusProche)
            if plusProche==dC :  listeProxis.append("Compactée")
            if plusProche==dSC : listeProxis.append("Semi compactée")
            if plusProche==dF :  listeProxis.append("Foisonnée")
        except:
            return
                               
    references = restaureReferences()
    if  not((protocole,"C")  in references.keys() and
        (protocole,"SC")  in references.keys() and
        (protocole,"F")  in references.keys()):
        return
    listeProxis = list()
    [proxi(e) for e in ("etendue","ecartType","tortuosite mediane transversale","tortuosite mediane longitudinale")]
    compte = Counter(listeProxis).most_common(2)
    rapport  =None
    if compte[0][1]==4:
         rapport  = "la zone testée est une zone "+compte[0][0]
    if compte[0][1]==3:
         rapport  = "la zone testée est très probablement une zone "+compte[0][0]     
    if compte[0][1]==2 and compte[1][1]==1:
         rapport  = "la zone testée est probablement une zone "+compte[0][0]
    if compte[0][1]==2 and compte[1][1]==2:
        if listeProxis[2]==listeProxis[3]:  # si les 2 tortuosités sont dans la même zone alors elles sont prioritaires sur la dispersion des z
             rapport  = "la zone testée est probablement une zone "+listeProxis[3]         
    if rapport:
         rapport="Au vu des valeurs des tortuosités et de l'étendue et de l'écart type des Z : \n"+rapport+"\n"
    else:
        rapport = "Au vu des valeurs des tortuosités et de l'étendue et de l'écart type des Z : aucune correspondance"
    return rapport
    
def synthese(stat,protocole):
    # clés de stat (sur les Z épurés ) : "marges supprimées","nombre","borneMini","borneMaxi","nombreRetenu",
    # "moyenne","ecartType","maxi","mini","etendue","Nombre de classes","histo","classeModale","mode"
    # clés de stat provenant de XYZ : "min_x","max_x","min_x","max_x","lePas",nombreDePointsDansLePly,nombreDeMaillesSansValeur,fichierPly,fichierMNT,listeDesZ
    # clés créé par tortu : "tortuosites transversales" et "tortuosites longitudinales"
    # et "tortuosite moyenne transversale" "tortuosite mediane transversale" "tortuosite maxi transversale" "tortuosite mini transversale"
    
    rapport  = "Synthèse des observations sur le fichier :\n"+stat["fichierPly"]+".\n\n"
    rapport += "Variance sur les Z : "+stat["variance"].__str__()+"\n"
    rapport += "Ecart type sur les Z : "+stat["ecartType"].__str__()+"\n"
    rapport += "Etendue des Z (= épaisseur de la surface) : "+stat["etendue"].__str__()+"\n\n"
    rapport += "Tortuosité transversale : "+stat["tortuosite moyenne transversale"].__str__()+"\n"
    rapport += "Tortuosité longitudinale : "+stat["tortuosite moyenne longitudinale"].__str__()+"\n"
    rapport += "\nMétrique du protocole : '"+metrique(protocole)+"'"
    
    return rapport


def uneCourbe(liste, axe, titre,couleur):
    # abonde le subplot axe avec la fonction de répartition de la 'liste'
    if type(liste)!=type(numpy.ndarray(1)):
        liste = numpy.asarray(liste,dtype=numpy.float32)
    histo, bin_edges = numpy.histogram(liste, bins=50, normed=True)  
    dx = bin_edges[1] - bin_edges[0]
    cumul = numpy.cumsum(histo)*dx
    plot = axe.plot(bin_edges[:-1], cumul, c=couleur)
    axe.grid()
    axe.set(title=titre)
    axe.set_ylim([0,1])

def unHistogramme(liste, axe, titre,couleur="blue"):
    if liste.__len__()==0:return
    # abonde le subplot axe avec la fonction de répartition de la 'liste'
    if type(liste)!=type(numpy.ndarray(1)):
        liste = numpy.asarray(liste,dtype=numpy.float32)
    plot = axe.hist(liste,50)
    axe.grid()
    axe.set(title=titre)
    
   
########################################### Utilitaires STANDARDS ##############################


def heure():        #  time.struct_time(tm_year=2015, tm_mon=4, tm_mday=7, tm_hour=22, tm_min=56, tm_sec=23, tm_wday=1, tm_yday=97, tm_isdst=1)
        return ("le %(jour)s/%(mois)s/%(annee)s à %(heure)s:%(minutes)s:%(secondes)s") % {"jour" : str(time.localtime()[2]), "mois" : str(time.localtime()[1]), "annee" : str(time.localtime()[0]), "heure" : str(time.localtime()[3]), "minutes" : str(time.localtime()[4]), "secondes": str(time.localtime()[5])}

def is_number(s):
    if type(s) not in (type(str()),type(float()),type(int()),type(numpy.float64()),type(numpy.int64()),type(numpy.int32()),type(numpy.float32())):
        return False
    try:
        float(s)
        return True
    except ValueError:
        return False

def supprimeFichier(fichier):
    try:    os.remove(fichier)
    except Exception as e:
        return "Erreur suppression fichier :"+str(e)
    
########################################### Sauvegarde des paramètres, affichage

def sauveParam():
    with open(fichierParam, mode="wb") as sauve:
        pickle.dump((nbMaillesParPointDuNuage,protocoleParDefaut,listeItemsAffiches),
                    sauve)

def restaureParam():
    global nbMaillesParPointDuNuage,protocoleParDefaut    
    if not os.path.exists(fichierParam): return
    try:
        with open(fichierParam, mode="rb") as restaure:
            r = pickle.load(restaure)
            nbMaillesParPointDuNuage = r[0]
            protocoleParDefaut = r[1]
    except Exception as e:
        print("erreur restauration paramètres : "+str(e))

def afficheParam():
    app.encadre("Paramètres\n\n"+
                "nombre de mailles par points du nuage : "+str(nbMaillesParPointDuNuage)+"\n\n"+
                "soit :\nnombre moyen de points dans une maille : "+str(round(1/nbMaillesParPointDuNuage,2)),
                "\nFichier trace :",fichierTrace,
                "\nTableau au format texte des résultats :",fichierCalculPly) 
    return

########################################### Gestion des références : sauve, restaure, affiche, supprime, métrique, liste protocoles

def saisieReference():      # saisie d'une nouvelle référence
    global protocoleParDefaut     
    # saisie du contexte : protocole, compactage effectif sur la zone, fichier ply
    
    app.menage()
    liste = listeProtocoles()
    if liste:
       message = "\nListe des protocoles actuels: \n - "+"\n - ".join(listeProtocoles())
    else:
        message = "Donner le nom du nouveau protocole."
        protocoleParDefaut = ""
    protocole = tkinter.simpledialog.askstring( "Protocole utilisé pour effectuer les photos.",
                                                "nom du protocole : texte libre, sera demandé pour effectuer les tests\n "+
                                                "Le protocole est relatif aux conditions de prise de vue et de création du ply\n"+
                                                "L'unité de mesure des x,y et z est unique pour les fichiers issus d'un même protocole\n"+
                                                message+"\n",
                                                 initialvalue=protocoleParDefaut,
                                                parent=fenetre
                                               )
    if protocole==None: return   
    if protocole!=protocoleParDefaut:
       protocoleParDefaut=protocole
       sauveParam()
       
    # la zone de référence que l'on va traiter est-elle : Compactée, semi-Compactée, Foisonnée ?
    
    compactage = tkinter.simpledialog.askstring("Compactage de la référence",
                                                "Indiquer si la référence est une zone :\n - Compactée (=C),\n - Semi-compactée (=SC)\n - foisonnée (=F)",
                                                 initialvalue="C",
                                                parent=fenetre
                                               )
    if compactage==None: return
    if compactage not in ("C","SC","F"):
        app.encadre("protocole:",protocole,"\nCompactage:",compactage,"\nCompactage incorrect : doit être C, SC ou F, \nAbandon")
        return

    # choix du fichier .ply a traiter
    
    fichierPly = quelFichier(titre="fichier PLY pour la référence",extension=("PLY","*.ply"))
    if not os.path.exists(fichierPly):
        app.encadre("protocole:",protocole,"\nCompactage:",compactage,"\nPas de fichier PLY : Abandon")        
        return

    # création de la métrique pous ce protocole si nouveau :

    metrique(protocole)

    # toutes les infos sont là pour effectuer les calculs
    
    app.encadre("Ajout d'une référence pour :\nprotocole : ",protocole,"\nCompactage:",compactage,"Fichier PLY : ",fichierPly)
    
    # Extraction des x y et z, écriture du fichier xyz, listeDesZ
        
    XYZ = ecrireMNT(fichierPly)         # des infos sur la liste des XYZ, dans un dictionnaire
    if type(XYZ["min_x"])==str():       # si erreur dans le fichier ply alors le messages est dans la clé min_x :
        app.encadre("Erreur lors de la lecture du fichier ply :\n\n"+XYZ["min_x"])
        return
    
    # calcul et affichagez des statistiques "basiques"
    
    stat = statsBasiques(XYZ["listeDesZ"])

    # calcul des tortuosités transversales et longitudinales sur 200 lignes aléatoires :
    # clés créé par tortu : "tortuosites transversales" et "tortuosites longitudinales"

    tortu = tortuosity_surfacique(XYZ["fichierMNT"])

    # fusion des 3 dictionnaires  en un seul : stat
    
    stat.update(XYZ)   
    stat.update(tortu)

    # Ajout de la référence dans le dictionnaire des références :
    # structure : la clé composé du tuple (protocole, niveau de compactage) la valeur qui est le dictionnaire stat
    
    ajoutReference(protocole,compactage,stat)

    # Ajout dans les résutats de traitement des fichiers PLY :

    ajoutStatPly(fichierPly,stat)

    # Affichage d'une synthèse finale

    app.encadre(synthese(stat,protocole))
    app.encadrePlus("\n\n Pour plus de détails consulter la trace")
    app.encadrePlus("\n\n FIN DE l'ENREGISTREMENT DE LA REFERENCE\n Protocole : "+protocole+" ---- compactage : "+compactage)

def sauveReferences(references):
    # le paramètre 'references' contient le dictionnaire de toutes les références
    # clé = tuple (protocole, niveaau de compactage)
    # valeur = dictionnaire nommé 'stat' provenant de XYZ et stat (stat générales, tortuosité)
    with open(fichierReference, mode="wb") as sauve:
        pickle.dump(references,
                    sauve)

def restaureReferences():   
    # structure de la variable references :
    # dictionnaire :
    # clé = tuple (protocole, niveau de compactage ou 'metrique')
    # valeur = dictionnaire nommé 'stat' provenant de XYZ et stat

    # clés de stat (sur les Z épurés ) : "marges supprimées","nombre","borneMini","borneMaxi","nombreRetenu",
    # "moyenne","ecartType","maxi","mini","etendue","Nombre de classes","histo","classeModale","mode"
    # clés de XYZ : "min_x","max_x","min_x","max_x","lePas",nombreDePointsDansLePly,nombreDeMaillesSansValeur,fichierPly,fichierMNT,listeDesZ
    # clés créé par tortu : "tortuosites transversales" et "tortuosites longitudinales"
    # clé pour la métrique : "métrique"
    
    # si pas sauvegardé, alors création d'un dictionnaire vide references[(protocole,compactage)] = (stat,XYZ)
    references = dict()                             
    if not os.path.exists(fichierReference):
        return references
    try:
        with open(fichierReference, mode="rb") as restaure:
            references = pickle.load(restaure)
    except Exception as e:
        app.encadre("erreur restauration des références, création d'un dictionnaire vide : "+str(e))            
    return references

def afficheReferences():
    references = restaureReferences()   #     references[(protocole,compactage)] = (XYZ,stat)
    if references==dict():
        app.encadre("pas de références")
        return
    app.encadre("Les fichiers  des références :\n\n")
    l = ["protocole : "+str(a)+" -- compactage : "+str(b)+" -- fichier : "+str(references[(a,b)]["fichierMNT"])
         for a,b in references.keys()
         if b in ("C","SC","F")]
    app.encadrePlus("\n".join(l))
##    if (protocole,"") in references:
##        metrique = str(references[(a,"")]["métrique"])
##    else:
##        metrique = "inconnue"

    app.encadrePlus("\n\nLes caractéristiques essentielles des références : ")
    m = [str(a)+" "+str(b)+
         "; métrique : "+metrique(a)+
         "; étendue des Z : "+str(round(references[(a,b)]["etendue"],3))+
         "; ecart type des Z : "+str(round(references[(a,b)]["ecartType"],3))+
         "  ; tortuosité transversale : "+str(references[(a,b)]["tortuosite mediane transversale"])+
         ", longitudinale : "+str(references[(a,b)]["tortuosite mediane longitudinale"]) 
         for a,b in references.keys()
         if b in ("C","SC","F") ]

    app.encadrePlus("\n","\n".join(m))

def ajoutReference(protocole, compactage,stat):
    references = restaureReferences()
    references[(protocole,compactage)] = stat
    sauveReferences(references)
    
def supprimeReference():
    app.encadre("Non implémenté")

def supprimeReferences():
    app.menage()
    if not os.path.exists(fichierReference):
        app.encadre("Pas de références !")
        return
    references = restaureReferences()
    protocolesCompactage = [(a,b) for a,b in references.keys()]
    referencesASupprimer = choisirItem(protocolesCompactage, titre="Choisir les protocoles à supprimer ",mode="extended").listeChoisie # single ou extended
    if not referencesASupprimer: return
    [references.pop(e) for e in referencesASupprimer]
    sauveReferences(references)
    app.encadre("Suppression effectuée.")
    
    # Gestion de la métrique des ply pour une référence:

def saisieMetrique():

    app.menage()
    listeDesProtocoles = listeProtocoles()
    if not listeDesProtocoles:
        app.encadre("Aucun protocole.")
        return        
    protocole = tkinter.simpledialog.askstring( "Définir l'unité de mesure d'un protocole.",
                                                "Indiquer le protocole :\n "+
                                                "\nListe des protocoles actuels: \n - "+"\n - "+"\n - ".join(listeDesProtocoles)+"\n",
                                                initialvalue=protocoleParDefaut,
                                                parent=fenetre
                                               )
    if protocole==None: return
    if protocole not in listeDesProtocoles:
        app.encadre(protocole+" n'est pas un protocole connu.")
        return

    # y-a-t-il déjà une métrique  ?
       
    choixMetrique = tkinter.simpledialog.askstring( "Métrique pour le protocole.",
                                                "Quelle est l'unité de mesure pour ce protocole :\n "+
                                                "Les valeurs des x,y et z sont-elles en mètres, en cm ou inconnue\n"+
                                                "Indiquer ci dessous en texte la longueur terrain correspondant à l'unité de mesure utilisée dans le fichier\n"+
                                                "\nPar exemple : 'métre' ou 'cm' ou '50 cm' ou 'inconnue'",
                                                 initialvalue=metrique(protocole),
                                                parent=fenetre
                                               )
    if not choixMetrique: return

    # sauvegarde :
    references = restaureReferences()
    if (protocole,"metrique") in references:        
        references[(protocole,"metrique")]["metrique"] = choixMetrique
    else:
        references[(protocole,"metrique")] = {"metrique":choixMetrique}

    sauveReferences(references)

def metrique(protocole):
    references = restaureReferences()
    if (protocole,"metrique") in references:
        metriqueActuelle = references[(protocole,"metrique")]["metrique"]
    else:
        metriqueActuelle = "inconnue"        
        references[(protocole,"metrique")] = {"metrique":metriqueActuelle}
    return metriqueActuelle

    # Gestion des protocoles : liste
 
def listeProtocoles():
    references = restaureReferences()
    if references==dict():
        return
    return set([a for a,b in references.keys()])
    
########################################### Gestion des résultats de calcul sur PLY : sauve, restaure, ajoute, affiche, supprime

def sauveStatPly(calculPly):
    # le paramètre 'stat' contient le dictionnaire de tous les calculs sur tous les ply
    # clé = chemin complet du fichier ply
    # valeur = dictionnaire provenant de XYZ et stat (stat générales, tortuosité)
    with open(fichierCalculPly, mode="wb") as sauve:
        pickle.dump(calculPly,
                    sauve)

def restaureStatPly():    
    calculPly = dict()
    if not os.path.exists(fichierCalculPly):
        return calculPly
    try:
        with open(fichierCalculPly, mode="rb") as restaure:
            calculPly = pickle.load(restaure)
    except Exception as e:
        app.encadre("erreur restauration des résultats de calcul sur les PLY, création d'un dictionnaire vide : "+str(e))            
    return calculPly

def ajoutStatPly(fichier,stat):  # sauvegarde les résultats de calcul dans le fichier qui va bien
    calculPly = restaureStatPly()
    calculPly[fichier] = stat
    sauveStatPly(calculPly)

def afficheStatPly():
    calculPly = restaureStatPly()   # restaure le tableau des valeurs mémorisées
    if not calculPly:
        app.encadre("Pas de résultat de calculs mémorisés")
        return
    longueurNom = 20    
    tableau = list()
    # création du tableau en mémoire : les valeurs sont arrondies et seules quelques colonnes sont retenues
    # la longueur max des noms de fichier est calculée, la clé est conservée pour tri utltérieur
    for e in calculPly: # le nom du ply est la clé du dico
        nomFichier = os.path.basename(e)
        longueurNom = max(longueurNom,nomFichier.__len__())        
        uneLigne = list()        
        uneLigne.append(nomFichier)
        for i in listeItemsAffiches[1:]:
            if is_number(calculPly[e][i]):
                uneLigne.append(str(round(calculPly[e][i],5)))
        tableau.append(uneLigne)
    # ajout ligne d'entête
    tableau.insert(0,listeItemsAffiches) # pour les titres des colonnes        
    # mise en forme de la ligne du tableau :
    nbItems = listeItemsAffiches.__len__()
    largeursItems = [e.__len__()+2 for e in listeItemsAffiches]
    largeursItems[0] = longueurNom+2 # correction pour longueur du nom de fichier
    formateTableau(tableau,"tableau des statistiques sur les Z\n",largeursItems)

def supprimeCalculs():
    calculPly = restaureStatPly()
    fichierDesCalculs = calculPly.keys()
    aSupprimer = choisirItem(fichierDesCalculs,"Choisir les fichiers dont les calculs seront supprimés",mode="extended").listeChoisie
    if not aSupprimer: return
    [calculPly.pop(k,None) for k in aSupprimer]
    sauveStatPly(calculPly)
    
def choixTri():
    global colonneDeTri
    colonneDeTri = choisirItem(listeItemsAffiches,"Choisir la colonne de tri").retour
    if colonneDeTri:
        colonneDeTri = colonneDeTri[0]
        afficheStatPly()

def changerColonnes():
    choisirColonnesResultats()
    afficheStatPly()
    
########################################### Choix des colonnes affichées dans le tableau des résultats

def choisirColonnesResultats():
    app.menage()    
    global listeItemsAffiches
    stat = restaureStatPly()
    if stat==dict():
        app.encadre("Pas de résultats mémorisés")
        return
    unDico = stat.popitem()[1]
    if not unDico:
        app.encadre("Pas de résultat mémorisé")
        return        
    listeColonnes = list(unDico.keys())    # les colonnes (on ne propose pas de choisir la première car c'est la clé : le nom du fichier)
    listeColonnesResultat = [e for e in unDico if is_number(unDico[e])]
    listeItemsChoisis = choisirItem(listeColonnesResultat[1:],"Choisir les colonnes affichées dans le tableau résultat des calculs"+
                                    "\nliste actuelle : "+str(listeItemsAffiches),mode="extended").listeChoisie
    if listeItemsChoisis:
        app.encadre("Liste précedente : ",listeItemsAffiches)
        listeItemsChoisis.insert(0,listeItemsAffiches[0]) # on ajoute le nom du fichier
        global colonneDeTri     # pour éviter des erreurs si la valeur a été modifiée
        colonneDeTri = 0
        listeItemsAffiches = listeItemsChoisis
    else: return
    sauveParam()
    app.encadre("\nListe nouvelle : ",listeItemsAffiches)

def choisirColonnesParDefaut():
    app.menage()
    global listeItemsAffiches    
    listeItemsAffiches = listeDesItemsParDefaut
    sauveParam()
    app.encadre("\nListe nouvelle : ",listeItemsAffiches)
    

########################################### Modifie la taille de la maille utilisée pour construire le maillage : par défaut une maille = un point du nuage

def modifMaille():
    global nbMaillesParPointDuNuage    
    app.menage()    
    propose = tkinter.simpledialog.askstring(   "nombre de mailles par point",
                                                "Indiquer combien de mailles par point du nuage ? \nValeurs raisonnables entre "+
                                                str(minNbMaillesParPointDuNuage)+" et "+str(maxNbMaillesParPointDuNuage)+
                                                "\nConsulter l'aide pour vous documenter.",
                                                 initialvalue=str(nbMaillesParPointDuNuage),
                                                parent=fenetre
                                               )
    if propose==None: return
    try:
        p=float(propose)
        nbMaillesParPointDuNuage = p        
        if p<=maxNbMaillesParPointDuNuage and p>=minNbMaillesParPointDuNuage:
            message = ("Nouvelle valeur pour le nombre de mailles par point du nuage : "+str(p)+
                      "\n\nsoit :\n\nnombre moyen de points dans une maille : "+str(round(1/nbMaillesParPointDuNuage,2)))
        else: message = ("Nouvelle valeur pour le nombre de mailles par point du nuage : "+str(p)+
                         "\n\nsoit :\n\nnombre moyen de points du nuage dans une maille : "+str(round(1/nbMaillesParPointDuNuage,2))+
                         "\n\nAttention : valeur retenue,\n mais hors des limites raisonnables proposées "+
                         str(minNbMaillesParPointDuNuage)+" et "+str(maxNbMaillesParPointDuNuage))
        sauveParam()
    except: message = "valeur non numérique : "+str(propose)
    app.encadre(message)



########################################### Outil standard : affiche un tableau et l'écrit sur fichier ##############################################

def formateTableau(tableau,titre,largeursColonnes): # tableau est la liste des listes des lignes du tableau
    fonte='courier 10'
    nbItems=tableau[0].__len__()
    if nbItems<1:
        self.encadre("Le tableau demandé est vide : pas de résultats.")
        return
    # tri du tableau si besoin
    tableau = trierTableau(tableau,colonneDeTri)    # colonne de tri variable globale  
    formatLigne = ((nbItems)*"{{:{}}}! ").format(*largeursColonnes)
    app.encadre(titre+"\n",fonte=fonte)
    tableau.insert(1,nbItems*" ")
    [app.encadrePlus(formatLigne.format(*ligne)+"\n",fonte=fonte) for ligne in tableau]
    with open(fichierTableauResultats, 'a',encoding='utf-8') as f:
        f.write("\n------------\n"+nomApplication+version+heure()+"\n")
        f.write(titre+"\n")            
        [f.write(formatLigne.format(*ligne)+"\n") for ligne in tableau]
    app.boutonTriTableau.pack(ipadx=5,ipady=5,padx=10,pady=10)    
    app.boutonChangerColonnes.pack(ipadx=5,ipady=5,padx=10,pady=10) 
    app.boutonAideSynthese.pack(ipadx=5,ipady=5,padx=10,pady=10)
    
def trierTableau(tableau,colonne,lignesEntete=1):
    table = tableau[lignesEntete:]
    tableTri = sorted(table,key=lambda colonnes : colonnes[colonne])
    tableFinale = tableau[:lignesEntete]+tableTri
    return tableFinale

    
########################################### Outil standard : saisir une valeur dans une listbox ##############################################


class choisirItem():

    def __init__(self, listeItems="", titre="Choisir un item",mode="single"): # single ou extended
        self.listeChoisie = list()
        self.retour = list()
        self.choix = list()
        if not listeItems:
            app.encadre("Rien à choisir")
            return
        app.menage()
        self.enveloppe = tkinter.Frame(fenetre,width=750,relief='sunken',container=True)        
        top = self.top = tkinter.Toplevel(width=250,relief='sunken',use=self.enveloppe.winfo_id())
        top.transient(fenetre)        
        app.encadre(titre)
        self.listeItems = list(listeItems)
        self.frame = tkinter.Frame(top)
        self.choix = tkinter.Listbox(self.frame,selectmode=mode,)
        hauteur = min(25,listeItems.__len__())
        largeur = min(100,3+max([e.__len__() for e in listeItems]))
        self.choix.config(width=50,height=hauteur)
        self.frame.pack()
        self.valider = tkinter.Button(self.frame, text = "Valider", command = self.selectionItem)
        self.annuler = tkinter.Button(self.frame, text = "Annuler", command = self.abandon)        
        self.choix.pack(side = "top")
        self.valider.pack()
        self.annuler.pack()
        [self.choix.insert('end',e) for e in listeItems]
        self.choix.select_set(0)
        top.grab_set()
        self.enveloppe.pack()
        fenetre.wait_window(self.enveloppe)
        
    def selectionItem(self):
        self.retour = self.choix.curselection()
        self.listeChoisie = [self.listeItems[e] for e in self.retour]
        if self.listeChoisie:
            self.choix = self.listeChoisie[0]
        self.valider.destroy()
        self.enveloppe.destroy()
        app.menage()

    def abandon(self):
        self.retour = None
        self.enveloppe.destroy()
        app.menage()
    
########################################### INITIALISATIONS METIER ##############################################        

# Constantes personnalisées

version = " V1.8 " # version sans multiprocessing, fichier source compactage7.ply
nomApplication = "Compact Test"
geometrieFenetre = "1000x600+100+100"
iconeTexte = "R0lGODlhIAAgAIcAMfr8+EqrpcfLEe16CJnE1Lnb3Hm7whaXjuzdu+VLEp64HuiRL9TYVfPImeqoU4e1NAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACwAAAAAIAAgAAcI/gABCBxIEACCgwgENliYsKDDhwMVKHjwQOCAiwMgaiwoUaLABRgbboSIYKLEhCAvNhipkUFHBQwAOMC4gOVDBAI6CoiJAOMAkTYFMhCQUwHRjzSDDhxK1CjRmA18OlDKlKjVozKlssR5VQCAqzEBpLy4YGXBgwyqWk2oNmFPnwMWOGjQsOvVhAUCdHU7NoFfvwnt7hSYN4CBvQCi/l0cGGxDAgEiB3jQte/iBGzTiixgQHLkAlxnwh3A2CFnz5EJCB1L0wFQAAViE+iM2nABpD7LPixwoHdvw5INGJhNgPUAs7AJKFfN27dv28tnP6DZsMDs4cphO39+GwBx5TNrcCbHHl1ggOeeVXtfbmABXvLf1Q887bk7+9uc2RPoDhFyfdjkWXefTYVFZoBA7AUwYFAFKgggZAcMZwB/QflnGIKdRbifUgT9x9lv8nHonWTMnXdAABRyWOCBCJiIoogdSiaQczASJJxw5slY444DBQQAOw=="
print("Début de "+nomApplication+" "+heure())


############################### Variables globales métiers

lePas = float()
remplissage = -9999

# methode d'interpolation utilisée 
methode = 'linear'              # alternative : nearest

# paramètres par défaut pour la première utilisation du programme :

# Nombre de mailles pour chaque point du nuage (entre 2  et 20) Par défaut : 5
#il y a perte d'information si le nombre est inférieur à 1
nbMaillesParPointDuNuage = 1    #
minNbMaillesParPointDuNuage = 0.1
maxNbMaillesParPointDuNuage = 10
protocoleParDefaut = "Protocole 1"

#fichier trace : trace l'affichage écran
repertoireData = os.path.join(os.getenv('APPDATA'),'compactage')
try: os.mkdir(repertoireData)
except: pass
fichierTrace = os.path.join(repertoireData,'trace.txt')
fichierTraceSauve = os.path.join(repertoireData,'trace.sav')
fichierParam = os.path.join(repertoireData,'param')    # pour la sauvegarde du nombre de points par maille
fichierReference = os.path.join(repertoireData,'reference.sav') # pour la sauvegarde du dico des references
fichierReferenceSauve = os.path.join(repertoireData,'referenceSauve.sav') # pour la sauvegarde du dico des references
fichierCalculPly = os.path.join(repertoireData,'calculPlySauve.sav') # sauve tous les calculs fait sur les ply
fichierTableauResultats = os.path.join(repertoireData,'tableauResultat.txt') # le tableau des résultats


# liste des colonnes affichés dans le tableau des résultats de calcul
# clés de stat (sur les Z épurés ) : "marges supprimées","nombre","borneMini","borneMaxi","nombreRetenu",
# "moyenne","ecartType","maxi","mini",,"Nombre de classes","histo","classeModale","mode"
# clés de XYZ : "min_x","max_x","min_x","max_x","lePas",nombreDePointsDansLePly,nombreDeMaillesSansValeur,fichierPly,fichierMNT,listeDesZ
# clés créé par tortu : "tortuosites transversales" et "tortuosites longitudinales"

listeItemsAffiches     = ["fichier","nombre","ecartType","kurtosis","etendue","tortuosite moyenne transversale","tortuosite moyenne longitudinale",]
listeDesItemsParDefaut = ["fichier","nombre","ecartType","kurtosis","etendue","tortuosite moyenne transversale","tortuosite moyenne longitudinale",]
colonneDeTri = 0  # colonne de tri du tableau des résultats par défaut

############################### LANCEMENT PROGRAMME ##############################################        

        
if __name__ == "__main__":
    fenetre = tkinter.Tk()   
    app = interface(fenetre)
    app.mainloop()
    fenetre.destroy()
