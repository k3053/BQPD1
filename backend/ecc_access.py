import streamlit as st
import time
from web3_config import web3, contract

st.set_page_config(page_title="Phase 3: ECC QP Access", layout="centered")
st.title("🏫 ECC: Access Question Paper")

selected_ecc = st.selectbox("🔐 ECC Wallet", web3.eth.accounts[6:])

if st.button("🔓 Fetch QP"):
    try:
        qp_uid, ipfs_hash = contract.functions.getQPForECC(selected_ecc).call({'from': selected_ecc})
        st.success(f"✅ Access granted for QP: {qp_uid}")
        st.markdown(f"📂 [Download Encrypted QP](https://ipfs.io/ipfs/{ipfs_hash})")
        st.markdown("🔑 *Use the decryption key shared by TA to open this file*")
    except Exception as e:
        st.error(f"❌ Access Denied or Not Yet Unlocked:\n{str(e)}")
