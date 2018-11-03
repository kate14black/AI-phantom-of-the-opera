from enum import Enum
import copy
from collections import deque

class Tuile:

    class Status(Enum):
        clean = 0
        suspect = 1

        def __repr__(self):
            return '<{c!s}.{str!s}>'.format(c=self.__class__.__name__, str=self)

        def __str__(self):
            return self.name

    class Color(Enum):
        rose = 1
        gris = 2
        rouge = 3
        marron = 4
        bleu = 5
        violet = 6
        blanc = 7
        noir = 8

        def __repr__(self):
            return '<{c!s}.{str!s}>'.format(c=self.__class__.__name__, str=self)

        def __str__(self):
            return self.name

    def __init__(self, color: Color, status: Status=None, position: int=None):
        self._color = color
        self._position = position
        self._status = status

    def __repr__(self):
        return '<{c!s}: {str!s}>'.format(c=self.__class__.__name__, str=self)

    def __str__(self):
        return '{_color!s}-{_position!s}-{_status!s}'.format(**self.__dict__)

    @property
    def color(self):
        return self._color

    @property
    def position(self):
        return self._position

    @position.setter
    def position(self, position):
        self._position = position

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, status):
        self._status = status


class skip(object):
    """
    Protects item from becaming an Enum member during class creation.
    """
    def __init__(self, value):
        self.value = value

    def __get__(self, instance, ownerclass=None):
        return self.value


class Question(list):

    class Type(Enum):
        unknown = 0
        tuile_dispo = 1
        position_dispo = 2
        activer_pouvoir = 3

        @skip
        class pouvoir(Enum):
            gris = 4
            violet = 6
            blanc = 7

            @skip
            class bleu(Enum):
                un = 5.1
                deux = 5.2

                def __repr__(self):
                    return '<{!s}>'.format(self)

                def __str__(self):
                    return 'Type.pouvoir.{!s}.{!s}'.format(type(self).__name__, self.name)

            def __repr__(self):
                return '<{!s}>'.format(self)

            def __str__(self):
                return 'Type.{!s}.{!s}'.format(type(self).__name__, self.name)

        def __repr__(self):
            return '<{!s}>'.format(self)

        def __str__(self):
            return '{!s}.{!s}'.format(type(self).__name__, self.name)
            # return self.name

    def __init__(self, tuile: Tuile, line: str, type: Type, *args):
        self._tuile = tuile
        self._line = line
        self._type = type
        list.__init__(self, *args)

    def __getitem__(self, key):
        return list.__getitem__(self, key)

    def __repr__(self):
        return '<{c!s}:{on!r} {t!r} {s!r}>'.format(c=self.__class__.__name__, on=self._tuile,
                                                   t=self._type, s=list.__repr__(self))

    def __str__(self):
        return '{t!s} {s!s}'.format(t=self._type, s=list.__str__(self))

    @property
    def tuile(self):
        return self._tuile

    @property
    def line(self):
        return self._line

    @property
    def type(self):
        return self._type

    @property
    def list(self):
        return list

