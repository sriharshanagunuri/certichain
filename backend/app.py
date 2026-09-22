from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from web3 import Web3
import hashlib
import json
import os
import secrets
from datetime import datetime

app = Flask(__name__, static_folder="../frontend", static_url_path="")
CORS(app)

# ============================================================
# PATHS
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "../data")

os.makedirs(DATA_DIR, exist_ok=True)

COLLEGES_FILE = os.path.join(DATA_DIR, "colleges.json")
API_REQUESTS_FILE = os.path.join(DATA_DIR, "api_requests.json")
CERTIFICATES_FILE = os.path.join(DATA_DIR, "certificates.json")
VERIFICATION_HISTORY_FILE = os.path.join(
    DATA_DIR, "verification_history.json"
)
ADMINS_FILE = os.path.join(DATA_DIR, "admins.json")
ADMIN_SESSIONS_FILE = os.path.join(DATA_DIR, "admin_sessions.json")


# ============================================================
# BLOCKCHAIN CONFIGURATION
# ============================================================
# ============================================================
# BLOCKCHAIN CONFIGURATION
# ============================================================

RPC_URL = "http://127.0.0.1:8545"

CONTRACT_ADDRESS = Web3.to_checksum_address(
    "0x9fE46736679d2D9a65F0992F2272dE9f3c7fa6e0"
)

ABI_FILE = os.path.join(BASE_DIR, "CertificateRegistry.json")

w3 = Web3(Web3.HTTPProvider(RPC_URL))

contract = None

try:
    with open(ABI_FILE, "r", encoding="utf-8") as f:
        contract_json = json.load(f)

    abi = contract_json.get("abi", contract_json)

    contract = w3.eth.contract(
        address=CONTRACT_ADDRESS,
        abi=abi
    )

    print("Blockchain connected.")
    print("Contract:", CONTRACT_ADDRESS)
    print("Contract exists:", len(w3.eth.get_code(CONTRACT_ADDRESS)) > 0)

except Exception as e:
    print("Blockchain setup error:", e)
# ============================================================
# INITIAL DATA
# ============================================================

def initialize_files():

    if not os.path.exists(COLLEGES_FILE):
        save_json(COLLEGES_FILE, [])

    if not os.path.exists(API_REQUESTS_FILE):
        save_json(API_REQUESTS_FILE, [])

    if not os.path.exists(CERTIFICATES_FILE):
        save_json(CERTIFICATES_FILE, [])

    if not os.path.exists(VERIFICATION_HISTORY_FILE):
        save_json(VERIFICATION_HISTORY_FILE, [])

    if not os.path.exists(ADMIN_SESSIONS_FILE):
        save_json(ADMIN_SESSIONS_FILE, [])

# ============================================================
# JSON HELPERS
# ============================================================

def load_json(filename, default=None):
    if default is None:
        default = []

    if not os.path.exists(filename):
        return default

    try:
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return default


def save_json(filename, data):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
def initialize_admin():

    admins = load_json(ADMINS_FILE, [])

    if len(admins) == 0:

        admins = [
            {
                "admin_id": "ADM-001",
                "username": "systemadmin",
                "password": "SYS-ADMIN-2026",
                "role": "SYSTEM_ADMIN",
                "status": "ACTIVE"
            }
        ]

        save_json(ADMINS_FILE, admins)

        print()
        print("================================================")
        print("DEFAULT SYSTEM ADMIN CREATED")
        print("Username : systemadmin")
        print("Password : SYS-ADMIN-2026")
        print("================================================")
        print()


initialize_files()
initialize_admin()


# ============================================================
# COMMON FUNCTIONS
# ============================================================

def generate_college_id():

    colleges = load_json(COLLEGES_FILE, [])

    number = len(colleges) + 1

    while True:

        college_id = f"COL-{number:04d}"

        if not any(
            c.get("college_id") == college_id
            for c in colleges
        ):
            return college_id

        number += 1


