# E7_RTA_Data

Collects data from the official [E7 match history website](https://epic7.gg.onstove.com) API.

# Usage
## Data collection
```
main.py --update
```
Download the list of players in each region who have data in RTA

```
main.py --filter --cores n
```
Filter the aforementioned file to get a list of players in each region with emperor or legend rank
>[!NOTE]
>This process will take an absurd amount of time since it will do an API call for each player in each file.  
>You can reduce the time it takes by increasing the number of cores allocated to the task

>[!Warning]
>Increasing the number of cores might cause problems in the final file due to multiple cores trying to write on the same file simultaneously.  
>Feel free to modify the code so that each worker writes in a different file and merge all files at the end

```
main.py --load --region [asia, global, eu, jpn, kor]
```
Load all available matches for all players previously filtered.
>[!NOTE]
>You might see in the code that a core option is available, but the process is fast enough for one core (since the number of players is lower than the filter task and a single request is done for each players and not for each matches)  
>If you want to use multiple cores for this task, it is mandatory to solve the simultaneous writing problem.

>[!NOTE]
>To filter multiple regions at once, use
>```
>main.py --load --region asia global eu
>```
>for example to process players from asia, global and eu regions.


## Data processing
```
main.py --preprocess
```
Transform the collected data 
is_win | ally_hero_0 | ally_hero_0_art | ally_hero_0_set1 | ally_hero_0_set2 | ally_hero_0_set3 | ... | enemy_hero_0 | enemy_hero_0_art | enemy_hero_0_set1 | enemy_hero_0_set2 | enemy_hero_0_set3 | ...
--- | --- | --- | --- |--- |--- |--- |--- |--- |--- |--- |--- |---

for each character that is not banned.  
Will then proceed to label encoding and shuffle the ally hero data to create the same data with different order for heroes input.

>[!NOTE]
>Feel free to change the data processing part to fit your model

#Requirement
Tested with python 3.10  
Required libraries:
```
requests
tqdm
pandas
scikit-learn
numpy
argparse
```
