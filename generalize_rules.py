# -*- coding: utf-8 -*-

def generalize(qnas):
    """Generalize the rules.

    Args:
        qnas (tuple): Tuple with question and answer.

    Yield:
        str: Rule generalized.
    """
    generalized_rules = list()
    i = 0
    for (question, answer) in qnas:
        i += 1
        rule = '\nu: U{} ({})\n\t{}'.format(i, question, answer)
        yield rule
    return generalized_rules
