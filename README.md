# To-Do-List

# DE GUZMANS EXPLANATION AT THE BOTTOM

To-Do-List is mini-project made with Flask and MongoDB. Dockerfile is also available to make docker image and docker containers.

## Built using :
```sh
	Flask : Python Based mini-Webframework
	MongoDB : Database Server
	Pymongo : Database Connector ( For creating connectiong between MongoDB and Flask )
	HTML5 (jinja2) : For Form and Table
```

## Set up environment for using this repo:
```
Install Python ( If you don't have already )
	$ sudo apt-get install python

Install MongoDB ( Make sure you install it properly )
	$ sudo apt install -y mongodb


Install Dependencies of the application (Flask, Bson and PyMongo)
	$ pip install -r requirements.txt
```

## Run the application
```
Run MongoDB
1) Start MongoDB
	$ sudo service mongod start
2) Stop MongoDB
	$ sudo service mongod stop

Run the Flask file(app.py)
	$ FLASK_ENV=development python app.py

Go to http://localhost:5000 with any of browsers and DONE !!
	$ open http://localhost:5000

To exit press Ctrl+C
```

## Using [Docker](https://www.docker.com) [Docker-Compose](https://docs.docker.com/compose)

Make sure that you are inside the project directory, where `docker-compose.yaml` file is present. Now, building and running the application server container and mongodb container using `docker-compose` :
```
Building or fetching the necessary images and later, creating and starting containers for the application
    $ docker-compose up -d

Go to http://localhost:5000 with any of browsers and DONE !!
    $ open http://localhost:5000
```

### Running, Debugging and Stopping the application under the hood
```
For almost all of the `docker-compose` commands, make sure that you are inside the project directory, where `docker-compose.yaml` file is present.

Passing `-d` flag along with docker-compose, runs the application as daemon
    $ docker-compose up -d

Seeing all of the logs from the application deployed.
    $ docker-compose logs

Stopping the application
    $ docker-compose down
```

## Screenshot :

![Screenshot of the Output](https://github.com/CoolBoi567/ToDo-List-using-Flask-and-MongoDB/blob/master/static/images/screenshot.jpg?raw=true "Screenshot of Output")

Thanks to Twitter for emoji support with [Twemoji](https://github.com/twitter/twemoji).

Made with ❤️ from Nepal 🇳🇵


---

## DE GUZMANS Enhancement: Task Comments REST API

I have extended the original author's codebase by implementing a native, machine-to-machine **REST API backend for Task Comments** on the `feature/api-crud` branch. 

###  Implementation and Explanation of The Architecture

* **Database Integration:** Initialized a new `comments` collection inside MongoDB.
* **Data Formatting:** All requests and responses strictly utilize **JSON** payloads.
* **Serialization:** Developed custom BSON-to-JSON utility handlers to cleanly serialize MongoDB ObjectIDs into standard string formats.

---

### 📖 OpenAPI / Swagger 3.0 Specification

```yaml
openapi: 3.0.3
info:
  title: ToDo Application - Task Comments REST API
  version: 1.0.0
  description: REST API endpoints for managing annotations and comments on tasks.
paths:
  /api/comments:
    post:
      summary: Create a new task comment
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required:
                - task_id
                - text
              properties:
                task_id:
                  type: string
                  example: "62da1234567890abcdef1234"
                text:
                  type: string
                  example: "This is a critical sub-task note."
      responses:
        '201':
          description: Comment created successfully
        '400':
          description: Bad Request (Missing required fields)
    get:
      summary: Retrieve task comments
      parameters:
        - name: task_id
          in: query
          required: false
          schema:
            type: string
          description: Optional filter to retrieve comments for a specific task
      responses:
        '200':
          description: A JSON array of comment objects
          
  /api/comments/{id}:
    put:
      summary: Update an existing comment's text
      parameters:
        - name: id
          in: path
          required: true
          schema:
            type: string
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required:
                - text
              properties:
                text:
                  type: string
                  example: "Updated comment text."
      responses:
        '200':
          description: Comment updated successfully
        '400':
          description: Bad Request (Missing text field)
        '404':
          description: Comment ID not found
    delete:
      summary: Delete a comment
      parameters:
        - name: id
          in: path
          required: true
          schema:
            type: string
      responses:
        '200':
          description: Comment deleted successfully
        '400':
          description: Invalid ID format supplied
        '404':
          description: Comment ID not found
