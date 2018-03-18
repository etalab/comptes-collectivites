#!/bin/bash
DEBUT=2000
FIN=2016

echo "Téléchargement des fichiers ODS"
for DEP in `seq -w 01 19` 2A 2B `seq 21 95` `seq 971 974` 976
do
  # création des dossiers pour ranger les fichiers
  for ANNEE in `seq $DEBUT $FIN`; do mkdir -p $ANNEE/$DEP; done
  ./download.py $DEP
done

echo "Conversion parallelisée des ODS en CSV"
seq $DEBUT $FIN | parallel ./ods2json_batch.sh :::

echo "Cumul fichier $DEBUT-$FIN"
csvstack 20*.csv > temp.csv
csvsort -c dep,commune,annee temp.csv > comptes_communes_$DEBUT-$FIN.csv
rm temp.csv
