from hashlib import sha1


def key_to_big_int(key: str) -> int:   
    node_key_digest = sha1(str(key).encode('utf-8')).hexdigest()
    return int(int(node_key_digest, 16) % 1E16)
