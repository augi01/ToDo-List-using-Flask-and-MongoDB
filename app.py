from flask import Flask, render_template,request,redirect,url_for # For flask implementation
from pymongo import MongoClient # Database connector
from bson.objectid import ObjectId # For ObjectId to work
from bson.errors import InvalidId # For catching InvalidId exception for ObjectId
import os

mongodb_host = os.environ.get('MONGO_HOST', 'localhost')
mongodb_port = int(os.environ.get('MONGO_PORT', '27017'))
client = MongoClient(mongodb_host, mongodb_port)    #Configure the connection to the database
db = client.camp2016    #Select the database
todos = db.todo #Select the collection

app = Flask(__name__)
title = "TODO with Flask"
heading = "ToDo Reminder"
#modify=ObjectId()

def redirect_url():
	return request.args.get('next') or \
		request.referrer or \
		url_for('index')

@app.route("/list")
def lists ():
	#Display the all Tasks
	todos_l = todos.find()
	a1="active"
	return render_template('index.html',a1=a1,todos=todos_l,t=title,h=heading)

@app.route("/")
@app.route("/uncompleted")
def tasks ():
	#Display the Uncompleted Tasks
	todos_l = todos.find({"done":"no"})
	a2="active"
	return render_template('index.html',a2=a2,todos=todos_l,t=title,h=heading)


@app.route("/completed")
def completed ():
	#Display the Completed Tasks
	todos_l = todos.find({"done":"yes"})
	a3="active"
	return render_template('index.html',a3=a3,todos=todos_l,t=title,h=heading)

@app.route("/done")
def done ():
	#Done-or-not ICON
	id=request.values.get("_id")
	task=todos.find({"_id":ObjectId(id)})
	if(task[0]["done"]=="yes"):
		todos.update_one({"_id":ObjectId(id)}, {"$set": {"done":"no"}})
	else:
		todos.update_one({"_id":ObjectId(id)}, {"$set": {"done":"yes"}})
	redir=redirect_url()	# Re-directed URL i.e. PREVIOUS URL from where it came into this one

#	if(str(redir)=="http://localhost:5000/search"):
#		redir+="?key="+id+"&refer="+refer

	return redirect(redir)

#@app.route("/add")
#def add():
#	return render_template('add.html',h=heading,t=title)

@app.route("/action", methods=['POST'])
def action ():
	#Adding a Task
	name=request.values.get("name")
	desc=request.values.get("desc")
	date=request.values.get("date")
	pr=request.values.get("pr")
	todos.insert_one({ "name":name, "desc":desc, "date":date, "pr":pr, "done":"no"})
	return redirect("/list")

@app.route("/remove")
def remove ():
	#Deleting a Task with various references
	key=request.values.get("_id")
	todos.delete_one({"_id":ObjectId(key)})
	return redirect("/")

@app.route("/update")
def update ():
	id=request.values.get("_id")
	task=todos.find({"_id":ObjectId(id)})
	return render_template('update.html',tasks=task,h=heading,t=title)

@app.route("/action3", methods=['POST'])
def action3 ():
	#Updating a Task with various references
	name=request.values.get("name")
	desc=request.values.get("desc")
	date=request.values.get("date")
	pr=request.values.get("pr")
	id=request.values.get("_id")
	todos.update_one({"_id":ObjectId(id)}, {'$set':{ "name":name, "desc":desc, "date":date, "pr":pr }})
	return redirect("/")

@app.route("/search", methods=['GET'])
def search():
	#Searching a Task with various references

	key=request.values.get("key")
	refer=request.values.get("refer")
	if(refer=="id"):
		try:
			todos_l = todos.find({refer:ObjectId(key)})
			if not todos_l:
				return render_template('index.html',a2=a2,todos=todos_l,t=title,h=heading,error="No such ObjectId is present")
		except InvalidId as err:
			pass
			return render_template('index.html',a2=a2,todos=todos_l,t=title,h=heading,error="Invalid ObjectId format given")
	else:
		todos_l = todos.find({refer:key})
	return render_template('searchlist.html',todos=todos_l,t=title,h=heading)

@app.route("/about")
def about():
	return render_template('credits.html',t=title,h=heading)

# ==========================================
# NEW REST API FEATURE: TASK COMMENTS (CRUD)
# ==========================================
from flask import jsonify

# Select a new collection for our comments feature
comments_collection = db.comments

@app.route("/api/comments", methods=['POST'])
def create_comment():
    """CREATE: Add a comment to a task"""
    data = request.get_json()
    
    # Validation: Check if required fields exist
    if not data or 'task_id' not in data or 'text' not in data:
        return jsonify({"error": "Missing required fields: task_id and text"}), 400
        
    try:
        # Validate that the provided task_id is a valid MongoDB ObjectId
        task_id = ObjectId(data['task_id'])
    except InvalidId:
        return jsonify({"error": "Invalid task_id format"}), 400

    new_comment = {
        "task_id": task_id,
        "text": data['text'],
        "author": data.get('author', 'Anonymous')
    }
    
    result = comments_collection.insert_one(new_comment)
    new_comment['_id'] = str(result.inserted_id)
    new_comment['task_id'] = str(new_comment['task_id'])
    
    return jsonify(new_comment), 201


@app.route("/api/comments", methods=['GET'])
def get_all_comments():
    """READ ALL: Fetch all comments or filter by task_id"""
    task_id_query = request.args.get('task_id')
    query = {}
    
    if task_id_query:
        try:
            query['task_id'] = ObjectId(task_id_query)
        except InvalidId:
            return jsonify({"error": "Invalid task_id format in query parameter"}), 400

    comments_list = []
    for comment in comments_collection.find(query):
        comment['_id'] = str(comment['_id'])
        comment['task_id'] = str(comment['task_id'])
        comments_list.append(comment)
        
    return jsonify(comments_list), 200


@app.route("/api/comments/<string:comment_id>", methods=['PUT'])
def update_comment(comment_id):
    """UPDATE: Modify an existing comment's text"""
    try:
        oid = ObjectId(comment_id)
    except InvalidId:
        return jsonify({"error": "Invalid comment_id format"}), 400

    data = request.get_json()
    if not data or 'text' not in data:
        return jsonify({"error": "Missing field: text"}), 400

    # Check if comment exists
    existing = comments_collection.find_one({"_id": oid})
    if not existing:
        return jsonify({"error": "Comment not found"}), 404

    comments_collection.update_one({"_id": oid}, {"$set": {"text": data['text']}})
    
    existing['text'] = data['text']
    existing['_id'] = str(existing['_id'])
    existing['task_id'] = str(existing['task_id'])
    
    return jsonify(existing), 200


@app.route("/api/comments/<string:comment_id>", methods=['DELETE'])
def delete_comment(comment_id):
    """DELETE: Erase a comment"""
    try:
        oid = ObjectId(comment_id)
    except InvalidId:
        return jsonify({"error": "Invalid comment_id format"}), 400

    existing = comments_collection.find_one({"_id": oid})
    if not existing:
        return jsonify({"error": "Comment not found"}), 404

    comments_collection.delete_one({"_id": oid})
    return jsonify({"message": "Comment successfully deleted"}), 200

if __name__ == "__main__":
	env = os.environ.get('FLASK_ENV', 'development')
	port = int(os.environ.get('PORT', 5000))
	debug = False if env == 'production' else True
	app.run(debug=True)
	app.run(port=port, debug=debug)
	# Careful with the debug mode..