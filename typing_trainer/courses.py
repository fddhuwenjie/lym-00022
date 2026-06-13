from dataclasses import dataclass, field
from typing import List, Dict


@dataclass
class Lesson:
    id: int
    name: str
    difficulty: int
    description: str
    texts: List[str] = field(default_factory=list)


WORD_LIBRARY: Dict[str, List[str]] = {
    'th': ['the', 'this', 'that', 'there', 'their', 'they', 'them', 'then', 'than', 'those', 'these', 'think', 'though', 'through', 'thing', 'think', 'thank', 'thousand', 'three', 'thirty'],
    'he': ['he', 'her', 'here', 'help', 'hello', 'heavy', 'heart', 'head', 'health', 'hear', 'heat', 'heaven', 'heavy', 'hedge', 'heel', 'height', 'heir', 'helicopter', 'hell', 'helmet'],
    'in': ['in', 'into', 'inside', 'include', 'income', 'increase', 'indeed', 'independent', 'indicate', 'individual', 'industry', 'influence', 'information', 'initial', 'injury', 'instant', 'instead', 'institute', 'instruction', 'insurance'],
    'er': ['her', 'over', 'under', 'other', 'after', 'never', 'ever', 'number', 'another', 'brother', 'father', 'mother', 'sister', 'together', 'whether', 'however', 'forever', 'whatever', 'whoever', 'whichever'],
    'an': ['an', 'and', 'another', 'answer', 'anxiety', 'any', 'animal', 'announce', 'annual', 'another', 'ancient', 'angle', 'angry', 'animal', 'ankle', 'anniversary', 'annoy', 'annual', 'anonymous', 'another'],
    're': ['re', 'are', 'there', 'here', 'where', 'were', 'require', 'real', 'reason', 'receive', 'recent', 'record', 'reduce', 'refer', 'reflect', 'region', 'regular', 'relate', 'remember', 'repeat'],
    'on': ['on', 'one', 'only', 'onto', 'once', 'online', 'only', 'opinion', 'option', 'order', 'organization', 'origin', 'other', 'another', 'person', 'reason', 'season', 'son', 'ton', 'won'],
    'at': ['at', 'that', 'what', 'water', 'later', 'matter', 'plate', 'date', 'rate', 'state', 'create', 'debate', 'educate', 'graduate', 'hate', 'late', 'native', 'private', 'relate'],
    'en': ['en', 'then', 'when', 'men', 'women', 'children', 'open', 'often', 'even', 'given', 'heaven', 'listen', 'often', 'seven', 'ten', 'then', 'tighten', 'weaken', 'wooden', 'written'],
    'nd': ['and', 'land', 'understand', 'second', 'hand', 'stand', 'band', 'brand', 'command', 'demand', 'expand', 'grand', 'island', 'land', 'mainland', 'rand', 'sand', 'scandal', 'sland', 'thousand'],
    'ti': ['ti', 'time', 'still', 'until', 'title', 'traditional', 'traffic', 'train', 'transfer', 'travel', 'treat', 'tree', 'trial', 'tribe', 'trick', 'trip', 'trouble', 'true', 'trust', 'try'],
    'es': ['es', 'is', 'was', 'as', 'has', 'does', 'goes', 'yes', 'always', 'because', 'business', 'cases', 'close', 'else', 'eyes', 'face', 'false', 'glass', 'horse', 'house'],
    'te': ['te', 'the', 'they', 'them', 'then', 'there', 'their', 'these', 'those', 'together', 'to', 'too', 'two', 'team', 'tech', 'tell', 'ten', 'test', 'text', 'thank'],
    'of': ['of', 'off', 'offer', 'office', 'officer', 'official', 'often', 'okay', 'old', 'olive', 'once', 'one', 'only', 'open', 'opera', 'opinion', 'opportunity', 'option', 'or', 'orange'],
    'st': ['st', 'is', 'as', 'has', 'was', 'list', 'first', 'last', 'fast', 'past', 'cast', 'cost', 'dust', 'east', 'fast', 'frost', 'guest', 'host', 'just', 'lost', 'mist'],
    'ed': ['ed', 'red', 'bed', 'led', 'fed', 'wed', 'used', 'asked', 'called', 'changed', 'closed', 'considered', 'ended', 'expected', 'followed', 'helped', 'included', 'interested', 'needed', 'opened'],
    'ng': ['ng', 'thing', 'something', 'nothing', 'anything', 'everything', 'bring', 'during', 'evening', 'feeling', 'following', 'happening', 'having', 'hearing', 'including', 'interesting', 'king', 'living', 'long', 'morning'],
    'al': ['al', 'all', 'also', 'always', 'call', 'fall', 'hall', 'mall', 'small', 'tall', 'wall', 'already', 'although', 'animal', 'annual', 'another', 'central', 'final', 'general', 'national'],
    'it': ['it', 'its', 'hit', 'bit', 'fit', 'kit', 'pit', 'sit', 'wit', 'exit', 'fruit', 'habit', 'limit', 'profit', 'submit', 'admit', 'commit', 'deposit', 'exhibit', 'orbit'],
    'as': ['as', 'has', 'was', 'ask', 'task', 'fast', 'last', 'past', 'cast', 'class', 'glass', 'grass', 'mass', 'pass', 'plaster', 'plastic', 'master', 'faster', 'disaster'],
}

