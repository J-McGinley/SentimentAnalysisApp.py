from tkinter.tix import *
import os
import threading
import webbrowser
from time import sleep
from tkinter import ACTIVE, tix
import matplotlib.pyplot as plt
import matplotlib
from matplotlib import style, animation
from tweepy import Stream
from tweepy import OAuthHandler
from tweepy.streaming import StreamListener
import json
import Sentiment_mod as sentimentMod
import tkinter.messagebox as box


# Application is bundled using pyinstaller, therefore the resource path must point to sys._MEIPASS\relative_path
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


# Make safe method, simply strips special characters from the string unless they are specifically needed for the
# purposes of the application. This is used on all .get() methods and helps in preventing any kind
# of code injection / hacking
def makeSafe(text):
    cleanedText = ''.join(char for char in text if char.isalnum() or char == '@' or char == '#' or char == '-' or
                          char == ' ' or char == '$')
    return cleanedText


# showPlot method. This method creates a matplotlib animation, based on the information below.
# The first few lines are simply to do with the style of the plot
# The funcanimation method implements animate from below to read the information for plotting live
def showPlot():
    global subplot
    global entry
    matplotlib.use('TkAgg')
    style.use("ggplot")
    figure = plt.figure()
    subplot = figure.add_subplot(1, 1, 1)
    figure.canvas.set_window_title(makeSafe(entry.get()))
    plot = animation.FuncAnimation(figure, animate, interval=100)
    plt.show()
    # According to the console this line throws an error, however it also fixes a bug which occurs when it is not here
    figure.protocol("WM_DELETE_WINDOW", lambda arg=figure: plt.close(figure))


# Animate method. This sets matplotlib to interactive mode, then it opens the sentiment output file and reads the values
# for each instance in sentiment list increment x by 1. If sentiment is positive increment y by 1, elif sentiment is
# negative increment y by -1
def animate(i):
    try:
        plt.ion()
        filePath = resource_path(os.path.dirname(os.path.abspath(__file__))) + "\\sentiment-output.txt"
        sentiment_output = open(filePath, "r").read()
        sentiment_list = sentiment_output.split('\n')

        xValues = []
        yValues = []

        x = 0
        y = 0

        for sentiment in sentiment_list:
            x += 1
            if "pos" in sentiment:
                y += 1
            elif "neg" in sentiment:
                y -= 1

            xValues.append(x)
            yValues.append(y)

        subplot.clear()
        subplot.plot(xValues, yValues)
    except Exception:
        box.showinfo("File missing.", message="Check sentiment-output.txt is in dist folder.")
        window.destroy()


# stream method which is attached to tkinter run button, this method sets the global var connected as true which allows
# the stream listener to work. It then opens the sentiment output file and clears it of any previous analysis. Finally
# it calls the connect method from below.
def stream(SearchTerm):
    try:
        global connected
        connected = True
        filePath = resource_path(os.path.dirname(os.path.abspath(__file__))) + "\\sentiment-output.txt"
        output = open(filePath, "r+")
        output.truncate(0)
        connect(SearchTerm)
    except Exception:
        box.showinfo("Connection error.", message="Check Internet connection.")


# Connect method which is called in stream method. This establishes the connection to the twitter API and streams tweets
# which contain the SearchTerm string that the user enters. We only get english tweets as the algorithms are only
# trained on english language data.
def connect(SearchTerm):
    try:
        auth = OAuthHandler(ckey, csecret)
        auth.set_access_token(atoken, asecret)
        # The method Stream is not the same as my method above. With a capital S this is a class of the tweepy package
        twitterStream = Stream(auth, Listener())
        twitterStream.filter(track=[SearchTerm], languages=["en"])
    except Exception:
        box.showinfo("Connection error.", message="Check Internet connection.")


