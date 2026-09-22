from flask import Flask, request, render_template_string
import requests

app = Flask(__name__)

# Main Certificate Validation Backend
BACKEND_URL = "https://certichain-jrxk.onrender.com"


# =========================================================
# MOCK COLLEGE HOME PAGE
# =========================================================

@app.route("/", methods=["GET"])
def home():

    return render_template_string("""
<!DOCTYPE html>
<html>

<head>

    <title>Mock College Certificate Registration</title>

    <meta name="viewport" content="width=device-width, initial-scale=1">

    <style>

        body {
            margin: 0;
            font-family: Arial, sans-serif;
            background: #f1f5f9;
            color: #1e293b;
        }

        .header {
            background: #123c69;
            color: white;
            padding: 25px;
            text-align: center;
        }

        .header h1 {
            margin: 0;
            font-size: 28px;
        }

        .header p {
            margin: 8px 0 0;
        }

        .container {
            max-width: 850px;
            margin: 35px auto;
            padding: 0 20px;
        }

        .card {
            background: white;
            padding: 30px;
            border-radius: 12px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        }

        .card h2 {
            color: #123c69;
            margin-top: 0;
        }

        .row {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
        }

        .field {
            margin-bottom: 18px;
        }

        label {
            display: block;
            font-weight: bold;
            margin-bottom: 7px;
        }

        input {
            width: 100%;
            box-sizing: border-box;
            padding: 12px;
            border: 1px solid #cbd5e1;
            border-radius: 7px;
            font-size: 15px;
        }

        button {
            width: 100%;
            padding: 14px;
            background: #1769d1;
            color: white;
            border: none;
            border-radius: 7px;
            font-size: 16px;
            font-weight: bold;
            cursor: pointer;
        }

        button:hover {
            background: #0f55ad;
        }

        .info {
            margin-top: 20px;
            padding: 15px;
            background: #eff6ff;
            border-left: 4px solid #1769d1;
        }

        @media(max-width: 700px) {

            .row {
                grid-template-columns: 1fr;
            }

        }

    </style>

</head>


<body>


<div class="header">

    <h1>XYZ Institute of Technology</h1>

    <p>Mock College Certificate Registration System</p>

</div>


<div class="container">


    <div class="card">


        <h2>Register Certificate</h2>


        <p>
            Enter the certificate details to register the
            certificate in the Certificate Validation System.
        </p>


        <form
            action="/register"
            method="POST"
            autocomplete="off"
        >


            <div class="row">


                <div class="field">

                    <label>Certificate ID</label>

                    <input
                        type="text"
                        name="certificate_id"
                        autocomplete="off"
                        required
                    >

                </div>


                <div class="field">

                    <label>Student Name</label>

                    <input
                        type="text"
                        name="student_name"
                        autocomplete="off"
                        required
                    >

                </div>


            </div>


            <div class="row">


                <div class="field">

                    <label>Course</label>

                    <input
                        type="text"
                        name="course"
                        autocomplete="off"
                        required
                    >

                </div>


                <div class="field">

                    <label>Branch</label>

                    <input
                        type="text"
                        name="branch"
                        autocomplete="off"
                        required
                    >

                </div>


            </div>


            <div class="row">


                <div class="field">

                    <label>Academic Year</label>

                    <input
                        type="text"
                        name="year"
                        autocomplete="off"
                        required
                    >

                </div>


                <div class="field">

                    <label>Issued Date</label>

                    <input
                        type="date"
                        name="issued_date"
                        autocomplete="off"
                        required
                    >

                </div>


            </div>


            <div class="field">

                <label>College Name</label>

                <input
                    type="text"
                    name="college_name"
                    autocomplete="off"
                    required
                >

            </div>


            <button type="submit">

                Register Certificate

            </button>


        </form>


        <div class="info">

            <b>Process:</b>

            Mock College → REST API → Flask Backend
            → SHA-256 → Blockchain

        </div>


    </div>


</div>


</body>

</html>
""")


