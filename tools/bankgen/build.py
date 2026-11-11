"""사용법: python3 build.py [번호 ...]   예) python3 build.py 01 02
각 노트북 모듈(nbNN.py)의 build() 를 실행해 bank/question-bank-final-NN.json 을 만든다."""
import sys, importlib, glob, os
from lib import NOTE, report
OUT = '/home/claude/INFSUB/bank'
nums = sys.argv[1:] or sorted(os.path.basename(f)[2:4] for f in glob.glob(os.path.join(os.path.dirname(__file__) or '.', 'nb??.py')))
total = 0
for n in nums:
    mod = importlib.import_module(f'nb{n}')
    b = mod.build()
    b.dump(f'{OUT}/question-bank-final-{n}.json', [mod.SRC + '.ipynb'] + getattr(mod, 'EXTRA_SOURCE', []), NOTE)
    report(b); total += len(b.qs)
print('합계', total)
