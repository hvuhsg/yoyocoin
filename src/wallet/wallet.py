from loguru import logger
import ecdsa
import binascii

from config import Config


def decode_signature(sig, o):
    res = tuple(map(int, sig.decode().split(":")))
    return res


def encode_signature(r, s, o):
    return f"{r}:{s}".encode()


class Wallet:
    main_wallet = None

    @classmethod
    def get_main_wallet(cls):
        return cls.main_wallet

    @classmethod
    def set_main_wallet(cls, wallet):
        cls.main_wallet = wallet

    def __init__(self, secret_passcode: str = None):
        if secret_passcode is None:
            logger.warning("Wallet is generated by random")
            self.private_key = ecdsa.SigningKey.generate(curve=Config.ECDSA_CURVE)
        else:
            self.private_key = ecdsa.SigningKey.from_secret_exponent(
                secexp=int.from_bytes(secret_passcode.encode(), "little"),
                curve=Config.ECDSA_CURVE,
            )
        self.public_key = self.private_key.get_verifying_key()

        self.private_address = self.private_key.to_string().hex()
        self.public_address = self.public_key.to_string("compressed").hex()

        self._nonce: int = 1

    @property
    def nonce(self):
        res = self._nonce
        self._nonce += 1
        return res

    @property
    def public(self) -> str:
        return self.public_address

    @property
    def private(self) -> str:
        return self.private_address

    def sign(self, hash_hexdigest: str):
        signature = self.private_key.sign_digest(
            bytes.fromhex(hash_hexdigest),
            sigencode=encode_signature,
        )
        return signature

    @classmethod
    def verify_signature(cls, verifying_key: str, signature: str, hash_str: str):
        public_key_string = binascii.unhexlify(verifying_key)
        vk = ecdsa.VerifyingKey.from_string(
            public_key_string,
            curve=Config.ECDSA_CURVE,
            valid_encodings=["compressed", "raw"],
        )
        try:
            vk.verify_digest(
                signature, bytes.fromhex(hash_str), sigdecode=decode_signature
            )
        except ecdsa.BadSignatureError:
            return False
        else:
            return True
