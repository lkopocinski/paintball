from paintball.knowledge_source import KnowledgeSource


TEST_KNOWLEDGE_SOURCES_DIR = './knowledge_source'
TEST_KNOWLEDGE_SOURCE_DICT = {
    'test': {
        'testowy': ['0.600', '0.400'],
        'testerski': ['0.700'],
        'tester': ['0.500']
    },
    'tulipan': [
        'kwiat', ['0.400', '0.600'],
        'tyskie', ['0.700'],
    ],
}


def test_load_knowledge_source():
    ks = KnowledgeSource(TEST_KNOWLEDGE_SOURCES_DIR)
    ks.load()

    assert str(ks.knowledge_dict) == TEST_KNOWLEDGE_SOURCE_DICT
