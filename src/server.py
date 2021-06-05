from os import urandom

from flask import Flask, jsonify, request
import ecdsa

from src.blockchain import Blockchain


# Instantiate the Node
app = Flask(__name__)

# Generate a globally unique address for this node
secret = int.from_bytes(urandom(16), byteorder="little")
private = ecdsa.SigningKey.from_secret_exponent(secret)
public = private.get_verifying_key()
node_identifier = public.to_string()

# Instantiate the Blockchain
blockchain = Blockchain()


@app.route("/transactions/new", methods=["POST"])
def new_transaction():
    values = request.get_json()

    # Check that the required fields are in the POST'ed data
    required = ["sender", "recipient", "amount", "fee", "signature"]
    if not all(k in values for k in required):
        return "Missing values", 400

    # Create a new Transaction
    try:
        index = blockchain.new_transaction(
            sender=values["sender"],
            recipient=values["recipient"],
            amount=values["amount"],
            fee=values["fee"],
            signature=values["signature"],
        )
    except ValueError:  # invalid signature
        return "Invalid Signature", 400

    response = {"message": f"Transaction will be added to Block {index}"}
    return jsonify(response), 201


@app.route("/chain", methods=["GET"])
def full_chain():
    response = {
        "chain": blockchain.chain,
    }
    return jsonify(response), 200


@app.route("/chain_length", methods=["GET"])
def chain_info():
    response = {
        "length": blockchain.state.length,
        "last_hash": blockchain.state.last_block_hash,
        "score": blockchain.state.score,
    }
    return jsonify(response), 200


@app.route("/nodes/register", methods=["POST"])
def register_nodes():
    values = request.get_json()

    nodes = values.get("nodes")
    if nodes is None:
        return "Error: Please supply a valid list of nodes", 400

    for node in nodes:
        blockchain.register_node(node)

    response = {
        "message": "New nodes have been added",
        "total_nodes": list(blockchain.nodes),
    }
    return jsonify(response), 201


@app.route("/nodes/resolve", methods=["GET"])
def consensus():
    replaced = blockchain.resolve_conflicts()

    if replaced:
        response = {"message": "Our chain was replaced", "new_chain": blockchain.chain}
    else:
        response = {"message": "Our chain is authoritative", "chain": blockchain.chain}

    return jsonify(response), 200


if __name__ == "__main__":
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument(
        "-p", "--port", default=5000, type=int, help="port to listen on"
    )
    args = parser.parse_args()
    port = args.port

    app.run(host="0.0.0.0", port=port)
