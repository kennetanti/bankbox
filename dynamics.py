from flask import request
import builtin_dynamics
import btc_blockchain

def index(user=None):
  return {}
def index_priv(user):
  return user.balance
pub_sources = {		"index": index,
			"create_account": builtin_dynamics.create_account}
priv_sources = {	"index": index_priv,
			"new_deposit": btc_blockchain.new_deposit,
                        "bitcoin_deposit_check": btc_blockchain.check_deposit}
