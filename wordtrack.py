#! /usr/bin/python
"""
Wordtrack (Griatch 2014)

Usage:
    wordtrack.py start [days [wordgoal]] | plot | <wordcount>

A wordcount tracker that mimics the word-counting mechanism of
NaNoWriMo (www.nanowrimo.org). No code of theirs were used and this is
not in any way related or endorsed by nanowrimo. I just thought their
display was nice and encouraging and would like to have it for other
times of the year too.

Start a tracking like this:

    wordtrack.py start [days [wordgoal]]

This will create a new file wordtrack.txt in the same directory, to
store the tracking information (this is an easily readable file).The
period always starts from the current day and you can only have on
period running at a time (if you run start again, you will start
over). You can define the length of your writing period and how many
words you want to attempt to write in that time.  Defaults are 30 days
and 50 000 words.

To update your word count, do:

    wordtrack.py <wordcount>

This registers your current word count and displays the current
statistics. You can update as many times as you want in a day, only
the latest will be stored.

You can make a plot of your current progress. For this you need
the matplotlib library:

    wordtrack.py plot

You can view the statistics for the current period by calling
wordtrack without arguments.
"""

USAGE = """
 Usage:
   python wordtrack [start [days [wordgoal]] | plot | <wordcount>]

    arguments:
      (no args) - show current statistics
      start  - start a new period, starting from today
         days - number of days in period (default 30)
         wordgoal - target # of words (default 50 000)
      plot - plot your progress (requires matplotlib)
      <wordcount> - store a new wordcount
"""

import sys
import math
import datetime

# default config values

DEFAULT_FILE = "./wordtrack.dat"
DEFAULT_TIME_PERIOD = 30
DEFAULT_WORDGOAL = 50000


def _read_wordtrack_file(filename):
    """
    Parses a wordcount file. The file is on
    the following format:

    # wordtrack data file.

    ----------------------
    startdate: YY-MM-DD
    enddate: YY-MM-DD
    wordgoal: NN
    day NN1: NN
    day NN2: NN
    day NN3: NN
    ...

    -----------------------
    ...

    """
    tracks = []
    data = []

    try:
        with open(filename, "r") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if line.startswith("---"):
                    # store previous data
                    if data:
                        tracks.append(data)
                    data = []
                    continue
                name, value = [part.strip() for part in line.split(":")]
                if name == "startdate":
                    startdate = [int(part) for part in value.split("-", 3)]
                    data.append(datetime.date(*startdate))
                elif name == "enddate":
                    enddate = [int(part) for part in value.split("-", 3)]
                    data.append(datetime.date(*enddate))
                elif name == "wordgoal":
                    data.append(int(value))
                elif name.startswith("day"):
                    data.append(int(value))
    except IOError:
        pass

    if data:
        # save any remaining the data
        tracks.append(data)
    return tracks


def _save_wordtrack_file(filename, tracks):

    """
    Save the track information to a file

    ----------------------
    startdate: YY-MM-DD
    enddate: YY-MM-DD
    wordgoal: NN
    day NN1: NN
    day NN2: NN
    day NN3: NN
    ...

    -----------------------
    ...
    """

    trackstring = """
-----------------------
startdate: %s
enddate: %s
wordgoal: %s
"""
    with open(filename, "w") as f:
        for track in tracks:
            # each track is a list
            # (startdate, enddate, wordgoal, day1, day2, ...)
            f.write(trackstring % (str(track[0]), str(track[1]), str(track[2])))
            daystring = "\n".join("day %i: %i" % (i+1, val) for i, val in enumerate(track[3:]))
            f.write(daystring)


