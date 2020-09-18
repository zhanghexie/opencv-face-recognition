from FaceGui import Face_App
from Manage import Manage
import time
import threading
g = Manage()
f = Face_App()
run = False
if f.run_manage:
    print('\n'*10)
    run = True
del f
if run:
    g.run()

