from typing import Tuple

import plwn
from plwn.exceptions import SynsetNotFound


class PLWN:

    def __init__(self):
        self._plwd = plwn.load_default()

    def synset_len(self, synset_id: int) -> int:
        lexical_units = self.synset_lexical_units(synset_id)
        return len(lexical_units)

    def synset_lexical_units(self, synset_id: int) -> Tuple:
        try:
            synset = self._plwd.synset_by_id(synset_id)
        except SynsetNotFound:
            return tuple()
        else:
            return synset.lexical_units
