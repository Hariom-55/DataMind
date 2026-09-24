MAX_VISUALIZATION_POINTS = 500
MAX_HISTOGRAM_BINS = 100
MAX_CORRELATION_COLUMNS = 30
MAX_RARE_VALUES = 20


def evenly_spaced_sample(items: list, limit: int = MAX_VISUALIZATION_POINTS) -> list:
    if len(items) <= limit:
        return items
    if limit <= 1:
        return [items[0]] if items else []
    last_index = len(items) - 1
    indices = [round(index * last_index / (limit - 1)) for index in range(limit)]
    return [items[index] for index in indices]
