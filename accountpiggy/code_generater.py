import random

class CodeGenerator:
    nouns = [
        '요이','기린','사자','호랑이','거북이','치타','고구마','감자',
    ]
    adjective =[
        '잠자는','달리는','즐거운','행동하는','난폭한','배부른','예민한',
    ]

    def get_noun_noun_code(self):
        first = random.randrange(0,len(self.nouns))
        second = random.randrange(0,len(self.nouns))
        if second==first:
            if second==0:
                second = second+1
            else:
                second = second-1
        return (self.nouns[first],self.nouns[second])

    def get_adjective_noun_code(self):
        first = random.randrange(0,len(self.nouns))
        second = random.randrange(0,len(self.adjective))
        return (self.nouns[first],self.adjective[second])