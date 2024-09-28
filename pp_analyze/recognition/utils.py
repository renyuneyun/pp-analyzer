from deepdiff import DeepDiff, DeepHash


def dict_equal(d1, d2):
    diff = DeepDiff(d1, d2)
    return not diff


def dict_hash(d) -> str:
    return DeepHash(d)[d]