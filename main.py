# ================================================================
# Chicago Traffic Camera Analysis Project
# ================================================================
# Name: David Bodansky
# Date: 2/9/25
# Description:
#   This project allows the user to obtain different kinds of information from the 
#   Chicago traffic camera database in an organized format and for some options the 
#   user even has the ability to graph that information for a more visual look.

import sqlite3
import matplotlib.pyplot as plt
from datetime import datetime
import datetime

##################################################################  
#
# print_stats
#
# Given connection to database, executes various SQL queries to retrieve and output basic stats.
def print_stats(dbConn):
    dbCursor = dbConn.cursor()
    
    print("General Statistics:")
    
    dbCursor.execute("SELECT COUNT(*) FROM RedCameras;")
    row = dbCursor.fetchone()
    dbCursor.execute("SELECT COUNT(*) FROM SpeedCameras;")
    row1 = dbCursor.fetchone()
    dbCursor.execute("SELECT COUNT(*) FROM RedViolations;")
    row2 = dbCursor.fetchone()
    dbCursor.execute("SELECT COUNT(*) FROM SpeedViolations;")
    row3 = dbCursor.fetchone()
    dbCursor.execute("SELECT MIN(Violation_Date), MAX(Violation_Date) FROM RedViolations;")
    row4 = dbCursor.fetchone()
    dbCursor.execute("SELECT SUM(Num_Violations) FROM RedViolations;")
    row5 = dbCursor.fetchone()
    dbCursor.execute("SELECT SUM(Num_Violations) FROM SpeedViolations;")
    row6 = dbCursor.fetchone()
    start_date = row4[0]
    end_date = row4[1]
    print("  Number of Red Light Cameras:", f"{row[0]:,}")
    print("  Number of Speed Cameras:", f"{row1[0]:,}")
    print("  Number of Red Light Camera Violation Entries:", f"{row2[0]:,}")
    print("  Number of Speed Camera Violation Entries:", f"{row3[0]:,}")
    print(f"  Range of Dates in the Database: {start_date} - {end_date}")
    print("  Total Number of Red Light Camera Violations:", f"{row5[0]:,}")
    print("  Total Number of Speed Camera Violations:", f"{row6[0]:,}")
    
####################################################################################### 
# Menu Function
def print_menu():
    print("Select a menu option: ")
    print("  1. Find an intersection by name")
    print("  2. Find all cameras at an intersection")
    print("  3. Percentage of violations for a specific date")
    print("  4. Number of cameras at each intersection")
    print("  5. Number of violations at each intersection, given a year")
    print("  6. Number of violations by year, given a camera ID")
    print("  7. Number of violations by month, given a camera ID and year")
    print("  8. Compare the number of red light and speed violations, given a year")
    print("  9. Find cameras located on a street")
    print("or x to exit the program.")

################################################################################### Command 1
def command1(): # Code called when user writes 1 from the menu
    print("Your choice --> ")
    find_int = input("Enter the name of the intersection to find (wildcards _ and % allowed): ")
    dbCursor = dbConn.cursor() # Connection to database established
    dbCursor.execute("""SELECT Intersection_ID, Intersection
                    FROM Intersections WHERE Intersection LIKE ? 
                    ORDER BY Intersection ASC""", (find_int,))
    rows = dbCursor.fetchall() # Fetches all rows
    
    if rows:
        for row in rows:
            print(f"{row[0]} : {row[1]}") # Prints all queried lines
    else:
        print("No intersections matching that name were found.")
    print("")

    print_menu()

################################################################################### Command 2
def command2(): # Code called when user writes 2 from the menu
    print("Your choice --> ")
    find_int = input("Enter the name of the intersection (no wildcards allowed): \n")
    dbCursor = dbConn.cursor()
    # Query for redcameras
    dbCursor.execute("""SELECT RedCameras.Camera_ID, RedCameras.Address
                    FROM RedCameras 
                    JOIN Intersections ON RedCameras.Intersection_ID = Intersections.Intersection_ID
                    WHERE Intersection LIKE ? 
                    ORDER BY RedCameras.Camera_ID ASC""", (find_int,))
    rows = dbCursor.fetchall() # red light cameras

    # Query for speedcameras
    dbCursor.execute("""SELECT SpeedCameras.Camera_ID, SpeedCameras.Address
                    FROM SpeedCameras 
                    JOIN Intersections ON SpeedCameras.Intersection_ID = Intersections.Intersection_ID
                    WHERE Intersection LIKE ? 
                    ORDER BY SpeedCameras.Camera_ID ASC""", (find_int,))
    rows1 = dbCursor.fetchall() # speed cameras
    
    if rows:
        print("Red Light Cameras:")
        for row in rows:
            print(f"    {row[0]} : {row[1]}") # Prints all queried lines
    else:
        print("No red light cameras found at that intersection.")

    print("")

    if rows1:
        print("Speed Cameras:")
        for row in rows1:
            print(f"    {row[0]} : {row[1]}") # Prints all queried lines
    else:
        print("No speed cameras found at that intersection.")

    print("")
    print_menu() # Calls menu function