def generate_api_key():
    return "API-" + secrets.token_urlsafe(24)


def find_college_by_id(college_id):

    colleges = load_json(COLLEGES_FILE, [])

    for college in colleges:

        if college.get("college_id") == college_id:
            return college

    return None


def find_college_by_username(username):

    colleges = load_json(COLLEGES_FILE, [])

    for college in colleges:

        if college.get("username") == username:
            return college

    return None


def find_college_by_api_key(api_key):

    colleges = load_json(COLLEGES_FILE, [])

    for college in colleges:

        if college.get("api_key") == api_key:
            return college

    return None


def generate_hash(certificate_data):

    ordered_data = {
        "certificate_id": certificate_data.get(
            "certificate_id", ""
        ),
        "student_name": certificate_data.get(
            "student_name", ""
        ),
        "course": certificate_data.get(
            "course", ""
        ),
        "branch": certificate_data.get(
            "branch", ""
        ),
        "year": certificate_data.get(
            "year", ""
        ),
        "college_name": certificate_data.get(
            "college_name", ""
        ),
        "issued_date": certificate_data.get(
            "issued_date", ""
        )
    }

    text = json.dumps(
        ordered_data,
        sort_keys=True,
        separators=(",", ":")
    )

    return hashlib.sha256(
        text.encode("utf-8")
    ).hexdigest()


def authenticate_api_key():

    api_key = request.headers.get("X-API-Key")

    if not api_key:
        return None

    return find_college_by_api_key(api_key)


def authenticate_admin():

    authorization = request.headers.get(
        "Authorization", ""
    )

    if not authorization.startswith("Bearer "):
        return None

    token = authorization.replace(
        "Bearer ", "", 1
    ).strip()

    if not token:
        return None

    sessions = load_json(
        ADMIN_SESSIONS_FILE, []
    )

    admins = load_json(
        ADMINS_FILE, []
    )

    for session in sessions:

        if session.get("token") == token:

            for admin in admins:

                if (
                    admin.get("admin_id")
                    == session.get("admin_id")
                    and admin.get("status")
                    == "ACTIVE"
                ):
                    return admin

    return None


# ============================================================
# HOME
# ============================================================

@app.route("/")
def home():

    return send_from_directory(
        app.static_folder,
        "index.html"
    )


# ============================================================
# HEALTH CHECK
# ============================================================

@app.route("/api/health", methods=["GET"])
def health():

    return jsonify({
        "status": "running",
        "blockchain_connected": w3.is_connected(),
        "contract": CONTRACT_ADDRESS
    })


# ============================================================
# COLLEGE REGISTRATION
# ============================================================

@app.route(
    "/api/colleges/register",
    methods=["POST"]
)
def register_college():

    data = request.get_json() or {}

    college_name = str(
        data.get("college_name", "")
    ).strip()

    contact_person = str(
        data.get("contact_person", "")
    ).strip()

    email = str(
        data.get("email", "")
    ).strip()

    if not college_name:

        return jsonify({
            "success": False,
            "message": "College name is required."
        }), 400

    if not contact_person:

        return jsonify({
            "success": False,
            "message": "Contact person is required."
        }), 400

    if not email:

        return jsonify({
            "success": False,
            "message": "Email is required."
        }), 400

    colleges = load_json(
        COLLEGES_FILE, []
    )

    for college in colleges:

        if (
            college.get("college_name", "")
            .lower()
            == college_name.lower()
        ):

            return jsonify({
                "success": False,
                "message": "College is already registered."
            }), 409

    college_id = generate_college_id()

    username = college_name

    password = secrets.token_urlsafe(8)

    college = {
        "college_id": college_id,
        "college_name": college_name,
        "username": username,
        "password": password,
        "contact_person": contact_person,
        "email": email,
        "api_key": None,
        "api_status": "NOT_REQUESTED",
        "status": "ACTIVE",
        "created_at": datetime.now().isoformat()
    }

    colleges.append(college)

    save_json(
        COLLEGES_FILE,
        colleges
    )

    return jsonify({
        "success": True,
        "message": "College registered successfully.",
        "college": {
            "college_id": college_id,
            "college_name": college_name,
            "username": username,
            "password": password
        }
    })


