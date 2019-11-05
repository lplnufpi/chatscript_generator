import generate

class Test(object):

    def test_add_intentions_syns(self):
        question = 'Como vai você?'
        intents = {'vai': ['está', 'é']}
        result = generate.add_intentions_syns(question, intents)

        assert result == 'Como (vai|está|é) você?'