class Parser:
    file_question = 'questions.txt'
    file_response = 'reponses.txt'
    file_info = 'infos.txt'

    def __init__(self, id: int):
        self._id = id
        self._list_question = deque([])
        self._hist_tuiles = {
            Tuile.Color.rose: deque([Tuile(Tuile.Color.rose)]),
            Tuile.Color.gris: deque([Tuile(Tuile.Color.gris)]),
            Tuile.Color.rouge: deque([Tuile(Tuile.Color.rouge)]),
            Tuile.Color.marron: deque([Tuile(Tuile.Color.marron)]),
            Tuile.Color.bleu: deque([Tuile(Tuile.Color.bleu)]),
            Tuile.Color.violet: deque([Tuile(Tuile.Color.violet)]),
            Tuile.Color.blanc: deque([Tuile(Tuile.Color.blanc)]),
            Tuile.Color.noir: deque([Tuile(Tuile.Color.noir)]),
        }
        self._current_tuile = None

    def get_phantom(self, file: str=file_info):
        if self._id == 0:
            return ""
        path = './{id}/{file}'.format(id=self._id, file=file)
        with open(path, 'r') as f:
            phantom = f.readline()
            print(phantom)
            if "fantôme" in phantom:
                phantom = phantom.split(":")[1][1:][:-1]
            else:
                phantom = None
            f.close()
            return phantom

    def is_end(self, file: str=file_info):
        path = './{id}/{file}'.format(id=self._id, file=file)
        with open(path, 'r') as f:
            x = list(f)
            if len(x) > 0:
                f.close()
                return "Score final" in (x[-1])
            f.close()
            return False

    @staticmethod
    def get_tuile_dispo(line: str):
        """ ex: Tuiles disponibles : [rose-3-clean, gris-4-clean] choisir entre 0 et 2 """
        q = line
        new_tuiles = {
            Tuile.Color[x[0]]: Tuile(
                Tuile.Color[x[0]],
                Tuile.Status[x[2].strip()],
                int(x[1].strip())
            ) for x in [x.strip().split('-') for x in q[q.index('[') + 1: q.index(']')].split(',')]
        }
        return new_tuiles

    def get_question(self, file: str=file_question):
        path = './{id}/{file}'.format(id=self._id, file=file)
        with open(path, 'r') as f:
            line = f.readline()
            print("line" + line)
            f.close()
            q = None
            if 'Tuiles disponibles :' in line:
                self._current_tuile = None
                t = self.get_tuile_dispo(line)
                self._append_to_hist(self, t)
                q = Question(self._current_tuile, line, Question.Type.tuile_dispo, t)

            elif 'positions disponibles :' in line:
                q = Question(self._current_tuile, line, Question.Type.position_dispo,
                             self.position_dispo(line))

            elif 'Voulez-vous activer le pouvoir' in line:
                q = Question(self._current_tuile, line, Question.Type.activer_pouvoir,
                             self.activer_pouvoir(line))

            # pouvoir gris
            elif 'Quelle salle obscurcir ? (0-9)' in line:
                q = Question(self._current_tuile, line, Question.Type.pouvoir.gris,
                             self.pouvoir_gris(line))

            # pouvoir bleu 1
            elif 'Quelle salle bloquer ? (0-9)' in line:
                q = Question(self._current_tuile, line, Question.Type.pouvoir.bleu.un,
                             self.pouvoir_bleu_un(line))

            # pouvoir bleu 2
            elif 'Quelle sortie ? Chosir parmi :' in line:
                q = Question(self._current_tuile, line, Question.Type.pouvoir.bleu.deux,
                             self.pouvoir_bleu_deux(line))

            # pouvoir violet
            elif 'Avec quelle couleur échanger (pas violet!) ?' in line:
                q = Question(self._current_tuile, line, Question.Type.pouvoir.violet,
                             self.pouvoir_violet(line, copy.deepcopy(self.get_all_tuiles(self)).values()))

            # pouvoir blanc
            elif ', positions disponibles :' in line:
                q = Question(self._current_tuile, line, Question.Type.pouvoir.blanc,
                             self.pouvoir_blanc(line))

            if q is not None:
                self._list_question.appendleft(q)
            return q

    def get_all_tuiles(self):
        return {k: self._hist_tuiles[k][0] for k in self._hist_tuiles}

    def _append_to_hist(self, lst: list):
        for k, v in self._hist_tuiles.items():
            if k in lst and k != lst[k]:
                self._hist_tuiles[k].appendleft(lst[k])

    @staticmethod
    def activer_pouvoir(line: str):
        """ Voulez-vous activer le pouvoir (0/1) ?  """
        return [0, 1]

    @staticmethod
    def position_dispo(line: str):
        """ positions disponibles : {1, 3}, choisir la valeur """
        q = line
        return [int(x) for x in q[q.index('{') + 1:q.index('}')].split(',')]

    @staticmethod
    def pouvoir_gris(line: str):
        """ Quelle salle obscurcir ? (0-9) """
        return [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

    @staticmethod
    def pouvoir_bleu_un(line: str):
        """ Quelle salle bloquer ? (0-9) """
        return [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

    @staticmethod
    def pouvoir_bleu_deux(line: str):
        """ Quelle sortie ? Chosir parmi : {0, 2} """
        q = line
        return [int(x) for x in q[q.index('{') + 1:q.index('}')].split(',')]

    @staticmethod
    def pouvoir_violet(line: str, lst: list):
        """ Avec quelle couleur échanger (pas violet!) ?  """
        return [x for x in lst if x.color is not Tuile.Color.violet]

    @staticmethod
    def pouvoir_blanc(line: str):
        """ rose-6-suspect, positions disponibles : {5, 7}, choisir la valeur """
        q = line
        [int(x) for x in q[q.index('{') + 1:q.index('}')].split(',')]
        return [int(x) for x in q[q.index('{') + 1:q.index('}')].split(',')]

    @property
    def id(self):
        return self._id

    @property
    def list_question(self):
        return self._list_question