# =========================================================
# REGISTER CERTIFICATE
# =========================================================

@app.route("/register", methods=["POST"])
def register_certificate():

    certificate_id = request.form.get(
        "certificate_id", ""
    ).strip()

    student_name = request.form.get(
        "student_name", ""
    ).strip()

    course = request.form.get(
        "course", ""
    ).strip()

    branch = request.form.get(
        "branch", ""
    ).strip()

    year = request.form.get(
        "year", ""
    ).strip()

    college_name = request.form.get(
        "college_name", ""
    ).strip()

    issued_date = request.form.get(
        "issued_date", ""
    ).strip()


    # Check all fields

    if not all([
        certificate_id,
        student_name,
        course,
        branch,
        year,
        college_name,
        issued_date
    ]):

        return "Please fill all certificate fields.", 400


    # =====================================================
    # CERTIFICATE DATA
    # =====================================================

    certificate_data = {

        "certificate_id": certificate_id,

        "student_name": student_name,

        "course": course,

        "branch": branch,

        "year": year,

        "college_name": college_name,

        "issued_date": issued_date

    }


    # =====================================================
    # SEND CERTIFICATE DATA TO MAIN BACKEND
    # =====================================================

    try:

        response = requests.post(

            BACKEND_URL +
            "/api/certificates/register",

            json=certificate_data,

            timeout=10

        )


        try:

            backend_result = response.json()

        except Exception:

            backend_result = {}


        if response.ok:

            return render_template_string("""
<!DOCTYPE html>

<html>

<head>

    <title>Certificate Registered</title>

    <style>

        body {
            margin: 0;
            font-family: Arial, sans-serif;
            background: #f1f5f9;
        }

        .container {
            max-width: 650px;
            margin: 100px auto;
            padding: 20px;
        }

        .card {
            background: white;
            padding: 40px;
            border-radius: 12px;
            text-align: center;
            box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        }

        .success {
            color: #166534;
            font-size: 22px;
            font-weight: bold;
        }

        .details {
            margin-top: 25px;
            text-align: left;
            line-height: 2;
        }

        button {
            margin-top: 25px;
            padding: 12px 25px;
            background: #1769d1;
            color: white;
            border: none;
            border-radius: 6px;
            font-size: 15px;
            cursor: pointer;
        }

    </style>

</head>


<body>


<div class="container">


    <div class="card">


        <div class="success">

            ✓ Certificate Registered Successfully

        </div>


        <div class="details">

            <b>Certificate ID:</b>
            {{ certificate_id }}

            <br>

            <b>Student Name:</b>
            {{ student_name }}

            <br>

            <b>Course:</b>
            {{ course }}

            <br>

            <b>Branch:</b>
            {{ branch }}

            <br>

            <b>Academic Year:</b>
            {{ year }}

            <br>

            <b>College:</b>
            {{ college_name }}

            <br>

            <b>Issued Date:</b>
            {{ issued_date }}

        </div>


        <button onclick="window.location.href='/'">

            Register Another Certificate

        </button>


    </div>


</div>


</body>

</html>
""",

                certificate_id=certificate_id,
                student_name=student_name,
                course=course,
                branch=branch,
                year=year,
                college_name=college_name,
                issued_date=issued_date

            )


        else:

            return (
                "Certificate registration failed.<br><br>"
                + str(backend_result),
                500
            )


    except requests.exceptions.RequestException:

        return """

        <h2>Backend Connection Failed</h2>

        <p>
        Could not connect to the Certificate Validation Backend.
        </p>

        <p>
        Make sure the backend is running on port 5000.
        </p>

        """, 500


# =========================================================
# START MOCK COLLEGE SERVER
# =========================================================

if __name__ == "__main__":

    app.run(

        host="0.0.0.0",

        port=5050,

        debug=True

    )