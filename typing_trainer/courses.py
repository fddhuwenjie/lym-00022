from dataclasses import dataclass, field
from typing import List


@dataclass
class Lesson:
    id: int
    name: str
    difficulty: int
    description: str
    texts: List[str] = field(default_factory=list)


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
