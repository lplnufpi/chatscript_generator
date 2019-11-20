class Rule(object):
    label = None
    original_question = None
    question = None
    answer = None
    title = None
    entities = None


class Topic(object):
    name = None
    keywords = None
    rules = None
    generalized_rules = None