################################################################################### Command 3
def command3(): # Code called when user writes 3 from the menu
    print("Your choice --> ")
    dbCursor = dbConn.cursor()
    
    # Gets min/max dates from database
    dbCursor.execute("SELECT MIN(Violation_Date), MAX(Violation_Date) FROM SpeedViolations;")
    min_max_dates = dbCursor.fetchone()
    
    if not min_max_dates or not min_max_dates[0]:  # Handles cases where no data exists at all
        print("No violation records exist in the database.")
        print_menu()
        return

    min_date, max_date = min_max_dates  # Extracts min and max dates
    
    # Prompts for date input
    find_vio = input("Enter the date that you would like to look at (format should be YYYY-MM-DD): ").strip()

    # Manually validates date format
    date = find_vio
    
    # Checks for different valid date formats
    if (len(date) == 10 and date[4] == '-' and date[7] == '-') or (len(date) == 10 and date[2] == '/' and date[5] == '/') or (len(date) == 8 and date[1] == '/' and date[3] == '/') or (len(date) == 8 and date[4] == '-' and date[6] == '-'):
        # Some valid formats are (YYYY-MM-DD, MM/DD/YY, MM-DD-YY)
        pass
    else:
        print("\nInvalid date format. Please enter the date in YYYY-MM-DD format.\n")
        return

    # Checks date is within range
    if not (min_date <= find_vio <= max_date):
        print("No violations on record for that date.")
        print_menu()
        return

    # Fetches red light violations
    dbCursor.execute("SELECT SUM(Num_Violations) FROM RedViolations WHERE Violation_Date = ?", (find_vio,))
    red_light_violations = dbCursor.fetchone()[0] or 0  # Convert None to 0

    # Fetches speed violations
    dbCursor.execute("SELECT SUM(Num_Violations) FROM SpeedViolations WHERE Violation_Date = ?", (find_vio,))
    speed_violations = dbCursor.fetchone()[0] or 0  # Convert None to 0

    # Calculates total violations
    total_violations = red_light_violations + speed_violations

    if total_violations == 0:
        print("No violations on record for that date.")
    else:
        red_light_percentage = (red_light_violations / total_violations * 100)
        speed_percentage = (speed_violations / total_violations * 100)

        print("Number of Red Light Violations:", f"{red_light_violations:,}", f"({red_light_percentage:.3f}%)")
        print("Number of Speed Violations:", f"{speed_violations:,}", f"({speed_percentage:.3f}%)")
        print(f"Total Number of Violations: {total_violations:,}")

    print("")
    print_menu()