COMMON_WORDS: List[str] = [
    'the', 'be', 'to', 'of', 'and', 'a', 'in', 'that', 'have', 'I',
    'it', 'for', 'not', 'on', 'with', 'he', 'as', 'you', 'do', 'at',
    'this', 'but', 'his', 'by', 'from', 'they', 'we', 'say', 'her', 'she',
    'or', 'an', 'will', 'my', 'one', 'all', 'would', 'there', 'their', 'what',
    'so', 'up', 'out', 'if', 'about', 'who', 'get', 'which', 'go', 'me',
    'when', 'make', 'can', 'like', 'time', 'no', 'just', 'him', 'know', 'take',
    'people', 'into', 'year', 'your', 'good', 'some', 'could', 'them', 'see', 'other',
    'than', 'then', 'now', 'look', 'only', 'come', 'its', 'over', 'think', 'also',
    'back', 'after', 'use', 'two', 'how', 'our', 'work', 'first', 'well', 'way',
    'even', 'new', 'want', 'because', 'any', 'these', 'give', 'day', 'most', 'us',
    'great', 'between', 'need', 'under', 'never', 'city', 'tree', 'cross', 'still', 'should',
    'every', 'is', 'was', 'are', 'been', 'has', 'had', 'did', 'does', 'doing',
    'may', 'might', 'must', 'shall', 'write', 'being', 'each', 'find', 'many', 'long',
    'down', 'side', 'been', 'now', 'such', 'much', 'own', 'same', 'through', 'where',
    'right', 'look', 'came', 'come', 'made', 'may', 'part', 'place', 'while', 'world',
    'year', 'took', 'sound', 'house', 'found', 'great', 'think', 'head', 'stand', 'found',
    'page', 'country', 'learn', 'hand', 'study', 'still', 'learn', 'plant', 'cover', 'food',
    'sun', 'thought', 'book', 'let', 'eye', 'carry', 'might', 'got', 'open', 'seem',
    'together', 'next', 'white', 'children', 'begin', 'got', 'walk', 'example', 'ease', 'paper',
    'group', 'always', 'music', 'those', 'both', 'mark', 'often', 'letter', 'until', 'mile',
    'river', 'car', 'feet', 'care', 'dark', 'carry', 'power', 'took', 'town', 'fine',
    'certain', 'fly', 'fall', 'lead', 'cry', 'dark', 'machine', 'note', 'wait', 'plan',
    'figure', 'star', 'box', 'noun', 'field', 'rest', 'correct', 'able', 'pound', 'done',
    'beauty', 'drive', 'stood', 'contain', 'front', 'teach', 'week', 'final', 'gave', 'green',
    'quick', 'develop', 'ocean', 'warm', 'free', 'minute', 'strong', 'special', 'mind', 'behind',
    'clear', 'tail', 'produce', 'fact', 'space', 'heard', 'best', 'hour', 'better', 'true',
    'during', 'hundred', 'five', 'remember', 'step', 'early', 'hold', 'west', 'ground', 'interest',
    'reach', 'fast', 'verb', 'sing', 'listen', 'six', 'table', 'travel', 'less', 'morning',
    'ten', 'simple', 'several', 'vowel', 'toward', 'war', 'lay', 'against', 'pattern', 'slow',
    'center', 'love', 'person', 'money', 'serve', 'appear', 'road', 'map', 'rain', 'rule',
    'govern', 'pull', 'cold', 'notice', 'voice', 'energy', 'hunt', 'probable', 'bed', 'brother',
    'egg', 'ride', 'cell', 'believe', 'perhaps', 'pick', 'sudden', 'count', 'square', 'reason',
    'length', 'represent', 'art', 'subject', 'region', 'energy', 'hunt', 'probable', 'bed', 'brother'
]

