

import importlib

MODEL_NAME="simplified_hanim"

mod = importlib.import_module( MODEL_NAME )

with open("simplified_hanim.roundtrip.x3d", "w") as outp:
    outp.write( mod.newModel.XML())
