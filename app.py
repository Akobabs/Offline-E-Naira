from flask import Flask, request, jsonify, render_template
from database import init_db, get_user, get_user_by_id, save_transaction, get_transactions, complete_transaction, get_db_connection_flask, close_db_connection
from crypto import encrypt_data, decrypt_data
import json
import os
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)

init_db()

@app.teardown_appcontext
def teardown_db(exception):
    close_db_connection()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/ussd', methods=['POST'])
def ussd():
    session_id = request.form.get('sessionId', '12345')
    phone_number = request.form.get('phoneNumber', '08012345678')
    text = request.form.get('text', '')

    logger.debug(f"Received request: sessionId={session_id}, phoneNumber={phone_number}, text={text}")

    try:
        inputs = text.split('*') if text else []
        user = get_user(phone_number)

        if not user:
            logger.debug(f"No user found for phone: {phone_number}")
            return jsonify({'response': "END User not found"})

        if not inputs:
            response = "CON Welcome to eNaira Offline\n1. Send Money\n2. Check Balance\n3. View Transactions\n4. Sync Transactions"
        elif inputs[0] == '1':
            if len(inputs) == 1:
                response = "CON Enter Recipient ID:"
            elif len(inputs) == 2:
                response = "CON Enter Amount:"
            elif len(inputs) == 3:
                response = "CON Enter PIN:"
            elif len(inputs) == 4:
                try:
                    amount = float(inputs[2])
                    pin = inputs[3]
                    logger.debug(f"Processing transaction: amount={amount}, recipient={inputs[1]}, pin={pin}")
                    recipient = get_user_by_id(inputs[1])
                    if not recipient:
                        logger.debug(f"Recipient not found: {inputs[1]}")
                        response = "END Recipient not found"
                    elif pin != user['pin']:
                        logger.debug("Incorrect PIN")
                        response = "END Incorrect PIN"
                    elif amount > user['balance']:
                        response = "END Insufficient balance"
                    else:
                        tx_data = {
                            "sender_id": user['id'],
                            "recipient_id": inputs[1],
                            "amount": amount,
                            "timestamp": "2025-04-11T12:00:00"
                        }
                        logger.debug("Encrypting transaction data...")
                        encrypted_tx = encrypt_data(tx_data)
                        tx_file = f'data/tx_{session_id}.json'
                        logger.debug(f"Writing to file: {tx_file}")
                        with open(tx_file, 'w') as f:
                            json.dump(encrypted_tx, f)
                        logger.debug("Saving transaction to database...")
                        save_transaction(user['id'], inputs[1], amount)
                        logger.debug(f"Transaction saved: {tx_data}")
                        response = f"END Transaction initiated: Send {amount} Naira to ID {inputs[1]}"
                except ValueError:
                    logger.debug(f"Invalid amount: {inputs[2]}")
                    response = "END Invalid amount"
        elif inputs[0] == '2':
            response = f"END Your balance is {user['balance']} Naira"
        elif inputs[0] == '3':
            transactions = get_transactions(user['id'])
            if not transactions:
                response = "END No transactions found"
            else:
                tx_list = []
                for tx in transactions[:3]:
                    if tx['sender_id'] == user['id']:
                        tx_str = f"Sent {tx['amount']} Naira to {tx['recipient_id']} on {tx['timestamp'][:10]}"
                    else:
                        tx_str = f"Received {tx['amount']} Naira from {tx['sender_id']} on {tx['timestamp'][:10]}"
                    tx_list.append(tx_str)
                response = "END " + "\n".join(tx_list)
        elif inputs[0] == '4':
            tx_file = f'data/tx_{session_id}.json'
            logger.debug(f"Checking for file: {tx_file}")
            if os.path.exists(tx_file):
                logger.debug("File found, reading...")
                try:
                    with open(tx_file, 'r') as f:
                        encrypted_tx = json.load(f)
                    logger.debug("Decrypting transaction...")
                    tx_data = decrypt_data(encrypted_tx)
                    logger.debug(f"Decrypted data: {tx_data}")
                    conn = get_db_connection_flask()
                    cursor = conn.cursor()
                    cursor.execute('SELECT id FROM transactions WHERE sender_id = ? AND recipient_id = ? AND amount = ? AND status = ?',
                                   (tx_data['sender_id'], tx_data['recipient_id'], tx_data['amount'], 'pending'))
                    tx = cursor.fetchone()
                    logger.debug(f"Database query result: {tx}")
                    if tx:
                        logger.debug(f"Completing transaction ID {tx[0]}")
                        complete_transaction(tx[0], tx_data['sender_id'], tx_data['recipient_id'], tx_data['amount'])
                        logger.debug(f"Deleting file: {tx_file}")
                        os.remove(tx_file)
                        response = "END Transactions synced successfully"
                    else:
                        logger.debug("No matching pending transaction found")
                        response = "END No pending transactions found"
                except Exception as e:
                    logger.error(f"Sync error: {str(e)}")
                    response = f"END Sync failed: {str(e)}"
            else:
                logger.debug("No file found")
                response = "END No offline transactions to sync"
        else:
            response = "END Invalid option"

        logger.debug(f"Sending response: {response}")
        return jsonify({'response': response})

    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return jsonify({'response': f"END Server error: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True)