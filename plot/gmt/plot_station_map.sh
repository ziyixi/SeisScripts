CPT=seis_extend.cpt

cat << EOF > $CPT
0 blue 20 blue
20 skyblue 40 skyblue
40 green 55 green
55 yellow 70 yellow
70 red 284 red
EOF


gmt begin stations png,pdf,eps
    gmt set FONT_ANNOT_PRIMARY 6p FORMAT_GEO_MAP ddd:mm
    gmt set MAP_FRAME_WIDTH 2p MAP_GRID_PEN_PRIMARY 0.25p,gray,2_2:1

    gmt set FONT_LABEL 6p,20 MAP_LABEL_OFFSET 4p
    gmt coast -JD125/35/30/40/7.0i -R70/180/0/70 -G244/243/239 -S167/194/223 -Bxafg -Byafg -Lg85/11+o-0.3c/0.0c+c11+w900k+f+u+l'scale'
    gmt psxy -St0.07c -C$CPT ../data/station_contribution

    gmt colorbar -C$CPT -DjBR+w3c/0.2c+ml+o3.0c/0.0c -By+l"event count" -L -S

    gmt plot -W1p,red << EOF
>
91.3320117152011 9.37366242174489
74.6060844556399 61.1396992149365
>
74.6060844556399 61.1396992149365
174.409435753150 48.6744705245903
>
174.409435753150 48.6744705245903
144.284491292185 2.08633373396527
>
144.284491292185 2.08633373396527
91.3320117152011 9.37366242174489
EOF

gmt end