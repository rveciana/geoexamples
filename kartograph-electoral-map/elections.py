from kartograph import Kartograph
from kartograph.options import read_map_descriptor
import sys
K = Kartograph()
css = open("elections.css").read()
cfg = read_map_descriptor(open("elections.json"))
K.generate(cfg, outfile='elections.svg', format='svg', stylesheet=css)

