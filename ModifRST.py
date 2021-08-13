# -*- coding: utf-8 -*-
"""
Created on Wed Aug  4 16:33:27 2021

@author: Alban Van Laethem
"""

import os, glob
import zipfile

# Supprime les anciens fichiers finaux
for root, dirs, files in os.walk('Final/'):
    for dir in dirs :
        if dir != 'Images':
            for file in files:
                os.remove(os.path.join(root, file))

# Unzip des fichiers originaux provenant de Jupyter
for filePath in glob.glob('Original/*.zip'):
    pathname, extension = os.path.splitext(filePath)
    with zipfile.ZipFile(filePath, 'r') as zip_ref:
        fileName = pathname.split('\\')
        destPath = './Final/'+fileName[-1]+'/'
        zip_ref.extractall(destPath)

# Modifie les fichiers originaux pour être bon pour Sphinx
for filePath in glob.glob('Final/*/*.rst'):
    fileName = os.path.basename(filePath)
    
    # Lecture du fichier initial
    fichier = open(filePath,'r')
    lignes = fichier.readlines()
    
    # Supprimer les morceaux de codes inutiles s'il y en a
    for index, ligne in enumerate(lignes, start=0):
        if "from IPython.display import HTML" in ligne:
            del lignes[0:52]
            del lignes[-14:-1]
            break
            
        elif index == 10:
            break
        
    for index, ligne in enumerate(lignes, start=0):
        
        # Pour cacher les blocs de codes
        if ".. code::" in ligne:
            ligne = ligne.replace("code", "hidden-code-block")
            lignes[index] = ligne
            lignes.insert(index+1, '   :starthidden: True\n')
            
        # Pour gérer les images ajoutées
        elif ".. figure::" in ligne:
            ligne = ligne.replace("attachment:", "Images/")
            ligne = ligne.replace("figure", "image")
            lignes[index] = ligne
            del lignes[index+3:index+4]
            lignes.insert(index+1, '   :align: center\n')
            
        # Pour centrer les images générées
        elif ".. image::" in ligne:
            lignes.insert(index+1, '   :align: center\n')
        
        # Pour afficher les avertissements comme il faut
        elif """<div class="alert alert-block alert-danger">""" in ligne:
            lignes[index] = ".. warning::\n"
            del lignes[index+1]
            i = 1
            while lignes[index+i] != '\n':
                lignes[index+i] = '   ' + lignes[index+i]
                i += 1
            del lignes[index+i+1:index+i+4]
            del lignes[index-2:index-1]
            
        
    fichier.close()
    
    # Ecriture du fichier modifié
    #fichier = open("Modified/"+fileName,'w')
    fichier = open(filePath,'w')
    fichier.writelines(lignes)
    fichier.close()

    print("File modified: " + filePath)