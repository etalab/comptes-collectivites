#!/bin/bash

# conversion d'une série de fichiers annuels
# exemple: ./ods2json_batch.sh 2016

rm -f $1/*.csv
for D in $(ls -1 $1/ )
do
  echo $D
  ./ods2json.py CSV $D $1/$D/*.ods > $1/$D.csv
done
