from collections import defaultdict


def load_knowledge_source(file_path):
    ks_dict = defaultdict(list)

    with open(file_path, 'r') as f:
        for line in f:
            source, target, support = line.strip().split(';')
            ks_dict[source].append((target, support))

    return ks_dict
