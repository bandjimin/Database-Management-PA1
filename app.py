#imports
import os
from random import choices

from helper import helper
from db_operations import db_operations

#global variables
db_ops = db_operations("playlist.db")

#functions
def startScreen():
    print("Welcome to your playlist!")
    # Create table if it doesn't exist
    if not db_ops.does_table_exist("songs"):
        db_ops.create_songs_table()
    db_ops.populate_songs_table("songs.csv")

#show user menu options
def options():
    print('''Select from the following menu options: 
    1. Find songs by artist
    2. Find songs by genre
    3. Find songs by feature
    4. Load new songs
    5. Update songs
    6. Delete song
    7. Exit''')
    return helper.get_choice([1,2,3,4,5,6,7])

#search for songs by artist
def search_by_artist():
    #get list of all artists in table
    artist_query = '''
    SELECT DISTINCT Artist FROM songs;
    '''

    artists = db_ops.select_query(artist_query)

    #show all artists, create dictionary of options, and let user choose
    options = {}
    for i, artist in enumerate(artists):
        options[i+1] = artist[0]
        print(f"{i+1}. {artist[0]}")

    index = helper.get_choice(list(options.keys()))

    #user can ask to see 1, 5, or all songs
    print("How many songs would you like to see? 1, 5, or all?")
    num = helper.get_choice([1, 5, 0]) # 0 will represent all songs

    #print results
    query = '''
    SELECT Name from songs 
    WHERE Artist = :artist
    '''
    params = {"artist": options[index]}

    if num:
        query += " LIMIT :limit"
        params["limit"] = num

    query += ";"
    results = db_ops.single_attribute_params(query, params)
    helper.pretty_print(results)

#search songs by genre
def search_by_genre():
    #get list of genres
    genre_query = '''
    SELECT DISTINCT Genre 
    FROM songs;
    '''
    genres = db_ops.select_query(genre_query)

    #show genres in table and create dictionary
    options = {}
    for i, genre in enumerate(genres):
        options[i+1] = genre[0]
        print(f"{i+1}. {genre[0]}")
    index = helper.get_choice(list(options.keys()))

    #user can ask to see 1, 5, or all songs
    print("How many songs would you like to see? 1, 5, or 0=all?")
    num = helper.get_choice([1, 5, 0]) # 0 will represent all songs
    params = {"genre": options[index]}

    song_query = '''
    SELECT Name FROM songs 
    WHERE Genre = :genre 
    ORDER BY RANDOM()
    '''

    if num:
        song_query += " LIMIT :limit"
        params["limit"] = num

    song_query += ";"

    #print results
    results = db_ops.single_attribute_params(song_query, params)
    helper.pretty_print(results)

#search songs table by features
def search_by_feature():
    #features we want to search by
    features = ["Energy", "Danceability", "Acousticness", "Liveness", "Loudness"]

    #show features in table and create dictionary
    options = {}
    for i, feature in enumerate(features):
        options[i+1] = feature
        print(f"{i+1}. {feature}")
    index = helper.get_choice(list(options.keys()))


    #user can ask to see 1, 5, or all songs
    print("How many songs would you like to see? 1, 5, or 0=all?")
    num = helper.get_choice([1, 5, 0]) # 0 will represent all songs
    params = {"feature": options[index]}
    
    song_query = '''
    SELECT Name FROM songs
    '''

    if index == 1:
        song_query += "ORDER BY Energy "
    elif index == 2:
        song_query += "ORDER BY Danceability "
    elif index == 3:
        song_query += "ORDER BY Acousticness "
    elif index == 4:
        song_query += "ORDER BY Liveness "
    elif index == 5:
        song_query += "ORDER BY Loudness "

    #what order does the user want this returned in?
    print("In what order would you like the results returned?")
    print("0=Descending, 1=Ascending")
    order = helper.get_choice([0,1])

    if order:
        song_query += "ASC"
    else:
        song_query += "DESC"

    if num:
        song_query += " LIMIT :limit"
        params["limit"] = num
    
    song_query += ";"

    #print results
    results = db_ops.single_attribute_params(song_query, params)
    helper.pretty_print(results)

