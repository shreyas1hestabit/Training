### system overview

### services breakdown

we have divided our system into 3 parts/containers

<strong>CLIENT</strong>

- UI of the browser, basically the part which is visible to the user.
- send http requests to the backend server
- does not contain any business logic or db access.
- used node.js and express
- port used is 5173

![cl](./screenshots/client.png)

<strong>SERVER</strong>

- acts like a kitchen where actual work takes place.
- handle API requests
- implement business logic
- communicate with MongoDB
- used nodejs and express
- port used is 3002

![se](/screenshots/server.png)

<strong>MONGODB</strong>

- contains the data for the application
- data is stored using docker volumes for persistence
- used mongodb
- port used 27017 (internal only)

### communication flow

```bash
client
   |---->communicates with server over HTTP
server
   |----->communicates using mongoDB protocol
mongoDB
```

### networking strategy

- Docker Compose creates a private bridge network
- Services communicate using service names instead of localhost
- Database is not exposed to the host for security reasons

### data persistence

- used docker volume so that mongodb data is not lost even after closing the application.
- did not used volumes in client or server containers.

### port mapping strategy

- client and server ports are exposed to the host for browser eccess.
- mongodb port is not exposed externally

### deployment flow

```bash
create a network using docker compose
                  |
mongodb container gets started
                  |
server is connected to mongodb
                  |
client starts and we can see UI in browser
```

### design decisions and alternatives

- we used seperate containers as:
<ul>
<li>improves scalability and isolation</li>
<li>allows independent service updates</li>
</ul>

- we used docker compose because:
<ul>
<li>allows single command deployment else we would need to start all the containers explicitly with 3 diff commands</li>
<li>simplified networking and configuration</li>
</ul>

- mongodb is a container because
<ul>
<li>to provide a consistent environment accross the application</li>
<li>also avoids host dependency issues</li>
</ul>

### benefits of this architecture

- clean seperated containers each with its own assigned task
- easy scaling and maintainance
