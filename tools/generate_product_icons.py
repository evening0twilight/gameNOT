"""Original 32px line pictograms; no font glyphs or third-party assets."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1];out=ROOT/'game/assets/product018/icons';out.mkdir(parents=True,exist_ok=True)
# Shared primitive vocabulary, distinct silhouettes for related operations.
p={
'cross':'M16 7v18M7 16h18','arrow':'M5 16h22m-7-7 7 7-7 7','shield':'M16 4 27 8v9c0 6-6 10-11 12C11 27 5 23 5 17V8Z','bolt':'m19 3-12 16h9l-3 10 12-17h-9Z','eye':'M3 16Q16 1 29 16Q16 31 3 16ZM16 11a5 5 0 1 0 0 10a5 5 0 1 0 0-10','box':'M5 10 16 4l11 6v15l-11 5-11-5ZM5 10l11 6 11-6M16 16v14','gear':'M10 7 7 10l-4 1v9l4 1 3 4 1 4h9l1-4 4-4 4-1v-9l-4-1-4-3-1-4h-9ZM16 11a5 5 0 1 0 0 10a5 5 0 1 0 0-10','person':'M16 4a4 4 0 1 0 0 8a4 4 0 1 0 0-8M8 28v-9q8-10 16 0v9','book':'M3 5q7-2 13 3q6-5 13-3v22q-6-3-13 0q-7-3-13 0ZM16 8v19','wave':'M3 14q4-8 8 0t8 0t10 0M3 24q4-8 8 0t8 0t10 0','clock':'M16 3a13 13 0 1 0 0 26a13 13 0 1 0 0-26M16 7v10l7 4','hand':'M8 16V8q0-4 4-2v9V5q2-3 4 0v10V6q3-2 4 1v9V10q4-1 4 3v12q-8 9-14 0l-5-5q-3-5 3-4Z','signal':'M16 27V15M11 12q5-5 10 0M7 8q9-9 18 0M3 4q13-11 26 0','flag':'M7 29V4q8-4 18 1v13q-10-5-18-1','coins':'M4 10q12-10 24 0q-12 10-24 0ZM4 10v11q12 10 24 0V10','bed':'M3 27V7M3 20h26v7M8 20V10h8v10M16 14h10l3 6','tool':'m6 26 14-14M18 4q-4 2-3 7l6 6q5 1 8-3l-7-2-2-7Z','steps':'M7 6h6v8H7ZM19 18h6v8h-6ZM7 18h6M19 10h6','check':'m5 16 7 8L27 7','return':'M12 5 4 13l8 8M4 13h18q8 0 8 12','speaker':'M3 12h6l8-7v22l-8-7H3ZM22 10q7 6 0 12','pause':'M10 5v22M22 5v22','save':'M5 3h19l5 5v21H3V3ZM9 3v9h13V3M9 29V18h14v11','map':'m3 7 8-4 10 4 8-4v23l-8 4-10-4-8 4ZM11 3v23M21 7v23','link':'M15 8 19 4q8-3 10 5q0 4-8 10M17 24l-4 4q-8 3-10-5q0-4 8-10M10 22 22 10'}
shapes={
'lin_1':('cross','M3 3h6M3 3v6M23 29h6v-6'),'lin_3':('cross','m3 27 7-3-3-4'),
'xu_1':('arrow','M5 24q0-18 12-18'),'xu_3':('arrow','M5 7v18'),
'su_1':('eye','M16 0v5M0 16h5M27 16h5'),'su_3':('signal','m21 26 5-4 3 4'),
'chen_1':('bolt','M3 3 29 29'),'chen_3':('shield','M11 15h10M16 10v10'),
'ye_1':('bolt','M4 3v26M28 3v26'),'ye_3':('wave','M3 4h26'),
'he_1':('shield','M16 8v16'),'he_3':('box','M3 27h7M22 27h7'),
'mo_1':('signal','M11 24h10'),'mo_3':('flag','M3 14H0M29 14h3'),
'jiang_1':('box','m1 16 4-3m22 3 4-3'),'jiang_3':('hand','M24 3v8M20 7h8'),
'crowbar':('tool',''),'medkit':('box','M12 21h8M16 17v8'),'winch':('link',''),'shield':('shield',''),'insulation':('bolt','M3 29h26'),'scanner':('eye',''),'stretcher':('bed','M5 29h22'),'medicine':('cross','M6 3h20v26H6Z'),
'protected_work':('tool','M2 3h8v5'),'mutual_cover':('shield','M10 16h12'),'relay_carry':('hand','M4 3h12'),'coordinated_pull':('link','M2 2h7M23 30h7'),
'infirmary':('cross','M3 29V8l13-6 13 6v21'),'workshop':('gear',''),'rest_area':('bed',''),'communications':('signal',''),
'credits':('coins',''),'supplies':('box',''),'parts':('gear','M13 15h6'),
'move':('steps',''),'attack':('bolt',''),'push':('arrow',''),'stabilize':('cross',''),'pickup':('hand',''),'interact':('tool',''),'drop':('box','M3 31h26'),'extract':('flag',''),'leave_site':('arrow','M26 3v26'),'end_round':('clock',''),'undo':('return',''),'relations':('link',''),'journal':('book','')}
assert len(shapes)==48
for name,(base,extra) in shapes.items():
 (out/(name+'.svg')).write_text('<svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="-2 -2 36 36"><g fill="none" stroke="#91d8c8" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="'+p[base]+'"/>'+('<path d="'+extra+'"/>' if extra else '')+'</g></svg>')
(ROOT/'docs/product018-icons.json').write_text(json.dumps({'method':__doc__,'icons':list(shapes)},indent=2)+'\n')
