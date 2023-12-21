# Cryptography-Project
## Environment initialization
Windows: `MyProjectEnvt\Scripts\activate.bat`

Linux: `source MyProjectEnvt/bin/activate`
Once the environment is activated, you will see this result in the command prompt:

Windows: `(MyProjectEnvt) C:\Users\...\Cryptography-Project>`

Linux: `(MyProjectEnvt) $ /home/.../Cryptography-Project$`

## Install dependencies
Windows: `(MyProjectEnvt) C:\Users\...\Cryptography-Project> py -m install Django`

Linux: `(MyProjectEnvt) $ /home/.../Cryptography-Project$ pip install Django`

**This repo has already set up a project - [Cryptography-Project/website](https://github.com/lanphuongnt/Cryptography-Project/tree/main/Cryptography-Project/website)**.

To run the project, you need to go to the directory `Cryptography-Project/website` and run the command:
`(MyProjectEnvt) C:\Users\...\Cryptography-Project\website> py manage.py runserver`

**This repo has already set up an app - [Cryptography-Project/website/myfirstapp](https://github.com/lanphuongnt/Cryptography-Project/tree/main/Cryptography-Project/website/myfirstapp)**

## Connect to the database
First, we need to install PyMongo:
```
pip install pymongo
pip install dnspython
```
Using PyMongo, we can concurrently run multiple databases by specifying the right database name to the connection instance.

Let us create a sample pymongo session. There are two approaches for this:

1. We can create a client in the utils file that can be used by any view that wants to interact with MongoDB. Create a utils.py file in your project folder (same location as manage.py) and instantiate the client:
```python
from pymongo import MongoClient
def get_db_handle(db_name, host, port, username, password):

 client = MongoClient(host=host,
                      port=int(port),
                      username=username,
                      password=password
                     )
 db_handle = client['db_name']
 return db_handle, client
```
This method can then be used in `./myfirstapp/view.py`.

2. Another approach to get the connection is to use the connection_string:
```python
from pymongo import MongoClient
client = MongoClient('connection_string')
db = client['db_name']
```
where
```python
connection_string = "mongodb+srv://<username>:<password>@<cluster-address>/test?retryWrites=true&w=majority"
```
For example:
```python
makemyrx_db = client['sample_medicines']
#collection object
medicines_collection = makemyrx_db['medicinedetails']
```

# dupliCat3