################################################################################### Command 4
def command4(): # Code called when user writes 4 from the menu
    print("Your choice --> ")
    dbCursor = dbConn.cursor()

    # Query to get total number of red light cameras
    dbCursor.execute("SELECT COUNT(*) FROM RedCameras")
    total_red_cameras = dbCursor.fetchone()[0]

    # Query to get total number of speed cameras
    dbCursor.execute("SELECT COUNT(*) FROM SpeedCameras")
    total_speed_cameras = dbCursor.fetchone()[0]

    # Query to get number of red light cameras at each intersection
    dbCursor.execute("""
        SELECT Intersections.Intersection_ID, Intersections.Intersection, COUNT(RedCameras.Camera_ID)
        FROM Intersections
        INNER JOIN RedCameras ON Intersections.Intersection_ID = RedCameras.Intersection_ID
        GROUP BY Intersections.Intersection_ID, Intersections.Intersection
        ORDER BY COUNT(RedCameras.Camera_ID) DESC, Intersections.Intersection_ID DESC;
    """)
    red_camera_results = dbCursor.fetchall()

    # Query to get number of speed cameras at each intersection
    dbCursor.execute("""
        SELECT Intersections.Intersection_ID, Intersections.Intersection, COUNT(SpeedCameras.Camera_ID)
        FROM Intersections
        INNER JOIN SpeedCameras ON Intersections.Intersection_ID = SpeedCameras.Intersection_ID
        GROUP BY Intersections.Intersection_ID, Intersections.Intersection
        ORDER BY COUNT(SpeedCameras.Camera_ID) DESC, Intersections.Intersection_ID DESC;
    """)
    speed_camera_results = dbCursor.fetchall()

    # Prints number of red light cameras at each intersection
    print("Number of Red Light Cameras at Each Intersection")
    for intersection_id, intersection, count in red_camera_results:
        percentage = (count / total_red_cameras * 100)  # Calculates percentage of red cameras at this intersection
        print(f"  {intersection} ({intersection_id}) : {count} ({percentage:.3f}%)")  # Displays intersection and percentage

    # Print the number of speed cameras at each intersection
    print("\nNumber of Speed Cameras at Each Intersection")
    for intersection_id, intersection, count in speed_camera_results:
        percentage = (count / total_speed_cameras * 100)  # Calculates percentage of speed cameras at this intersection
        print(f"  {intersection} ({intersection_id}) : {count} ({percentage:.3f}%)")  # Displays intersection and percentage

    print("")
    print_menu()


################################################################################### Command 5
def command5(): # Code called when user writes 5 from the menu
    print("Your choice --> ")
    dbCursor = dbConn.cursor()

    year = input("Enter the year that you would like to analyze: \n")

    # Checks year format
    if not (year.isdigit() and len(year) == 4 and 2014 <= int(year) <= 2024):
        print(f"Number of Red Light Violations at Each Intersection for {year}")
        print("No red light violations on record for that year.")
        print("")
        print(f"Number of Speed Violations at Each Intersection for {year}")
        print("No speed violations on record for that year.")
    else:
        # Query for total red light violations in given year
        dbCursor.execute("""
            SELECT SUM(Num_Violations) 
            FROM RedViolations 
            WHERE strftime('%Y', Violation_Date) = ?""", (year,))
        total_red_violations = dbCursor.fetchone()[0]

        # Query for total speed violations in given year
        dbCursor.execute("""
            SELECT SUM(Num_Violations) 
            FROM SpeedViolations 
            WHERE strftime('%Y', Violation_Date) = ?""", (year,))
        total_speed_violations = dbCursor.fetchone()[0]

        # Query for red light violations per intersection
        dbCursor.execute("""
            SELECT Intersections.Intersection_ID, Intersections.Intersection, SUM(RedViolations.Num_Violations)
            FROM RedViolations
            JOIN RedCameras ON RedViolations.Camera_ID = RedCameras.Camera_ID
            JOIN Intersections ON RedCameras.Intersection_ID = Intersections.Intersection_ID
            WHERE strftime('%Y', RedViolations.Violation_Date) = ?
            GROUP BY Intersections.Intersection_ID, Intersections.Intersection
            ORDER BY SUM(RedViolations.Num_Violations) DESC, Intersections.Intersection_ID DESC;
        """, (year,))
        red_violation_results = dbCursor.fetchall()

        # Query for speed violations per intersection
        dbCursor.execute("""
            SELECT Intersections.Intersection_ID, Intersections.Intersection, SUM(SpeedViolations.Num_Violations)
            FROM SpeedViolations
            JOIN SpeedCameras ON SpeedViolations.Camera_ID = SpeedCameras.Camera_ID
            JOIN Intersections ON SpeedCameras.Intersection_ID = Intersections.Intersection_ID
            WHERE strftime('%Y', SpeedViolations.Violation_Date) = ?
            GROUP BY Intersections.Intersection_ID, Intersections.Intersection
            ORDER BY SUM(SpeedViolations.Num_Violations) DESC, Intersections.Intersection_ID DESC;
        """, (year,))
        speed_violation_results = dbCursor.fetchall()

        # Query total number of red light cameras in Chicago
        dbCursor.execute("SELECT COUNT(*) FROM RedCameras")
        total_red_cameras = dbCursor.fetchone()[0]

        # Query total number of speed cameras in Chicago
        dbCursor.execute("SELECT COUNT(*) FROM SpeedCameras")
        total_speed_cameras = dbCursor.fetchone()[0]

        # Outputs red light violations
        print(f"\nNumber of Red Light Violations at Each Intersection for {year}")
        for intersection_id, intersection, count in red_violation_results:
            percentage = (count / total_red_violations * 100)
            print(f"  {intersection} ({intersection_id}) : {count:,} ({percentage:.3f}%)")
        print(f"Total Red Light Violations in {year} : {total_red_violations:,}")

        # Outputs speed camera violations
        print(f"\nNumber of Speed Violations at Each Intersection for {year}")
        for intersection_id, intersection, count in speed_violation_results:
            percentage = (count / total_speed_violations * 100)
            print(f"  {intersection} ({intersection_id}) : {count:,} ({percentage:.3f}%)")
        print(f"Total Speed Violations in {year} : {total_speed_violations:,}")

    print("")
    print_menu()

