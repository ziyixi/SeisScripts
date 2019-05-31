gmt begin geology pdf,eps
    # set some constant
    gmt set FONT_ANNOT_PRIMARY 6p FORMAT_GEO_MAP ddd:mm
    gmt set MAP_FRAME_WIDTH 2p MAP_GRID_PEN_PRIMARY 0.25p,gray,2_2:1
    gmt set FONT_LABEL 6p,20 MAP_LABEL_OFFSET 4p

    gmt grdinfo @earth_relief_03m
    gmt coast -JD125/35/30/40/7.0i -R70/180/0/70 -G244/243/239 -S167/194/223 -Bxafg -Byafg  -Lg85/11+o-0.3c/0.0c+c11+w900k+f+u+l'scale'
    gmt grdimage -JD125/35/30/40/7.0i -R70/180/0/70 @earth_relief_03m -Cglobe

    gmt psxy -Sf-8/0.1c+l+b -Gblack ./data/japan.trench.data
    gmt psxy -Sf-8/0.1c+l+b -Gblack ./data/kuril.trench.data
    gmt psxy -Sf-8/0.1c+l+b -Gblack ./data/bonin.trench.data

    gmt meca  -Sd0.4c/0.05c -Gblack -M ../data/psmeca_japan


# text
    gmt pstext -F+f7p << EOF
148 38 japan
EOF

    gmt pstext -F+f7p << EOF
147 30 Izu Bonin
EOF

    gmt pstext -F+f7p << EOF
150 41 Kuril
EOF

#box
    gmt plot -W1p,black << EOF
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
    gmt makecpt -A0 -Cno_green -T-750/0 > slab.cpt
    # gmt grdimage ./data/kur_slab2_dep_02.24.18.grd -Cslab.cpt -V 
    gmt psxy ./data/japan.slab.contour -W0.7p -Cslab.cpt -V

    gmt colorbar -Cslab.cpt -DjBR+w3c/0.3c+ml+o3.0c/0.0c -Bx150+lDepth -By+lkm  -S

#line
    gmt psxy -W1p,red,-  << EOF
>
110 54
141.91 24.98
EOF


gmt end