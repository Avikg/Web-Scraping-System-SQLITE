import requests
import sqlite3
import random
from bs4 import BeautifulSoup
import re

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
        Rank_3_nation TEXT
    )
""")
conn.commit()

# Step 3: Parse the HTML and extract URLs for 2 random Olympics from 1968 to 2020
olympic_years = list(range(1968, 2021, 4))
selected_years = random.sample(olympic_years, 10)
print("Years chosen:", selected_years)
olympic_urls = []
cnt=0

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
        #         link = columns[2].find("a", href=True)
        #         print(olympic_urls)   

#print(olympic_urls)


# Step 4: Extract and insert data into the database
for url in olympic_urls:
    response = requests.get(url, headers=headers)
    olympic_soup = BeautifulSoup(response.text, "html.parser")
    
    name = olympic_soup.find("h1", {"class": "firstHeading"}).text.strip()
    # print("\nName: "+name)
    # print("\nURL:"+url)
    year = int(name.split()[0])
    # print("\nYear: "+str(year))
    host_city_data =olympic_soup.find("th", text="Host city").find_next("td").text.strip().replace(",", "")
    host_city_list = [city.strip() for city in host_city_data.split(',')]
    host_city=host_city_data
    # print("\nHost City: "+host_city)
    table_part=olympic_soup.find("table", {"class": "infobox"})
    
    # Navigate to the table
    participating_nations_table = olympic_soup.find("table", {"class": "wikitable collapsible"})
    # Initialize an empty list to store the participating nations
    participating_nations = []
    rows_part= participating_nations_table.find_all("tr")[1:][0].find_all("td")[0].find_all("ul")[0].find_all("li")
    # print(rows_part)
    for row in rows_part:
        country = row.find_all("a")[0].string
        cnt+=1
        participating_nations.append(country)
    participating_nations_string = ','.join(participating_nations)
    # print("\nParticipating Nations: "+participating_nations_string)
    
    athletes = olympic_soup.find("th", text="Athletes").find_next("td").text.strip().replace(",", "")
    #Split the string by '(' and take the first part
    parts = athletes.split('(')
    numeric_string = parts[0]

    # Remove commas and other non-numeric characters
    numeric_string = ''.join(filter(str.isdigit, numeric_string))

    # Convert the numeric string to an integer
    athletes_integer = int(numeric_string)
    
    # print("\nNo of Athletes: "+str(athletes_integer))
    
    sports_table = olympic_soup.find_all("table", {"class": "wikitable"})[1]
    # Initialize an empty list to store the sports
    sports_list = []

    # Iterate through the rows in the table and extract the sport names
    for row in sports_table.find_all("tr"):
        # Find the cell containing the sport name (usually in the first column)
        cell = row.find("td")
        if cell:
            sport_name = cell.get_text(strip=True)
            sports_list.append(sport_name)
    sports_list_string = ','.join(sports_list)      
    # Remove parentheses and join with commas
    cleaned_data = ', '.join(re.findall(r'\b\w+\b', sports_list_string))

    # Print the cleaned data
    # print("\nSports Lists: "+sports_list_string)        

    rank = olympic_soup.find("table", {"class": "wikitable sortable plainrowheaders jquery-tablesorter"})
    top3 = []
    for rows in rank.find_all("tbody"):
        count = 0
        for i in  rows.find_all("tr"):
            if count == 0:
                count+= 1 
                continue
            if count == 4: 
                break
            count+=1 
            a_tag = i.find('th', {'scope': 'row'}).find('a')

            # Extract the text within the <a> tag
            text_within_a_tag = a_tag.text
            
            top3.append(text_within_a_tag)
    
    # print("Top3 ranks: ")
    # print(top3)
    
    #Inserting into the DB
    cursor.execute("""
        INSERT INTO SummerOlympics (
            Name, WikipediaURL, Year, HostCity, ParticipatingNations, Athletes, Sports, Rank_1_nation, Rank_2_nation, Rank_3_nation
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (name, url, year, host_city, participating_nations_string, athletes_integer, sports_list_string, top3[0], top3[1], top3[2]))

    conn.commit()

# Step 5: Print answers to questions
if year in selected_years:
    cursor.execute("SELECT AVG(ParticipatingNations) FROM SummerOlympics WHERE Year IN (?, ?)", selected_years)
    average_participating_nations = cursor.fetchone()[0]
    avg=cnt/2
    print("Average number of countries participating in the two Olympics:", avg)

    year=selected_years[0]
    cursor.execute("""
        SELECT DISTINCT Rank_1_nation, Rank_2_nation, Rank_3_nation
        FROM SummerOlympics s1
        WHERE s1.Year = ?
    """, (year,))

    s1_ranks= cursor.fetchone()

    year=selected_years[1]
    cursor.execute("""
        SELECT DISTINCT Rank_1_nation, Rank_2_nation, Rank_3_nation
        FROM SummerOlympics s1
        WHERE s1.Year = ? 
    """, (year,))

    s2_ranks = cursor.fetchone()
    common_rank=[]
    if s1_ranks and s2_ranks is not None:
        for rank in s1_ranks:
            if rank in s2_ranks:
                common_rank.append(rank)

    if common_rank is not None:
        print("Common nations in Rank 1, Rank 2, and Rank 3 for the chosen two years: ")
        print(common_rank)
    else:
        print("No common nations in Rank 1, Rank 2, and Rank 3 for the chosen two years.")
    
    
# query = "SELECT * from SummerOlympics"
# result = cursor.execute(query)
# print("\nThe Database contains:\n")
# for row in result:
#     print(row)
cursor.close()    
# Close the database connection
conn.close()

