import plwn


class PLWN:

    def __init__(self):
        self.plwd = plwn.load_default()

    def synset_len(self, synset_id):
        try:
            synset = self.plwd.synset_by_id(synset_id)
            return len(synset.lexical_units)
        except Exception:
            return 1

    def synset_lexical_units(self, synset_id):
        try:
            synset = self.plwd.synset_by_id(synset_id)
            return synset.lexical_units
        except Exception:
            return []
