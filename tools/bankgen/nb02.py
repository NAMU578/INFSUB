"""기말.2 훈련세트와 테스트세트"""
from lib import Bank
from data import PRE_NP

SRC = '기말.2.훈련세트와 테스트세트'
NOTE = '(`fish_data` 는 도미 35마리, 빙어 14마리 순서의 (49, 2) 배열, `fish_target` 은 1이 35개, 0이 14개인 배열)'
BIASED = ("train_input = fish_data[:35]\ntrain_target = fish_target[:35]\ntest_input = fish_data[35:]\ntest_target = fish_target[35:]\n"
          "kn = KNeighborsClassifier()\nkn.fit(train_input, train_target)")
SPLIT = "train_input, test_input, train_target, test_target = train_test_split(\n    fish_data, fish_target, random_state=42)"


def build():
    b = Bank('02', SRC, PRE_NP)
    PRE_KN = PRE_NP + "\nkn = KNeighborsClassifier()"
    PRE_SPLIT = PRE_NP + "\n" + SPLIT

    # ── 개념 분류 ──
    b.C(code=BIASED, stem=f'다음 코드에 대한 설명으로 옳은 것만 <보기>에서 모두 고른 것은? {NOTE}',
        items=[("`train_target` 의 값은 모두 1이다.", "bool((train_target == 1).all())"),
               ("`test_input` 의 샘플 수는 14이다.", "len(test_input) == 14"),
               ("`kn.score(test_input, test_target)` 은 1.0이다.", "kn.score(test_input, test_target) == 1.0")],
        why="앞 35개는 전부 도미, 뒤 14개는 전부 빙어입니다. 도미만 보고 훈련한 모델은 빙어를 전부 도미로 예측해서 테스트 정확도가 0.0이 됩니다. 이것이 샘플링 편향입니다.",
        tags=['샘플링 편향', '슬라이싱'])
    b.C(code=SPLIT, stem=f'다음 코드에 대한 설명으로 옳은 것만 <보기>에서 모두 고른 것은? {NOTE}',
        items=[("`train_input.shape` 은 `(36, 2)` 이다.", "train_input.shape == (36, 2)"),
               ("`test_target.shape` 은 `(13, 1)` 이다.", "test_target.shape == (13, 1)"),
               ("같은 코드를 다시 실행해도 `train_input` 의 내용은 같다.", "np.array_equal(train_input, train_test_split(fish_data, fish_target, random_state=42)[0])")],
        why="비율을 정하지 않으면 테스트 세트가 25%라서 49개가 36개와 13개로 나뉩니다. 정답 배열은 1차원이라 shape 이 `(13,)` 입니다. `random_state` 가 같으면 섞이는 순서가 같아 결과가 재현됩니다.",
        tags=['train_test_split', 'shape', 'random_state'])
    b.C(stem='훈련 세트와 테스트 세트에 대한 설명으로 옳은 것만 <보기>에서 모두 고른 것은?',
        items=[("모델의 성능은 훈련에 쓰지 않은 테스트 세트로 평가해야 한다.", True),
               ("특정 클래스가 한쪽 세트에 몰려 있는 것을 샘플링 편향이라고 한다.", True),
               ("데이터를 섞지 않고 앞에서부터 잘라도 편향은 생기지 않는다.", False)],
        why="훈련한 데이터로 평가하면 답을 미리 알고 보는 시험과 같습니다. 데이터가 클래스별로 정렬되어 있으면 앞에서부터 자를 때 한쪽 세트에 한 클래스만 들어가므로 반드시 섞어서 나눠야 합니다.",
        tags=['훈련 세트', '테스트 세트', '샘플링 편향'], ref='셀 [9]~[16] 데이터 편향')
    b.C(code="np.random.seed(42)\nindex = np.arange(49)\nnp.random.shuffle(index)\ntrain_input = fish_data[index[:35]]\ntest_input = fish_data[index[35:]]",
        stem=f'다음 코드에 대한 설명으로 옳은 것만 <보기>에서 모두 고른 것은? {NOTE}',
        items=[("`index` 에는 0부터 48까지의 정수가 한 번씩 들어 있다.", "sorted(index.tolist()) == list(range(49))"),
               ("`train_input.shape` 은 `(35, 2)` 이다.", "train_input.shape == (35, 2)"),
               ("`np.random.shuffle(index)` 는 `index` 는 그대로 두고 섞인 새 배열을 돌려준다.", False)],
        why="`shuffle` 은 넘겨받은 배열 자체의 순서를 바꾸고 아무것도 돌려주지 않습니다. 섞인 번호의 앞 35개로 훈련 세트를, 나머지 14개로 테스트 세트를 뽑습니다.",
        tags=['shuffle', '배열 인덱싱'])
    b.C(code="a = np.column_stack(([1, 2, 3], [4, 5, 6]))\nb = np.concatenate((np.ones(2), np.zeros(3)))", pre='import numpy as np',
        items=[("`a.shape` 은 `(3, 2)` 이다.", "a.shape == (3, 2)"),
               ("`a[0]` 은 `[1 4]` 이다.", "a[0].tolist() == [1, 4]"),
               ("`b` 의 원소는 6개이다.", "len(b) == 6")],
        why="`column_stack` 은 리스트들을 열로 나란히 붙이므로 3행 2열이 되고 첫 행은 [1 4] 입니다. `concatenate` 는 1 두 개와 0 세 개를 이어 붙여 원소가 5개입니다.",
        tags=['column_stack', 'concatenate'])

    # ── 빈칸 ──
    b.B("fish_data = np.㉠((fish_length, fish_weight))\nfish_target = np.㉡((np.ones(35), np.zeros(14)))\nprint(fish_data.shape, fish_target.shape)",
        ('column_stack', 'concatenate'), [('concatenate', 'column_stack'), ('row_stack', 'concatenate'), ('column_stack', 'zeros'), ('array', 'concatenate')],
        why="두 리스트를 열로 나란히 붙여 (49, 2) 를 만드는 것은 `column_stack`, 두 배열을 한 줄로 이어 (49,) 를 만드는 것은 `concatenate` 입니다.",
        tags=['column_stack', 'concatenate'])
    b.B("np.random.㉠(42)\nindex = np.㉡(49)\nnp.random.shuffle(index)\nprint(len(index), index.min(), index.max())",
        ('seed', 'arange'), [('shuffle', 'arange'), ('seed', 'zeros'), ('fix', 'arange'), ('seed', 'array')],
        why="`np.random.seed()` 로 난수의 시작점을 고정하고, `np.arange(49)` 로 0~48 번호를 만든 다음 섞습니다.", tags=['seed', 'arange'])
    b.B("train_input, test_input, train_target, test_target = ㉠(\n    fish_data, fish_target, ㉡=42)\nprint(train_input.shape, test_input.shape)",
        ('train_test_split', 'random_state'), [('train_test_split', 'seed'), ('test_train_split', 'random_state'), ('split', 'random_state'), ('train_test_split', 'test_size')],
        why="데이터를 섞어서 나누는 함수는 `train_test_split` 이고, 섞는 방법을 고정하는 매개변수는 `random_state` 입니다. `test_size=42` 로 쓰면 테스트 세트가 42개가 됩니다.",
        tags=['train_test_split', 'random_state'])
    b.B("from sklearn.㉠ import train_test_split\ntrain_input, ㉡, train_target, test_target = train_test_split(\n    fish_data, fish_target, random_state=42)\nprint(test_input.shape)",
        ('model_selection', 'test_input'), [('model_selection', 'train_target'), ('neighbors', 'test_input'), ('model_selection', 'test_target'), ('preprocessing', 'test_input')],
        why="`train_test_split` 은 `sklearn.model_selection` 에 있고, 돌려주는 순서는 훈련 입력, **테스트 입력**, 훈련 정답, 테스트 정답입니다.",
        tags=['train_test_split', '반환 순서'])
    b.B("train_input = fish_data[:㉠]\ntest_input = fish_data[㉡:]\nprint(len(train_input), len(test_input))",
        ('35', '35'), [('35', '14'), ('34', '35'), ('35', '36'), ('36', '35')],
        why="`[:35]` 는 인덱스 0~34의 35개, `[35:]` 는 인덱스 35~48의 14개입니다. 끝 인덱스는 포함하지 않으므로 두 곳에 같은 35를 써야 빠지거나 겹치는 샘플이 없습니다.",
        tags=['슬라이싱'])

    # ── 경계값 ──
    b.D("print(len(fish_data[:5]), len(fish_data[44:]), len(fish_data[35:]))", ['5 4 14', '5 5 13', '6 5 14', '5 44 35'],
        stem=f'다음 코드를 실행했을 때 출력되는 것은? {NOTE}',
        why="`[:5]` 는 인덱스 0~4의 5개, `[44:]` 는 44~48의 5개, `[35:]` 는 35~48의 14개입니다.", tags=['슬라이싱'])
    b.D(SPLIT + "\nprint(len(train_input), len(test_input))", ['37 12', '35 14', '34 15', '24 25'],
        stem=f'다음 코드를 실행했을 때 출력되는 것은? {NOTE}',
        why="기본 테스트 비율은 25%입니다. 49 × 0.25 = 12.25 를 올림해 테스트 세트가 13개, 나머지 36개가 훈련 세트입니다.", tags=['train_test_split', '기본 비율'])
    b.D("X = np.arange(100).reshape(50, 2)\ny = np.arange(50)\na, b, c, d = train_test_split(X, y, test_size=0.2, random_state=0)\nprint(len(a), len(b))",
        ['45 5', '10 40', '37 13', '38 12'],
        why="`test_size=0.2` 이면 50개의 20%인 10개가 테스트 세트이고, 첫 번째로 돌려받는 `a` 는 훈련 입력 40개, 두 번째 `b` 는 테스트 입력 10개입니다.", tags=['test_size'])
    b.D("X = np.arange(20).reshape(10, 2)\ny = np.arange(10)\na, b, c, d = train_test_split(X, y, random_state=0)\nprint(len(a), len(b))",
        ['8 2', '5 5', '9 1', '6 4'],
        why="기본 테스트 비율 25%를 10개에 적용하면 2.5개인데, 올림해서 테스트 세트가 3개, 훈련 세트가 7개가 됩니다.", tags=['train_test_split', '올림'])
    b.D("index = np.arange(49)\nprint(len(index[:35]), len(index[35:]), index[35])", ['35 14 36', '35 13 35', '36 13 35', '34 15 34'],
        why="`np.arange(49)` 는 0~48 입니다. `[:35]` 는 35개, `[35:]` 는 14개이고 인덱스 35의 값은 35입니다.", tags=['arange', '슬라이싱'])

    # ── 상태 예측 ──
    b.R(BIASED + "\nprint(kn.score(test_input, test_target))", ['1.0', '0.7142857142857143', '0.2857142857142857', '0.5'],
        stem=f'다음 코드를 실행했을 때 출력되는 것은? {NOTE}',
        why="훈련 세트에는 도미만, 테스트 세트에는 빙어만 있습니다. 모델이 빙어 14마리를 전부 도미로 예측하므로 하나도 맞히지 못해 0.0 입니다.", tags=['샘플링 편향'])
    b.R("fish_data = np.column_stack((fish_length, fish_weight))\nfish_target = np.concatenate((np.ones(35), np.zeros(14)))\nprint(fish_data.shape, fish_target.shape)",
        ['(2, 49) (49,)', '(49, 2) (49, 1)', '(98,) (49,)', '(49, 2) (2,)'],
        stem='`fish_length`, `fish_weight` 는 각각 값이 49개인 리스트이다. 다음 코드를 실행했을 때 출력되는 것은?',
        why="`column_stack` 은 두 리스트를 열로 붙여 49행 2열을 만들고, `concatenate` 는 1차원 배열 두 개를 이어 원소 49개인 1차원 배열을 만듭니다.", tags=['column_stack', 'concatenate', 'shape'])
    b.R(SPLIT + "\nprint(train_target.shape, test_target.shape)", ['(36, 2) (13, 2)', '(36, 1) (13, 1)', '(35,) (14,)', '(13,) (36,)'],
        stem=f'다음 코드를 실행했을 때 출력되는 것은? {NOTE}',
        why="정답 배열은 1차원이라 shape 에 열 크기가 없습니다. 훈련 36개, 테스트 13개이므로 `(36,)` 과 `(13,)` 입니다.", tags=['train_test_split', 'shape'])
    b.R("print(np.column_stack(([1, 2, 3], [4, 5, 6])).tolist())", ['[[1, 2, 3], [4, 5, 6]]', '[1, 2, 3, 4, 5, 6]', '[[1, 4, 2], [5, 3, 6]]', '[[4, 1], [5, 2], [6, 3]]'],
        pre='import numpy as np',
        why="`column_stack` 은 각 리스트를 하나의 **열**로 세워서 붙입니다. 그래서 행은 [1, 4], [2, 5], [3, 6] 입니다.", tags=['column_stack'])
    b.R("print(np.concatenate((np.ones(2), np.zeros(3))))", ['[1 1 0 0 0]', '[[1. 1.] [0. 0. 0.]]', '[1. 1. 1. 0. 0.]', '[2. 3.]'], pre='import numpy as np',
        why="`np.ones`, `np.zeros` 는 실수 배열을 만들기 때문에 `1.`, `0.` 처럼 점이 붙어 출력됩니다. 1이 두 개, 0이 세 개 이어집니다.", tags=['concatenate', 'ones', 'zeros'])
    b.R("arr = np.array([10, 20, 30, 40, 50])\nidx = np.array([3, 0, 4])\nprint(arr[idx], arr[idx[:2]])", ['[40 10 50] [10 20]', '[30 10 40] [30 10]', '[40 10 50] [40 10 50]', '[10 40 50] [10 40]'],
        pre='import numpy as np',
        why="배열을 인덱스로 넣으면 그 번호의 원소를 순서대로 뽑습니다. `idx[:2]` 는 [3, 0] 이므로 [40 10] 입니다. 노트북의 `input_arr[index[:35]]` 와 같은 원리입니다.", tags=['배열 인덱싱'])

    # ── 대조 ──
    b.X("# 방법1: 앞에서부터 자르기\nkn.fit(fish_data[:35], fish_target[:35])\nprint(kn.score(fish_data[35:], fish_target[35:]))\n\n"
        "# 방법2: 섞어서 나누기\ntr_in, te_in, tr_tg, te_tg = train_test_split(fish_data, fish_target, random_state=42)\nkn.fit(tr_in, tr_tg)\nprint(kn.score(te_in, te_tg))",
        [('1.0', '0.0'), ('0.0', '0.0'), ('1.0', '1.0'), ('0.7142857142857143', '1.0')], pre=PRE_KN,
        stem=f'`kn` 은 `KNeighborsClassifier()` 객체이다. ㉠, ㉡에 출력되는 값으로 알맞은 것은? {NOTE}',
        why="앞에서부터 자르면 훈련 세트에 도미만 있어서 빙어뿐인 테스트 세트를 하나도 맞히지 못합니다(0.0). 섞어서 나누면 두 세트에 도미와 빙어가 모두 들어가 1.0 이 나옵니다.", tags=['샘플링 편향', 'train_test_split'])
    b.X("# 방법1\nprint(train_input.shape)\n\n# 방법2\nprint(train_target.shape)", [('(36, 2)', '(36, 2)'), ('(36,)', '(36,)'), ('(36, 2)', '(36, 1)'), ('(13, 2)', '(13,)')],
        pre=PRE_SPLIT, stem=f'`train_test_split(fish_data, fish_target, random_state=42)` 로 나눈 결과이다. ㉠, ㉡에 출력되는 값으로 알맞은 것은? {NOTE}',
        why="입력은 샘플마다 [길이, 무게] 두 값이 있어 2차원 `(36, 2)` 이고, 정답은 샘플마다 값이 하나라 1차원 `(36,)` 입니다.", tags=['shape'])
    b.X("a = [1, 2, 3]\nb = [4, 5, 6]\n# 방법1\nprint(np.column_stack((a, b)).shape)\n\n# 방법2\nprint(np.concatenate((a, b)).shape)",
        [('(2, 3)', '(6,)'), ('(3, 2)', '(3, 2)'), ('(6,)', '(3, 2)'), ('(3, 2)', '(2, 3)')], pre='import numpy as np',
        why="`column_stack` 은 열로 나란히 붙여 3행 2열을, `concatenate` 는 한 줄로 이어 원소 6개인 1차원 배열을 만듭니다.", tags=['column_stack', 'concatenate'])
    b.X("a = np.arange(5)\nr = np.random.shuffle(a)\n# 방법1\nprint(r)\n\n# 방법2\nprint(len(a))", [('[0 1 2 3 4]', '5'), ('None', '0'), ('5', 'None'), ('[4 3 2 1 0]', '5')],
        pre='import numpy as np',
        why="`np.random.shuffle` 은 배열 자체를 섞고 **아무것도 돌려주지 않으므로** `r` 은 `None` 입니다. `a` 는 순서만 바뀌었을 뿐 원소 5개가 그대로 있습니다.", tags=['shuffle', 'None'])
    b.X("arr = np.array([[1, 2], [3, 4], [5, 6]])\n# 방법1\nprint(arr[:, 0])\n\n# 방법2\nprint(arr[0])", [('[1 2]', '[1 3 5]'), ('[1 3 5]', '[1 3 5]'), ('[1 2]', '[1 2]'), ('[2 4 6]', '[1 2]')],
        pre='import numpy as np',
        why="`arr[:, 0]` 은 모든 행의 0번 열(첫 번째 특성)이고, `arr[0]` 은 0번 행(첫 번째 샘플)입니다. 산점도를 그릴 때 `train_input[:, 0]` 으로 길이만 꺼낸 것과 같습니다.", tags=['2차원 슬라이싱'])

    # ── 조건 매핑 ──
    b.S(["입력 `fish_data` 와 정답 `fish_target` 을 섞어서 훈련 세트와 테스트 세트로 나눈다.", "실행할 때마다 같은 결과가 나오게 한다."],
        "train_test_split(fish_data, fish_target, random_state=42)",
        ["train_test_split(fish_data, random_state=42)", "train_test_split(fish_target, fish_data, random_state=42)",
         "train_test_split(fish_data, fish_target, seed=42)", "train_test_split(fish_data, fish_target, test_size=42)"],
        code="train_input, test_input, train_target, test_target = ____", chk="print(train_input.shape, test_target.shape)",
        why="입력, 정답 순서로 넣고 `random_state` 로 섞는 방법을 고정합니다. 입력만 넣으면 돌려받는 값이 2개뿐이고, 입력과 정답의 순서를 바꾸면 변수에 엉뚱한 배열이 들어갑니다.",
        tags=['train_test_split'])
    b.S(["값이 49개씩인 리스트 `fish_length`, `fish_weight` 로 배열을 만든다.", "결과의 shape 은 `(49, 2)` 이고 한 행이 [길이, 무게] 이다."],
        "np.column_stack((fish_length, fish_weight))",
        ["np.concatenate((fish_length, fish_weight))", "np.column_stack(fish_length, fish_weight)", "np.array((fish_length, fish_weight))", "np.row_stack((fish_length, fish_weight))"],
        code="fish_data = ____", chk="print(fish_data.shape)",
        why="`column_stack` 에 두 리스트를 **튜플 하나로 묶어** 넘깁니다. `np.array((…))` 나 `row_stack` 은 (2, 49) 가 되고, `concatenate` 는 원소 98개인 1차원 배열이 됩니다.",
        tags=['column_stack'])
    b.S(["1이 35개, 그 뒤에 0이 14개인 1차원 배열을 만든다."], "np.concatenate((np.ones(35), np.zeros(14)))",
        ["np.column_stack((np.ones(35), np.zeros(14)))", "np.concatenate(np.ones(35), np.zeros(14))", "np.ones(35) + np.zeros(14)", "np.concatenate((np.zeros(35), np.ones(14)))"],
        code="fish_target = ____", chk="print(fish_target.shape, int(fish_target[:35].sum()), int(fish_target[35:].sum()))",
        why="`np.ones(35)` 와 `np.zeros(14)` 를 튜플로 묶어 `concatenate` 에 넘깁니다. 길이가 다른 배열은 `+` 로 더하거나 `column_stack` 으로 붙일 수 없습니다.", tags=['concatenate'])
    b.S(["`index` 는 0~48 을 무작위로 섞은 배열이다.", "`input_arr` 에서 섞인 순서의 **앞 35개** 샘플을 뽑는다."], "input_arr[index[:35]]",
        ["input_arr[:35]", "input_arr[index[35:]]", "index[input_arr[:35]]", "input_arr[index][35:]"],
        code="train_input = ____", chk="print(train_input.shape, bool((train_input[0] == input_arr[index[0]]).all()))",
        pre=PRE_NP + "\ninput_arr = np.array(fish_data)\nnp.random.seed(42)\nindex = np.arange(49)\nnp.random.shuffle(index)",
        why="섞인 인덱스의 앞 35개(`index[:35]`)를 배열 인덱스로 넣습니다. `input_arr[:35]` 는 섞지 않은 원래 순서의 앞 35개라서 전부 도미입니다.", tags=['배열 인덱싱', 'shuffle'])

    # ── 서답형 ──
    b.W("빈칸 ㉠ 에 들어갈 함수 이름을 쓰시오. (배열의 순서를 무작위로 섞는 함수)", "shuffle", pre='import numpy as np',
        code="np.random.seed(42)\nindex = np.arange(5)\nnp.random.㉠(index)\nprint(sorted(index.tolist()))",
        why="`np.random.shuffle(배열)` 은 배열의 순서를 그 자리에서 섞습니다. 정렬해서 출력하면 원래 숫자가 그대로 있는 것을 볼 수 있습니다.", tags=['shuffle'])
    b.W("빈칸 ㉠ 에 들어갈 매개변수 이름을 쓰시오. (실행할 때마다 같은 결과가 나오게 하는 값)", "random_state",
        code="a, b, c, d = train_test_split(fish_data, fish_target, ㉠=42)\nprint(a.shape, b.shape)",
        why="`random_state` 에 같은 값을 주면 섞이는 순서가 같아져 결과가 재현됩니다.", tags=['random_state'])
    b.W("샘플 60개를 `train_test_split()` 으로 나눌 때 비율을 지정하지 않으면 테스트 세트의 샘플은 몇 개인지 쓰시오.", "15", accept=['15개'],
        chk="X = np.zeros((60, 2)); y = np.zeros(60)\nprint(len(train_test_split(X, y, random_state=0)[1]))",
        why="기본 테스트 비율은 25%이므로 60 × 0.25 = 15개입니다.", tags=['기본 비율'])
    b.W("빈칸 ㉠ 에 들어갈 함수 이름을 쓰시오.", "column_stack",
        code="fish_data = np.㉠((fish_length, fish_weight))\nprint(fish_data.shape)",
        why="두 리스트를 열로 나란히 붙여 (49, 2) 배열을 만드는 함수는 `column_stack` 입니다.", tags=['column_stack'])
    b.W(f"다음 코드로 나눈 **훈련 세트**의 샘플은 몇 개인지 쓰시오. {NOTE}", "36", accept=['36개'], code=SPLIT,
        chk=SPLIT + "\nprint(len(train_input))",
        why="테스트 세트는 49 × 0.25 = 12.25 를 올림한 13개이고, 나머지 36개가 훈련 세트입니다.", tags=['기본 비율'])

    # ── 서술형 ──
    b.E("도미 35마리, 빙어 14마리가 이 순서로 들어 있는 데이터에서 앞 35개를 훈련 세트로, 뒤 14개를 테스트 세트로 나누어 K-최근접 이웃 모델을 훈련했더니 테스트 정확도가 0.0이 나왔다. 그 이유와 해결 방법을 쓰시오.",
        "훈련 세트에는 도미만, 테스트 세트에는 빙어만 들어가는 샘플링 편향이 생겼기 때문이다. 모델은 빙어를 본 적이 없어 테스트 세트의 빙어를 모두 도미로 예측한다. 데이터를 무작위로 섞은 뒤 나누어(예: train_test_split) 두 세트에 도미와 빙어가 골고루 들어가게 해야 한다.",
        "필수 요소(모두 있어야 정답): (1) 훈련 세트에 도미만(또는 한 종류만) 있고 테스트 세트에 빙어만 있다는 점, 즉 편향. (2) 그래서 빙어를 전부 틀린다는 점 또는 빙어를 학습하지 못했다는 점. (3) 해결: 무작위로 섞어서 나눈다 / train_test_split 을 쓴다 / 두 세트에 두 클래스가 골고루 들어가게 한다 중 하나. 이유만 쓰고 해결 방법이 없으면 오답.",
        ['샘플링 편향'], code=BIASED, chk=BIASED + "\nprint(kn.score(test_input, test_target))")
    b.E("모델을 훈련한 데이터로 정확도를 구하면 1.0이 나오더라도 그 값만으로 모델의 성능을 믿기 어렵다. 그 이유를 쓰고, 성능을 올바르게 평가하려면 데이터를 어떻게 사용해야 하는지 설명하시오.",
        "훈련에 쓴 데이터는 모델이 이미 정답을 알고 있는 데이터라서, 그것으로 평가하는 것은 답을 미리 알려 주고 시험을 보는 것과 같다. 데이터를 훈련 세트와 테스트 세트로 나누어 훈련 세트로만 학습하고, 학습에 쓰지 않은 테스트 세트로 평가해야 한다.",
        "필수 요소(모두 있어야 정답): (1) 훈련에 쓴 데이터는 이미 본(정답을 아는) 데이터라 새 데이터에 대한 성능을 알 수 없다는 취지. (2) 훈련 세트와 테스트 세트로 나누어 훈련에 쓰지 않은 데이터로 평가한다는 점.",
        ['훈련 세트', '테스트 세트'])
    b.E("넘파이로 데이터를 직접 섞어서 나눌 때, 입력 배열과 정답 배열을 각각 따로 섞지 않고 **하나의 인덱스 배열을 섞은 뒤 두 배열에 똑같이 적용**한다. 그 이유를 쓰시오.",
        "입력의 각 샘플과 그 정답은 같은 위치에 있어야 짝이 맞는다. 입력과 정답을 따로 섞으면 섞인 순서가 서로 달라져 샘플과 정답의 짝이 어긋난다. 같은 인덱스 배열을 쓰면 두 배열이 같은 순서로 섞여 짝이 유지된다.",
        "필수 요소: 입력 샘플과 정답의 대응(짝)이 유지되어야 한다는 점, 따로 섞으면 그 대응이 깨진다는 점. 둘 중 하나의 취지가 분명하면 정답. '무작위로 섞기 위해서'처럼 섞는 목적만 쓰면 오답.",
        ['shuffle', '배열 인덱싱'])
    return b
