import requests
import sqlite3
from bs4 import BeautifulSoup


import warnings
warnings.filterwarnings("ignore")

# Step 1: Check the database for rows where DONE_OR_NOT_DONE flag is 0
conn = sqlite3.connect("OlympicsData.db")
cursor = conn.cursor()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"}

# Function to fetch Wikipedia page and populate the database
def fetch_and_populate_data(url):
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
    #cleaned_data = ', '.join(re.findall(r'\b\w+\b', sports_list_string))

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
        UPDATE SummerOlympics SET
            Name=?, Year=?, HostCity=?, ParticipatingNations=?, Athletes=?, Sports=?, Rank_1_nation=?, Rank_2_nation=?, Rank_3_nation=? 
            WHERE WikipediaURL=?
        
    """, (name, year, host_city, participating_nations_string, athletes_integer, sports_list_string, top3[0], top3[1], top3[2], url))

    conn.commit()
    
    


#Main Function
query = "SELECT * from SummerOlympics"
result = cursor.execute(query)
while True:
    row=cursor.execute("SELECT WikipediaURL FROM SummerOlympics WHERE DONE_OR_NOT_DONE = 0 LIMIT 1")
    url_to_process = list(row)[0][0]
    # print("url to process")
    # print(url_to_process)
    if url_to_process is not None:
        cursor.execute("UPDATE SummerOlympics SET DONE_OR_NOT_DONE = 1 WHERE WikipediaURL = ?", (url_to_process,))
        conn.commit()
        fetch_and_populate_data(url_to_process)
    else:
        break
cursor.close()    
#Close the database connection
conn.close()




