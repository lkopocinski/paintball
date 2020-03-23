from collections import defaultdict
from pathlib import Path


class KnowledgeSource:

    def __init__(self, source_dir):
        self.source_path = Path(source_dir)
        self.knowledge_dict = defaultdict(dict)

    def load(self):
        for file_path in self.source_path.glob('*.tsv'):
            self._load_knowledge(file_path)

    def _load_knowledge(self, file_path):
        with open(str(file_path), 'r') as f:
            for line in f:
                source, target, support = line.strip().split('\t')
                try:
                    self.knowledge_dict[source][target].append(support)
                except:
                    self.knowledge_dict[source][target] = [support]
