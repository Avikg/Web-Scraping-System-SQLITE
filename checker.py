import sqlite3
import warnings

warnings.filterwarnings("ignore")

# Function to check if all rows are populated
def all_rows_populated(cursor):
    cursor.execute("SELECT COUNT(*) FROM SummerOlympics WHERE DONE_OR_NOT_DONE = 0")
    count = cursor.fetchone()[0]
    return count == 0

def avg_no_athletes(cursor):
    cursor.execute("SELECT Athletes FROM SummerOlympics WHERE Athletes IS NOT NULL")
    athlete_counts = [row[0] for row in cursor.fetchall() if row[0] is not None]

    # Calculate the average number of athletes
    if athlete_counts:
        avg_athletes = sum(athlete_counts) / len(athlete_counts)
    else:
        avg_athletes = 0
    print(f"The average number of athletes is: {avg_athletes:.2f}")
    

# Function to get the country within the top 3 for the maximum time
def years_chosen(cursor):
    cursor.execute("""
        SELECT Year
        FROM SummerOlympics
    """)
    rows = cursor.fetchall()
    print("\nYears are:")
    for row in rows:
        print(row)
    
def max_time_country(cursor):
    cursor.execute("SELECT Rank_1_nation, Rank_2_nation, Rank_3_nation FROM SummerOlympics WHERE Rank_1_nation IS NOT NULL")
    rows = cursor.fetchall()

    # Create a dictionary to count country occurrences
    country_counts = {}
    for row in rows:
        for country in row:
            if country not in country_counts:
                country_counts[country] = 0
            country_counts[country] += 1

    # Find the country with the maximum count
    max_country, max_count = max(country_counts.items(), key=lambda x: x[1])
    
    # Print the result
    print("The country within the top 3 for the maximum time is:", max_country)
    print("It appeared in the top 3 ranks", max_count, "times.")


# Step 1: Check if all rows are populated and no process is working
conn = sqlite3.connect("OlympicsData.db")
cursor = conn.cursor()

if all_rows_populated(cursor):
    print("All rows populated")
    years_chosen(cursor)
    max_time_country(cursor)
    avg_no_athletes(cursor)
    
else:
    print("Not all rows are populated. Database is still processing.")

cursor.close()
conn.close()
