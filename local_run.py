from flashtext2 import KeywordProcessor, MatchingConflictException

try:
    kp = KeywordProcessor()
    kp.add_keywords_from_dict({
        "New York": ["NYC", "NY", "Big Apple"],
        "Los Angeles": ["LA"]
    })

    print(kp.extract_keywords("I visited New York"))
except MatchingConflictException as err:
    print(str(err))

try:
    kp = KeywordProcessor()
    kp.add_keywords_from_dict({
        "New York": ["NYC", "NY", "Big Apple"],
        "Los Angeles": ["LA", "Big Apple"]
    })

    print(kp.extract_keywords("I visited New York"))
except MatchingConflictException as err:
    print(str(err))

try:
    kp = KeywordProcessor()
    kp.add_keywords_from_dict({
        "New York": ["NYC", "NY", "Big Apple"],
        "Los Angeles": ["LA"]
    })

    print(kp.extract_keywords("I visited NY and LA"))
except MatchingConflictException as err:
    print(str(err))
