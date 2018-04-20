import model
import app

if __name__ == '__main__':
    print("Hello, welcome to the program!")
    new_or_old = input('''
        To begin, would you like to add new data to the database
        or work with existing data? Enter 'new' to run a new query
        and add additional entries to the databases. Enter 'existing'
        to work with existing data. Enter 'quit' to exit the program.
        ''')
    keyword = ''
    if new_or_old == 'new':
        keyword = input("Please enter a search term or:  ")
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
            keyword = input("Please enter another search term or 'continue' to move on:  ")
    if new_or_old == 'existing' or keyword == 'continue':
        app.app.run(debug=False)
    else:
        print("Goodbye!")
