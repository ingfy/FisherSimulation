"""Utility library for FisherSimulation."""

def smart_line_sep(words, separator, char_limit, line_separator):
    """Join words by a separator, but limited by a line limit.

    Parameters:
        words:          A list of strings
        separator:      A string representing the separator between words on a 
                        line (space, ", ", etc.).
        char_limit:     Integer. The maximum number of characters allowed on a 
                        single line (including any indentation in 
                        line_separator).
        line_separator: A string representing the separator between lines, has
                        to include a "\n" character. All lines including the 
                        first are preceded by this string.

    Returns:
        A processed multi-line string.
    """

    assert "\n" in line_separator, "line_separator requires an '\n' character."
    tokens = [line_separator, words[0]]
    limit_count = \
        len(line_separator) - line_separator.index("\n") + len(words[0])
    for word in words[1:]:
        if limit_count + len(word) <= char_limit:
            # not on a new line, so add separator first
            tokens.append(separator)
            limit_count += len(separator)
        else:   # overflow
            tokens.append(line_separator)
            limit_count = len(line_separator) - 1
        tokens.append(word)
        limit_count += len(word)
    return "".join(tokens)


def update_map(old, updates):
    """Apply a set of updates to a map.
    
    Parameters:
        old:    A 2-dimensional list of do.Slot instances
        new:    A 2-dimensional list of do.Slot instances with None for 
                unchanged cells in the grid

    Returns:
        A 2-dimensional list of do.Slot instances representing the complete new
        map.
    """

    return [[old_cell if new_cell is None else new_cell 
        for (old_cell, new_cell) in zip(*row)] 
            for row in zip(old, updates)]