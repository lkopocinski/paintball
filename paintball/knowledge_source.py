from collections import defaultdict
from pathlib import Path


class KnowledgeSource:

    def __init__(self, source_dir):
        self.source_path = Path(source_dir)
        self.knowladge_dict = defaultdict(list)

    def load(self):
        for file_path in self.source_path.glob('*.tsv'):
            self._load_knowledge(file_path)

    def _load_knowledge(self, file_path):
        with open(str(file_path), 'r') as f:
            for line in f:
                source, target, support = line.strip().split('\t')
                self.knowladge_dict[source].append((target, support))
