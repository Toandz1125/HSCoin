from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import json
import hashlib
import jwt
import os
from functools import wraps
from blockchain import Blockchain
from datetime import datetime, timedelta
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes

def sign_data_with_ecc(data: str) -> str:
    """
    Ký dữ liệu bằng ECC và trả về chữ ký ở dạng hex.
    
    :param data: Dữ liệu cần ký (dạng chuỗi)
    :return: Chữ ký đã mã hóa ở dạng hex
    """
    # Tạo khóa ECC
    private_key = ec.generate_private_key(ec.SECP256R1())  # SECP256R1 là elliptic curve thường dùng
    
    # Chuyển dữ liệu thành bytes
    data_bytes = data.encode()
    
    # Ký dữ liệu
    signature = private_key.sign(
        data_bytes,
        ec.ECDSA(hashes.SHA256())
    )
    
    # Chuyển chữ ký thành dạng hex và trả về
    return signature.hex()

app = Flask(__name__, static_folder='src', static_url_path='/')

# Route để phục vụ trang index.html
@app.route('/')
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')

# Route để phục vụ các file tĩnh (CSS, JS, v.v.)
@app.route('/<path:path>')
def serve_static_files(path):
    return send_from_directory(app.static_folder, path)

CORS(app)

# Instantiate blockchain
blockchain = Blockchain()

# Configuration
app.config['SECRET_KEY'] = 'your-secret-key'  # Change this in production
USER_FILE = 'data/users.json'
DONATIONS_FILE = 'data/donations.json'

# Ensure data directory exists
os.makedirs('data', exist_ok=True)

# Initialize JSON files if they don't exist
def init_json_files():
    if not os.path.exists(USER_FILE):
        with open(USER_FILE, 'w') as f:
            json.dump([], f)
    if not os.path.exists(DONATIONS_FILE):
        with open(DONATIONS_FILE, 'w') as f:
            json.dump([], f)

init_json_files()

# Helper functions
def read_json_file(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)

def write_json_file(file_path, data):
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=4)

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': 'Token bị thiếu'}), 401
        try:
            token = token.split()[1]  # Remove 'Bearer ' prefix
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user = next((user for user in read_json_file(USER_FILE) 
                               if user['email'] == data['email']), None)
            if not current_user:
                return jsonify({'message': 'Token không hợp lệ'}), 401
        except:
            return jsonify({'message': 'Token không hợp lệ'}), 401
        return f(current_user, *args, **kwargs)
    return decorated

# Routes
@app.route('/auth/api/register', methods=['POST'])
def register():
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')

    if not all([name, email, password]):
        return jsonify({'success': False, 'message': 'Hãy điền đầy đủ thông tin'})

    users = read_json_file(USER_FILE)
    
    if any(user['email'] == email for user in users):
        return jsonify({'success': False, 'message': 'Email đã tồn tại'})

    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    new_user = {
        'name': name,
        'email': email,
        'password': hashed_password,
        'created_at': datetime.now().isoformat(),
        'coins': 0
    }
    
    users.append(new_user)
    write_json_file(USER_FILE, users)
    
    return jsonify({'success': True, 'message': 'Đăng ký thành công'})