# Stream listener class, this is what allows the application to update itself on data being received live from twitter
class Listener(StreamListener):

    # on data method, load the tweets from json into text and id vars. The tweet text is run through
    # sentimentMod.sentiment to get the classification and the confidence
    def on_data(self, data):
        try:
            global tweetlist
            all_tweets = json.loads(data)
            tweet = all_tweets['text']
            tweet_id = all_tweets['id']
            classification, confidence = sentimentMod.sentiment(tweet)
            # Write the output for each instance into the tweetList, this will be displayed in front end
            tweetlist.insert('end', str(classification) + ' --|-- ' + str(confidence) + ' --|-- ' + str(tweet) + '\n')
            tweetlist.insert('end', 'https://twitter.com/twitter/statuses/' + str(tweet_id) + '\n')
            # Check that the confidence of our voted classifier is above the human agreement threshold
            # If so we store the output of the classification in the sentiment output file
            if confidence * 100 >= 65:
                filePath = resource_path(os.path.dirname(os.path.abspath(__file__))) + "\\sentiment-output.txt"
                output = open(filePath, "a")
                output.write(classification)
                output.write('\n')
                output.close()

                # if connected return true else return false means that when we click stop in front end and connected
                # is set to false the listener will stop, until the run button is pressed again allowing the connect
                # var to return to true
                if connected:
                    return True
                else:
                    return False
        except Exception:
            box.showinfo("Connection error.", message="Check Internet connection.")

    # error handling method, which will display an error message in a tkinter box
    def on_error(self, status):
        box.showinfo('Info', message=status)

    # similar method to above, only displays if you exceed limit for connection to twitter Api, this is important as if
    # you get bounced back and try to reconnect you will be locked out for a lot longer
    def on_limit(self, status):
        box.showinfo('Info', message='Rate limit exceeded, wait 15 minutes before trying again.')
        sleep(15 * 60)
        return True


