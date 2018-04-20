import model
import app
import webbrowser

if __name__ == '__main__':
    print("Hello, welcome to the program!")
    new_or_old = input('''
        To begin, would you like to add new data to the database
        or work with old data? Enter 'new', 'old', or 'quit' to
        exit the program.
    ''')
    if new_or_old == 'new':
        keyword = input("Please enter a search term or 'continue' to move on:  ")
        while keyword != 'continue':
            exists = model.check_query(keyword)
            if exists == True:
                remove = input('''Would you like to delete this entry from the database
                and collect it again? yes/no   ''')
                if remove == 'yes':
                    model.remove_entry(keyword)
                    model.run_query(keyword)
                else:
                    print("Existing entry for {} will not be removed".format(keyword))
            else:
                model.run_query(keyword)
            keyword = input("Please enter a search term or 'continue' to move on:  ")
    elif new_or_old == 'old' or keyword == 'continue':
        keyword = input("Please enter a term to search within the database or 'quit'")
        while keyword != 'quit':
            app.app.run(debug=False)
            open = ''
            while open != 'new':
                if open == 'results':
                    webbrowser.open("http://127.0.0.1:5000/{}".format(keyword))
                elif open == 'graph':
                    #plotly graph
                    pass
                elif open == 'map':
                    #plotly graph
                    pass
                else:
                    print("Sorry, that wasn't understood.")
                open = input('''
                    To view results and links, type 'results'
                    To view a graph of links, type 'graph'
                    To view a map of result locations, type 'map'
                    Or to run a new query, type 'new'
                ''')
            keyword = input("Please enter a term to search within the database or 'quit'")
    else:
        print("Goodbye!")
