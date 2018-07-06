# coding: utf8
from ...symbols import (
  ADJ, ADV, NOUN, NUM, PRON, ADP, PUNCT, VERB, POS, X, CCONJ, INTJ, SCONJ
)
from ...lemmatizer import Lemmatizer

class PolishLemmatizer(Lemmatizer):
  _morph = None

  def __init__(self):
    super(PolishLemmatizer, self).__init__()
    try:
      from morfeusz2 import Morfeusz
    except ImportError:
      raise ImportError(
        'The Polish lemmatizer requires the morfeusz2-python library'
      )

    if PolishLemmatizer._morph is None:
      PolishLemmatizer._morph = Morfeusz(dict_name='polimorf')

  def __call__(self, string, univ_pos, morphology=None):
    univ_pos = self.normalize_univ_pos(univ_pos)

    if univ_pos not in ('ADJ', 'ADV', 'NOUN', 'NUM', 'PRON', 'ADP', 'PUNCT', 'VERB', 'X', 'CCONJ', 'INTJ', 'SCONJ'):
      return [string.lower()]

    analyses = self._morph.analyse(string)

    analyses = self._morph.analyse(string)
    filtered_analyses = []
    for analysis in analyses:
      analysis_pos, _ = morftag2ud(str(analysis[2][2]))
      if analysis_pos == univ_pos:
        filtered_analyses.append(analysis)

    if not len(filtered_analyses):
      return [string.lower()]

    if morphology is None or (len(morphology) == 1 and POS in morphology):
      return list(set([analysis[2][1] for analysis in filtered_analyses]))

    features_to_compare = [
      'Number',
      'Case',
      'Gender',
      'Person',
      'Degree',
      'Aspect',
      'Polarity',
      'Variant',
      'Tense',
      'NumType',
      'PrepCase',
    ]

    analyses, filtered_analyses = filtered_analyses, []
    for analysis in analyses:
      _, analysis_morph = morftag2ud(str(analysis[2][2]))
      for feature in features_to_compare:
        if (feature in morphology and feature in analysis_morph and morphology[feature] != analysis_morph[feature]):
          break
      else:
        filtered_analyses.append(analysis)

    if not len(filtered_analyses):
      return [string.lower()]

    return list(set([analysis[2][1] for analysis in filtered_analyses]))

  @staticmethod
  def normalize_univ_pos(univ_pos):
    if isinstance(univ_pos, str):
      return univ_pos.upper()

    symbols_to_str = {
      ADJ: 'ADJ',
      ADV: 'ADV',
      ADP: 'ADP',
      NOUN: 'NOUN',
      NUM: 'NUM',
      PRON: 'PRON',
      PUNCT: 'PUNCT',
      VERB: 'VERB',
      X: 'X',
      CCONJ: 'CCONJ',
      INTJ: 'INTJ',
      SCONJ: 'SCONJ'
    }

    if univ_pos in symbols_to_str:
      return symbols_to_str[univ_pos]
    return None
  
  def is_base_form(self, univ_pos, morphology=None):
    # TODO
    raise NotImplementedError

  def det(self, string, morphology=None):
      return self(string, 'det', morphology)

  def num(self, string, morphology=None):
      return self(string, 'num', morphology)

  def pron(self, string, morphology=None):
      return self(string, 'pron', morphology)

  def lookup(self, string):
    analyses = self._morph.analyse(string)

    if len(analyses) == 1:
      return analyses[0][2][1]

    return string.lower()

def morftag2ud(morf_tag):
  gram_map = {
    '_POS': {
      'subst': 'NOUN',
      'interp': 'NOUN',
      'depr': 'NOUN',
      'adj': 'ADJ',
      'adja': 'ADJ',
      'adjp': 'ADJ',
      'adjc': 'ADJ',
      'adv': 'ADV',
      'num': 'NUM',
      'dig': 'NUM',
      'ppron12': 'PRON',
      'ppron3': 'PRON',
      'siebie': 'PRON',
      'fin': 'VERB',
      'bedzie': 'VERB',
      'aglt': 'VERB',
      'praet': 'VERB',
      'impt': 'VERB',
      'conjt': 'VERB',
      'imps': 'VERB',
      'inf': 'VERB',
      'pcon': 'VERB',
      'pant': 'VERB',
      'ger': 'VERB',
      'pact': 'VERB',
      'ppas': 'VERB',
      'winien': 'VERB',
      'pred': 'VERB',
      'prep': 'ADP',
      'conj': 'CCONJ',
      'qub': 'PRON',
      'interp': 'PUNCT',
      'interj': 'INTJ',
      'xxs': 'X',
      'xxx': 'X',
      'comp': 'SCONJ',
    },
    'Number': {
        'pl': 'Plur',
        'sg': 'Sing',
    },
    'Case': {
      'nom': 'Nom',
      'gen': 'Gen',
      'dat': 'Dat',
      'acc': 'Acc',
      'inst': 'Ins',
      'loc': 'Loc',
      'voc': 'Voc',
    },
    'Gender': {
      'm1': 'Masc',
      'm2': 'Masc',
      'm3': 'Masc',
      'f': 'Fem',
      'n': 'Neut',
    },
    'Person': {
      'pri': '1',
      'sec': '2',
      'ter': '3',
    },
    'Degree': {
      'pos': 'Pos',
      'comp': 'Cmp',
      'sup': 'Sup',
    },
    'Aspect': {
      'imperf': 'Imp',
      'perf': 'Perf',
    },
    'Polarity': {
      'aff': 'Pos',
      'neg': 'Neg',
    },
    'Variant': {
      'wok': 'Long',
      'nwok': 'Short',
    },
    'Tense': {
      'prt': 'Past',
      'prs': 'Pres',
      'fut': 'Fut',
    },
    'NumType': {
      'integer': 'Card',
      'frac': 'Fraction',
    },
    'PrepCase': {
      'praep': 'Pre',
      'npraep': 'Npr',
    },
  }

  pos = 'X'
  morphology = dict()
  unmatched = set()

  grams = morf_tag.replace('.', ':').split(':')
  for gram in grams:
    match = False
    for categ, gmap in sorted(gram_map.items()):
      if gram in gmap:
          match = True
          if categ == '_POS':
            pos = gmap[gram]
          else:
            morphology[categ] = gmap[gram]
    if not match:
      unmatched.add(gram)

  return pos, morphology