import sys
import requests
from bs4 import BeautifulSoup
import os


dep = sys.argv[1]
comm = ''
s = requests.session()
url = "https://www.impots.gouv.fr/cll/zf1/accueil/flux.ex"
flowKey = None
content_type = 'application/vnd.oasis.opendocument.spreadsheet'


def flow(resp):
    "Récupère et conserve la clé 'flowKey' entre appels"
    global flowKey
    h = BeautifulSoup(resp.text, 'lxml')
    for i in h.find_all('input'):
        if i['name'] == "_flowExecutionKey":
            flowKey = i['value']
    return(resp)


def reset(dep, initiale, comm):
    # page initiale
    flow(s.post(url, {'_flowId': 'accueilcclloc-flow'}))
    # choix du département
    flow(s.post(url,
                {'_flowExecutionKey': flowKey,
                 'nomdufluxencours': 'aucun',
                 'transitiondemandee': '_eventId_validercommunesetgroupts',
                 'critereDeSelection.codiqueDeptCommunesGroupts': dep,
                 '_eventId_validercommunesetgroupts': 'Ok'}))
    if initiale != '':
        flow(s.get(url,
                   params={'_flowExecutionKey': flowKey,
                           '_eventId': 'pagechoixcolllettre',
                           'critereDeSelection.initialeCol': i}))
        if comm != '':
            # sélection de la commune
            flow(s.get(url,
                       params={'_flowExecutionKey': flowKey,
                               '_eventId': 'pagecommunegfpbudget',
                               'critereDeSelection.nomCol': comm}))
            # chiffres clé (non détaillés)
            flow(s.get(url,
                       params={'_flowExecutionKey': flowKey,
                               '_eventId': 'chiffrescles'}))
            # fiche détaillée (HTML)
            flow(s.get(url,
                       params={'_flowExecutionKey': flowKey,
                               '_eventId': 'fichedetaillee'}))


for i in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ' if dep != '75' else 'P':
    reset(dep, '', '')
    print(i)
    # choix de l'initiale des noms de communes (sauf pour Paris)
    if dep == '75':
        communes = ['PARIS']
    else:
        p = flow(s.get(url,
                       params={'_flowExecutionKey': flowKey,
                               '_eventId': 'pagechoixcolllettre',
                               'critereDeSelection.initialeCol': i}))
        h = BeautifulSoup(p.text, 'lxml')
        communes = []
        for t in h.find_all(class_='tableBody'):
            for td in t.find_all('td'):
                communes.append(td['id'])
    for nom_commune in communes:
        for annee in range(2000, 2017):
            path = str(annee)+'/'+dep+'/'+dep+'_'+nom_commune+'.ods'
            # besoin de télécharger le fichier ?
            if not os.path.exists(path):
                # sommes-nous sur la bonne commune ?
                if comm != nom_commune:
                    comm = nom_commune
                    print(dep, comm)
                    # choix de la commune
                    flow(s.get(url,
                               params={'_flowExecutionKey': flowKey,
                                       '_eventId': 'pagecommunegfpbudget',
                                       'critereDeSelection.nomCol': comm}))
                    # chiffres clé (non détaillés)
                    flow(s.get(url,
                               params={'_flowExecutionKey': flowKey,
                                       '_eventId': 'chiffrescles'}))
                    # fiche détaillée (HTML)
                    flow(s.get(url,
                               params={'_flowExecutionKey': flowKey,
                                       '_eventId': 'fichedetaillee'}))

                # sélection de l'année
                flow(s.get(url,
                           params={'_flowExecutionKey': flowKey,
                                   '_eventId': 'changerexercice',
                                   'exerciceSelectionne': annee}))
                # téléchargement de l'export au format .ods
                p2 = s.get(url,
                           params={'_flowExecutionKey': flowKey,
                                   '_eventId': 'exportods'})

                if p2.headers['Content-Type'] == content_type:
                    with open(path, 'wb') as f:
                        for chunk in p2:
                            f.write(chunk)
                else:
                    print('!! ERR', path)
                    flowExecutionKey = reset(dep, i, comm)
        # on revient sur la lettre en cours...
        flow(s.get(url,
                   params={'_flowExecutionKey': flowKey,
                           '_eventId': 'choixalpha'}))
