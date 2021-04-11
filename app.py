from flask import Flask, render_template, request, redirect, session
import pandas as pd
import ast
import PyPDF2
from firebase import authentication, db
import pickle

app = Flask(__name__)
app.secret_key = "ReallySecret"


@app.route("/", methods=['GET', "POST"])
def poster():
    return render_template("poster.html")


@app.route('/login', methods=['GET', "POST"])
def login():
    return render_template("login.html")


@app.route("/info")
def info():
    return render_template("profile.html")


@app.route("/suggestion")
def suggestion():
    if "user" in session:

        return render_template("suggestion.html", user_name=session["user"])

    else:

        return render_template("login.html", login_fail="You have not logged in")


@app.route("/resume")
def resume():
    return render_template("resume_upload.html")


@app.route('/signup')
def signup():
    return render_template("signup.html")


@app.route('/home', methods=['GET', 'POST'])
def home():
    if "user" in session:
        eli_list, sal_list, le_eli, le_sal, model = db.load_model()

        leng_eli = len(list(eli_list))
        len_sal = len(list(sal_list))
        eli = request.form.get('eligibility')
        sal = request.form.get('salary')
        if request.method == "POST":
            hearing = request.form.get('hearing')
            vision = request.form.get('vision')
            learning_disability = request.form.get('learning_disability')
            mental_health = request.form.get('mental_health')
            other = request.form.get('other')

            test_data = pd.DataFrame(
                [
                    {"Hearing": int(hearing),
                     "Learning": int(learning_disability),
                     "Mental Health": int(mental_health),
                     "Other (Hand/Leg)": int(other),
                     "Vision": int(vision),
                     "Eligibility": eli,
                     'Salary': sal
                     }
                ]
            )

            test_data['Salary'] = le_sal.transform(test_data['Salary'])
            test_data['Eligibility'] = le_eli.transform(test_data['Eligibility'])

            pred = model.predict(test_data)[0]

            return render_template('home.html', leng_eli=leng_eli,
                                   list_eli=list(eli_list), len_sal=len_sal,
                                   list_sal=list(sal_list), prediction=f'Predicted Job is {pred}',
                                   user_name=session["user"]
                                   )

        return render_template('home.html',
                               leng_eli=leng_eli,
                               list_eli=list(eli_list),
                               len_sal=len_sal,
                               list_sal=list(sal_list),
                               user_name=session["user"]
                               )
    else:
        return render_template("login.html", login_fail="You have not logged in")


@app.route('/recommend', methods=['GET', 'POST'])
def recommend():
    if "user" in session:

        list_eli, sal_list, le_eli, le_sal, model = db.load_model()
        leng_eli = len(list(list_eli))
        len_sal = len(list(sal_list))

        reccomend = pickle.load(open('./models/recommend_model.pkl', 'rb'))

        if request.method == "POST":
            eli = request.form.get('eligibility')
            sal = request.form.get('salary')

            test_data = pd.DataFrame(
                [
                    {
                        "Eligibility": eli,
                        'Salary': sal
                    }
                ]
            )

            test_data['Salary'] = le_sal.transform(test_data['Salary'])
            test_data['Eligibility'] = le_eli.transform(test_data['Eligibility'])

            pred = reccomend.predict(test_data)[0]

            job_data = pd.read_csv('./models/Recommended.csv')

            comp_list = ast.literal_eval(job_data.T[pred]['Recommended Job'])

            prediction = comp_list[0:5]

            return render_template('recommend.html', len_sal=len_sal,
                                   len_eli=leng_eli, list_eli=list_eli,
                                   list_sal=sal_list, prediction=prediction,
                                   user_name=session["user"]
                                   )

        return render_template('recommend.html', len_sal=len_sal,
                               len_eli=leng_eli, list_eli=list_eli,
                               list_sal=sal_list, user_name=session["user"]
                               )
    else:
        return render_template("login.html", login_fail="You have not logged in")


@app.route("/login_up", methods=['POST'])
def login_up():
    eli_list, sal_list, le_eli, le_sal, model = db.load_model()

    leng_eli = len(list(eli_list))
    len_sal = len(list(sal_list))

    username = request.form["username"]
    password = request.form["password"]

    lo = authentication.login1(username, password)

    if lo:

        user1 = authentication.userNameExtract(username)

        session["user"] = user1
        return render_template('home.html',
                               leng_eli=leng_eli,
                               list_eli=list(eli_list),
                               len_sal=len_sal,
                               list_sal=list(sal_list),
                               user_name=session["user"])

    else:
        return render_template("login.html", login_fail="You have entered wrong email or password")


@app.route('/sign_up', methods=['POST'])
def sign_up():
    email = request.form["email"]
    password = request.form["psw"]
    con_password = request.form["psw-repeat"]

    if password == con_password and len(password) >= 6:

        sign_up1 = authentication.signup1(email, password)

        if sign_up1:
            return render_template("login.html")

        else:
            return render_template("signup.html", signup_fail="Email already exists")

    elif password == con_password:
        return render_template("signup.html", signup_fail="Password must be at least 6 characters")

    else:
        return render_template("signup.html", pass_fail="Passwords not matching ")


@app.route("/logout", methods=["GET", "POST"])
def logout():
    session.pop("user", None)
    return render_template("login.html")


@app.route("/profile_up", methods=["POST"])
def profile_up():
    fullname = request.form["fullname"]
    tod = request.form["tod"]
    city = request.form["city"]
    tel = request.form["tel"]
    zip1 = request.form["zip"]
    dict1 = {"fullname": fullname, "tod": tod, "city": city, "tel": tel, "zip": zip1}
    db.insertDetails(dict1)
    return render_template("poster.html")


@app.route('/resume_up', methods=['POST'])
def resume_up():
    if 'file' not in request.files:
        return redirect(request.url)

    file = request.files.get('file')

    if not file:
        return render_template('resume_upload.html')

    reader = PyPDF2.PdfFileReader(file)
    size = reader.numPages
    lx = []

    for i in range(0, size):
        page = reader.getPage(i)
        pdfData = page.extractText()
        lx.append(pdfData)
        page_end = f"End of page {i + 1}"
        lx.append("\n")
        lx.append(f"*****************************{page_end} *****************************")
        lx.append("\n")

    result = "".join(lx)
    del lx
    db.insertPdf(result)
    return render_template("poster.html")


if __name__ == "__main__":
    app.run(debug=True)
