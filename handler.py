import os
import requests
import sqlite3
import random
from bs4 import BeautifulSoup
import re
from time import time

import warnings
warnings.filterwarnings("ignore")

# Step 1: Fetch the main page of Summer Olympics Wikipedia
url = "https://en.wikipedia.org/wiki/Summer_Olympic_Games"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"}
response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.text, "html.parser")

# Step 2: Create SQLite database and table
conn = sqlite3.connect("OlympicsData.db")
cursor = conn.cursor()
cursor.execute("""
    CREATE TABLE IF NOT EXISTS SummerOlympics (
        Name TEXT,
        WikipediaURL TEXT,
        Year INTEGER,
        HostCity TEXT,
        ParticipatingNations TEXT,
        Athletes INTEGER,
        Sports TEXT,
        Rank_1_nation TEXT,
        Rank_2_nation TEXT,
        Rank_3_nation TEXT,
        DONE_OR_NOT_DONE INTEGER DEFAULT 0
    )
""")
conn.commit()

# Step 3: Parse the HTML and extract URLs for 2 random Olympics from 1968 to 2020
olympic_years = list(range(1968, 2021, 4))
selected_years = random.sample(olympic_years, 10)
print("Years chosen:", selected_years)
olympic_urls = []

table = soup.find("table", {"class": "sortable wikitable"})
rows = table.find_all("tr")[1:]  # Skip the header row
#print(rows)

for row in rows:
    columns = row.find_all("td")
    if len(columns) >= 1:
        year_text = columns[0].text.strip()
        year_tex= year_text[0:4]
        #print(year_tex)
        link="https://en.wikipedia.org/wiki/" +  year_tex + "_Summer_Olympics"
        #olympic_urls.append(link)
        year=int(year_tex)
        if year in selected_years:
            olympic_urls.append(link)
            cursor.execute("""
                INSERT INTO SummerOlympics (WikipediaURL)
                VALUES (?)
            """, (link,))
            conn.commit()
            
query = "SELECT * from SummerOlympics"
result = cursor.execute(query)
print("\nThe Database contains:\n")
for row in result:
    print(row)
cursor.close()    
#Close the database connection
conn.close()

print("Entering Parallel Processing...")   
global start
start=time()
global end
# Spawn three processes to run handler.py concurrently 
for _ in range(3):
    os.system("python3 scrapper.py &")
    # os.system("start /b python3 scrapper.py")
end=time()

diff_parallel=end-start    
os.system("python3 checker.py")

print("Entering Normal Processing...")   
start=time()
os.system("python3 23CS60R78_assgn_6_2.py")
end=time()
diff_normal=end-start 
speedup=((diff_normal-diff_parallel)/diff_normal)*100
with open("23CS60R78_Assgn_6_3.txt", "w") as file:
    file.write("Speedup for parallel processes: "+ str(speedup))