def _stats(tracking_data):
    """
    Get statistics on the word count over time, as per nanowrimo.

    Input:
        wordcount_list - a list of integer word counts, one per day
        starting_date - a datetime.date object giving the starting point of the period.
        target_time_period - the number of days to write
        target_word_count - number of words aimed to write during time period
    """

    starting_date = tracking_data[0]
    ending_date = tracking_data[1]
    wordgoal = tracking_data[2]
    wordcount_list = tracking_data[3:]

    target_time_period = (ending_date - starting_date).days + 1
    current_day = (datetime.date.today() - starting_date).days + 1
    #current_day = (datetime.date(2014, 11, 25) - starting_date).days + 1

    days_remaining = target_time_period - current_day + 1
    total_words_written = wordcount_list[-1] if wordcount_list else 0
    target_average_word_count = float(wordgoal) / target_time_period if target_time_period else 0
    average_words_per_day = float(total_words_written) / current_day if current_day else 0
    words_written_today = 0
    if current_day == 1:
        words_written_today = wordcount_list[0]
    else:
        words_written_today = wordcount_list[-1] - wordcount_list[-2]
    words_remaining = wordgoal - total_words_written
    current_goal_day = current_day + int(math.ceil(words_remaining / average_words_per_day if average_words_per_day else 0))
    if current_goal_day != current_day:
        finish_date = datetime.date.today() + datetime.timedelta(current_goal_day - current_day)
    else:
        finish_date = "Not started yet!"
    needed_word_count = float(words_remaining) / days_remaining if days_remaining else 0

    # validation
    if days_remaining < 0:
        days_remaining = "Time passed!"
    if words_remaining < 0:
        words_remaining = "Goal reached!"
    if current_day > target_time_period:
        current_day = "Time passed!"

    return {"starting_date": starting_date,
            "ending_date": ending_date,
            "average_words_per_day": int(average_words_per_day),
            "words_written_today": words_written_today,
            "target_word_count": wordgoal,
            "target_average_word_count": int(math.ceil(target_average_word_count)),
            "total_words_written": total_words_written,
            "words_remaining": words_remaining,
            "current_day": current_day,
            "days_remaining": days_remaining,
            "finish_day": current_goal_day + 1, # needed for correct plot
            "finish_date": finish_date,
            "needed_word_count": int(math.ceil(needed_word_count))}


def _plot(tracking_data):
    """
    Use matplotlib to plot histogram and curve
    """
    try:
        from matplotlib import pyplot
    except ImportError:
        return "Plotting requires matplotlib, please install matplotlib and try again."
    wordcount_list = tracking_data[3:]
    stats = _stats(tracking_data)
    counts = wordcount_list + [0 for i in range(stats["days_remaining"] + 1)]
    Ncount = len(counts)
    days = [1 + i for i in range(Ncount)]
    target_average = [i * stats["target_average_word_count"] for i in range(Ncount)]
    current_average = [i * stats["average_words_per_day"] for i in range(Ncount)]
    x1, x2, y1, y2 = stats["finish_day"], Ncount, 0, stats["target_word_count"]
    gshade = ((x1,x1,x2,x2), (y1,y2,y2,y1))
    goal_line = ((x1,x1), (y1,y2))
    x1, x2, y1, y2 = Ncount, Ncount +2, 0, stats["target_word_count"]
    rshade = ((x1,x1,x2,x2), (y1,y2,y2,y1))
    deadline = ((x1,x1), (y1,y2))

    # creating the plots
    print "plotting ..."
    pyplot.close("all")
    fig, ax1 = pyplot.subplots()

    ax1.set_xlim(0, Ncount + 2)
    ax1.set_ylim(0, stats["target_word_count"] + 1)
    ax1.set_title("Wordtrack %s - %s" % (stats["starting_date"], stats["ending_date"]))
    ax1.set_xlabel("Day number")
    ax1.set_ylabel("Words written")
    ax1.plot(days, target_average, '--', c="r", linewidth=4, label="target average")
    ax1.plot(days, current_average, '*', c="b", linewidth=4, label="current average")
    ax1.fill(*gshade, alpha=0.2, color="g")
    ax1.plot(*goal_line, c="g")
    ax1.fill(*rshade, alpha=0.2, color="r")
    ax1.plot(*deadline, c="r")
    ax1.bar(days, counts, color="black")
    # ax1.legend(loc=2)
    ax1.text(0.03, 0.97, _display(stats), transform=ax1.transAxes, fontsize=10,
            horizontalalignment='left', verticalalignment='top',
            bbox={"boxstyle":"round", "alpha":0.2, "facecolor":"white"})
    pyplot.tight_layout()
    pyplot.show()


