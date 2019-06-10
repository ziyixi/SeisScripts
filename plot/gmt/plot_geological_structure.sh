gmt begin geology pdf,eps
    # set some constant
    gmt set FONT_ANNOT_PRIMARY 6p FORMAT_GEO_MAP ddd:mm
    gmt set MAP_FRAME_WIDTH 2p MAP_GRID_PEN_PRIMARY 0.25p,gray,2_2:1
    gmt set FONT_LABEL 6p,20 MAP_LABEL_OFFSET 4p

    gmt grdinfo @earth_relief_03m
    gmt coast -JD125/35/30/40/7.0i -R70/180/0/70 -G244/243/239 -S167/194/223 -Bxafg -Byafg  -Lg85/11+o-0.3c/0.0c+c11+w900k+f+u+l'scale'
    gmt grdimage -JD125/35/30/40/7.0i -R70/180/0/70 @earth_relief_03m -Cland_china.cpt

    # gmt psxy -Sf-8/0.1c+l+b -Gblack ./data/japan.trench.data
    # gmt psxy -Sf-8/0.1c+l+b -Gblack ./data/kuril.trench.data
    # gmt psxy -Sf-8/0.1c+l+b -Gblack ./data/bonin.trench.data



# # text
#     gmt pstext -F+f7p << EOF
# 148 38 japan
# EOF

#     gmt pstext -F+f7p << EOF
# 147 30 Izu Bonin
# EOF

#     gmt pstext -F+f7p << EOF
# 150 41 Kuril
# EOF

#box
#     gmt plot -W1p,black << EOF
# >
# 91.3320117152011 9.37366242174489
# 74.6060844556399 61.1396992149365
# >
# 74.6060844556399 61.1396992149365
# 174.409435753150 48.6744705245903
# >
# 174.409435753150 48.6744705245903
# 144.284491292185 2.08633373396527
# >
# 144.284491292185 2.08633373396527
# 91.3320117152011 9.37366242174489
# EOF
    gmt makecpt -A0 -Cgray -T-750/0 > slab.cpt
    # gmt grdimage ./data/kur_slab2_dep_02.24.18.grd -Cslab.cpt -V 
    gmt psxy ./data/japan.slab.contour -W0.7p -Cslab.cpt -V

    gmt colorbar -Cslab.cpt -DjBR+w3c/0.1c+ml+o3.0c/0.0c -Bx150+l"Slab Contour Depth" -By+lkm  -S
    # gmt colorbar -D-0.5/-0.1/4.3/0.1h -B+l"Topography (m)": -Cland_china.cpt -X10.75

# #line
#     gmt psxy -W1p,red,-  << EOF
# >
# 110 54
# 141.91 24.98
# EOF

    echo 145 30 328 3200 | gmt plot -S=0.2i -W1.5p,magenta
    echo 140 36.4 250 3200 | gmt plot -S=0.2i -W1.5p,magenta
    echo 140 36.4 70 800 | gmt plot -S=0.2i -W1.5p,magenta

    # plate boundaries
    gmt psxy -W1p,255/0/0 /Users/ziyixi/Projects/SeisScripts/plot/gmt/figures/Plate_Boundaries/nuvel1_boundaries

    # beach ball
    # gmt meca  -Sd0.2c/0.05c -Gblack -M ../data/psmeca_japan

    # other parts
    set volcano = "/Users/ziyixi/Projects/SeisScripts/plot/gmt/figures/plots/Volcanoes/ChinaVolcano.xy"
    set block2 = "/Users/ziyixi/Projects/SeisScripts/plot/gmt/figures/plots/China_blocks/block2d_mod.txt"
    set block3 = "/Users/ziyixi/Projects/SeisScripts/plot/gmt/figures/plots/China_blocks/China_Basins"
    echo 1
    gmt psxy -W0.5p /Users/ziyixi/Projects/SeisScripts/plot/gmt/figures/plots/China_blocks/block2d_mod.txt
    echo 2
    gmt psxy -W0.5p /Users/ziyixi/Projects/SeisScripts/plot/gmt/figures/plots/China_blocks/China_Basins
    echo 3
    cat /Users/ziyixi/Projects/SeisScripts/plot/gmt/figures/plots/Volcanoes/ChinaVolcano.xy | awk '{print $3,$2}' | gmt psxy -Wthin -St0.15 -G255/0/0
    echo 4
    # gmt colorbar -D-0.5/-0.1/4.3/0.1h -B+l"Topography (m)": -Cland_china.cpt -X2.75
    gmt colorbar -Cland_china.cpt -DjBR+w3c/0.1c+ml+o4.5c/0.0c -Bx1000+l"Topography" -By+lm  -S


gmt end