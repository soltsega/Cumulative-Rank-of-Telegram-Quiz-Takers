what i wanted to do?
It is writing a python script that can make a cumulative rank of telegram quiz bot top users

# What the data look like at first
🏆 Top results in the quiz 'የዮሐንስ ወንጌል'

🖊 5 questions
⏱ 45 seconds per question
🤓 24 people took the quiz

 🥇 @habtetsega – 5 (1 min 35 sec)
 🥈 @semwwn – 5 (2 min 28 sec)
 🥉 @BEING_MIAPHYSITE – 4 (45.6 sec)
  4.  @Secretmis – 4 (50.4 sec)
  5.  @thanna_347 – 4 (55 sec)
  6.  @dagiheb – 4 (1 min 2 sec)
  7.  @bellabest – 4 (1 min 7 sec)
  8.  @Hc2812 – 4 (1 min 10 sec)
  9.  @Gebre_selasie – 4 (1 min 10 sec)
 10.  @Aklilu000 – 4 (1 min 11 sec)
 11.  @Mis_iraq – 4 (1 min 12 sec)
 12.  @Psa_lm19 – 4 (1 min 31 sec)
 13.  @bruktawit16 – 4 (1 min 44 sec)
 14.  @Nablis_21 – 3 (46.9 sec)
 15.  @tsedal_12 – 3 (1 min 3 sec)
 16.  @jordaw – 3 (1 min 5 sec)
 17.  @herrybm97 – 3 (1 min 8 sec)
 18.  @nathy2127 – 3 (1 min 24 sec)
 19.  @infinity21B – 3 (1 min 26 sec)
 20.  @Hemen6254 – 2 (52.8 sec)
 ...
 ..
 .


 🏆 Top results in the quiz 'የዮሐንስ ወንጌል'

🖊 5 questions
⏱ 45 seconds per question
🤓 23 people took the quiz

 🥇 @Nablis_21 – 5 (1 min 12 sec)
 🥈 @Bersi3_19 – 5 (1 min 13 sec)
 🥉 @dagiheb – 5 (1 min 31 sec)
  4.  @MAFIt3 – 4 (54.7 sec)
  5.  @Aklilu000 – 4 (59.8 sec)
  6.  @BEING_MIAPHYSITE – 4 (1 min 1 sec)
  7.  @Psa_lm19 – 4 (1 min 15 sec)
  8.  @bellabest – 4 (1 min 26 sec)
  9.  @Mis_iraq – 4 (1 min 27 sec)
 10.  @jordaw – 4 (1 min 49 sec)
 11.  @herrybm97 – 4 (2 min 6 sec)
 12.  @semwwn – 4 (1 min 50 sec)
 13.  @Gebre_selasie – 3 (1 min 6 sec)
 14.  @Hc2812 – 3 (1 min 20 sec)
 15.  @infinity21B – 3 (1 min 47 sec)
 16.  @Souljom – 2 (33.4 sec)
 17.  @Secretmis – 2 (52.9 sec)
 18.  @Jude2124 – 2 (1 min 11 sec)
 19.  @Semi2424 – 2 (1 min 49 sec)
 20.  @nathy2127 – 2 (2 min 14 sec)
 ...
 ..
 .


 the number of quzzes may be about 20-30+ but it has to handle more than that

 # what we will do to preprocess?
 - Removing the appendages at the beginning of the data
 like this:
```
🏆 Top results in the quiz 'የዮሐንስ ወንጌል'

🖊 5 questions
⏱ 45 seconds per question
🤓 24 people took the quiz
```
the script will remove the appendages and save the data in a csv file. It will take advantage of the keywords or symbols or emoji's
# What the script will do?
1. Preprocess the data
2. Make a cumulative rank of the users
What the script will consider to make a rank:
- the number of quizzes the user took. the user that took as many quizzes as possible will be at the top. This portio will take 20% of the score
- the average time the user took to answer the quiz. the user that took the least time will be at the top. This portio will take 40% of the score. Example: if the user took 20 quizzes, then the sript will add the total time and divide it by 20 to get the average time. take care here not to divide by the total quizzes provided but the number of quizzes the user took. the provider might have provided a total number of quizzes but the user might have taken less quizzes
- the the average score of correct answers the user got. The script will first calculate the score of each user and then the user that got the most score will be at the top. Example: if the user took 20 quizzes, then the sript will add the total score and divide it by 20 to get the average score. This portio will take 40% of the score
3. Save the data in a csv file
4. Make a cumulative rank of the users
5. 