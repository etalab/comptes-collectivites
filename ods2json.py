#!/usr/bin/env python3
import sys
import subprocess
import re
import json
import sqlite3
from lxml import etree
import os

""" Conversion de fichiers ODS des comptes des communes provenant de la DGFiP
    en fichier JSON ou CSV """


def ods2matrix(filename):
    # conversion d'un fichier .ods (xml zippé) en tableau 2D
    matrix = [['' for c in range(20)] for r in range(100)]
    tempdir = '/dev/shm/ods2json'+str(os.getpid())
    os.mkdir(tempdir)
    subprocess.call('unzip -qod "%s" "%s"' % (tempdir, filename), shell=True)
    with open(tempdir+'/content.xml', 'rb') as ods:
        tree = etree.XML(ods.read())
        row = 0
        body = tree.find('{%s}body' % tree.nsmap['office'])
        for r in body.iter('{%s}table-row' % tree.nsmap['table']):
            cell = 0
            for c in r.iter('{%s}table-cell' % tree.nsmap['table']):
                for e in c.iter():
                    if e.tag == ('{%s}span' % tree.nsmap['text']):
                        matrix[row][cell] = e.text.replace('\xa0', '')
                cell = cell + 1
            row = row + 1
    subprocess.call('rm -rf "%s"' % tempdir, shell=True)
    return matrix


# format de sortie
output = sys.argv[1]
if output != 'JSON':
    print("annee,dep,depcom,commune,population,produits_total,prod_impots_locaux,prod_autres_impots_taxes,prod_dotation,charges_total,charges_personnel,charges_achats,charges_financieres,charges_contingents,charges_subventions,resultat_compatble,invest_ressources_total,invest_ress_emprunts,invest_ress_subventions,invest_ress_fctva,invest_ress_retours,invest_emplois_total,invest_empl_equipements,invest_empl_remboursement_emprunts,invest_empl_charges,invest_empl_immobilisations,excedent_brut,cap_autofinancement,cap_autofinancement_nette,dette_encours_total,dette_encours_bancaire,avance_tresor,dette_annuite,fond_de_roulement,taxe_habitation,taxe_habitation_base,taxe_foncier_bati,taxe_foncier_bati_base,taxe_non_bati,taxe_non_bati_base,taxe_add_non_bati,taxe_add_non_bati_base,cotis_fonciere_entreprises,cotis_fonciere_entreprises_base,cotisation_valeur_ajoutee_entreprises,impot_forfait_entreprise_reseau,taxe_surf_commerciales,compensation_relais_2010,taxe_professionnelle,taxe_professionnelle_base")   # noqa

# code INSEE Département
dep = sys.argv[2]
# base sqlite pour retrouver le code INSEE des communes
db = sqlite3.connect('cog_histo.db').cursor()