SENTENCE_TEMPLATES: List[str] = [
    "The {} {} {} across the {} {}.",
    "{} {} {} the {} {} in the {}.",
    "When {} {} {}, {} {} {}.",
    "{} {} to {} {} {} for {}.",
    "{} {} {} {} {} {} every {}.",
    "{} {} {} {} {} {} today.",
    "If {} {} {}, then {} {} {}.",
    "{} and {} {} {} {} {} together.",
    "The {} {} {} {} {} {} last {}.",
    "{} {} {} {} {} {} before {}.",
    "Please {} {} the {} {} {} now.",
    "{} {} {} {} {} {} yesterday.",
    "How {} {} {} {} {} {}?",
    "{} {} {} {} {} {} and {}.",
    "The {} {} {} {} {} {} {}."
]

ADJECTIVES: List[str] = [
    'quick', 'brown', 'lazy', 'happy', 'sad', 'big', 'small', 'bright', 'dark', 'warm',
    'cold', 'old', 'new', 'fast', 'slow', 'smart', 'kind', 'brave', 'calm', 'clean',
    'clear', 'cool', 'crazy', 'curious', 'cute', 'dangerous', 'dark', 'dead', 'deep', 'different',
    'difficult', 'dirty', 'dry', 'early', 'easy', 'empty', 'expensive', 'fair', 'famous', 'far',
    'fast', 'fat', 'few', 'fine', 'flat', 'friendly', 'full', 'funny', 'future', 'good',
    'great', 'green', 'hard', 'healthy', 'heavy', 'high', 'hot', 'huge', 'human', 'important',
    'kind', 'large', 'last', 'late', 'lazy', 'light', 'little', 'long', 'low', 'main',
    'major', 'new', 'nice', 'old', 'open', 'past', 'poor', 'popular', 'possible', 'private',
    'quick', 'quiet', 'ready', 'real', 'recent', 'red', 'rich', 'right', 'same', 'serious'
]

VERBS: List[str] = [
    'run', 'jump', 'walk', 'talk', 'sing', 'dance', 'eat', 'drink', 'sleep', 'work',
    'play', 'read', 'write', 'draw', 'paint', 'cook', 'clean', 'wash', 'fix', 'build',
    'make', 'create', 'design', 'develop', 'learn', 'teach', 'study', 'practice', 'train', 'compete',
    'win', 'lose', 'try', 'fail', 'succeed', 'start', 'stop', 'begin', 'end', 'continue',
    'help', 'love', 'like', 'hate', 'want', 'need', 'wish', 'hope', 'plan', 'prepare',
    'wait', 'hurry', 'move', 'stay', 'leave', 'come', 'go', 'arrive', 'depart', 'return',
    'send', 'receive', 'give', 'take', 'bring', 'carry', 'hold', 'drop', 'catch', 'throw',
    'push', 'pull', 'lift', 'lower', 'raise', 'rise', 'fall', 'stand', 'sit', 'lie',
    'turn', 'rotate', 'spin', 'circle', 'reach', 'stretch', 'bend', 'twist', 'shake', 'wave',
    'point', 'touch', 'feel', 'see', 'hear', 'smell', 'taste', 'notice', 'observe', 'watch'
]

NOUNS: List[str] = [
    'cat', 'dog', 'bird', 'fish', 'tree', 'flower', 'book', 'car', 'house', 'road',
    'river', 'mountain', 'ocean', 'sun', 'moon', 'star', 'cloud', 'rain', 'snow', 'wind',
    'boy', 'girl', 'man', 'woman', 'child', 'family', 'friend', 'teacher', 'student', 'doctor',
    'city', 'town', 'village', 'park', 'garden', 'forest', 'desert', 'island', 'beach', 'lake',
    'apple', 'banana', 'orange', 'grape', 'lemon', 'melon', 'peach', 'pear', 'berry', 'cherry',
    'table', 'chair', 'bed', 'sofa', 'desk', 'shelf', 'cup', 'plate', 'bowl', 'spoon',
    'fork', 'knife', 'glass', 'bottle', 'box', 'bag', 'basket', 'clock', 'lamp', 'mirror',
    'picture', 'frame', 'painting', 'photo', 'map', 'globe', 'computer', 'phone', 'tv', 'radio',
    'music', 'song', 'dance', 'game', 'sport', 'team', 'player', 'coach', 'referee', 'fan',
    'story', 'novel', 'poem', 'essay', 'letter', 'email', 'message', 'report', 'article', 'news'
]

