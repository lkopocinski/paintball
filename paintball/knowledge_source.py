from pathlib import Path

import pandas as pd


class KnowledgeSource:
    EXT = '.tsv'
    SEP = ';'
    COLUMNS = ['source', 'target', 'support']

    def __init__(self, source_dir: Path):
        self._source_dir = source_dir
        self._knowledge_df = self._load()

    def _load(self) -> pd.DataFrame:
        files_paths = self._source_dir.glob(f'*{self.EXT}')
        data_frames = [
            pd.read_csv(path, sep=self.SEP, columns=self.COLUMNS)
            for path in files_paths
        ]
        return pd.concat(data_frames, ignore_index=True)
