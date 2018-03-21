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
head -n 1 $ANNEE/$DEBUT.csv > comptes_communes_$DEBUT-$FIN.csv
for ANNEE in `seq $DEBUT $FIN`
do
  head -n 1 $ANNEE/01.csv > $ANNEE.csv
  for F in $ANNEE/*.csv
  do
    tail -n +2 $F >> $ANNEE.csv
    tail -n +2 $F >> comptes_communes_$DEBUT-$FIN.csv
  done
done
