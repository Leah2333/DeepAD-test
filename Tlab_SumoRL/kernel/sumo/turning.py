def find_all_turns(plans):
    """Get all plans with turnings.
    Paramters
    ---------
    plans : list
        a list of all routing plans
    """
    turns = []
    for i, plan in enumerate(plans):
        for e1, e2 in zip(plan[:-1], plan[1:]):
            e1_a, e1_b = e1.split('to')
            e2_a, e2_b = e2.split('to')
            if (e1_a == e2_b) and (e1_b == e2_a):
                turns.append(i)
                break
    return turns


def has_turn_link(plan):
    for e1, e2 in zip(plan[:-1], plan[1:]):
        e1_a, e1_b = e1.split('to')
        e2_a, e2_b = e2.split('to')
        if (e1_a == e2_b) and (e1_b == e2_a):
            return True
    return False


def has_duplicate_link(plan):
    traversed = []
    for e in plan:
        if e not in traversed:
            traversed.append(e)
        else:
            return True
    return False


def validate_plan(plan):
    turn = has_turn_link(plan)
    duplicate = has_duplicate_link(plan)
    return not (turn or duplicate)