# ============================================================
# COLLEGE LOGIN
# ============================================================

@app.route(
    "/api/colleges/login",
    methods=["POST"]
)
def college_login():

    data = request.get_json() or {}

    username = str(
        data.get("username", "")
    ).strip()

    password = data.get("password", "")

    college = find_college_by_username(
        username
    )

    if not college:

        return jsonify({
            "success": False,
            "message": "Invalid username or password."
        }), 401

    if college.get("password") != password:

        return jsonify({
            "success": False,
            "message": "Invalid username or password."
        }), 401

    return jsonify({
        "success": True,
        "message": "College login successful.",
        "college": {
            "college_id": college["college_id"],
            "college_name": college["college_name"],
            "username": college["username"],
            "api_status": college.get(
                "api_status",
                "NOT_REQUESTED"
            )
        }
    })


# ============================================================
# API ACCESS REQUEST
# ============================================================

@app.route(
    "/api/college/api-request",
    methods=["POST"]
)
def request_api_access():

    data = request.get_json() or {}

    college_id = str(
        data.get("college_id", "")
    ).strip()

    college = find_college_by_id(
        college_id
    )

    if not college:

        return jsonify({
            "success": False,
            "message": "College not found."
        }), 404

    requests_data = load_json(
        API_REQUESTS_FILE, []
    )

    for item in requests_data:

        if (
            item.get("college_id") == college_id
            and item.get("status") == "PENDING"
        ):

            return jsonify({
                "success": False,
                "message": "API access request is already pending."
            }), 400

    request_id = (
        "REQ-" +
        secrets.token_hex(4).upper()
    )

    new_request = {
        "request_id": request_id,
        "college_id": college_id,
        "college_name": college["college_name"],
        "status": "PENDING",
        "requested_at": datetime.now().isoformat(),
        "processed_at": None
    }

    requests_data.append(
        new_request
    )

    save_json(
        API_REQUESTS_FILE,
        requests_data
    )

    college["api_status"] = "PENDING"

    colleges = load_json(
        COLLEGES_FILE, []
    )

    for index, item in enumerate(colleges):

        if item.get("college_id") == college_id:

            colleges[index] = college
            break

    save_json(
        COLLEGES_FILE,
        colleges
    )

    return jsonify({
        "success": True,
        "message": "API access request submitted.",
        "request": new_request
    })


# ============================================================
# ADMIN LOGIN
# ============================================================

@app.route(
    "/api/admin/login",
    methods=["POST"]
)
def admin_login():

    data = request.get_json() or {}

    username = str(
        data.get("username", "")
    ).strip()

    password = data.get("password", "")

    admins = load_json(
        ADMINS_FILE, []
    )

    for admin in admins:

        if (
            admin.get("username") == username
            and admin.get("password") == password
            and admin.get("status") == "ACTIVE"
        ):

            token = secrets.token_urlsafe(32)

            sessions = load_json(
                ADMIN_SESSIONS_FILE, []
            )

            sessions.append({
                "token": token,
                "admin_id": admin["admin_id"],
                "created_at": datetime.now().isoformat()
            })

            save_json(
                ADMIN_SESSIONS_FILE,
                sessions
            )

            return jsonify({
                "success": True,
                "message": "System Admin login successful.",
                "token": token,
                "admin": {
                    "admin_id": admin["admin_id"],
                    "username": admin["username"],
                    "role": admin["role"]
                }
            })

    return jsonify({
        "success": False,
        "message": "Invalid System Admin credentials."
    }), 401


# ============================================================
# ADMIN - VIEW API REQUESTS
# ============================================================

