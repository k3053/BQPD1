import streamlit as st
import time
from web3_config import web3, contract

st.set_page_config(page_title="Phase 3: TA Grants ECC Access", layout="centered")
st.title("📤 TA: Grant ECC Access to a QP")

ta_account = web3.eth.accounts[0]  # TA assumed to be first account

qp_uid = st.text_input("📄 QP UID", placeholder="e.g., PS001")
selected_ecc = st.selectbox("🏫 Select ECC Address", web3.eth.accounts[6:])  # Assuming ECCs are acc[6]+
unlock_time = st.slider("⏱️ Delay until QP can be accessed (in minutes)", 0, 60, 10)

if st.button("Grant Access"):
    try:
        unlock_timestamp = int(time.time()) + unlock_time * 60

        tx = contract.functions.allowAccessToECC(qp_uid, selected_ecc, unlock_timestamp).transact({'from': ta_account})
        web3.eth.wait_for_transaction_receipt(tx)

        st.success(f"✅ Access granted to {selected_ecc} for QP `{qp_uid}`")
        st.markdown(f"🔓 Unlock time: `{unlock_timestamp}` (Epoch)")
    except Exception as e:
        st.error(f"❌ Failed: {e}")
