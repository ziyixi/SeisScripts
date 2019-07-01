CPT=seis_extend.cpt

cat << EOF > $CPT
0 blue 20 blue
20 skyblue 40 skyblue
40 green 55 green
55 yellow 70 yellow
70 red 284 red
EOF


gmt begin relocation png,pdf,eps
    gmt set FONT_ANNOT_PRIMARY 6p FORMAT_GEO_MAP ddd:mm
    gmt set MAP_FRAME_WIDTH 2p MAP_GRID_PEN_PRIMARY 0.25p,gray,2_2:1

    gmt set FONT_LABEL 6p,20 MAP_LABEL_OFFSET 4p
    gmt coast -JD125/35/30/40/7.0i -R70/180/0/70 -G244/243/239 -S167/194/223 -Bxafg -Byafg -Lg85/11+o-0.3c/0.0c+c11+w900k+f+u+l'scale'
    gmt psxy -St0.07c -C$CPT ../data/station_contribution

    # echo 145 30 328 3200 | gmt plot -S=0.2i -Wthin,red,..-
    # echo 140 36.4 250 3200 | gmt plot -S=0.2i -Wthin,red,..-
    # echo 140 36.4 70 800 | gmt plot -S=0.2i -Wthin,red,..-
#     gmt plot -Wthin,black,- << EOF
# >
# 145 30
# 120.37 52.39
# >
# 148.63 38.58
# 110.67 22.77
# EOF

    gmt plot -Wthin,magenta << EOF
>
145 30
120.37 52.39
>
148.63 38.56
124.95 30.7
EOF
    
    gmt pstext -F+f10p <<EOF
146.5 28.5 1
150.5 39 2
EOF

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

#     gmt plot -W0.01c,black << EOF
# >
# 141.1 34.2
# 141.9 34.8
# >
# 141.9 34.8
# 138.0 39.8
# >
# 138.0 39.8
# 137.0 39.2
# >
# 137.0 39.2
# 141.1 34.2
# EOF

    gmt plot -W0.01cthin,black << EOF
>
119.4 51.7
122.0 52.9
>
122.0 52.9
135.6 43.3
>
135.6 43.3
133.0 42.1
>
133.0 42.1
119.4 51.7
EOF

    gmt plot -W0.01c,black << EOF
>
140 38.3
143 35.9
>
143 35.9
131 31.5
>
131 31.5
128 34.0
> 
128 34.0
140 38.3
EOF

#     gmt plot -W0.01c,black << EOF
# >
# 123.5 31.1
# 124.5 29.6
# >
# 124.5 29.6
# 110.5 22.1
# > 
# 110.5 22.1
# 109.5 23.4
# >
# 109.5 23.4
# 123.5 31.1
# EOF

    gmt psxy -Sa0.2c -Gblack << EOF
138.1700 31.6100
EOF


gmt end