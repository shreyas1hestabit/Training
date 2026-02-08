# specifying our base image
FROM node:latest 
# set current working directory inside the container. if folder does not exist docker creates on its own.
WORKDIR /app
# copying package.json from host machine
COPY package.json .
# build time command used to install all the dependencies mentioned in package.json
RUN npm install
# copy all the files of the current folder
COPY . .
# only for documentation -> tells that we are using port 3000.
EXPOSE 3000
# command to start our app in the container
CMD ["npm","start"]