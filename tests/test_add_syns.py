import add_syns

class Test(object):

    def test_add_intentions_syns(self):
        question = 'Como vai você?'
        intents = {'vai': ['está', 'é']}
        result = add_syns.add_intentions_syns(question, intents)

        assert result == 'Como [vai|está|é] você?'