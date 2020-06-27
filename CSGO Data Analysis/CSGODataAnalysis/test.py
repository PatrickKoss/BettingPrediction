from datetime import datetime

import requests
import pandas as pd
import os

date = datetime.strptime("1-5-2020", "%d-%m-%Y")
print(datetime.fromtimestamp(1451442397))
print(datetime.timestamp(date))

# r = requests.get("https://api.opendota.com/api/proMatches")
# print(len(r.json()))
