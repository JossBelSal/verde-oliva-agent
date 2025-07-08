import re
import pandas as pd
from decimal import Decimal
from sqlalchemy.orm import Session
from db.session import SessionLocal

CSV_FILE = "data/servicios.csv"

#================================================
#=============== HELPERS DE LIMPIEZA=============

re_num = re.compile(r"\d+(?:[\.,]\d+)?")

def _to_minutes(raw: str) -> tuple[int,int|None]:
    """
    "1 hora" = 60 min, None
    "1-1.5 hrs" = 60, 90 min
    "6-8 hrs = 360, 480 min
    """
    nums = [float(n.replace(",",".")) for n in re_num.findall(raw)]
    if not nums:
        return (None, None)
    mins = [int(x*60) for x in nums]
    return (mins[0], mins[1] if len(mins)> 1 else None)

