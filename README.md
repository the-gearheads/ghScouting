# ghScouting

  

## Introduction
ghScouting is Team 1189's scouting app. The purpose of this app is to provide a seamless method of logging the performance of FRC teams during matches. Teams must create a config file following the syntax explained below in order to configure the particular data that will be logged. Then, this app runs a flask server on port 5000, where scouters can input information regarding the performance of a team in a specific match. The data is then saved to a DB file, which can easily be converted to a .csv to view the data more easily. The data of several scouters can then be compounded and analyzed by the scouting team to make informed decisions during alliance selection.

  

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
Once this project is installed on all scouting devices, run the wsgi.py file to start the app. Then, open http://localhost:5000/[config file name without yaml extension] on a browser to log the data. Once matches are over, open http://localhost:5000/[config file name without yaml extension]/csv to recieve a csv file in string format containing the logged data. It also generates a csv file in the root directory called `eggs.csv` that contains the logged data.