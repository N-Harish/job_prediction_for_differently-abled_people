import pyrebase
import pickle

firebaseConfig = {
    "apiKey": "AIzaSyD9f3HFSy87eIdAdVBa2LGeZxiVXsXnSlY",
    "authDomain": "auth-b9834.firebaseapp.com",
    "databaseURL": "https://auth-b9834-default-rtdb.firebaseio.com",
    "projectId": "auth-b9834",
    "storageBucket": "auth-b9834.appspot.com",
    "messagingSenderId": "285880819001",
    "appId": "1:285880819001:web:a15af1c999b55b9cf39ce8",
    "measurementId": "G-MTPKM9Z4TR"
}

firebase1 = pyrebase.initialize_app(firebaseConfig)
db = firebase1.database()


def insertDetails(dict):
    db.child("Details").push({"Details": dict})


def insertPdf(pdfData):
    db.child("Pdf Data").push({"Resume Details": pdfData})


def load_model():
    le_eli = pickle.load(open('./models/labelencoder_eligibility.sv', 'rb'))

    le_sal = pickle.load(open('./models/labelencoder_salary.sv', 'rb'))

    eli_list = pickle.load(open('./models/eligibility_list.sv', 'rb'))

    sal_list = pickle.load(open('./models/Salary.sv', 'rb'))

    model = pickle.load(open('./models/model.sv', 'rb'))

    return eli_list, sal_list, le_eli, le_sal, model