@app.route(
    "/api/admin/api-requests",
    methods=["GET"]
)
def admin_api_requests():

    admin = authenticate_admin()

    if not admin:

        return jsonify({
            "success": False,
            "message": "Unauthorized System Admin access."
        }), 401

    requests_data = load_json(
        API_REQUESTS_FILE, []
    )

    return jsonify({
        "success": True,
        "requests": requests_data
    })


# ============================================================
# ADMIN - APPROVE API REQUEST
# ============================================================

@app.route(
    "/api/admin/api-requests/<request_id>/approve",
    methods=["POST"]
)
def approve_api_request(request_id):

    admin = authenticate_admin()

    if not admin:

        return jsonify({
            "success": False,
            "message": "Unauthorized System Admin access."
        }), 401

    requests_data = load_json(
        API_REQUESTS_FILE, []
    )

    colleges = load_json(
        COLLEGES_FILE, []
    )

    target_request = None

    for item in requests_data:

        if item.get("request_id") == request_id:

            target_request = item
            break

    if not target_request:

        return jsonify({
            "success": False,
            "message": "API request not found."
        }), 404

    if target_request.get("status") == "APPROVED":

        return jsonify({
            "success": False,
            "message": "Request is already approved."
        }), 400

    api_key = generate_api_key()

    target_request["status"] = "APPROVED"

    target_request["processed_at"] = (
        datetime.now().isoformat()
    )

    target_request["processed_by"] = (
        admin["username"]
    )

    for college in colleges:

        if (
            college.get("college_id")
            == target_request.get("college_id")
        ):

            college["api_key"] = api_key
            college["api_status"] = "APPROVED"

            break

    save_json(
        API_REQUESTS_FILE,
        requests_data
    )

    save_json(
        COLLEGES_FILE,
        colleges
    )

    return jsonify({
        "success": True,
        "message": "API access approved.",
        "api_key": api_key
    })


# ============================================================
# ADMIN - REJECT API REQUEST
# ============================================================

@app.route(
    "/api/admin/api-requests/<request_id>/reject",
    methods=["POST"]
)
def reject_api_request(request_id):

    admin = authenticate_admin()

    if not admin:

        return jsonify({
            "success": False,
            "message": "Unauthorized System Admin access."
        }), 401

    requests_data = load_json(
        API_REQUESTS_FILE, []
    )

    colleges = load_json(
        COLLEGES_FILE, []
    )

    target_request = None

    for item in requests_data:

        if item.get("request_id") == request_id:

            target_request = item
            break

    if not target_request:

        return jsonify({
            "success": False,
            "message": "API request not found."
        }), 404

    target_request["status"] = "REJECTED"

    target_request["processed_at"] = (
        datetime.now().isoformat()
    )

    target_request["processed_by"] = (
        admin["username"]
    )

    for college in colleges:

        if (
            college.get("college_id")
            == target_request.get("college_id")
        ):

            college["api_status"] = "REJECTED"
            break

    save_json(
        API_REQUESTS_FILE,
        requests_data
    )

    save_json(
        COLLEGES_FILE,
        colleges
    )

    return jsonify({
        "success": True,
        "message": "API access request rejected."
    })


# ============================================================
# API STATUS
# ============================================================

@app.route(
    "/api/college/api-status/<college_id>",
    methods=["GET"]
)
def api_status(college_id):

    college = find_college_by_id(
        college_id
    )

    if not college:

        return jsonify({
            "success": False,
            "message": "College not found."
        }), 404

    return jsonify({
        "success": True,
        "status": college.get(
            "api_status",
            "NOT_REQUESTED"
        ),
        "api_key": college.get("api_key")
    })


# ============================================================
# CERTIFICATE REGISTRATION
# ============================================================

