Wordtrack
=========

This is a wordcount tracker that mimics the word-counting mechanism
and statistics shown by [NaNoWriMo](www.nanowrimo.org) (National Novel
Writing Month), a nonprofit-run event where you attempt to write a
novel of 50 000 words during the month of November.

No code of theirs were used and this little program is not in any way
related or endorsed by the NaNoWriMo organization. I just thought
their display was nice and encouraging and would like to have it for
other times of the year too:

```
    Period: 2014-11-01 - 2014-11-30

    Your average per day:  2203
    Words written today:   1800
    Target word count:     50000
    Target average word
           count per day:  1667
    Total words written:   22037
    Words remaining:       27963
    Current day:           10
    Days remaining:        21
    At this rate you
          will finish on:  2014-11-23
    Words per day to
          finish on time:  1332
```


## Install

You need git and Python 2.7.

Just `cd` to place you want the program folder to end up and do

```
git clone https://github.com/Griatch/wordtrack.git
```

The program is run from the install folder.


## Usage

Wordtrack is run from the installation folder, in a terminal.

```
    python wordtrack [start [days [wordgoal]] | <wordcount>]
```


## Examples

Start a tracking like this:

```
    python wordtrack.py start
```

This will create a new file wordtrack.txt in the same directory. This
is the data file storing the wordcounts (it's easily human-readable). This
defaults to tracking a period of 30 days and a word-count goal of
50000 words (NaNoWriMo's default). The period always starts from the
current day.

You can specify other periods and word-goals. To set a period of 20
days and a word-goal of 30 000 words, do:

```
    python wordtrack.py start 20 30000
```

you can only have one
period running at a time (if you run `start` again, you will start
over).

To start updating your word count, check your text editor for your
current word count and give it as a number:

```
    wordtrack.py <wordcount>
```

This registers your current word count and displays the current
statistics. You can update as many times as you want in a day, only
the latest will be stored.

You can view the statistics for the current period by calling
wordtrack without arguments.
