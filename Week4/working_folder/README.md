## WEEK 4 DAY 1

In today's task we have to create the basic file structure of our project. We have created multiple folders because each folder has its own responsiblity, if we break this project becomes unmaintainable. The responsiblity of each folder is explained in <a href="ARCHITECTURE.md">.

To complete this task we need to know 4 main things:

<ol>
<li>JavaScript language</li>
<li>Node.js for runtime</li>
<li>Express framework</li>
<li>system desgin to understand architecture and patterns</li>
</ol>

<h5>HOW I COMPLETED TODAY'S TASK</h3>
I divided the whole task into four phases.
<h3>PHASE 1</h3>

<strong>STEP 1: </strong>

Created Project folder and initialized node in it. Name of our project folder is week4. After we initialized it <stong>package.json</strong> file is created. This file contains all the necessary details about our project like name, version, description,author, keywords, dependecies(libraries and modules which we have installed in our porject with their respective versions) etc.

<strong>STEP 2:</strong>

we have installed `dotenv` dependency for now, going to install rest as we move forward with the project. We use dotenv because node can not read `.env` file by default, so dotenv is used to load such files.

<strong>STEP 3:</strong>

next we are going to create all the folders which are mentioned in the task description.

<strong>STEP 4:</strong>

then we created .env.local file in our project root. This file will contain all the configuration of our project like port, runtime env etc. all the data is stored in the form of key value pairs. This basically is responsible for storing enviornment variables that are specific to one's local machine. we create this file in root because of two reasons:

<ol>
<li>It contains sensetive data like API Keys, database credentials which are meant to be private and not pushed on github. so to avoid the chances of it getting pushed on github we keep it out of our main app folder.</li>
<li>as this file contains configurations and data which needs to be used by or applied to the whole project folder we keep this in root and it also allows developers to configure enviornment seamlessly.</li>
</ol>

<strong>STEP 5:</strong>

now we coded config/index.js. in this file we first imported dotenv library and path module. the we checked or node env and if nothing is set then set our enviornment to local. next we defined a function to read and load the env file. this will help to set a port to our process. then we exported our config because it is a rule that configs should be centralized.

<strong>STEP 6:</strong>

create a test.js file in root. this is a temporary file used to test the working of the files we our creating. in this file we imported config so that we can test it and then console log it. we could see that our env is set to local and port to 3000 meaning it is working perfectly.

<h3>PHASE 2</h3>
our goal for this phase was to create a centralized logger. We need a logger because in production logs are not saved, there are no levels(info,warn,error etc) hence making debugging difficult.

<strong>STEP 1:</strong>

install winston. it is a popular library for node.js applications, desgined to provide a flexible and robust logging system. we are using this because it is highly customizable with features like multiple transports(could send logs to multiple destination simultaneously), has logging levels, custom formating, can include additional contextual metadata like request ID, User ID etc.

Other alternatives to winston are Pino, Bunyan, Signale, Morgan etc.

<strong>STEP 2:</strong>
create a utils/logger.js file.

<strong>STEP 3:</strong>
write code in this js file. first we imported winston followed by creating a logger instance which will be reused in the whole app. then we defined the log level to info as it provides a high-level overview of application's normal and expected operations without excessive details of lower levels. Basically info bht bade data ko filter out krk granular, per-transactiln message deta hai which are useful during development, making important events easier to spot. Then we defined the format on how we want our log to be displayed. we used timestamp method to store the time when a log is created. After this we will create a transport array which will tell ki log kahan jayega. for now we are storing our logs in logs/app.log. lastly we exported the logger so that it can be imported in whole project and we could log every entry exit made in our project.

<strong>STEP 4:</strong>
we would import our logger in test.js and check the working of logger. if it enters the logs in app.log then our system is working perfectly.

<h3>PHASE 3</h3>
The goal in this phase of task is to create database loader, this will check if the db is connected before loading the app and if not then app fails to start. We have created a seperate db loader because if we add this in index.js then startup flow would be messy, error would not be handeled and it would also create problems in scaling.

<strong>STEP 1:</strong>

install mongoose. it is an object data modelling library which provides structured, schema-based solution to interact with mongo db.

<strong>STEP 2:</strong>
create loaders/db.js.

<strong>STEP 3:</strong>
we write code in this file. first import mongoose, config and logger from logger.js. next define an async function for db connection. use await taaki jb tk db ready na ho app aage na bade. then create a startup confirmation message using logger.info followed by error handling of the db. if the connection fails then exit the app.

<strong>STEP 4:</strong>
update the config by adding dbUrl in it.

<strong>STEP 5:</strong>
update local env by adding local path to db_url.

<strong>STEP 6:</strong>
test the working. see for the log stating db connected.