@app.route(
    "/api/v1/certificates",
    methods=["POST"]
)
def api_register_certificate():

    college = authenticate_api_key()

    if not college:

        return jsonify({
            "success": False,
            "message": "Invalid or missing API key."
        }), 401

    data = request.get_json() or {}

    required_fields = [
        "certificate_id",
        "student_name",
        "course",
        "branch",
        "year",
        "college_name",
        "issued_date"
    ]

    for field in required_fields:

        if not str(
            data.get(field, "")
        ).strip():

            return jsonify({
                "success": False,
                "message": f"{field} is required."
            }), 400

    certificate_id = str(
        data["certificate_id"]
    ).strip()

    certificates = load_json(
        CERTIFICATES_FILE, []
    )

    for certificate in certificates:

        if (
            certificate.get("certificate_id")
            == certificate_id
        ):

            return jsonify({
                "success": False,
                "message": "Certificate ID already exists."
            }), 409

    certificate_data = {
        "certificate_id": certificate_id,
        "student_name": str(
            data["student_name"]
        ).strip(),
        "course": str(
            data["course"]
        ).strip(),
        "branch": str(
            data["branch"]
        ).strip(),
        "year": str(
            data["year"]
        ).strip(),
        "college_name": str(
            data["college_name"]
        ).strip(),
        "issued_date": str(
            data["issued_date"]
        ).strip()
    }

    certificate_hash = generate_hash(
        certificate_data
    )

    # ========================================================
    # BLOCKCHAIN REGISTRATION
    # ========================================================

    try:

        if not w3.is_connected():

            return jsonify({
                "success": False,
                "message": "Blockchain network is not connected."
            }), 500

        if contract is None:

            return jsonify({
                "success": False,
                "message": "Smart contract is not loaded."
            }), 500

        # Check that the contract actually exists
        contract_code = w3.eth.get_code(
            CONTRACT_ADDRESS
        )

        if contract_code == b"" or contract_code == b"0x":

            return jsonify({
                "success": False,
                "message": (
                    "Smart contract was not found at the configured "
                    "address. The Hardhat contract may need to be "
                    "deployed again."
                )
            }), 500

        # Hardhat default account
        account = w3.eth.accounts[0]

        # Make sure the account has funds
        balance = w3.eth.get_balance(account)

        if balance == 0:

            return jsonify({
                "success": False,
                "message": "Hardhat account has no ETH balance."
            }), 500

        nonce = w3.eth.get_transaction_count(
            account,
            "pending"
        )

        transaction = (
            contract.functions.registerCertificate(
                certificate_id,
                certificate_hash
            ).build_transaction({
                "from": account,
                "nonce": nonce,
                "gas": 3000000,
                "gasPrice": w3.to_wei(
                    "1", "gwei"
                ),
                "chainId": w3.eth.chain_id
            })
        )

        tx_hash = w3.eth.send_transaction(transaction)
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

        if receipt.status != 1:
            return jsonify({
                "success": False,
                "message": "Blockchain transaction failed."
            }), 500

        blockchain_tx = tx_hash.hex()

    except Exception as e:
        print("BLOCKCHAIN REGISTRATION ERROR:", str(e))

        return jsonify({
            "success": False,
            "message": "Certificate could not be registered on blockchain.",
            "error": str(e)
        }), 500      

    # ========================================================
    # SAVE CERTIFICAzTE
    # ========================================================

    certificate_record = {
        **certificate_data,
        "certificate_hash": certificate_hash,
        "issuer_college_id": college["college_id"],
        "issuer_college_name": college["college_name"],
        "blockchain_transaction": blockchain_tx,
        "registered_at": datetime.now().isoformat()
    }

    certificates.append(
        certificate_record
    )

    save_json(
        CERTIFICATES_FILE,
        certificates
    )

    return jsonify({
        "success": True,
        "message": "Certificate registered successfully.",
        "certificate_id": certificate_id,
        "certificate_hash": certificate_hash,
        "blockchain_transaction": blockchain_tx,
        "issuer_college": college["college_name"]
    })


