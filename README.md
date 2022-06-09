# ghScouting

  

## Introduction
ghScouting is the scouting app used by Team 1189. It hosts a flask server (on port 5000), and logs data into an Sqlite database, which can be converted to a CSV file for easy manipulation. It's configured using a YAML config file, specifying which data you wish to log. Once you've collected your scouting data, you can merge the data from your scouters and analyze it to help make informed decisions during alliance selection.
  

## Setup
Complete the following installations:
```
$pip install -r requirements.txt
```
This program will be run on each scouting device. Ex. A game involving 6 robots per match would have 6 scouters each with their own device, and this app will run separately on all of them.

  

## Configuration
Create a yaml file as follows:

1 - The file should normally start with the following:
```
page_type: form
gearheads_banner:
	type: image
	filename: gearheads.png
	position: top
matchnum:
	type: number
	display: Match Number
	position: float
	required: true
team:
	type: number
	display: Team Number
	position: float
	required: true
...
Game-specific questions
...
submit_button:
	type: submit
	method: post
	text: Submit
```

  

2 - Game-specific questions have the following format:
 ([] = should be filled in)
```
[question name (not shown to scouter)]:
	type: [question type]
	display: [question name shown to scouter]
	...
	more options that are dependent on the type of question
	...
```
3 - Question types:
 - Number: Scouter enters a, well, number
	 - min: specifies min value allowed
ex. `min: 0`

- Radio: Multiple choice

	- options: a list of choices provided to scouter
	   ex . 
	   ```
	   options: 
		   -'Apples'
		   - 2
		   - 'Oranges'
		```
- checkbox: Multiple choice that allows multiple answers (i.e. a checkbox)


	- options: a list of choices provided to scouter (similar to above)
	   ex . 
	   ```
	   options: 
		   -'Apples'
		   - 2
		   - 'Oranges'
		```

- textarea: an area where scouters input text (kinda self-explanatory)

4 - In config/config.yml, change the value of `default` to the name of your config file (without the extension).
ex. `default: my_cool_config_file`

## Usage
Once this project is installed on all scouting devices, run the wsgi.py file to start the app. Then, open [http://localhost:5000/\[config file name without yaml extension\]](http://localhost:5000/%5Bconfig%20file%20name%20without%20yaml%20extension%5D) on a browser to log the data. Once matches are over, open [http://localhost:5000/\[config file name without yaml extension\]/csv](http://localhost:5000/%5Bconfig%20file%20name%20without%20yaml%20extension%5D/csv) to recieve a csv file in string format containing the logged data. It also generates a csv file in the root directory called `eggs.csv` that contains the logged data.