################################################################################### Command 6
def command6(): # Code called when user writes 6 from the menu
    print("Your choice --> ")
    dbCursor = dbConn.cursor()

    # Prompts user for Camera ID
    camera_id = input("Enter a camera ID: ").strip()

    # Checks if camera exists in either table
    dbCursor.execute("SELECT COUNT(*) FROM RedCameras WHERE Camera_ID = ?", (camera_id,))
    red_camera_exists = dbCursor.fetchone()[0] > 0

    dbCursor.execute("SELECT COUNT(*) FROM SpeedCameras WHERE Camera_ID = ?", (camera_id,))
    speed_camera_exists = dbCursor.fetchone()[0] > 0

    if not red_camera_exists and not speed_camera_exists:
        print("No cameras matching that ID were found in the database.")
        print("")
    else:
        # Queries number of violations per year for this camera
        dbCursor.execute("""
            SELECT strftime('%Y', Violation_Date) AS Year, SUM(Num_Violations)
            FROM RedViolations
            WHERE Camera_ID = ?
            GROUP BY Year
            ORDER BY Year ASC;
        """, (camera_id,))
        red_violations = dbCursor.fetchall()

        dbCursor.execute("""
            SELECT strftime('%Y', Violation_Date) AS Year, SUM(Num_Violations)
            FROM SpeedViolations
            WHERE Camera_ID = ?
            GROUP BY Year
            ORDER BY Year ASC;
        """, (camera_id,))
        speed_violations = dbCursor.fetchall()

        # Merges red and speed violations
        violations = red_violations if red_camera_exists else speed_violations

        # Displays violations count per year
        print(f"Yearly Violations for Camera {camera_id}")
        for year, count in violations:
            print(f"{year} : {count:,}")

        # Asks user if they want to plot
        plot_choice = input("\nPlot? (y/n) \n").strip()
        if plot_choice == "y":
            years = [year for year, _ in violations]
            counts = [count for _, count in violations]

            # Plots data
            plt.figure(figsize=(8, 5))
            plt.plot(years, counts, linestyle="-", color='blue', linewidth=2)
            plt.xlabel("Year")
            plt.ylabel("Number of Violations")
            plt.title(f"Yearly Violations For Camera {camera_id}")
            plt.xticks(years)
            plt.show()

    print_menu()