# ============================================================
# CERTIFICATE VERIFICATION
# ============================================================

@app.route(
    "/api/certificates/verify/<certificate_id>",
    methods=["POST"]
)
def verify_certificate(certificate_id):

    certificate_id = certificate_id.strip() 
    submitted_data = request.get_json(silent=True) or {}
    submitted_certificate = {
        "certificate_id": certificate_id,
        "student_name": str(submitted_data.get("student_name", "")).strip(),
        "course": str(submitted_data.get("course", "")).strip(),
        "branch": str(submitted_data.get("branch", "")).strip(),
        "year": str(submitted_data.get("year", "")).strip(),
        "college_name": str(submitted_data.get("college_name", "")).strip(),
        "issued_date": str(submitted_data.get("issued_date", "")).strip()
    }

    submitted_hash = generate_hash(submitted_certificate)

    certificates = load_json(CERTIFICATES_FILE, [])

    stored_certificate = None

    for certificate in certificates:
        if certificate.get("certificate_id") == certificate_id:
            stored_certificate = certificate
            break

    if not stored_certificate:
        return jsonify({
            "success": True,
            "valid": False,
            "status": "NOT REGISTERED",
            "message": "Certificate ID was not found."
        })

    try:
        if not w3.is_connected() or contract is None:
            return jsonify({
                "success": False,
                "message": "Blockchain is not connected."
            }), 500

        blockchain_result = contract.functions.getCertificate(
            certificate_id
        ).call()

        blockchain_hash = blockchain_result[0]
        certificate_exists = blockchain_result[3]

    except Exception as e:
        print("BLOCKCHAIN VERIFICATION ERROR:", str(e))

        return jsonify({
            "success": False,
            "message": "Unable to verify the certificate on blockchain."
        }), 500

    if certificate_exists and blockchain_hash == submitted_hash:
        valid = True
        status = "VALID"
        message = "Certificate is valid and verified on blockchain."
    else:
        valid = False
        status = "TAMPERED"
        message = "Certificate details do not match the blockchain record."

    history = load_json(VERIFICATION_HISTORY_FILE, [])

    history.append({
        "certificate_id": certificate_id,
        "status": status,
        "verified_at": datetime.now().isoformat()
    })

    save_json(VERIFICATION_HISTORY_FILE, history)

    return jsonify({
        "success": True,
        "valid": valid,
        "status": status,
        "message": message,
        "certificate": stored_certificate,
        "certificate_hash": stored_certificate["certificate_hash"],
        "blockchain_hash": blockchain_hash
    })
# ============================================================
# DASHBOARD
# ============================================================

@app.route(
    "/api/dashboard/<college_id>",
    methods=["GET"]
)
def dashboard(college_id):

    college = find_college_by_id(
        college_id
    )

    if not college:

        return jsonify({
            "success": False,
            "message": "College not found."
        }), 404

    certificates = load_json(
        CERTIFICATES_FILE,
        []
    )

    college_certificates = []

    for certificate in certificates:

        if (
            certificate.get("issuer_college_id")
            == college_id
        ):

            college_certificates.append(
                certificate
            )

    history = load_json(
        VERIFICATION_HISTORY_FILE,
        []
    )

    return jsonify({
        "success": True,
        "college": {
            "college_id": college["college_id"],
            "college_name": college["college_name"],
            "api_status": college.get(
                "api_status",
                "NOT_REQUESTED"
            ),
            "api_key": college.get("api_key")
        },
        "certificates": college_certificates,
        "verification_history": history
    })


# ============================================================
# RUN SERVER
# ============================================================

if __name__ == "__main__":

    print()
    print("==============================================")
    print(" CERTIFICATE VALIDATION BACKEND")
    print("==============================================")
    print(" Server : http://127.0.0.1:5000")
    print(" Blockchain:", w3.is_connected())
    print(" Contract:", CONTRACT_ADDRESS)
    print("==============================================")
    print()

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )