# -*- coding: utf-8 -*-"""Inscrire des gens à la formation simdut."""# Bibliothèque standardfrom pathlib import Path# Imports relatifsfrom ...outils.reseau.msforms import MSFormConfig, MSFormfrom ...outils.reseau.courriel import Courrielclass SSTSIMDUTInscriptionConfig(MSFormConfig):    def default(self):        return (Path(__file__).parent / 'inscription.cfg').open().read()class SSTSIMDUTInscriptionForm(MSForm):    def nettoyer(self, cadre):        cadre = self.convertir_champs(cadre)        return cadre.loc[:, ['date', 'Nom', 'Prénom', 'Courriel',                             'Matricule', 'Département', 'Langue',                             'Statut', 'Professeur ou supérieur immédiat']]    def action(self, cadre):        if not cadre.empty():            fichier_temp = Path('nouvelles_entrées.xlsx')            cadre.to_excel(fichier_temp)            message = 'Bonjour! Voici les nouvelles inscriptions à faire pour le SIMDUT. Bonne journée!'            html = f'<p>{message}</p>{cadre.to_html()}'            courriel = Courriel(self.config.get('courriel', 'destinataire'),                                self.config.get('courriel', 'expéditeur'),                                self.config.get('courriel', 'objet'),                                message,                                html,                                pièces_jointes=[fichier_temp])            courriel.envoyer(self.config.get('courriel', 'serveur'))