################################################################################### Command 7
def command7(): # Code called when user writes 7 from the menu
    print("Your choice --> ")
    dbCursor = dbConn.cursor()

    # Prompts user for Camera ID
    camera_id = input("Enter a camera ID: ").strip()

    # Checks if camera exists in either table
    dbCursor.execute("SELECT COUNT(*) FROM RedCameras WHERE Camera_ID = ?", (camera_id,))
    red_camera_exists = dbCursor.fetchone()[0] > 0

    dbCursor.execute("SELECT COUNT(*) FROM SpeedCameras WHERE Camera_ID = ?", (camera_id,))
    speed_camera_exists = dbCursor.fetchone()[0] > 0

    if not red_camera_exists and not speed_camera_exists:
        print("No cameras matching that ID were found in the database.\n")
    else:
        # Prompts user for year
        year = input("Enter a year: ").strip()
        
        # Queries number of violations per month for this camera in given year
        dbCursor.execute("""
            SELECT strftime('%m', Violation_Date) AS Month, SUM(Num_Violations)
            FROM RedViolations
            WHERE Camera_ID = ? AND strftime('%Y', Violation_Date) = ?
            GROUP BY Month
            ORDER BY Month ASC;
        """, (camera_id, year))
        red_violations = dbCursor.fetchall()

        dbCursor.execute("""
            SELECT strftime('%m', Violation_Date) AS Month, SUM(Num_Violations)
            FROM SpeedViolations
            WHERE Camera_ID = ? AND strftime('%Y', Violation_Date) = ?
            GROUP BY Month
            ORDER BY Month ASC;
        """, (camera_id, year))
        speed_violations = dbCursor.fetchall()

        # Merges red/speed violations
        violations = red_violations if red_camera_exists else speed_violations

        # Displays violations count per month
        print(f"Monthly Violations for Camera {camera_id} in {year}")
        for month, count in violations:
            print(f"{month}/{year} : {count:,}")

        # Asks user if they want to plot
        plot_choice = input("\nPlot? (y/n) \n").strip().lower()
        if plot_choice == "y" and (2014 <= int(year) <= 2024):
            months = [f"{month}" for month, _ in violations]
            counts = [count for _, count in violations]

            # Plots data
            plt.figure(figsize=(8, 5))
            plt.plot(months, counts, linestyle="-", color='blue', linewidth=2)
            plt.xlabel("Month")
            plt.ylabel("Number of Violations")
            plt.title(f"Monthly Violations for Camera {camera_id} ({year})")
            plt.xticks(months)  # Rotate for better readability
            plt.show()
    print_menu()

################################################################################### Command 8
def command8(): # Code called when user writes 8 from the menu
    print("Your choice --> ")
    dbCursor = dbConn.cursor()

    # Prompts user for year
    year = input("Enter a year: ").strip()

    # Checks for leap year
    days_in_year = 366 if datetime.datetime.strptime(f"{year}-12-31", "%Y-%m-%d").timetuple().tm_yday == 366 else 365

    # Initializes arrays with zeros for all days in year
    red_violations = [0] * days_in_year
    speed_violations = [0] * days_in_year

    # Generates complete list of dates for year
    start_date = datetime.date(int(year), 1, 1)
    all_dates = [(start_date + datetime.timedelta(days=i)).strftime("%Y-%m-%d") for i in range(days_in_year)]

    # Queries red light violations
    dbCursor.execute("""
        SELECT strftime('%j', Violation_Date) AS DayOfYear, SUM(Num_Violations)
        FROM RedViolations
        WHERE strftime('%Y', Violation_Date) = ?
        GROUP BY DayOfYear
        ORDER BY DayOfYear ASC;
    """, (year,))
    
    red_data = dbCursor.fetchall()
    for day_of_year, count in red_data:
        red_violations[int(day_of_year) - 1] = count  # Convert to zero-based index

    # Queries speed violations
    dbCursor.execute("""
        SELECT strftime('%j', Violation_Date) AS DayOfYear, SUM(Num_Violations)
        FROM SpeedViolations
        WHERE strftime('%Y', Violation_Date) = ?
        GROUP BY DayOfYear
        ORDER BY DayOfYear ASC;
    """, (year,))
    
    speed_data = dbCursor.fetchall()
    for day_of_year, count in speed_data:
        speed_violations[int(day_of_year) - 1] = count  # Convert to zero-based index

    # Extracts only non-zero data for display
    non_zero_red = [(all_dates[i], red_violations[i]) for i in range(days_in_year) if red_violations[i] > 0]
    non_zero_speed = [(all_dates[i], speed_violations[i]) for i in range(days_in_year) if speed_violations[i] > 0]

    # Prints first and last 5 non-zero days
    print("Red Light Violations:")
    for date, count in non_zero_red[:5] + non_zero_red[-5:]:
        print(f"{date} {count:}")

    print("Speed Violations:")
    for date, count in non_zero_speed[:5] + non_zero_speed[-5:]:
        print(f"{date} {count:}")

    # Asks user if they want to plot
    plot_choice = input("\nPlot? (y/n) ").strip().lower()
    if plot_choice == "y":
        # Plots data
        plt.figure(figsize=(12, 6))
        plt.plot(range(days_in_year), red_violations, linestyle="-", color='red', linewidth=2, label="Red Light Violations")
        plt.plot(range(days_in_year), speed_violations, linestyle="-", color='orange', linewidth=2, label="Speed Violations")

        plt.xlabel("Day")
        plt.ylabel("Number of Violations")
        plt.title(f"Violations Each Day of {year}")
        plt.legend()

        # Sets x axis ticks from 50 to 350 with step 50
        tick_positions = list(range(0, 351, 50))
        tick_labels = [str(i) for i in tick_positions]
        plt.xticks(tick_positions, tick_labels, rotation=45, fontsize=8)

        plt.grid(axis="y", linestyle="--", alpha=0.7)
        plt.show()

    print("")

    print_menu()

