from logging import getLogger
from typing import List, Tuple

logger = getLogger("service")


def ngrams(field: str, n: int = 3):
    return [field[i:i+n] for i in range(len(field)-n+1)]


def tversky_index(text1: str,
                  text2: str,
                  a: float = None,
                  b: float = None,
                  q: int = 3,
                  pad: bool = True):
    if text1 in {None, ''} or text2 in {None, ''}:
        return 0
    
    if len(text1) < q or len(text2) < q:
        return 0

    ngram1, ngram2 = set(ngrams(text1, q)), set(ngrams(text2, q))
    agree_tot = len(ngram1.intersection(ngram2))
    v1 = len(ngram1) - agree_tot
    v2 = len(ngram2) - agree_tot

    if a != None and b != None:
        a = a/float(a+b)
        b = b/float(a+b)
    elif a <= 1.0 and a >= 0.0:
        b = 1-a
    elif b <= 1.0 and b >= 0.0:
        a = 1-b
    else:
        a = 0.5
        b = 0.5
    try:
        return float(agree_tot)/(agree_tot+a*v1+b*v2)
    except:
        logger.error(
            f'Error with `{text1}` | `{text2}`', exc_info=True
        )
        return 0


def tversky_compare(val: str,
                    options: List[str],
                    threshold: float = 0.90) -> List[Tuple[str, float]]:
    results = [
        (option, tversky_index(val, option, .5, .5)) for option in options
    ]
    results = sorted(
        [val for val in results if val[1] >= threshold], key=lambda x: x[1]
    )
    return results