def _display(stats):
    """
    Take stats dictionary and display on same format as nanowrimo.
    """
    output = """
    Period: {starting_date} - {ending_date}

    Your average per day:  {average_words_per_day}
    Words written today:   {words_written_today}
    Target word count:     {target_word_count}
    Target average word
           count per day:  {target_average_word_count}
    Total words written:   {total_words_written}
    Words remaining:       {words_remaining}
    Current day:           {current_day}
    Days remaining:        {days_remaining}
    At this rate you
          will finish on:  {finish_date}
    Words per day to
          finish on time:  {needed_word_count}
    """
    return output.format(**stats)


# access functions

def wordtrack_display(filename=DEFAULT_FILE):
    """
    Show the word count in a nice list
    """
    tracks = _read_wordtrack_file(filename)
    current = tracks[-1] if tracks else []
    if current:
        return _display(_stats(current))


def wordtrack_plot(filename=DEFAULT_FILE):
    """
    Display a plot of the data
    """
    tracks = _read_wordtrack_file(filename)
    current = tracks[-1] if tracks else []
    if current:
        return _plot(current)


def wordtrack_update(filename=DEFAULT_FILE, wordcount=0):
    """
    Add or update wordcount in the data file
    """
    tracks = _read_wordtrack_file(filename)
    if not tracks:
        return

    current = tracks[-1] if tracks else []
    wordcount_list = current[3:]
    stats = _stats(current)

    if isinstance(stats["days_remaining"], basestring):
        print "Please start a new time period."
        return

    iday = max(0, stats["current_day"])
    nlist = len(wordcount_list)
    diff = nlist - iday
    if diff == -1:
        # new day - add new count
        wordcount_list.append(wordcount)
    elif diff < -1:
        # days with nothing written
        for i in range(abs(diff)):
            wordcount_list.append(0)
        wordcount_list.append(wordcount)
    else:
        # replace last count
        wordcount_list[iday - 1] = wordcount
    current = current[:3] + wordcount_list
    tracks[-1] = current
    _save_wordtrack_file(filename, tracks)
    stats = _stats(current)


def wordtrack_start(filename=DEFAULT_FILE, days=DEFAULT_TIME_PERIOD, wordgoal=DEFAULT_WORDGOAL):
    """
    Create a new wordcount record (this stops previous count)
    """
    startdate = datetime.date.today()
    enddate = startdate + datetime.timedelta(days)
    tracks = _read_wordtrack_file(filename)
    # create the new record and save it
    tracks.append([startdate, enddate, wordgoal, 0])
    _save_wordtrack_file(filename, tracks)


# Main call

if __name__ == "__main__":

    filename = DEFAULT_FILE
    argv = sys.argv
    nlen = len(argv)
    if nlen < 2:
        out = wordtrack_display(filename)
        print out if out else USAGE
    else:
        if argv[1].lower() in ("start", "s"):
            # start a new period
            days = DEFAULT_TIME_PERIOD
            wordgoal = DEFAULT_WORDGOAL
            if nlen > 2:
                days = int(argv[2])
            if nlen > 3:
                wordgoal = int(argv[3])
            wordtrack_start(filename=filename, days=days, wordgoal=wordgoal)
            print "Started new wordtrack period (%s days including today) with the goal of writing %s words. Good luck!" % (days, wordgoal)
        elif argv[1].lower() in ("plot", "p"):
            err = wordtrack_plot(filename=filename)
            if err:
                print err
        elif argv[1] in ("help", "h", "--help"):
            print USAGE
        elif argv[1].isdigit():
            # register a new word count
            wordtrack_update(filename, int(argv[1]))
            out = wordtrack_display(filename)
            print out if out else USAGE
        else:
            print "Malformed input. Use --help."