################################################################################### Command 9
def command9(): # Code called when user writes 9 from the menu
    print("Your choice --> ")
    dbCursor = dbConn.cursor()

    # Gets street name from user
    street_name = input("Enter a street name: ").strip()

    # Queries for red light cameras on street
    dbCursor.execute("""
        SELECT Camera_ID, Address, Latitude, Longitude
        FROM RedCameras
        WHERE Address LIKE ?
        ORDER BY Camera_ID ASC
    """, (f"%{street_name}%",))  # Uses wildcards
    red_cameras = dbCursor.fetchall()

    # Query for speed cameras on street
    dbCursor.execute("""
        SELECT Camera_ID, Address, Latitude, Longitude
        FROM SpeedCameras
        WHERE Address LIKE ?
        ORDER BY Camera_ID ASC
    """, (f"%{street_name}%",))
    speed_cameras = dbCursor.fetchall()

    if not red_cameras and not speed_cameras:
        print(f"There are no cameras located on that street.")
    else:
        # Prints list of cameras found
        print(f"\nList of Cameras Located on Street: {street_name}")

        if red_cameras:
            print("  Red Light Cameras:")
            for camera in red_cameras:
                print(f"     {camera[0]} : {camera[1]} ({camera[2]}, {camera[3]})")
        else:
            print("  Red Light Cameras:")

        if speed_cameras:
            print("  Speed Cameras:")
            for camera in speed_cameras:
                print(f"     {camera[0]} : {camera[1]} ({camera[2]}, {camera[3]})")
        else:
            print("  Speed Cameras:")

        # Asks if user wants to plot cameras
        plot_choice = input("\nPlot? (y/n) ").strip()

        if plot_choice == "y":
            # Prepares coordinates for plotting
            red_x = [camera[3] for camera in red_cameras]
            red_y = [camera[2] for camera in red_cameras]
            speed_x = [camera[3] for camera in speed_cameras]
            speed_y = [camera[2] for camera in speed_cameras]

            # Loads map image
            image = plt.imread("chicago.png")
            xydims = [-87.9277, -87.5569, 41.7012, 42.0868]

            plt.imshow(image, extent=xydims)

            # Plots red light cameras in red
            plt.plot(red_x, red_y, 'ro', label="Red Light Cameras")

            # Plots speed cameras in orange
            plt.plot(speed_x, speed_y, 'ro', color='orange', label="Speed Cameras")

            # Annotates each camera with its ID
            for camera in red_cameras:
                plt.annotate(camera[0], (camera[3], camera[2]), color='black', fontsize=8)

            for camera in speed_cameras:
                plt.annotate(camera[0], (camera[3], camera[2]), color='black', fontsize=8)

            # Sets map limits and title
            plt.xlim([-87.9277, -87.5569])
            plt.ylim([41.7012, 42.0868])
            plt.title(f"Cameras on {street_name}")
            plt.legend()

            # Plots data on map
            plt.show()

    print("")
    print_menu()

# Ends program when user writes x

def commandx():
    print("Your choice --> Exiting program.")
    global run
    run = False

def commandError():
    print("Your choice --> Error, unknown command, try again...\n")
    print_menu()

#
# main
#
dbConn = sqlite3.connect('chicago-traffic-cameras.db')
run = True

# Beginning project explanation
print("Project 1: Chicago Traffic Camera Analysis")
print("CS 341, Spring 2025")
print()
print("This application allows you to analyze various")
print("aspects of the Chicago traffic camera database.")
print()
print_stats(dbConn)
print()
print_menu()

# Loop runs until user quits by writing x
while run:
    inp = input()
    
    if inp == "1":
        command1()
    elif inp == "2":
        command2()
    elif inp == "3":
        command3()
    elif inp == "4":
        command4()
    elif inp == "5":
        command5()
    elif inp == "6":
        command6()
    elif inp == "7":
        command7()
    elif inp == "8":
        command8()
    elif inp == "9":
        command9()
    elif inp == "x":
        commandx()
    else:
        commandError()
#
# done
#
