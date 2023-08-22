import json
import requests

def keep_unique_dicts(lst, keys):
    unique_dicts = set()
    result = []

    for dct in lst:
        # Extract values of specified keys as a tuple
        values = tuple(dct[key] for key in keys)

        # Check if the tuple of values is unique
        if values not in unique_dicts:
            # Add the tuple to the set of unique tuples
            unique_dicts.add(values)
            # Add the dictionary to the result list
            result.append(dct)
    
    return result


def get_unique_lines(file):
    lines = []
    with open(file) as handle:
        for idx, line in enumerate(handle):
            try:
                lines.append(json.loads(line))
            except json.JSONDecodeError:
                print(f"Error reading line {idx + 1} in {file.name}")
                pass
        
    lines = keep_unique_dicts(lines, ["context", "title"])
    return lines


def get_markdown_table(results, metrics=["CL-Recall", "Accuracy", "Accuracy (Disamb.)"]):
    datasets = ["aida-b", "tweeki", "reddit-posts", "reddit-comments", "wned-wiki",
            "shadowlinks-tail", "shadowlinks-shadow", "shadowlinks-top"]

    res = ('|    |' + ' | '.join(datasets) + ' |' + '\n').upper()
    res += '|-' + '-|-'.join('-' * 3 for i in range(len(datasets) + 1)) + '-|' + '\n'
    for metric in metrics:
        res += f'| {metric}' 
        for dataset in datasets:
            try:
                res += ' | ' + str(results[dataset][metric])
            except KeyError:
                res += ' | - '
        res += ' |' + '\n'

    return res.replace("SHADOWLINKS", "SLINKS").replace("COMMENTS", "COMM.")


def is_same_page(page1, page2, session=None):
    api_url = 'https://en.wikipedia.org/w/api.php'

    params1 = {
        'action': 'query',
        'prop': 'info',
        'titles': "|".join([page1, page2]),
        'format': 'json',
        'redirects': 1
    }
    if session is None:
        response = requests.get(api_url, params=params1).json()
    else:
        response = session.get(api_url, params=params1).json()
    
    page_info = response['query']['pages']
    if '-1' in page_info.keys() or len(page_info.keys()) == 2:
        return False
    else:
        return True
    