@app.route('/auth/api/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not all([email, password]):
        return jsonify({'success': False, 'message': 'Hãy điền đầy đủ thông tin'})

    users = read_json_file(USER_FILE)
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    
    user = next((user for user in users if user['email'] == email 
                 and user['password'] == hashed_password), None)
    
    if not user:
        return jsonify({'success': False, 'message': 'Email hoặc mật khẩu không đúng'})

    token = jwt.encode({
        'email': user['email'],
        'exp': datetime.utcnow() + timedelta(days=1)
    }, app.config['SECRET_KEY'])

    return jsonify({
        'success': True,
        'token': token,
        'user': {
            'name': user['name'],
            'email': user['email']
        }
    })

@app.route('/auth/api/donate', methods=['POST'])
@token_required
def donate(current_user):
    data = request.get_json()
    amount = data.get('amount')
    cause = data.get('cause')
    card_number = data.get('cardNumber')
    password = data.get('password')  # Get the password from the request

    # Validate input fields
    if not all([amount, cause]):
        return jsonify({'success': False, 'message': 'Hãy điền đầy đủ thông tin'})

    # Validate amount is a positive number
    if amount <= 0:
        return jsonify({'success': False, 'message': 'Số tiền phải là số dương'}), 400

    # Validate password
    if not password:
        return jsonify({'success': False, 'message': 'Mật khẩu là bắt buộc'}), 400

    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    if hashed_password != current_user['password']:
        return jsonify({
            'success': False,
            'message': 'Mật khẩu không hợp lệ'
        }), 403

    # Validate cause
    # valid_causes = ['academic incentive scholarship', 'full scholarship', 'government scholarship', 'partial scholarship']
    valid_causes = ['sách', 'cây', 'vé sự kiện', 'vé vào phòng nghiên cứu']
    if cause not in valid_causes:
        return jsonify({
            'success': False, 
            'message': 'Nguyên nhân được chọn không hợp lệ'
        }), 400

    # Encrypt card number
    encrypted_card_number = sign_data_with_ecc(card_number)

    # Create a new transaction in the blockchain
    transaction = blockchain.new_transaction(current_user['email'], cause, amount)

    # Update user's coins
    if current_user['coins'] >= amount:
        current_user['coins'] -= amount  # Giảm coins khi donate
    else:
        return jsonify({'success': False, 'message': 'Không đủ tiền'}), 400
    users = read_json_file(USER_FILE)
    for user in users:
        if user['email'] == current_user['email']:
            user['coins'] = current_user['coins']
            break
    write_json_file(USER_FILE, users)

    # Create a new donation record
    new_donation = {
        'user_email': current_user['email'],
        'user_name': current_user['name'],
        'amount': amount,
        'cause': cause,
        'card_number': encrypted_card_number,
        'date': datetime.now().isoformat(),
        'transaction_id': transaction['transaction_id']
    }

    # Save the donation to donations.json
    try:
        donations = read_json_file(DONATIONS_FILE)
        donations.append(new_donation)
        write_json_file(DONATIONS_FILE, donations)
    except Exception as e:
        return jsonify({'success': False, 'message': 'Không lưu được dữ liệu giao dịch'}), 500

    # Return success response with donation details
    return jsonify({
        'success': True,
        'message': 'Donation successful',
        'transaction_id': transaction['transaction_id'],
        'donation_details': new_donation  # Include donation details for the dashboard
    })

@app.route('/auth/api/user', methods=['GET'])
@token_required
def get_user_info(current_user):
    return jsonify({'success': True, 'user': current_user}), 200

@app.route('/auth/api/donations', methods=['GET'])
@token_required
def get_donations(current_user):
    if not os.path.exists('data/donations.json'):
        return jsonify({'success': True, 'donations': []}), 200

    with open('data/donations.json', 'r') as file:
        donations = json.load(file)

    # Filter donations for the current user
    user_donations = [donation for donation in donations if donation['user_email'] == current_user['email']]
    
    return jsonify({'success': True, 'donations': user_donations}), 200

@app.route('/auth/api/donation_stats', methods=['GET'])
def get_donation_stats():
    donations = read_json_file(DONATIONS_FILE)
    stats = {}
    total = 0

    for donation in donations:
        cause = donation['cause']
        amount = donation['amount']
        if cause in stats:
            stats[cause] += amount
        else:
            stats[cause] = amount
        total += amount

    return jsonify({'success': True, 'stats': stats}), 200

@app.route('/auth/api/all_donations', methods=['GET'])
def get_all_donations():
    donations = read_json_file(DONATIONS_FILE)
    return jsonify({'success': True, 'donations': donations}), 200

@app.route('/auth/api/buy_coin', methods=['POST'])
@token_required
def buy_coin(current_user):
    data = request.get_json()
    amount = data.get('amount')

    # Validate input
    if amount is None or not isinstance(amount, (int, float)):
        return jsonify({'success': False, 'message': 'Giá trị tiền không hợp lệ'}), 400

    # Read users from the JSON file
    users = read_json_file(USER_FILE)

    # Find the current user and update their coins
    for user in users:
        if user['email'] == current_user['email']:
            # Update the coins value
            user['coins'] = user.get('coins', 0) + amount # Add coins, default to 0 if not present
            break
    else:
        return jsonify({'success': False, 'message': 'Không tìm thấy người dùng'}), 404

    # Write the updated users back to the JSON file
    write_json_file(USER_FILE, users)

    cause = "Mua HSC"

    # Encrypt card number
    encrypted_card_number = sign_data_with_ecc("Encrypted-Card-Number")
    # Create a new transaction in the blockchain
    transaction = blockchain.new_transaction(current_user['email'], encrypted_card_number , amount)

    # Create a new donation record
    new_donation = {
        'user_email': current_user['email'],
        'user_name': current_user['name'],
        'amount': amount,
        'cause': cause,
        'card_number': encrypted_card_number,
        'date': datetime.now().isoformat(),
        'transaction_id': transaction['transaction_id']
    }

    # Save the donation to donations.json
    try:
        donations = read_json_file(DONATIONS_FILE)
        donations.append(new_donation)
        write_json_file(DONATIONS_FILE, donations)
    except Exception as e:
        return jsonify({'success': False, 'message': 'Không lưu được dữ liệu giao dịch'}), 500

    # Return success response with donation details
    return jsonify({
        'success': True,
        'message': 'Donation successful',
        'transaction_id': transaction['transaction_id'],
        'donation_details': new_donation  # Include donation details for the dashboard
    })

   
@app.route('/auth/api/sell_coin', methods=['POST'])
@token_required
def sell_coin(current_user):
    data = request.get_json()
    amount = data.get('amount')

    # Validate input
    if amount is None or not isinstance(amount, (int, float)):
        return jsonify({'success': False, 'message': 'Giá trị tiền không hợp lệ'}), 400

    # Read users from the JSON file
    users = read_json_file(USER_FILE)

    # Find the current user and update their coins
    for user in users:
        if user['email'] == current_user['email']:
            if user['coins'] >= abs(amount):
            # Update the coins value
                user['coins'] = user.get('coins', 0) + amount # Add coins, default to 0 if not present
                break
            else:
                return jsonify({'success': False,'message': 'Không đủ tiền. Đang chuyển hướng đến bảng điều khiển...'}), 403
    else:
        return jsonify({'success': False, 'message': 'Không tìm thấy người dùng'}), 404

    # Write the updated users back to the JSON file
    write_json_file(USER_FILE, users)

    cause = "Bán HSC"

    # Encrypt card number
    encrypted_card_number = sign_data_with_ecc("Encrypted-Card-Number")
    # Create a new transaction in the blockchain
    transaction = blockchain.new_transaction(current_user['email'], encrypted_card_number , amount)

    # Create a new donation record
    new_donation = {
        'user_email': current_user['email'],
        'user_name': current_user['name'],
        'amount': amount,
        'cause': cause,
        'card_number': encrypted_card_number,
        'date': datetime.now().isoformat(),
        'transaction_id': transaction['transaction_id']
    }

    # Save the donation to donations.json
    try:
        donations = read_json_file(DONATIONS_FILE)
        donations.append(new_donation)
        write_json_file(DONATIONS_FILE, donations)
    except Exception as e:
        return jsonify({'success': False, 'message': 'Không lưu được dữ liệu giao dịch'}), 500

    # Return success response with donation details
    return jsonify({
        'success': True,
        'message': 'Donation successful',
        'transaction_id': transaction['transaction_id'],
        'donation_details': new_donation  # Include donation details for the dashboard
    })

@app.route('/auth/api/payment_coin', methods=['POST'])
@token_required
def payment_coin(current_user):
    data = request.get_json()
    amount = data.get('amount')

    # Validate input
    if amount is None or not isinstance(amount, (int, float)):
        return jsonify({'success': False, 'message': 'Giá trị tiền không hợp lệ'}), 400

    # Read users from the JSON file
    users = read_json_file(USER_FILE)

    # Find the current user and update their coins
    for user in users:
        if user['email'] == current_user['email']:
            if user['coins'] >= abs(amount):
            # Update the coins value
                user['coins'] = user.get('coins', 0) + amount # Add coins, default to 0 if not present
                break
            else:
                return jsonify({'success': False,'message': 'Không đủ tiền. Đang chuyển hướng đến bảng điều khiển...'}), 403
    else:
        return jsonify({'success': False, 'message': 'Không tìm thấy người dùng'}), 404

    # Write the updated users back to the JSON file
    write_json_file(USER_FILE, users)

    cause = "Đóng học phí"

    # Encrypt card number
    encrypted_card_number = sign_data_with_ecc("Encrypted-Card-Number")
    # Create a new transaction in the blockchain
    transaction = blockchain.new_transaction(current_user['email'], encrypted_card_number , amount)

    # Create a new donation record
    new_donation = {
        'user_email': current_user['email'],
        'user_name': current_user['name'],
        'amount': amount,
        'cause': cause,
        'card_number': encrypted_card_number,
        'date': datetime.now().isoformat(),
        'transaction_id': transaction['transaction_id']
    }

    # Save the donation to donations.json
    try:
        donations = read_json_file(DONATIONS_FILE)
        donations.append(new_donation)
        write_json_file(DONATIONS_FILE, donations)
    except Exception as e:
        return jsonify({'success': False, 'message': 'Không lưu được dữ liệu giao dịch'}), 500

    # Return success response with donation details
    return jsonify({
        'success': True,
        'message': 'Donation successful',
        'transaction_id': transaction['transaction_id'],
        'donation_details': new_donation  # Include donation details for the dashboard
    })

@app.route('/auth/api/user_coins', methods=['GET'])
@token_required
def get_user_coins(current_user):
    if 'coins' not in current_user:
        return jsonify({'success': False, 'message': 'Không tìm thấy thông tin số lượng coins sở hữu'}), 40
    return jsonify({'success': True, 'coins': current_user['coins']}), 200
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
