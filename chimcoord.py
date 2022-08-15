import subprocess
from chimerax.core.commands import run
run(session, "cd /Users/psliz05/Dropbox/Mac/Documents/GitHub/pycrest/cmm_files")
run(session, "open /Users/psliz05/Dropbox/Mac/Documents/GitHub/pycrest/Test_Data/Extract/extract_tomo/201810XX_MPI/SV4_003_dff/SV4_003_dff000010_filt.mrc")
run(session, "set bgColor white;volume #1 level 0.5;")
run(session, "color radial #1.1 palette #ff0000:#ff7f7f:#ffffff:#7f7fff:#0000ff center 127.5,127.5,127.5;")
run(session, "ui mousemode right 'mark point'")