ADVERBS: List[str] = [
    'quickly', 'slowly', 'carefully', 'happily', 'sadly', 'easily', 'hardly', 'nearly', 'almost', 'already',
    'always', 'never', 'sometimes', 'often', 'usually', 'rarely', 'recently', 'soon', 'then', 'now',
    'here', 'there', 'everywhere', 'nowhere', 'somewhere', 'anywhere', 'up', 'down', 'left', 'right',
    'above', 'below', 'inside', 'outside', 'within', 'without', 'together', 'alone', 'again', 'still',
    'yet', 'just', 'only', 'even', 'also', 'too', 'very', 'extremely', 'highly', 'greatly',
    'really', 'actually', 'truly', 'definitely', 'certainly', 'probably', 'possibly', 'perhaps', 'maybe', 'likely',
    'fortunately', 'unfortunately', 'suddenly', 'gradually', 'immediately', 'eventually', 'finally', 'lastly', 'firstly', 'secondly',
    'however', 'therefore', 'thus', 'hence', 'besides', 'moreover', 'furthermore', 'nevertheless', 'nonetheless', 'otherwise'
]


COURSES: List[Lesson] = [
    Lesson(
        id=1,
        name="基础字母入门",
        difficulty=1,
        description="熟悉 home 键位与基础字母，从 ASDF JKL; 开始",
        texts=[
            "asdf jkl; asdf jkl; asdf jkl;",
            "aaa sss ddd fff jjj kkk lll ;;;",
            "asdf jkl; fjfj dkdk slsl a;a;",
            "the quick brown fox jumps over the lazy dog",
            "pack my box with five dozen liquor jugs"
        ]
    ),
    Lesson(
        id=2,
        name="常用单词练习",
        difficulty=2,
        description="高频英语单词训练，提升单词输入速度",
        texts=[
            "the be to of and a in that have I it for not on with he as you do at",
            "this but his by from they we say her she or an will my one all would there their what",
            "so up out if about who get which go me when make can like time no just him know take",
            "people into year your good some could them see other than then now look only come its over think also back after use two how our work first well way even new want because any these give day most us"
        ]
    ),
    Lesson(
        id=3,
        name="经典句子训练",
        difficulty=3,
        description="完整句子输入练习，包含标点符号",
        texts=[
            "The quick brown fox jumps over the lazy dog.",
            "Hello, World! This is a typing test.",
            "Practice makes perfect. Keep going and never give up.",
            "Learning to type fast is a valuable skill in the modern world.",
            "Success is not final, failure is not fatal: it is the courage to continue that counts."
        ]
    ),
    Lesson(
        id=4,
        name="编程基础语法",
        difficulty=4,
        description="常见编程语言基础结构练习",
        texts=[
            "for i in range(10):\n    print(i)",
            "def hello_world():\n    print('Hello, World!')",
            "if x > 0 and y > 0:\n    return True\nelse:\n    return False",
            "const sum = (a, b) => a + b;",
            "class Person {\n  constructor(name) {\n    this.name = name;\n  }\n}",
            "public static void main(String[] args) {\n    System.out.println(\"Hello\");\n}"
        ]
    ),
    Lesson(
        id=5,
        name="Python 代码片段",
        difficulty=5,
        description="实用 Python 代码片段练习",
        texts=[
            "def fibonacci(n):\n    if n <= 1:\n        return n\n    return fibonacci(n-1) + fibonacci(n-2)",
            "import os\nimport sys\nfrom pathlib import Path\n\nDATA_DIR = Path(__file__).parent / 'data'",
            "with open('file.txt', 'r', encoding='utf-8') as f:\n    content = f.read()\n    lines = content.splitlines()",
            "result = [x * 2 for x in numbers if x > 0]",
            "try:\n    value = int(input('Enter a number: '))\n    print(f'You entered: {value}')\nexcept ValueError:\n    print('That is not a valid number!')",
            "class Stack:\n    def __init__(self):\n        self.items = []\n\n    def push(self, item):\n        self.items.append(item)\n\n    def pop(self):\n        return self.items.pop() if self.items else None"
        ]
    ),
    Lesson(
        id=6,
        name="高级符号与混合",
        difficulty=6,
        description="复杂符号、数字与代码混合，挑战极限速度",
        texts=[
            "const regex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$/;",
            "SELECT * FROM users WHERE age >= 18 AND status = 'active' ORDER BY created_at DESC LIMIT 10;",
            "const obj = { key1: 'value1', key2: 123, nested: { a: true, b: null } };",
            "result = arr.filter(x => x > 0).map(x => x * 2).reduce((a, b) => a + b, 0);",
            "docker run -d -p 8080:80 --name myapp -v /data:/app/data -e NODE_ENV=production myimage:latest",
            "git log --oneline --graph --all --decorate --color=always | head -n 20"
        ]
    )
]


def get_course(course_id: int) -> Lesson:
    for course in COURSES:
        if course.id == course_id:
            return course
    raise ValueError(f"Course with id {course_id} not found")


def list_courses() -> List[Lesson]:
    return COURSES
