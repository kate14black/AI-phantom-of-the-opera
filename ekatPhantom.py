from random import randrange
import PhantomParser
from time import sleep


def lancer():
    fini = False
    old_question = None
    responses = PhantomParser.Parser
    responses.__init__(responses, 1)
    phantom = None
    while phantom is None:
        phantom = responses.get_phantom(responses)
    print(phantom)
    while not fini:
        question = responses.get_question(responses)
        if question != old_question and question is not None:
            print("question : type=" + question.pos.__str__())
            rf = open('./1/reponses.txt','w')
            rf.write(str(randrange(6)))
            rf.close()
            old_question = question
        sleep(0.01)
        fini = responses.is_end(responses, responses.file_info)
