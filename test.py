from firebase_admin import credentials,db,initialize_app

databaseURL = 'https://task1-a7033-default-rtdb.firebaseio.com/'

cred_obj = credentials.Certificate('task1-a7033-firebase-adminsdk-cmgki-bf83ccca15.json')
default_app = initialize_app(cred_obj, {
	'databaseURL':databaseURL
	})
ref = db.reference("/rqeadings")

def listener(event):
    print(event.event_type)  # can be 'put' or 'patch'
    print(event.path)  # relative to the reference, it seems
    print(event.data)  # new data at /reference/event.path. None if deleted

ref.listen(listener)