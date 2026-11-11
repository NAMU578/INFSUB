"""기말.1 K-최근접 이웃 알고리즘"""
from lib import Bank
from data import PRE_KNN

SRC = '기말.1.K-최근접 이웃 알고리즘'
NOTE49 = '(도미 35마리, 빙어 14마리의 [길이, 무게] 데이터. 정답은 도미 1, 빙어 0)'


def build():
    b = Bank('01', SRC, PRE_KNN)

    # ── 개념 분류 ──
    b.C(code="fish_data = [[l, w] for l, w in zip(length, weight)]\nfish_target = [1]*35 + [0]*14",
        stem='`length`, `weight` 는 도미 35마리와 빙어 14마리의 값을 차례로 담은 리스트이다. 다음 코드에 대한 설명으로 옳은 것만 <보기>에서 모두 고른 것은?',
        items=[("`len(fish_data)` 는 49이다.", "len(fish_data) == 49"),
               ("`fish_data[0]` 은 원소가 2개인 리스트이다.", "len(fish_data[0]) == 2"),
               ("`fish_target[35]` 는 1이다.", "fish_target[35] == 1")],
        why="`zip` 은 두 리스트에서 원소를 하나씩 꺼내 짝을 지어 주므로 `fish_data` 는 [길이, 무게] 49쌍이 됩니다. `fish_target` 은 인덱스 0~34가 1, 35~48이 0이라 `fish_target[35]` 는 0입니다.",
        tags=['zip', '리스트 내포', '타깃'])
    b.C(stem='K-최근접 이웃 알고리즘에 대한 설명으로 옳은 것만 <보기>에서 모두 고른 것은?',
        items=[("새 데이터를 예측할 때 가장 가까운 이웃들의 다수결로 정한다.", True),
               ("`KNeighborsClassifier` 의 이웃 수 기본값은 5이다.", True),
               ("이웃 수를 전체 데이터 수와 같게 하면 정확도가 가장 높아진다.", False)],
        why="K-최근접 이웃은 가까운 이웃 k개(기본 5개)를 보고 다수인 쪽으로 분류합니다. 이웃을 전체 데이터로 하면 어떤 샘플이든 다수 클래스로만 예측해서 오히려 정확도가 떨어집니다(노트북에서는 0.714).",
        tags=['KNN', 'n_neighbors'], ref='셀 [22]~[30] 인공지능 모델 학습, 이웃을 49개로 바꾼 실험')
    b.C(code="kn = KNeighborsClassifier()\nkn.fit(fish_data, fish_target)\nacc = kn.score(fish_data, fish_target)\npred = kn.predict([[30, 600]])",
        stem=f'다음 코드에 대한 설명으로 옳은 것만 <보기>에서 모두 고른 것은? {NOTE49}',
        items=[("`acc` 는 1.0이다.", "acc == 1.0"),
               ("`pred[0]` 은 1이다. 즉 도미로 예측한다.", "pred[0] == 1"),
               ("`acc` 는 훈련에 쓰지 않은 새 데이터로 평가한 값이다.", False)],
        why="훈련한 데이터 49개를 그대로 다시 넣어 평가했기 때문에 정확도 1.0이 나옵니다. 길이 30, 무게 600인 생선은 도미 쪽 이웃이 많아 1(도미)로 예측합니다.",
        tags=['fit', 'score', 'predict'])
    b.C(code="kn49 = KNeighborsClassifier(n_neighbors=49)\nkn49.fit(fish_data, fish_target)",
        stem=f'다음 코드에 대한 설명으로 옳은 것만 <보기>에서 모두 고른 것은? {NOTE49}',
        items=[("`kn49.score(fish_data, fish_target)` 는 35/49 와 같다.", "kn49.score(fish_data, fish_target) == 35/49"),
               ("`kn49.predict([[10, 7]])[0]` 은 0이다.", "kn49.predict([[10, 7]])[0] == 0"),
               ("`kn49` 는 49개 샘플을 모두 도미(1)로 예측한다.", "all(kn49.predict(fish_data) == 1)")],
        why="이웃이 49개면 전체 데이터가 이웃이라 항상 다수인 도미(35개)로 예측합니다. 빙어처럼 작은 [10, 7] 도 1로 예측하고, 도미 35개만 맞히므로 정확도는 35/49 입니다.",
        tags=['n_neighbors', '정확도'])
    b.C(code="a = [1]*3 + [0]*2\nb = [1, 2] + [3]\nc = [[x, y] for x, y in zip([1, 2], [5, 6])]", pre='',
        items=[("`a` 는 `[1, 1, 1, 0, 0]` 이다.", "a == [1, 1, 1, 0, 0]"),
               ("`b` 는 `[4, 5]` 이다.", "b == [4, 5]"),
               ("`c` 는 `[[1, 5], [2, 6]]` 이다.", "c == [[1, 5], [2, 6]]")],
        why="파이썬 리스트에서 `*` 는 반복, `+` 는 이어 붙이기입니다. `[1, 2] + [3]` 은 `[1, 2, 3]` 입니다. 원소끼리 더해지는 것은 넘파이 배열일 때입니다.",
        tags=['리스트 연산', 'zip'])

    # ── 빈칸 ──
    b.B("fish_data = [[l, w] for l, w in ㉠(length, weight)]\nprint(㉡(fish_data))", ('zip', 'len'),
        [('len', 'zip'), ('zip', 'sum'), ('range', 'len'), ('list', 'len')],
        why="두 리스트에서 원소를 하나씩 짝지어 꺼내는 함수는 `zip` 이고, 리스트의 원소 개수는 `len` 으로 셉니다. 도미 35 + 빙어 14 = 49쌍입니다.",
        tags=['zip', 'len'])
    b.B("from sklearn.㉠ import KNeighborsClassifier\nkn = KNeighborsClassifier()\nkn.㉡(fish_data, fish_target)\nprint(kn.score(fish_data, fish_target))",
        ('neighbors', 'fit'), [('neighbors', 'predict'), ('model_selection', 'fit'), ('linear_model', 'fit'), ('neighbors', 'train')],
        why="`KNeighborsClassifier` 는 `sklearn.neighbors` 에 있고, 훈련은 `fit(입력, 정답)` 으로 합니다.", tags=['import', 'fit'])
    b.B("kn49 = KNeighborsClassifier(㉠=49)\nkn49.fit(fish_data, fish_target)\nprint(kn49.㉡(fish_data, fish_target))",
        ('n_neighbors', 'score'), [('n_neighbors', 'predict'), ('neighbors', 'score'), ('k', 'score'), ('n_neighbors', 'fit')],
        why="이웃 수는 `n_neighbors` 로 정하고, 정확도는 `score(입력, 정답)` 이 돌려줍니다. 0.714… 는 35/49 입니다.", tags=['n_neighbors', 'score'])
    b.B("fish_target = [1]*㉠ + [0]*㉡\nprint(len(fish_target), sum(fish_target))", ('35', '14'),
        [('14', '35'), ('35', '49'), ('49', '35'), ('1', '0')], pre='',
        why="전체 길이가 49이고 합(1의 개수)이 35이므로 1이 35개, 0이 14개입니다.", tags=['타깃', '리스트 반복'])
    b.B("import matplotlib.pyplot as plt\nplt.scatter(bream_length, bream_weight)\nplt.scatter(smelt_length, smelt_weight)\nplt.㉠('length')\nplt.㉡('weight')\nplt.show()",
        ('xlabel', 'ylabel'), [('ylabel', 'xlabel'), ('xlim', 'ylim'), ('title', 'legend'), ('xticks', 'yticks')],
        stem='가로축 이름을 length, 세로축 이름을 weight 로 붙이려고 한다. ㉠, ㉡에 들어갈 것으로 알맞은 것은?', result=False,
        why="축 이름은 `plt.xlabel()`, `plt.ylabel()` 로 붙입니다. `xlim`/`ylim` 은 축의 범위, `xticks`/`yticks` 는 눈금입니다.", tags=['산점도', '축 이름'])

    # ── 경계값 ──
    b.D("kn = KNeighborsClassifier()\nkn.fit(fish_data, fish_target)\nfor n in range(5, 50):\n    kn.n_neighbors = n\n    score = kn.score(fish_data, fish_target)\n    if score < 1:\n        print(n, score)\n        break",
        ['5 0.9795918367346939', '17 0.9795918367346939', '49 0.7142857142857143', '18 0.7142857142857143'],
        stem=f'다음 코드를 실행했을 때 출력되는 것은? {NOTE49}',
        why="이웃 수를 5부터 늘리다가 정확도가 처음 1보다 작아지는 순간 한 번만 출력하고 `break` 로 끝납니다. 이웃이 18개일 때 처음으로 한 마리를 틀려 48/49 = 0.9795… 가 됩니다.",
        tags=['n_neighbors', 'break', '확인 문제'])
    b.D("fish_target = [1]*35 + [0]*14\nprint(fish_target[34], fish_target[35], fish_target[-1])",
        ['1 1 0', '0 0 0', '1 0 1', '0 1 0'], pre='',
        why="1이 35개이므로 인덱스 0~34가 1이고, 인덱스 35부터 0입니다. 마지막 원소도 0입니다.", tags=['인덱스', '타깃'])
    b.D("X = [[i] for i in range(50)]\ny = [1]*30 + [0]*20\nkn = KNeighborsClassifier(n_neighbors=50)\nkn.fit(X, y)\nprint(kn.score(X, y))",
        ['0.4', '1.0', '0.5', '0.714'],
        why="샘플 50개가 전부 이웃이므로 항상 다수 클래스인 1로 예측합니다. 정답이 1인 30개만 맞히므로 30/50 = 0.6 입니다.", tags=['n_neighbors', '정확도'])
    b.D("X = [[1], [2], [3], [6], [7], [8], [9]]\ny = [0, 0, 0, 1, 1, 1, 1]\nkn = KNeighborsClassifier()\nkn.fit(X, y)\nprint(kn.predict([[4]])[0], kn.predict([[5]])[0])",
        ['0 0', '1 1', '1 0', '1 0.5'],
        why="기본 이웃 수는 5입니다. 4에서 가까운 다섯 개는 3, 2, 6, 1, 7 이라 0이 3개로 다수이고, 5에서 가까운 다섯 개는 6, 3, 7, 2, 8 이라 1이 3개로 다수입니다.", tags=['이웃 5개', '다수결'])
    b.D("print(len(fish_data), len(fish_data[0]), len(fish_target))",
        ['49 49 2', '2 49 49', '98 2 49', '49 2 2'],
        stem=f'다음 코드를 실행했을 때 출력되는 것은? {NOTE49}',
        why="`fish_data` 는 샘플 49개의 리스트이고 각 샘플은 [길이, 무게] 2개 값입니다. 정답도 샘플 수와 같은 49개입니다.", tags=['데이터 구조'])

    # ── 상태 예측 ──
    b.R("print(fish_data[0], fish_target[0])", ['[25.4, 242.0] 0', '25.4 1', '[25.4, 26.3] 1', '[242.0, 25.4] 1'],
        stem='`length` 의 첫 값은 25.4, `weight` 의 첫 값은 242.0 이고 둘 다 도미의 값이다. 다음 코드를 실행했을 때 출력되는 것은?',
        why="`fish_data` 의 각 원소는 [길이, 무게] 순서의 리스트이고, 앞쪽 35개는 도미라서 정답이 1입니다.", tags=['데이터 구조'])
    b.R("print(kn.predict([[30, 600]]))", ['1', '[0]', '[[1]]', '[30, 600]'],
        stem=f'훈련된 모델 `kn` 으로 다음 코드를 실행했을 때 출력되는 것은? {NOTE49}',
        why="`predict` 는 샘플마다 예측값 하나씩을 담은 **배열**을 돌려줍니다. 샘플이 하나여도 `[1]` 처럼 배열로 나옵니다.", tags=['predict', '반환값'])
    b.R("kn49 = KNeighborsClassifier(n_neighbors=49)\nkn49.fit(fish_data, fish_target)\nprint(kn49.score(fish_data, fish_target))",
        ['1.0', '0.2857142857142857', '0.49', '0.35'],
        stem=f'다음 코드를 실행했을 때 출력되는 것은? {NOTE49}',
        why="49개 전부가 이웃이라 항상 도미로 예측하고, 도미 35개만 맞히므로 35/49 = 0.714… 입니다.", tags=['n_neighbors', '정확도'])
    b.R("print([1]*3 + [0]*2, [1, 2] + [3])", ['[1, 1, 1, 0, 0] [4, 5]', '[3, 0] [1, 2, 3]', '[3, 0] [4, 5]', '[1, 1, 1] [0, 0] [1, 2, 3]'], pre='',
        why="리스트의 `*` 는 반복, `+` 는 이어 붙이기입니다.", tags=['리스트 연산'])
    b.R("pairs = [[l, w] for l, w in zip([1, 2, 3], [10, 20, 30])]\nprint(pairs[1], len(pairs))",
        ['[1, 10] 3', '[2, 20] 2', '[1, 2] 3', '[10, 20] 6'], pre='',
        why="`zip` 은 같은 위치의 원소끼리 짝을 짓습니다. 두 번째 쌍은 [2, 20] 이고 쌍은 모두 3개입니다.", tags=['zip'])
    b.R("new = [30, 600]\nif kn.predict([new]) == 1:\n    print('도미')\nelse:\n    print('빙어')", ['빙어', '[1]', 'True', '도미 빙어'],
        stem=f'훈련된 모델 `kn` 으로 다음 코드를 실행했을 때 출력되는 것은? {NOTE49}',
        why="`[new]` 는 `[[30, 600]]` 이라 2차원 입력이 됩니다. 예측 결과가 1(도미)이므로 조건이 참입니다.", tags=['predict', '2차원 입력'])

    # ── 대조 ──
    b.X("import numpy as np\n# 방법1\nprint([1, 2] + [3, 4])\n\n# 방법2\nprint(np.array([1, 2]) + np.array([3, 4]))",
        [('[4, 6]', '[4 6]'), ('[1, 2, 3, 4]', '[1 2 3 4]'), ('[4, 6]', '[1 2 3 4]'), ('[1, 2, 3, 4]', '[4, 6]')], pre='',
        why="리스트의 `+` 는 이어 붙이기, 넘파이 배열의 `+` 는 같은 위치 원소끼리 덧셈입니다. 넘파이 배열은 출력할 때 쉼표가 없습니다.", tags=['리스트', '넘파이'])
    b.X("# 방법1: 이웃 5개\nprint(kn.score(fish_data, fish_target))\n\n# 방법2: 이웃 49개\nprint(kn49.score(fish_data, fish_target))",
        [('0.7142857142857143', '1.0'), ('1.0', '1.0'), ('1.0', '0.2857142857142857'), ('0.9795918367346939', '0.7142857142857143')],
        stem=f'`kn` 은 이웃 5개, `kn49` 는 이웃 49개로 같은 데이터를 훈련한 모델이다. ㉠, ㉡에 출력되는 값으로 알맞은 것은? {NOTE49}',
        why="이웃 5개면 49개를 모두 맞혀 1.0, 이웃 49개면 전부 도미로 예측해 35/49 입니다.", tags=['n_neighbors', '정확도'])
    b.X("# 방법1: 이웃 5개\nprint(kn.predict([[10, 7]])[0])\n\n# 방법2: 이웃 49개\nprint(kn49.predict([[10, 7]])[0])",
        [('1', '0'), ('0', '0'), ('1', '1'), ('0', '0.714')],
        stem=f'길이 10, 무게 7인 생선(빙어와 비슷한 크기)을 두 모델로 예측한다. ㉠, ㉡에 출력되는 값으로 알맞은 것은? {NOTE49}',
        why="이웃 5개 모델은 가까운 빙어 다섯 마리를 보고 0(빙어)으로 예측합니다. 이웃 49개 모델은 전체 데이터의 다수인 도미(1)로 예측합니다.", tags=['n_neighbors', 'predict'])
    b.X("# 방법1\nprint([1]*3)\n\n# 방법2\nprint([1*3])", [('[3]', '[1, 1, 1]'), ('[1, 1, 1]', '[1, 1, 1]'), ('[3]', '[3]'), ('[1, 1, 1]', '3')], pre='',
        why="`[1]*3` 은 리스트를 세 번 반복한 `[1, 1, 1]` 이고, `[1*3]` 은 숫자 3 하나가 든 리스트입니다.", tags=['리스트 반복'])

    # ── 조건 매핑 ──
    b.S(["K-최근접 이웃 분류 모델 객체를 만든다.", "예측할 때 참고하는 이웃의 수를 7개로 한다."],
        "KNeighborsClassifier(n_neighbors=7)",
        ["KNeighborsClassifier(k=7)", "KNeighborsClassifier(neighbors=7)", "KNeighborsClassifier().fit(7)", "KNeighborsClassifier(n=7)"],
        code="kn = ____", chk="print(kn.n_neighbors)",
        why="이웃 수를 정하는 매개변수의 이름은 `n_neighbors` 입니다.", tags=['n_neighbors'])
    b.S(["도미 3마리, 빙어 2마리의 정답 리스트를 만든다.", "도미는 1, 빙어는 0으로 표시하고 도미가 앞에 온다."],
        "[1]*3 + [0]*2", ["[1*3] + [0*2]", "[1, 0]*3", "[3]*1 + [2]*0", "[0]*3 + [1]*2"],
        code="target = ____", chk="print(target)", pre='',
        why="`[1]*3` 은 `[1, 1, 1]`, `[0]*2` 는 `[0, 0]` 이고 `+` 로 이어 붙입니다.", tags=['타깃'])
    b.S(["훈련된 모델 `kn` 으로 예측한다.", "길이 20, 무게 100인 생선 **한 마리**가 대상이다."],
        "kn.predict([[20, 100]])", ["kn.predict([20, 100])", "kn.predict(20, 100)", "kn.score([[20, 100]])", "kn.fit([[20, 100]])"],
        code="result = ____", chk="print(len(result))",
        why="입력은 샘플들의 리스트(2차원)여야 하므로 한 마리여도 `[[20, 100]]` 처럼 대괄호를 두 겹으로 씁니다.", tags=['predict', '2차원 입력'])
    b.S(["훈련된 모델 `kn` 의 정확도를 구한다.", "입력은 `fish_data`, 정답은 `fish_target` 이다."],
        "kn.score(fish_data, fish_target)", ["kn.score(fish_target, fish_data)", "kn.predict(fish_data, fish_target)", "kn.fit(fish_data, fish_target)", "kn.accuracy(fish_data)"],
        code="acc = ____", chk="print(acc)",
        why="`score(입력, 정답)` 순서입니다. 분류 모델의 `score` 는 정확도(맞힌 개수 ÷ 전체 개수)를 돌려줍니다.", tags=['score'])

    # ── 서답형 ──
    b.W("빈칸 ㉠ 에 들어갈 메서드 이름을 쓰시오. (모델을 훈련하는 메서드)", "fit",
        code="kn = KNeighborsClassifier()\nkn.㉠(fish_data, fish_target)\nprint(kn.score(fish_data, fish_target))",
        why="사이킷런 모델은 `fit(입력, 정답)` 으로 훈련합니다.", tags=['fit'])
    b.W("빈칸 ㉠ 에 들어갈 매개변수 이름을 쓰시오.", "n_neighbors",
        code="kn49 = KNeighborsClassifier(㉠=49)\nkn49.fit(fish_data, fish_target)\nprint(kn49.score(fish_data, fish_target))",
        why="참고할 이웃의 수는 `n_neighbors` 로 지정합니다.", tags=['n_neighbors'])
    b.W("도미 40마리와 빙어 10마리로 `KNeighborsClassifier(n_neighbors=50)` 모델을 훈련한 뒤, 같은 50마리로 `score()` 를 구하면 얼마인지 소수로 쓰시오.",
        "0.8", accept=['0.80', '4/5', '40/50', '80%', '.8'], chk="print(40/50)",
        why="50개 전부가 이웃이므로 항상 다수인 도미로 예측합니다. 도미 40마리만 맞히므로 40/50 = 0.8 입니다.", tags=['n_neighbors', '정확도'])
    b.W("빈칸 ㉠ 에 들어갈 함수 이름을 쓰시오.", "zip", pre='',
        code="length = [25.4, 26.3]\nweight = [242.0, 290.0]\nfish_data = [[l, w] for l, w in ㉠(length, weight)]\nprint(fish_data)",
        why="`zip` 은 두 리스트의 같은 위치 원소를 짝지어 하나씩 꺼내 줍니다.", tags=['zip'])

    # ── 서술형 ──
    b.E("도미 35마리와 빙어 14마리로 `KNeighborsClassifier(n_neighbors=49)` 모델을 훈련한 뒤 같은 데이터로 `score()` 를 구했더니 약 0.714가 나왔다. 이 값이 나온 이유를 설명하시오.",
        "이웃을 49개로 하면 전체 데이터 49개가 모두 이웃이 된다. 그러면 어떤 샘플이든 다수인 도미로 예측하므로 도미 35마리만 맞히고 빙어 14마리는 모두 틀린다. 따라서 정확도는 35/49 ≈ 0.714 이다.",
        "필수 요소(모두 있어야 정답): (1) 이웃 수가 전체 데이터 수(49)와 같아서 모든 데이터가 이웃이 된다는 점. (2) 그래서 항상 다수 클래스인 도미로 예측한다는 점. (3) 도미 35마리만 맞혀 35/49 가 된다는 계산 또는 그와 같은 뜻의 설명. '이웃이 많아서 부정확하다' 수준으로만 쓰고 다수 클래스나 35/49 를 언급하지 않으면 오답.",
        ['n_neighbors', '정확도'], chk="print(round(35/49, 3))")
    b.E("K-최근접 이웃 알고리즘이 새로운 생선 한 마리를 도미 또는 빙어로 분류하는 과정을 설명하시오. (이웃 수는 기본값을 쓴다고 가정)",
        "새 데이터와 훈련 데이터 사이의 거리를 계산해서 가장 가까운 이웃 5개를 찾는다. 그 5개 중 더 많은 쪽(다수결)의 클래스로 새 데이터를 분류한다.",
        "필수 요소(모두 있어야 정답): (1) 가장 가까운(거리가 가까운) 이웃을 찾는다는 점. (2) 이웃들의 다수결(더 많은 클래스)로 정한다는 점. 이웃 수 5는 언급하지 않아도 감점하지 않는다. '규칙이나 식을 학습한다'처럼 다른 알고리즘의 설명이면 오답.",
        ['KNN', '다수결'])
    b.E("훈련된 모델 `kn` 에 `kn.predict([30, 600])` 을 실행하면 오류가 난다. 오류가 나는 이유를 쓰고, 길이 30, 무게 600인 생선 한 마리를 예측하도록 코드를 고쳐 쓰시오.",
        "predict 의 입력은 샘플들이 모인 2차원 리스트(배열)여야 하는데 [30, 600] 은 1차원이기 때문이다.\n고친 코드: kn.predict([[30, 600]])",
        "필수 요소(모두 있어야 정답): (1) 입력이 2차원이어야 한다(샘플의 리스트여야 한다)는 이유. (2) kn.predict([[30, 600]]) 처럼 대괄호를 두 겹으로 쓴 코드. new = [30, 600]; kn.predict([new]) 도 정답으로 인정한다.",
        ['predict', '2차원 입력'], chk="print(kn.predict([[30, 600]]))")
    return b