def load_new_songs():
    song_query = '''
    SELECT * FROM songs;
    '''
    songs = db_ops.select_query(song_query)
    songIDs = [song[0] for song in songs]
    
    query = '''
    INSERT INTO songs (songID, Name, Artist, Album, releaseDate, Genre, Explicit, Duration, Energy, Danceability, Acousticness, Liveness, Loudness)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    '''
    filepath = input("Enter the path to the CSV file: ")

    # code below from Geeks for Geeks
    if not os.path.isfile(filepath):
        print("File does not exist or is not a file")
        return
    # end of copied code
        
    data = helper.data_cleaner(filepath)

    #take out duplicates and insert only new songs
    non_duplicate_data = []
    for row in data:
        if row[0] in songIDs:
            continue
        non_duplicate_data.append(row)
    

    if len(non_duplicate_data) != 0:
        db_ops.bulk_insert(query, non_duplicate_data)

    print(f"{len(non_duplicate_data)} new songs added to the database.")

def update_songs():
    song_query = '''
    SELECT * FROM songs
    WHERE Name = :name;
    '''
    name = input("Enter the name of the song you want to update: ")
    params = {"name": name}
    results = db_ops.select_query_params(song_query, params)
    if len(results) == 0:
        print("Song not found.")
        return
    result = results[0]

    print(f'''
    Song Name: {result[1]}
    Album Name: {result[3]}
    Artist Name: {result[2]}
    Release Date: {result[4]}
    Explicit Content: {result[6]}
    ''')

    # ask user what they want to modify
    print("What would you like to modify?")
    print("1. Song Name")
    print("2. Album Name")
    print("3. Artist Name")
    print("4. Release Date")
    print("5. Explicit Content")
    choice = helper.get_choice([1, 2, 3, 4, 5])

    # update the song in the database
    query = '''
    UPDATE songs 
    '''
    
    # get the new value from the user
    if choice == 1:
        new_value = input("Enter the new song name: ")
        query += "SET Name = :new_value WHERE songID = :id;"
    elif choice == 2:
        new_value = input("Enter the new album name: ")
        query += "SET Album = :new_value WHERE songID = :id;"
    elif choice == 3:
        new_value = input("Enter the new artist name: ")
        query += "SET Artist = :new_value WHERE songID = :id;"
    elif choice == 4:
        new_value = input("Enter the new release date (YYYY-MM-DD): ")
        for i, char in enumerate(new_value):
            if char not in "0123456789":
                if (i != 4 and i != 7) and char not in "-":
                    print("Invalid date format. Please use YYYY-MM-DD.")
                    return
        query += "SET releaseDate = :new_value WHERE songID = :id;"
    elif choice == 5:
        print("Enter the new explicit content value (0 or 1): ")
        new_value = helper.get_choice([0, 1])
        query += "SET Explicit = :new_value WHERE songID = :id;"

    db_ops.modify_query_params(query, {"new_value": new_value, "id": result[0]})

def delete_song():
    song_query = '''
    SELECT * FROM songs
    WHERE Name = :name;
    '''
    name = input("Enter the name of the song you want to delete: ")
    params = {"name": name}
    results = db_ops.select_query_params(song_query, params)
    if len(results) == 0:
        print("Song not found.")
        return
    result = results[0]

    print(f'''
    Song Name: {result[1]}
    Album Name: {result[3]}
    Artist Name: {result[2]}
    Release Date: {result[4]}
    Explicit Content: {result[6]}
    ''')

    # ask user if they are sure they want to delete the song
    print("Are you sure you want to delete this song? (y/n)")
    choice = input()
    if choice.lower() == "y":
        query = '''
        DELETE FROM songs 
        WHERE songID = :id;
        '''
        db_ops.modify_query_params(query, {"id": result[0]})
        print("Song deleted.")

if __name__ == "__main__":
    #main method
    startScreen()

    #program loop
    while True:
        user_choice = options()
        if user_choice == 1:
            search_by_artist()
        if user_choice == 2:
            search_by_genre()
        if user_choice == 3:
            search_by_feature()
        if user_choice == 4:
            load_new_songs()
        if user_choice == 5:
            update_songs()
        if user_choice == 6:
            delete_song()
        if user_choice == 7:
            print("Goodbye!")
            break

    db_ops.destructor()