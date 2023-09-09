from flask import Flask, request, make_response, jsonify
from flask_cors import CORS
from flask_migrate import Migrate
import ipdb

from models import db, Message


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

CORS(app)
migrate = Migrate(app, db)

db.init_app(app)

@app.route('/messages', methods=['GET', 'POST'])
def messages( ):

    if request.method == 'GET':

        msg_list = []
        for message in Message.query.order_by(Message.created_at).all():
            message_dict = message.to_dict()
            msg_list.append(message_dict)
       
        response = make_response(
            msg_list,
            200
        )
        return response
    else:

        new_msg_dict = request.get_json()
        new_message = Message(body = new_msg_dict["body"],
                            username = new_msg_dict["username"])
        
        db.session.add(new_message)
        db.session.commit()

        new_msg_dict = new_message.to_dict()

        response = make_response(
            new_msg_dict,
            201
        )
        return response
        


@app.route('/messages/<int:id>', methods=['DELETE', 'PATCH'])
def messages_by_id(id):
    if request.method == 'DELETE':
        delete_msg = Message.query.filter(Message.id == id).first()
        db.session.delete(delete_msg)
        db.session.commit()

        response_body = {
            "delete_successful": True,
            "message": "Message deleted."    
        }

        response = make_response(
            response_body,
            200
        )
        return response
    else:
        # We be patchin'

        # Find the message to be patched in the database.
        patch_msg = Message.query.filter(Message.id == id).first()
        # Get the json form of the request and extract the "body" and 
        # enter it into the patch message.
        new_msg_dict = request.get_json()
        patch_msg.body = new_msg_dict["body"]
        db.session.add(patch_msg)
        db.session.commit()

  
        # Now return the JSON contents of the patch message
        patch_msg_dict = patch_msg.to_dict()
        response = make_response ( 
            patch_msg_dict,
            200
        )            
        
        return response

if __name__ == '__main__':
    app.run(port=5555, debug = True)
