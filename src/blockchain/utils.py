def decode_signature(sig, o):
    res = tuple(map(int, sig.decode().split(":")))
    return res


def encode_signature(r, s, o):
    return f"{r}:{s}".encode()
