import streamlit as st
import json
import ipfshttpclient
from web3 import Web3
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import os

# ========== AES ENCRYPTION HELPERS ==========
BLOCK_SIZE = 16

def pad(data):
    padding = BLOCK_SIZE - len(data) % BLOCK_SIZE
    return data + bytes([padding] * padding)

def unpad(data):
    padding = data[-1]
    return data[:-padding]

def encrypt_file_aes(file_path, key):
    with open(file_path, 'rb') as f:
        data = f.read()
    data = pad(data)
    iv = get_random_bytes(16)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    encrypted = cipher.encrypt(data)
    encrypted_data = iv + encrypted

    enc_file_path = f"{file_path}.enc"
    with open(enc_file_path, 'wb') as f:
        f.write(encrypted_data)

    return enc_file_path

def decrypt_file_aes(enc_file_path, key, output_path):
    with open(enc_file_path, 'rb') as f:
        encrypted_data = f.read()
    iv = encrypted_data[:16]
    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypted = unpad(cipher.decrypt(encrypted_data[16:]))
    with open(output_path, 'wb') as f:
        f.write(decrypted)
    return output_path

# ========== WEB3 & IPFS SETUP ==========
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:7545"))  # Ganache

# Load contract ABI and address
contract_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'build', 'contracts', 'QPContract.json'))
with open(contract_path) as f:
    contract_json = json.load(f)
    abi = contract_json['abi']
    address = list(contract_json['networks'].values())[0]['address']

# with open("abi.json") as f:
#     abi = json.load(f)

contract_address = "0xCF86BeFE4Cce4C3033fBa795383C1A2118e76fAa"  # Replace with your contract address
contract = w3.eth.contract(address=contract_address, abi=abi)
account = w3.eth.accounts[0]

ipfs = ipfshttpclient.connect('/ip4/127.0.0.1/tcp/5001')  # IPFS daemon must be running

# ========== STREAMLIT UI ==========
st.title("Secure QP Storage System (Phase 2)")

menu = ["Upload QP", "Finalize QP", "Check QP"]
choice = st.sidebar.selectbox("Select Action", menu)

if choice == "Upload QP":
    st.header("Upload & Encrypt QP")
    qpid = st.text_input("Question Paper ID")
    file = st.file_uploader("Upload QP File (PDF/Doc)", type=["pdf", "docx", "txt"])

    if st.button("Encrypt & Upload"):
        if file and qpid:
            # Save uploaded file
            with open(file.name, "wb") as f:
                f.write(file.read())

            # Generate AES Key
            aes_key = get_random_bytes(16)
            enc_path = encrypt_file_aes(file.name, aes_key)

            # Upload encrypted file to IPFS
            ipfs_result = ipfs.add(enc_path)
            ipfs_hash = ipfs_result["Hash"]

            # Store hash on blockchain
            tx = contract.functions.storeQP(qpid, ipfs_hash).transact({'from': account})
            w3.eth.wait_for_transaction_receipt(tx)

            st.success("Encrypted QP uploaded to IPFS and hash stored on blockchain.")
            st.write("🔐 AES Key (hex):", aes_key.hex())
            st.write("📁 Encrypted File Hash:", ipfs_hash)

elif choice == "Finalize QP":
    st.header("Finalize Question Paper")
    qpid = st.text_input("QP ID to Finalize")
    num_tas = st.number_input("Number of TAs", min_value=1, step=1)
    ta_addresses = []
    sta_vals = []

    for i in range(int(num_tas)):
        ta_addr = st.text_input(f"TA {i+1} Ethereum Address")
        sta_val = st.text_input(f"STA Value for TA {i+1}")
        ta_addresses.append(ta_addr)
        sta_vals.append(sta_val)

    if st.button("Finalize QP"):
        tx = contract.functions.finalizeQP(qpid, ta_addresses, sta_vals).transact({'from': account})
        w3.eth.wait_for_transaction_receipt(tx)
        st.success("QP Finalized & STA values stored on blockchain.")

elif choice == "Check QP":
    st.header("Check QP Storage")
    qpid = st.text_input("Enter QP ID")
    if st.button("Check"):
        hash_code, timestamp = contract.functions.getQP(qpid).call()
        st.write("IPFS Hash:", hash_code)
        st.write("Timestamp:", timestamp)