# Main entry point of the application
if __name__ == "__main__":
    ckey = "Jof1GcuFS73t9cYBNXqJwNTEu"
    csecret = "FWiDTPYfCGbhWBzMHz4Lyd2mOehOIC1H91AAflmuXkxsK3aGOB"
    atoken = "964278597526704128-0IkCkkbM5jJi7SqlWrdanSL9BDAhPtd"
    asecret = "dbqPDhafa8VF5baSiOgip1fpH0eswnF4Wjr7AqISYjktg"
    # creating a tkinter window for the application front end
    window = tix.Tk()
    window.title("Sentiment Analysis Application")
    # Creating a top level window for logging in
    top = tkinter.Toplevel(height=720, width=1280)
    top.title("Login")
    # Connected set as true on launching the app
    connected = True

    # Stop method for button simply sets the global var connected as false. This will end the listener
    def stop():
        global connected
        connected = False

    # Clicked method, This starts two threads. There is one thread for the stream method which links to the listener.
    # The other thread is for the showplot method so that we can get our live graph
    # Each thread is a daemon so that there are no negative interactions with the main tkinter thread
    def clicked(SearchTerm):
        thread1 = threading.Thread(target=lambda searchTerm=SearchTerm: stream(SearchTerm))
        thread1.setDaemon(True)
        thread1.start()
        if plt.fignum_exists(1):
            box.showinfo("hi")
        thread2 = threading.Thread(target=showPlot())
        thread2.setDaemon(True)
        thread2.start()

    # Login method checks if the keys entered by the user are the same length as my keys. If they are then the keys are
    # accepted and the application is launched. This means that multiple users can have their own developer account and
    # use the app simultaneously
    def login():
        global ckey
        global csecret
        global atoken
        global asecret
        if len(makeSafe(consumerKeyEntry.get())) == len(ckey) and len(makeSafe(consumerSecretEntry.get())) == len(csecret) and \
                len(makeSafe(authTokenEntry.get())) == len(atoken) and len(makeSafe(authSecretEntry.get())) == len(asecret):
            ckey = makeSafe(consumerKeyEntry.get())
            csecret = makeSafe(consumerSecretEntry.get())
            atoken = makeSafe(authTokenEntry.get())
            asecret = makeSafe(authSecretEntry.get())
            window.deiconify()
            top.destroy()
        else:
            box.showinfo('Info', message='Invalid Login')

    # simple callback method which allows the user to access the url I have included in the login window
    def callback(url):
        try:
            webbrowser.open_new(url)
        except Exception:
            box.showinfo("Connection error.", message="Check Internet connection.")

    # checkQuit method which asks the user if they want to exit the application without logging in
    def checkQuit():
        msgBox = tkinter.messagebox.askquestion('Quit', "Are you sure you want to exit without logging in?")
        if msgBox == 'yes':
            window.destroy()

    # Method which allows users to access the tweet hyperlink in the tweetList
    def tweetCallback(url):
        try:
            url = tweetlist.get(ACTIVE)
            if 'https://twitter.com/twitter/statuses/' in url:
                webbrowser.open_new(url)
            else:
                pass
        except Exception:
            box.showinfo("Connection error.", message="Check Internet connection.")

    # Method which allows user to clear the tweetList for a new analysis
    def clearTweetList():
        tweetlist.delete(0, tkinter.END)


    # Styling the login window
    top_background_label = tkinter.Label(top, bg='#00EEFF')
    top_background_label.place(relwidth=1, relheight=1)
    consumerKeyEntry = tkinter.Entry(top)
    consumerSecretEntry = tkinter.Entry(top)
    authTokenEntry = tkinter.Entry(top)
    authSecretEntry = tkinter.Entry(top)
    # Introduction label for new users
    introductionLabel = tkinter.Label(top, text='Welcome to the Twitter Sentiment Analysis App. \n In order to have a '
                                                'fully working version for each user you must create a Twitter Api '
                                                'developer account and enter the Api keys below. \n This will allow '
                                                'you to pull the tweets for sentiment analysis.', bg='#00EEFF',
                                      font='Helvetica 14 bold')
    introductionLabel.place(anchor='center', relx=.5, rely=.05)
    # Hyperlink to twitter dev page for first time users
    link1 = tkinter.Label(top, text="Visit Twitter Developer page here.", fg="blue", cursor="hand2", bg="#FFFFFF")
    link1.place(anchor='center', relx=.5, rely=.12)
    link1.bind("<Button-1>", lambda e: callback("https://developer.twitter.com/en/apply-for-access"))
    # button 1 = login. When clicked this will call the login method
    topButton1 = tkinter.Button(top, text="Login", command=lambda: login(), bg='#90EE90', font='Helvetica 14 bold')

    # button 2 = cancel. When clicked this will call the cancel method
    topButton2 = tkinter.Button(top, text="Cancel", command=lambda: checkQuit(), bg='#F08080', font='Helvetica 14 bold')
    # Further styling of the login window
    consumerKeyLabel = tkinter.Label(top, text="Enter Consumer Key", bg='#00EEFF', font='Helvetica 14 bold')
    consumerSecretLabel = tkinter.Label(top, text="Enter Consumer Secret", bg='#00EEFF', font='Helvetica 14 bold')
    authTokenLabel = tkinter.Label(top, text="Enter Authentication Token", bg='#00EEFF', font='Helvetica 14 bold')
    authSecretLabel = tkinter.Label(top, text="Enter Authentication Secret", bg='#00EEFF', font='Helvetica 14 bold')
    consumerKeyEntry.place(anchor='center', relx=.5, rely=.2, relheight=.1, relwidth=.3)
    consumerKeyLabel.place(anchor='w', relx=.01, rely=.2, relheight=.1, relwidth=.2)
    consumerSecretEntry.place(anchor='center', relx=.5, rely=.4, relheight=.1, relwidth=.3)
    consumerSecretLabel.place(anchor='w', relx=.01, rely=.4, relheight=.1, relwidth=.2)
    authTokenEntry.place(anchor='center', relx=.5, rely=.6, relheight=.1, relwidth=.3)
    authTokenLabel.place(anchor='w', relx=.01, rely=.6, relheight=.1, relwidth=.2)
    authSecretEntry.place(anchor='center', relx=.5, rely=.8, relheight=.1, relwidth=.3)
    top.bind('<Return>', (lambda event: login()))
    top.bind('<Escape>', (lambda event: checkQuit()))
    authSecretLabel.place(anchor='w', relx=.01, rely=.8, relheight=.1, relwidth=.2)
    topButton1.place(relx=.8, rely=.4, relheight=.2, relwidth=.2)
    topButton2.place(relx=.8, rely=.6, relheight=.2, relwidth=.2)
    topTipLabel = tkinter.Label(top, text="Enter key can be used to log in. \n"
                                          "Escape key can be used to exit.",
                                bg='#00EEFF', font='Helvetica 14 bold')
    topTipLabel.place(anchor='se', relx=1, rely=1)
    # styling the main window
    main_background_label = tkinter.Label(window, bg='#00EEFF')
    main_background_label.place(relwidth=1, relheight=1)

    frame = tkinter.Frame(window, bg='#80c1ff', bd=5)
    frame.place(relx=.5, rely=.1, relwidth=.75, relheight=.1, anchor='n')

    entry = tkinter.Entry(frame, font=40)
    entry.place(relwidth=.5, relheight=1)

    # run button which will take entry from above and pass to a call on the clicked method
    button1 = tkinter.Button(frame, text='Run', font=40, command=lambda: clicked(makeSafe(entry.get())))
    button1.place(relx=.55, relheight=1, relwidth=.25)
    entry.bind('<Return>', (lambda event: clicked(makeSafe(entry.get()))))
    tip1 = Balloon(window)
    tip1.bind_widget(button1, balloonmsg="The run button will search for live tweets based on the search term. The "
                                         "output can be viewed below or in the animated graph that will pop up.")

    # stop button which calls the stop method
    button2 = tkinter.Button(frame, text='Stop', font=40, command=lambda: stop())
    button2.place(relx=.8, relheight=1, relwidth=.2)
    tip2 = Balloon(window)
    tip2.bind_widget(button2, balloonmsg="The stop button will stop the stream of tweets so that you can review "
                                         "the analysis before saving or closing.")

    # Styling the output box in the main window
    lower_frame = tkinter.Frame(window, bg='#80c1ff', bd=10)
    lower_frame.place(relx=.5, rely=.22, relwidth=.75, relheight=.6, anchor='n')

    label = tkinter.Label(lower_frame)
    label.place(relwidth=1, relheight=1)

    applicationInformation = tkinter.Label(window, text="This is the main window of the application, please enter a "
                                                        "search term to start streaming tweets, \n once you start "
                                                        "receiving tweets they will be displayed with the sentiment "
                                                        "and a link to the tweet in the list below. \n A graph will "
                                                        "also open plotting the sentiment.", font='Helvetica 14 bold', bg='#00EEFF')
    applicationInformation.place(anchor='n', relx=.5, rely=0)

    helpfulTips2 = tkinter.Label(window, text="Tips for new Users: \n"
                                              "--Enter key can be used to search.-- \n"
                                              "--Escape key can be used to clear tweet list.-- \n"
                                              "--Buttons have tooltips to further explain if you hover over them.-- \n"
                                              "--The graph will open in a new window which can be saved before closing "
                                              "and launching a new one.-- \n"
                                              "--The links below each tweet can be double clicked to open the tweet in "
                                              "a browser-- "
                                 , bg='#00EEFF', font='Helvetica 12 bold')
    helpfulTips2.place(anchor='s', relx=.5, rely=1)

    # Adding a scrollbar for large amounts of data
    vScrollbar = tkinter.Scrollbar(lower_frame)
    vScrollbar.pack(side='right', fill='y')
    hScrollbar = tkinter.Scrollbar(lower_frame, orient='horizontal')
    hScrollbar.pack(side='bottom', fill='x')
    tweetlist = tkinter.Listbox(label, yscrollcommand=vScrollbar.set, xscrollcommand=hScrollbar.set)
    # binding a callback function so that users can double click the tweet links and be brought to the tweet in their
    # browser
    tweetlist.bind("<Double-Button-1>", tweetCallback)
    tweetlist.bind('<Escape>', (lambda event: clearTweetList()))
    tweetlist.place(relwidth=1, relheight=1)
    vScrollbar.config(command=tweetlist.yview)
    hScrollbar.config(command=tweetlist.xview)
    # withdraw the main window so it is not seen before logging in
    window.withdraw()
    # set the window geometry and initialize it
    window.geometry('1280x720')
    top.protocol("WM_DELETE_WINDOW", lambda arg=top: checkQuit())
    window.mainloop()