for ods_f in sys.argv[3:]:
    t = ods2matrix(ods_f)
    population = t[2][1].replace("Population légale en vigueur au 1er janvier de l'exercice : ", "")  # noqa
    population = re.sub(r' habitant.*$', '', population)
    annee = t[4][1][-4:]
    commune = re.sub(r' - .*$', '', t[1][1])
    comm = re.sub(r' \(commune nouvelle.*$', '', commune).replace('Ç', 'C')
    cog = db.execute("SELECT insee FROM cog_histo WHERE nom = ? AND insee like ?",
                     (comm, dep+'%')).fetchone()
    try:
        insee = cog[0]
    except:
        insee = None
        #sys.stderr.write(commune)
        pass

    j = {}
    r = []
    if annee == '2016' and t[71][1] == 'Source DGFIP':
        j = {   'annee': int(annee),
                'insee': insee,
                'commune': commune,
                'dep': dep,
                'population': int(population),
                'produits_total': int(t[9][1]),
                'produits': {
                    'impots_locaux': int(t[10][1]),
                    'autres_impots_taxes': int(t[11][1]),
                    'dotation': int(t[12][1]),
                },
                'charges_total': int(t[13][1]),
                'charges': {
                    'personnel': int(t[14][1]),
                    'achats': int(t[15][1]),
                    'financieres': int(t[16][1]),
                    'contingents': int(t[17][1]),
                    'subventions': int(t[18][1]),
                },
                'resultat_comptable': int(t[19][1]),
                'invest_ressources_total': int(t[21][1]),
                'invest_ressources': {
                    'emprunts': int(t[22][1]),
                    'subventions': int(t[23][1]),
                    'fctva': int(t[24][1]),
                    'retours': int(t[25][1]),

                },
                'invest_emplois_total': int(t[26][1]),
                'invest_emplois': {
                    'depenses_equipement': int(t[27][1]),
                    'remboursement_emprunts': int(t[28][1]),
                    'charges_a_repartir': int(t[29][1]),
                    'immobilisations': int(t[30][1]),
                },
                'excedent_brut': int(t[37][1]),
                'capacite_autofinancement': int(t[38][1]),
                'capacite_autofinance_nette': int(t[39][1]),
                'dette': {
                    'encours_total': int(t[41][1]),
                    'encours_bancaire': int(t[42][1]),
                    'annuite': int(t[43][1])
                },
                'fond_de_roulement': int(t[45][1]),
                'fiscalite': {
                    'taxe_habitation': int(t[61][1]),
                    'taxe_habitation_base': int(t[52][1]),
                    'taxe_fonciere_bati': int(t[62][1]),
                    'taxe_fonciere_bati_base': int(t[54][1]),
                    'taxe_fonciere_non_bati': int(t[63][1]),
                    'taxe_fonciere_non_bati_base': int(t[56][1]),
                    'taxe_additionnelle_foncier_non_bati': int(t[64][1]),
                    'taxe_additionnelle_foncier_non_bati_base': int(t[57][1]),
                    'cotisation_fonciere_entreprises': int(t[65][1]),
                    'cotisation_fonciere_entreprises_base': int(t[58][1]),
                    'cotisation_valeur_ajoutee_entreprises': int(t[68][1]),
                    'impot_forfait_entreprise_de_reseau': int(t[69][1]),
                    'taxe_surfaces_commerciales': int(t[70][1]),
                }
            }

        r = [annee, '"'+dep+'"', '"'+insee+'"' if insee is not None else '',
             commune, population,
             t[9][1],  # produit_total
             t[10][1], t[11][1], t[12][1],
             t[13][1],  # charges total
             t[14][1], t[15][1], t[16][1], t[17][1], t[18][1],
             t[19][1],  # resultat
             t[21][1],  # invest_ressources
             t[22][1], t[23][1], t[24][1], t[25][1],
             t[26][1], # invest emploi total
             t[27][1], t[28][1], t[29][1], t[30][1],
             t[37][1],  # excédent
             t[38][1], t[39][1], t[41][1], t[42][1],
             '',
             t[43][1],  # annuité dette
             t[45][1],
             t[61][1], t[52][1],
             t[62][1], t[54][1],
             t[63][1], t[56][1],
             t[64][1], t[57][1],
             t[65][1], t[58][1],
             t[68][1],
             t[69][1],
             t[70][1],'','','']
    elif (annee in ['2015', '2014', '2013', '2012', '2011'] and
          t[70][1] == 'Source DGFIP'):
        j = {   'annee': int(annee),
                'insee': insee,
                'commune': re.sub(' - .*$', '', t[1][1]),
                'dep': dep,
                'population': int(population),
                'produits_total': int(t[9][1]),
                'produits': {
                    'impots_locaux': int(t[10][1]),
                    'autres_impots_taxes': int(t[11][1]),
                    'dotation': int(t[12][1]),
                },
                'charges_total': int(t[13][1]),
                'charges': {
                    'personnel': int(t[14][1]),
                    'achats': int(t[15][1]),
                    'financieres': int(t[16][1]),
                    'contingents': int(t[17][1]),
                    'subventions': int(t[18][1]),
                },
                'resultat_comptable': int(t[19][1]),
                'invest_ressources_total': int(t[21][1]),
                'invest_ressources': {
                    'emprunts': int(t[22][1]),
                    'subventions': int(t[23][1]),
                    'fctva': int(t[24][1]),
                    'retours': int(t[25][1]),

                },
                'invest_emplois_total': int(t[26][1]),
                'invest_emplois': {
                    'depenses_equipement': int(t[27][1]),
                    'remboursement_emprunts': int(t[28][1]),
                    'charges_a_repartir': int(t[29][1]),
                    'immobilisations': int(t[30][1]),
                },
                'excedent_brut': int(t[37][1]),
                'capacite_autofinancement': int(t[38][1]),
                'capacite_autofinance_nette': int(t[39][1]),
                'dette': {
                    'encours_total': int(t[41][1]),
                    'annuite': int(t[42][1])
                },
                'fond_de_roulement': int(t[44][1]),
                'fiscalite': {
                    'taxe_habitation': int(t[60][1]),
                    'taxe_habitation_base': int(t[51][1]),
                    'taxe_fonciere_bati': int(t[61][1]),
                    'taxe_fonciere_bati_base': int(t[53][1]),
                    'taxe_fonciere_non_bati': int(t[62][1]),
                    'taxe_fonciere_non_bati_base': int(t[55][1]),
                    'taxe_additionnelle_foncier_non_bati': int(t[63][1]),
                    'taxe_additionnelle_foncier_non_bati_base': int(t[56][1]),
                    'cotisation_fonciere_entreprises': int(t[64][1]),
                    'cotisation_fonciere_entreprises_base': int(t[57][1]),
                    'cotisation_valeur_ajoutee_entreprises': int(t[67][1]),
                    'impot_forfait_entreprise_de_reseau': int(t[68][1]),
                    'taxe_surfaces_commerciales': int(t[69][1]),
                }
            }

        r = [annee, '"'+dep+'"', '"'+insee+'"' if insee is not None else '',
             commune, population,
             t[9][1],  # produit_total
             t[10][1], t[11][1], t[12][1],
             t[13][1],  # charges total
             t[14][1], t[15][1], t[16][1], t[17][1], t[18][1],
             t[19][1],  # resultat
             t[21][1],  # invest_ressources
             t[22][1], t[23][1], t[24][1], t[25][1],
             t[26][1], # invest emploi total
             t[27][1], t[28][1], t[29][1], t[30][1],
             t[37][1],  # excédent
             t[38][1], t[39][1], t[41][1], '',
             '',
             t[42][1],  # annuité dette
             t[44][1],
             t[60][1], t[51][1],
             t[61][1], t[53][1],
             t[62][1], t[55][1],
             t[63][1], t[56][1],
             t[64][1], t[57][1],
             t[67][1],
             t[68][1],
             t[69][1],'','','']
    elif (annee in ['2010'] and
          t[65][1] == 'Source DGFIP'):
        j = {   'annee': int(annee),
                'insee': insee,
                'commune': re.sub(' - .*$', '', t[1][1]),
                'dep': dep,
                'population': int(population),
                'produits_total': int(t[9][1]),
                'produits': {
                    'impots_locaux': int(t[10][1]),
                    'autres_impots_taxes': int(t[11][1]),
                    'dotation': int(t[12][1])
                },
                'charges_total': int(t[13][1]),
                'charges': {
                    'personnel': int(t[14][1]),
                    'achats': int(t[15][1]),
                    'financieres': int(t[16][1]),
                    'contingents': int(t[17][1]),
                    'subventions': int(t[18][1])
                },
                'resultat_comptable': int(t[19][1]),
                'invest_ressources_total': int(t[21][1]),
                'invest_ressources': {
                    'emprunts': int(t[22][1]),
                    'subventions': int(t[23][1]),
                    'fctva': int(t[24][1]),
                    'retours': int(t[25][1])
                },
                'invest_emplois_total': int(t[26][1]),
                'invest_emplois': {
                    'depenses_equipement': int(t[27][1]),
                    'remboursement_emprunts': int(t[28][1]),
                    'charges_a_repartir': int(t[29][1]),
                    'immobilisations': int(t[30][1])
                },
                'excedent_brut': int(t[37][1]),
                'capacite_autofinancement': int(t[38][1]),
                'capacite_autofinance_nette': int(t[39][1]),
                'dette': {
                    'encours_total': int(t[41][1]),
                    'annuite': int(t[42][1])
                },
                'fond_de_roulement': int(t[44][1]),
                'fiscalite': {
                    'taxe_habitation': int(t[59][1]),
                    'taxe_habitation_base': int(t[51][1]),
                    'taxe_fonciere_bati': int(t[60][1]),
                    'taxe_fonciere_bati_base': int(t[53][1]),
                    'taxe_fonciere_non_bati': int(t[61][1]),
                    'taxe_fonciere_non_bati_base': int(t[55][1]),
                    'compensation_relais_2010': int(t[62][1]),
                    'cotisation_fonciere_entreprises': int(t[63][1]),
                    'cotisation_fonciere_entreprises_base': int(t[56][1]),
                }
            }
        r = [annee, '"'+dep+'"', '"'+insee+'"' if insee is not None else '',
             commune, population,
             t[9][1],  # produit_total
             t[10][1], t[11][1], t[12][1],
             t[13][1],  # charges total
             t[14][1], t[15][1], t[16][1], t[17][1], t[18][1],
             t[19][1],  # resultat
             t[21][1],  # invest_ressources
             t[22][1], t[23][1], t[24][1], t[25][1],
             t[26][1], # invest emploi total
             t[27][1], t[28][1], t[29][1], t[30][1],
             t[37][1],  # excédent
             t[38][1], t[39][1], t[41][1], '',
             '',
             t[42][1],  # annuité dette
             t[44][1],
             t[59][1], t[51][1],
             t[60][1], t[53][1],
             t[61][1], t[55][1],
             t[63][1], t[56][1],
             '', '',
             t[67][1],
             t[68][1],
             t[69][1],
             t[62][1],'','']

    elif (annee in ['2009'] and
          t[69][1] == 'Source DGFIP'):
        j = {   'annee': int(annee),
                'insee': insee,
                'commune': re.sub(' - .*$', '', t[1][1]),
                'dep': dep,
                'population': int(population),
                'produits_total': int(t[9][1]),
                'produits': {
                    'impots_locaux': int(t[10][1]),
                    'autres_impots_taxes': int(t[11][1]),
                    'dotation': int(t[12][1])
                },
                'charges_total': int(t[13][1]),
                'charges': {
                    'personnel': int(t[14][1]),
                    'achats': int(t[15][1]),
                    'financieres': int(t[16][1]),
                    'contingents': int(t[17][1]),
                    'subventions': int(t[18][1])
                },
                'resultat_comptable': int(t[19][1]),
                'invest_ressources_total': int(t[21][1]),
                'invest_ressources': {
                    'emprunts': int(t[22][1]),
                    'subventions': int(t[23][1]),
                    'fctva': int(t[24][1]),
                    'retours': int(t[25][1])
                },
                'invest_emplois_total': int(t[26][1]),
                'invest_emplois': {
                    'depenses_equipement': int(t[27][1]),
                    'remboursement_emprunts': int(t[28][1]),
                    'charges_a_repartir': int(t[29][1]),
                    'immobilisations': int(t[30][1])
                },
                'excedent_brut': int(t[37][1]),
                'capacite_autofinancement': int(t[38][1]),
                'capacite_autofinance_nette': int(t[39][1]),
                'dette': {
                    'encours_total': int(t[41][1]),
                    'annuite': int(t[42][1]),
                    'avance_tresor': int(t[43][1])
                },
                'fond_de_roulement': int(t[45][1]),
                'fiscalite': {
                    'taxe_habitation': int(t[60][1]),
                    'taxe_habitation_base': int(t[52][1]),
                    'taxe_fonciere_bati': int(t[62][1]),
                    'taxe_fonciere_bati_base': int(t[54][1]),
                    'taxe_fonciere_non_bati': int(t[64][1]),
                    'taxe_fonciere_non_bati_base': int(t[56][1]),
                    'taxe_professionnelle': int(t[66][1]),
                    'taxe_professionnelle_base': int(t[57][1]),
                }
            }
        r = [annee, '"'+dep+'"', '"'+insee+'"' if insee is not None else '',
             commune, population,
             t[9][1],  # produit_total
             t[10][1], t[11][1], t[12][1],
             t[13][1],  # charges total
             t[14][1], t[15][1], t[16][1], t[17][1], t[18][1],
             t[19][1],  # resultat
             t[21][1],  # invest_ressources
             t[22][1], t[23][1], t[24][1], t[25][1],
             t[26][1], # invest emploi total
             t[27][1], t[28][1], t[29][1], t[30][1],
             t[37][1],  # excédent
             t[38][1], t[39][1], t[41][1], '',
             t[42][1],  # annuité dette
             t[43][1],  # avance tresor
             t[45][1],
             t[60][1], t[52][1],
             t[62][1], t[54][1],
             t[64][1], t[56][1],
             '', '',
             '', '',
             '',
             '',
             '',
             '',
             t[66][1], t[57][1]  ## taxe pro
             ]

    elif (int(annee) < 2009 and t[53][1] == 'Source DGFIP'):
        j = {   'annee': int(annee),
                'insee': insee,
                'commune': re.sub(' - .*$', '', t[1][1]),
                'dep': dep,
                'population': int(population),
                'produits_total': int(t[9][1]),
                'produits': {
                    'impots_locaux': int(t[10][1]),
                    'autres_impots_taxes': int(t[11][1]),
                    'dotation': int(t[12][1])
                },
                'charges_total': int(t[13][1]),
                'charges': {
                    'personnel': int(t[14][1]),
                    'achats': int(t[15][1]),
                    'financieres': int(t[16][1]),
                    'contingents': int(t[17][1]),
                    'subventions': int(t[18][1])
                },
                'resultat_comptable': int(t[19][1]),
                'fiscalite': {
                    'taxe_habitation': int(t[22][1]),
                    'taxe_fonciere_bati': int(t[23][1]),
                    'taxe_fonciere_non_bati': int(t[24][1]),
                    'taxe_professionnelle': int(t[25][1]),
                },
                'invest_ressources_total': int(t[27][1]),
                'invest_ressources': {
                    'emprunts': int(t[28][1]),
                    'subventions': int(t[29][1]),
                    'fctva': int(t[30][1]),
                    'retours': int(t[31][1])
                },
                'invest_emplois_total': int(t[32][1]),
                'invest_emplois': {
                    'depenses_equipement': int(t[33][1]),
                    'remboursement_emprunts': int(t[34][1]),
                    'charges_a_repartir': int(t[35][1]),
                    'immobilisations': int(t[36][1])
                },
                'excedent_brut': int(t[43][1]),
                'capacite_autofinancement': int(t[44][1]),
                'capacite_autofinance_nette': int(t[45][1]),
                'dette': {
                    'encours_total': int(t[47][1]),
                    'annuite': int(t[48][1]),
                    'avance_tresor': int(t[49][1])
                },
                'fond_de_roulement': int(t[51][1]),
            }
        r = [annee, '"'+dep+'"', '"'+insee+'"' if insee is not None else '',
             commune, population,
             t[9][1],  # produit_total
             t[10][1], t[11][1], t[12][1],
             t[13][1],  # charges total
             t[14][1], t[15][1], t[16][1], t[17][1], t[18][1],
             t[19][1],  # resultat
             t[27][1],  # invest_ressources
             t[28][1], t[29][1], t[30][1], t[31][1],
             t[32][1], # invest emploi total
             t[33][1], t[34][1], t[35][1], t[36][1],
             t[43][1],  # excédent
             t[44][1], t[45][1], t[47][1], '',
             t[48][1],  # annuité dette
             t[49][1],  # avance tresor
             t[51][1],
             t[22][1], '',
             t[23][1], '',
             t[24][1], '',
             '', '',
             '', '',
             '',
             '',
             '',
             '',
             t[25][1], ''  ## taxe pro
             ]

    if output == 'json':
        print(json.dumps(j, sort_keys=True))
    else:
        print(",".join(r))
