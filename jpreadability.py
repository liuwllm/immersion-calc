from jreadability import compute_readability

def calc_readability(text):
    score = compute_readability(text)
    level = categorize_readability(score)

    return level

def categorize_readability(score):
    if 0.5 <= score < 1.5:
        return f"upper-advanced ({score})"
    elif 1.5 <= score < 2.5:
        return f"lower-advanced ({score})"
    elif 2.5 <= score < 3.5:
        return f"upper-intermediate ({score})"
    elif 3.5 <= score < 4.5:
        return f"lower-intermediate ({score})"
    elif 4.5 <= score < 5.5:
        return f"upper-elementary ({score})"
    elif 5.5 <= score < 6.5:
        return f"lower-elementary ({score})"
    else:
        return f"score out of range ({score})"  # In case the score is outside the valid range