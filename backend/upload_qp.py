import streamlit as st
import requests
from cryptography.fernet import Fernet
from web3_config import web3, contract

# Connect to local IPFS Desktop node (Kubo)
IPFS_API_URL = "http://127.0.0.1:5003/api/v0/add"

st.set_page_config(page_title="Phase 2: Upload Encrypted QP", layout="centered")
st.title("📄 Phase 2: Upload Encrypted Question Paper")

selected_account = st.selectbox("🔐 Select Wallet", web3.eth.accounts)
uid = st.text_input("🧾 Paper Setter UID", placeholder="e.g., PS001")

qp_file = st.file_uploader("📂 Upload QP (.txt or .pdf)", type=["txt", "pdf"])

if st.button("🔐 Encrypt & Upload"):
    if not qp_file or not uid:
        st.warning("Please provide UID and upload a file.")
    else:
        try:
            # Step 1: Encrypt the file using symmetric key
            key = Fernet.generate_key()
            cipher = Fernet(key)
            encrypted_data = cipher.encrypt(qp_file.read())

            # Step 2: Upload encrypted file to IPFS via raw HTTP POST
            files = {
                'file': ('encrypted_qp', encrypted_data)
            }
            response = requests.post(IPFS_API_URL, files=files)

            if response.status_code == 200:
                ipfs_hash = response.json()["Hash"]

                # Step 3: Store the IPFS hash on the blockchain
                tx = contract.functions.storeQP(uid, ipfs_hash).transact({'from': selected_account})
                web3.eth.wait_for_transaction_receipt(tx)

                st.success("✅ QP encrypted, uploaded, and recorded on blockchain!")
                st.markdown(f"🔗 **IPFS Hash:** `{ipfs_hash}`")
                st.markdown(f"🔑 **Symmetric Key (Save it):** `{key.decode()}`")
                st.markdown(f"[📂 View on IPFS.io](https://ipfs.io/ipfs/{ipfs_hash})")
            else:
                st.error(f"IPFS upload failed: {response.text}")

        except Exception as e:
            st.error(f"❌ Upload failed: {e}")
