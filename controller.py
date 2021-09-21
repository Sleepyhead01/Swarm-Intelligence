from api import *
import threading, os, sys, time

class myThread (threading.Thread):
   def __init__(self, botId):
      threading.Thread.__init__(self)
      self.botId = botId

   def run(self):
      os.system("python3 code.py "+str(self.botId))


level=0
numbots=1
while level == 0:
    level = int(input("Please enter level(1/2/3/4/5/6): "))
    if not (0 < level < 7):
        level = 0
        continue
    else:
        # TODO: Guided tour of the level
        if level == 1 or level == 2:
            numbots = 1
        elif level == 3 or level == 5:
            numbots = 2
        elif level == 4 or level == 6:
            numbots = max(min(8, int(input("Number of bots in play(max 8): "))),2)
        else:
            level = 0
            continue
print("Starting Level ", level," with ", numbots, "bot(s)")
set_new_map(level, numbots)
time.sleep(2)
if level == 1:
    os.system("python3 code.py 0")
    print("The final score is: " + str(get_score()))
elif level == 2:
    os.system("python3 code.py 0")
    print("The final score is: " + str(get_score()))
# elif level == 3:
#     os.system("python3 code.py 0")
#     print("The final score is: " + str(get_score()))
elif level == 3:
    threads = []
    for i in range(2):
        thread = myThread(i)
        threads.append(thread)
        thread.start()
    for t in threads:
        t.join()
    print("The final score is: "+str(get_score()))

# elif level == 4:
    # os.system("python3 code.py 0")
    # print("The final score is: " + str(get_score()))    
elif level == 4:
    threads = []
    for i in range(get_numbots()):
        thread = myThread(i)
        threads.append(thread)
        thread.start()
    for t in threads:
        t.join()
    print("The final score is: "+str(get_score()))
elif level == 5:
    # os.system("python3 code.py 0")
    # print("The final score is: " + str(get_score()))    
    threads = []
    for i in range(2):
        thread = myThread(i)
        threads.append(thread)
        thread.start()
    for t in threads:
        t.join()
    print("The final score is: "+str(get_score()))
elif level == 6:
    # os.system("python3 code.py 0")
    # print("The final score is: " + str(get_score()))
    threads = []
    for i in range(get_numbots()):
        thread = myThread(i)
        threads.append(thread)
        thread.start()
    for t in threads:
        t.join()
    print("The final score is: "+str(get_score()))
