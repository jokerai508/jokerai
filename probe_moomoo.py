import sys
try:
    import moomoo
    print("moomoo OK", moomoo.__version__)
except Exception as e:
    print("moomoo import error:", e)
    sys.exit(0)
