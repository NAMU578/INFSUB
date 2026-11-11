"""기말.3 스케일이 다른 특성처리"""
from lib import Bank
from data import PRE_NP, PRE_SCALE

SRC = '기말.3.스케일이 다른 특성처리'
NOTE = '(`fish_data` 는 도미 35마리, 빙어 14마리의 [길이, 무게] (49, 2) 배열, `fish_target` 은 도미 1, 빙어 0)'
ST = ('(`train_input`, `train_target` 은 `stratify` 로 나눈 훈련 세트 36개이고, `kn` 은 이 원래 값으로 훈련한 '
      '`KNeighborsClassifier()` 모델이다. `mean`, `std` 는 훈련 세트의 특성별 평균과 표준편차)')
STRAT = "train_input, test_input, train_target, test_target = train_test_split(\n    fish_data, fish_target, stratify=fish_target, random_state=42)"
SCALE = "train_scaled = (train_input - mean) / std\nkn.fit(train_scaled, train_target)"


def build():
    b = Bank('03', SRC, PRE_SCALE)
    PRE_SCALED = PRE_SCALE + "\n" + SCALE + "\ntest_scaled = (test_input - mean) / std\nnew = ([25, 150] - mean) / std"

    # ── 개념 분류 ──
    b.C(code=STRAT, pre=PRE_NP, stem=f'다음 코드에 대한 설명으로 옳은 것만 <보기>에서 모두 고른 것은? {NOTE}',
        items=[("테스트 세트의 도미는 9마리이다.", "int(test_target.sum()) == 9"),
               ("테스트 세트의 샘플은 13개이다.", "len(test_target) == 13"),
               ("`stratify` 를 쓰지 않았을 때와 테스트 세트의 도미 수가 같다.", "int(test_target.sum()) == int(train_test_split(fish_data, fish_target, random_state=42)[3].sum())")],
        why="`stratify=fish_target` 은 정답의 클래스 비율이 두 세트에 비슷하게 유지되도록 나눕니다. 테스트 세트는 도미 9, 빙어 4가 됩니다. `stratify` 없이 나누면 도미 10, 빙어 3이었습니다.",
        tags=['stratify', '클래스 비율'])
    b.C(code="kn = KNeighborsClassifier()\nkn.fit(train_input, train_target)\ndistances, indexes = kn.kneighbors([[25, 150]])",
        stem='`stratify` 로 나눈 훈련 세트(스케일을 맞추지 않은 원래 값)로 다음 코드를 실행했다. 설명으로 옳은 것만 <보기>에서 모두 고른 것은?',
        items=[("`kn.score(test_input, test_target)` 은 1.0이다.", "kn.score(test_input, test_target) == 1.0"),
               ("`kn.predict([[25, 150]])` 은 도미(1)로 예측한다.", "kn.predict([[25, 150]])[0] == 1"),
               ("`train_target[indexes]` 를 보면 이웃 5개 중 도미는 1개뿐이다.", "int(train_target[indexes].sum()) == 1")],
        why="테스트 정확도는 1.0이지만 길이 25, 무게 150인 생선은 빙어로 예측합니다. 이웃 5개 중 4개가 빙어이기 때문입니다. 무게의 값 범위가 길이보다 훨씬 커서 거리가 무게로만 정해진 결과입니다.",
        tags=['kneighbors', '스케일'])
    b.C(code="mean = np.mean(train_input, axis=0)\nstd = np.std(train_input, axis=0)\ntrain_scaled = (train_input - mean) / std",
        stem='`train_input` 은 shape 이 `(36, 2)` 인 훈련 세트이다. 다음 코드에 대한 설명으로 옳은 것만 <보기>에서 모두 고른 것은?',
        items=[("`mean.shape` 은 `(2,)` 이다.", "mean.shape == (2,)"),
               ("`train_scaled` 의 열마다 평균을 구하면 0에 가깝다.", "bool(np.allclose(train_scaled.mean(axis=0), 0))"),
               ("`train_scaled.shape` 은 `(36,)` 이다.", "train_scaled.shape == (36,)")],
        why="`axis=0` 은 열(특성)마다 계산하므로 평균과 표준편차가 2개씩 나옵니다. 브로드캐스팅으로 모든 행에 같은 계산이 적용되어 shape 은 `(36, 2)` 그대로이고, 표준점수로 바꾼 값은 평균 0, 표준편차 1이 됩니다.",
        tags=['표준점수', 'axis', '브로드캐스팅'])
    b.C(stem='특성의 스케일과 데이터 전처리에 대한 설명으로 옳은 것만 <보기>에서 모두 고른 것은?',
        items=[("표준점수는 (값 − 평균) ÷ 표준편차로 구한다.", True),
               ("테스트 세트는 테스트 세트 자신의 평균과 표준편차로 변환해야 한다.", False),
               ("K-최근접 이웃처럼 거리를 계산하는 알고리즘은 특성의 스케일에 영향을 받는다.", True)],
        why="테스트 세트와 새 샘플은 **훈련 세트의** 평균과 표준편차로 변환해야 같은 기준에서 비교할 수 있습니다. 거리 기반 알고리즘은 값 범위가 큰 특성에 끌려가므로 스케일을 맞춰야 합니다.",
        tags=['표준점수', '전처리'], ref='셀 [28]~[47] 표준점수로 바꾸기, 전처리 데이터로 모델 훈련하기')
    b.C(code=SCALE + "\nnew = ([25, 150] - mean) / std", stem=f'다음 코드에 대한 설명으로 옳은 것만 <보기>에서 모두 고른 것은? {ST}',
        items=[("`kn.predict([new])` 는 도미(1)로 예측한다.", "kn.predict([new])[0] == 1"),
               ("`new` 의 두 값은 모두 음수이다.", "bool(new[0] < 0 and new[1] < 0)"),
               ("`new` 는 테스트 세트의 평균과 표준편차로 변환한 값이다.", False)],
        why="길이 25와 무게 150은 훈련 세트의 평균(약 27.3, 454.1)보다 작아서 표준점수가 둘 다 음수입니다. 훈련 세트와 같은 기준으로 변환한 뒤 예측하면 도미로 올바르게 분류됩니다.",
        tags=['표준점수', 'predict'])

    # ── 빈칸 ──
    b.B("mean = np.㉠(train_input, axis=㉡)\nprint(mean.round(1))", ('mean', '0'), [('mean', '1'), ('std', '0'), ('sum', '0'), ('mean', '2')],
        stem='훈련 세트 `train_input` (shape `(36, 2)`)의 **특성별 평균**을 구하려고 한다. ㉠, ㉡에 들어갈 것으로 알맞은 것은?',
        why="평균은 `np.mean`, 열(특성)마다 계산하려면 `axis=0` 입니다. 길이의 평균 약 27.3, 무게의 평균 약 454.1 두 값이 나옵니다.", tags=['mean', 'axis'])
    b.B("distances, indexes = kn.㉠([[25, 150]])\nprint(train_target[㉡])", ('kneighbors', 'indexes'),
        [('kneighbors', 'distances'), ('neighbors', 'indexes'), ('predict', 'indexes'), ('n_neighbors', 'indexes')],
        stem=f'㉠, ㉡에 들어갈 것으로 알맞은 것은? {ST}',
        why="`kneighbors()` 는 가장 가까운 이웃까지의 거리와 이웃의 인덱스를 차례로 돌려줍니다. 인덱스로 `train_target` 을 뽑으면 이웃들의 정답을 볼 수 있습니다.", tags=['kneighbors'])
    b.B("train_scaled = (train_input - ㉠) / ㉡\nprint(np.allclose(train_scaled.std(axis=0), 1))", ('mean', 'std'),
        [('std', 'mean'), ('mean', 'mean'), ('train_target', 'std'), ('mean', 'train_input')],
        stem=f'훈련 세트를 표준점수로 바꾸려고 한다. ㉠, ㉡에 들어갈 것으로 알맞은 것은? {ST}',
        why="표준점수는 (값 − 평균) ÷ 표준편차입니다. 변환한 뒤에는 각 특성의 표준편차가 1이 됩니다.", tags=['표준점수'])
    b.B("train_input, test_input, train_target, test_target = train_test_split(\n    fish_data, fish_target, ㉠=fish_target, random_state=42)\nprint(int(test_target.㉡()), len(test_target))",
        ('stratify', 'sum'), [('stratify', 'max'), ('shuffle', 'sum'), ('test_size', 'sum'), ('stratify', 'mean')], pre=PRE_NP,
        stem=f'클래스 비율을 유지하며 나눈 뒤 테스트 세트의 도미 수와 전체 샘플 수를 출력하려고 한다. ㉠, ㉡에 들어갈 것으로 알맞은 것은? {NOTE}',
        why="클래스 비율을 맞추는 매개변수는 `stratify` 입니다. 도미가 1이므로 정답의 합이 도미의 수입니다.", tags=['stratify'])
    b.B(SCALE + "\ntest_scaled = (㉠ - mean) / std\nprint(kn.㉡(test_scaled, test_target))", ('test_input', 'score'),
        [('test_target', 'score'), ('train_input', 'predict'), ('test_input', 'fit'), ('test_scaled', 'score')],
        stem=f'㉠, ㉡에 들어갈 것으로 알맞은 것은? {ST}',
        why="테스트 입력도 훈련 세트의 `mean`, `std` 로 변환한 다음 `score(입력, 정답)` 으로 평가합니다.", tags=['표준점수', 'score'])

    # ── 경계값 ──
    b.D("distances, indexes = kn.kneighbors([[25, 150]])\nprint(distances.shape, indexes.shape)", ['(5,) (5,)', '(1, 5) (5,)', '(5, 1) (5, 1)', '(1, 36) (1, 36)'],
        stem=f'다음 코드를 실행했을 때 출력되는 것은? {ST}',
        why="샘플 1개에 대해 기본 이웃 5개를 찾으므로 거리와 인덱스 모두 1행 5열입니다.", tags=['kneighbors', 'shape'])
    b.D("print(np.mean(train_input, axis=0).shape, np.mean(train_input, axis=1).shape)", ['(36,) (2,)', '(2,) (2,)', '(1, 2) (36, 1)', '() ()'],
        stem='`train_input` 의 shape 은 `(36, 2)` 이다. 다음 코드를 실행했을 때 출력되는 것은?',
        why="`axis=0` 은 열마다 계산해 값이 2개, `axis=1` 은 행마다 계산해 값이 36개입니다. 특성별 평균이 필요하므로 노트북은 `axis=0` 을 씁니다.", tags=['axis'])
    b.D(STRAT + "\nprint(int(test_target.sum()), int(len(test_target) - test_target.sum()))", ['10 3', '9 3', '10 4', '35 14'], pre=PRE_NP,
        stem=f'다음 코드를 실행했을 때 출력되는 것은? {NOTE}',
        why="`stratify` 를 쓰면 테스트 세트 13개가 도미 9, 빙어 4로 나뉘어 원래 비율(2.5:1)에 가까워집니다. 쓰지 않았을 때는 도미 10, 빙어 3이었습니다.", tags=['stratify'])
    b.D("x = np.array([2, 4, 4, 4, 5, 5, 7, 9])\nz = (x - x.mean()) / x.std()\nprint(x.mean(), x.std(), z[0], z[-1])", ['5.0 2.0 -3.0 4.0', '5.0 2.0 1.5 -2.0', '5.0 4.0 -0.75 1.0', '40 2.0 -1.5 2.0'],
        pre='import numpy as np',
        why="평균 5, 표준편차 2입니다. 2의 표준점수는 (2 − 5) ÷ 2 = −1.5, 9의 표준점수는 (9 − 5) ÷ 2 = 2.0 입니다.", tags=['표준점수'])
    b.D("print((train_input - mean).shape, (train_input[0] - mean).shape)", ['(36, 2) (36, 2)', '(2,) (2,)', '(36,) (2,)', '(36, 2) ()'],
        stem='`train_input` 의 shape 은 `(36, 2)`, `mean` 의 shape 은 `(2,)` 이다. 다음 코드를 실행했을 때 출력되는 것은?',
        why="브로드캐스팅으로 `mean` 이 모든 행에 적용되어 `(36, 2)` 가 유지됩니다. `train_input[0]` 은 샘플 하나라 `(2,)` 이고 빼도 `(2,)` 입니다.", tags=['브로드캐스팅'])

    # ── 상태 예측 ──
    b.R("print(kn.predict([[25, 150]]))", ['[1.]', '[25, 150]', '[0. 1.]', '0.0'], stem=f'다음 코드를 실행했을 때 출력되는 것은? {ST}',
        why="스케일을 맞추지 않은 모델은 길이 25, 무게 150인 생선을 빙어(0)로 예측합니다. 정답 배열이 실수라서 `[0.]` 으로 출력됩니다.", tags=['스케일', 'predict'])
    b.R("distances, indexes = kn.kneighbors([[25, 150]])\nprint(train_target[indexes])", ['[[1. 1. 1. 1. 0.]]', '[[0. 0. 0. 0. 0.]]', '[1. 0. 0. 0. 0.]', '[[1. 1. 1. 1. 1.]]'],
        stem=f'다음 코드를 실행했을 때 출력되는 것은? {ST}',
        why="가장 가까운 이웃 다섯 중 도미는 한 마리뿐이고 나머지 넷은 빙어입니다. 그래서 다수결로 빙어가 됩니다. `indexes` 가 2차원이라 결과도 2차원입니다.", tags=['kneighbors'])
    b.R("a = np.array([[1, 10], [3, 30], [5, 50]])\nprint(np.mean(a, axis=0), np.mean(a, axis=1))", ['[ 5.5 16.5 27.5] [ 3. 30.]', '[ 3. 30.] [ 3. 30.]', '16.5 16.5', '[ 9. 90.] [11. 33. 55.]'],
        pre='import numpy as np',
        why="`axis=0` 은 열마다 평균을 내서 [3, 30], `axis=1` 은 행마다 평균을 내서 [5.5, 16.5, 27.5] 입니다.", tags=['axis'])
    b.R(SCALE + "\nnew = ([25, 150] - mean) / std\nprint(kn.predict([new]))", ['[0.]', '[25. 150.]', '[-0.23 -0.94]', '[1. 0.]'],
        stem=f'다음 코드를 실행했을 때 출력되는 것은? {ST}',
        why="훈련 세트와 새 샘플을 같은 기준(훈련 세트의 평균과 표준편차)으로 표준화하면 두 특성이 거리에 고르게 반영되어 도미(1)로 예측합니다.", tags=['표준점수', 'predict'])
    b.R("a = np.array([[1, 10], [3, 30]])\nprint((a - np.array([1, 10])).tolist())", ['[[0, 9], [2, 20]]', '[[0, 0], [3, 30]]', '[[0, 0]]', '[[1, 10], [2, 20]]'],
        pre='import numpy as np',
        why="shape 이 `(2,)` 인 배열이 각 행에 똑같이 적용됩니다(브로드캐스팅). 첫 행은 [1−1, 10−10], 둘째 행은 [3−1, 30−10] 입니다.", tags=['브로드캐스팅'])
    b.R("distances, indexes = kn.kneighbors([[25, 150]])\nprint(round(float(distances[0][0]), 1))", ['0.4', '150.0', '25.0', '5.0'],
        stem=f'가장 가까운 이웃은 길이 25.4, 무게 242.0 인 도미이다. 다음 코드를 실행했을 때 출력되는 것은? {ST}',
        why="거리는 √((25 − 25.4)² + (150 − 242)²) ≈ 92.0 입니다. 길이 차이 0.4는 거의 영향이 없고 무게 차이 92가 거리를 결정합니다.", tags=['거리', '스케일'])

    # ── 대조 ──
    b.X("# 방법1: 원래 값으로 훈련\nkn.fit(train_input, train_target)\nprint(kn.predict([[25, 150]]))\n\n"
        "# 방법2: 표준점수로 바꿔서 훈련\ntrain_scaled = (train_input - mean) / std\nkn.fit(train_scaled, train_target)\nprint(kn.predict([([25, 150] - mean) / std]))",
        [('[1.]', '[0.]'), ('[0.]', '[0.]'), ('[1.]', '[1.]'), ('[0.]', '[-0.23 -0.94]')],
        stem=f'㉠, ㉡에 출력되는 값으로 알맞은 것은? {ST}',
        why="원래 값으로 훈련하면 무게가 거리를 지배해 빙어(0)로, 표준점수로 바꾸면 두 특성이 고르게 반영되어 도미(1)로 예측합니다.", tags=['스케일', '표준점수'])
    b.X("a = np.array([[1, 2], [3, 4], [5, 6]])\n# 방법1\nprint(np.mean(a, axis=0))\n\n# 방법2\nprint(np.mean(a, axis=1))",
        [('[1.5 3.5 5.5]', '[3. 4.]'), ('[3. 4.]', '[3. 4.]'), ('3.5', '3.5'), ('[ 9. 12.]', '[ 3.  7. 11.]')], pre='import numpy as np',
        why="`axis=0` 은 열마다(세로 방향) 평균을 내서 값이 2개, `axis=1` 은 행마다(가로 방향) 평균을 내서 값이 3개입니다.", tags=['axis'])
    b.X("# 방법1\na, b, c, d = train_test_split(fish_data, fish_target, random_state=42)\nprint(int(d.sum()))\n\n"
        "# 방법2\na, b, c, d = train_test_split(fish_data, fish_target, stratify=fish_target, random_state=42)\nprint(int(d.sum()))",
        [('9', '10'), ('10', '10'), ('9', '9'), ('13', '9')], pre=PRE_NP,
        stem=f'`d` 는 테스트 세트의 정답(13개)이다. ㉠, ㉡에 출력되는 값(테스트 세트의 도미 수)으로 알맞은 것은? {NOTE}',
        why="`stratify` 없이 나누면 테스트 세트에 도미가 10마리(빙어 3), `stratify=fish_target` 을 쓰면 도미 9마리(빙어 4)로 원래 비율에 더 가깝습니다.", tags=['stratify'])
    b.X("x = np.array([2, 4, 4, 4, 5, 5, 7, 9])\n# 방법1\nprint(np.mean(x))\n\n# 방법2\nprint(np.std(x))", [('2.0', '5.0'), ('5.0', '5.0'), ('40.0', '2.0'), ('5.0', '4.0')],
        pre='import numpy as np',
        why="`np.mean` 은 평균(40 ÷ 8 = 5), `np.std` 는 표준편차(평균에서 떨어진 정도, 여기서는 2)를 구합니다.", tags=['mean', 'std'])

    # ── 조건 매핑 ──
    b.S(["훈련 세트 `train_input` (shape `(36, 2)`)에서 **특성(열)마다** 평균을 구한다.", "결과의 shape 은 `(2,)` 이다."], "np.mean(train_input, axis=0)",
        ["np.mean(train_input, axis=1)", "np.mean(train_input)", "np.mean(train_input, axis=2)", "np.sum(train_input, axis=0)"],
        code="mean = ____", chk="print(mean.shape, bool(np.isclose(mean[0], train_input[:, 0].mean())))",
        why="`axis=0` 이 열 방향 계산입니다. `axis` 를 생략하면 전체 원소의 평균 하나만 나옵니다.", tags=['mean', 'axis'])
    b.S(["테스트 세트 `test_input` 을 표준점수로 바꾼다.", "`mean`, `std` 는 **훈련 세트**에서 구한 값이며 이 값을 기준으로 삼는다."], "(test_input - mean) / std",
        ["(test_input - np.mean(test_input, axis=0)) / np.std(test_input, axis=0)", "(test_input - std) / mean", "test_input - mean / std", "(test_input + mean) * std"],
        code="test_scaled = ____", chk="print(test_scaled.shape, bool(np.allclose(test_scaled * std + mean, test_input)))",
        why="테스트 세트도 훈련 세트의 평균과 표준편차로 변환해야 같은 기준이 됩니다. 괄호가 없으면 나눗셈이 먼저 계산됩니다.", tags=['표준점수', '테스트 세트'])
    b.S(["입력과 정답을 훈련 세트와 테스트 세트로 나눈다.", "두 세트의 도미와 빙어 비율이 원래 데이터와 비슷하게 유지되게 한다."],
        "train_test_split(fish_data, fish_target, stratify=fish_target, random_state=42)",
        ["train_test_split(fish_data, fish_target, random_state=42)", "train_test_split(fish_data, fish_target, stratify=True, random_state=42)",
         "train_test_split(fish_data, fish_target, shuffle=fish_target, random_state=42)", "train_test_split(fish_data, fish_target, test_size=fish_target, random_state=42)"],
        code="train_input, test_input, train_target, test_target = ____", chk="print(int(test_target.sum()), len(test_target))", pre=PRE_NP,
        why="`stratify` 에는 `True` 가 아니라 **비율을 맞출 기준이 되는 정답 배열**을 넘깁니다.", tags=['stratify'])
    b.S(["훈련된 모델 `kn` 에서 샘플 `[25, 150]` 의 가장 가까운 이웃을 찾는다.", "이웃까지의 거리와 이웃의 인덱스를 함께 돌려받는다."], "kn.kneighbors([[25, 150]])",
        ["kn.neighbors([[25, 150]])", "kn.predict([[25, 150]])", "kn.kneighbors([25, 150])", "kn.score([[25, 150]])"],
        code="distances, indexes = ____", chk="print(distances.shape, indexes.shape)",
        why="`kneighbors()` 가 (거리, 인덱스) 두 배열을 돌려줍니다. 입력은 `predict` 와 마찬가지로 2차원이어야 합니다.", tags=['kneighbors'])

    # ── 서답형 ──
    b.W("어떤 특성의 평균이 20, 표준편차가 4이다. 값 26의 표준점수를 구하시오.", "1.5", accept=['1.50', '3/2', '+1.5'], chk="print((26 - 20) / 4)", pre='',
        why="(26 − 20) ÷ 4 = 1.5 입니다. 평균보다 표준편차의 1.5배만큼 크다는 뜻입니다.", tags=['표준점수'])
    b.W("빈칸 ㉠ 에 들어갈 매개변수 이름을 쓰시오.", "axis", code="mean = np.mean(train_input, ㉠=0)\nprint(mean.shape)",
        why="`axis=0` 으로 열(특성)마다 평균을 구합니다. 특성이 2개라 shape 이 `(2,)` 입니다.", tags=['axis'])
    b.W("빈칸 ㉠ 에 들어갈 매개변수 이름을 쓰시오. (두 세트의 클래스 비율을 원래 데이터와 비슷하게 맞춘다.)", "stratify", pre=PRE_NP,
        code="a, b, c, d = train_test_split(fish_data, fish_target, ㉠=fish_target, random_state=42)\nprint(int(d.sum()), len(d))",
        why="`stratify` 에 정답 배열을 넘기면 클래스 비율을 유지하며 나눕니다.", tags=['stratify'])
    b.W("빈칸 ㉠ 에 들어갈 메서드 이름을 쓰시오. (가장 가까운 이웃까지의 거리와 이웃의 인덱스를 돌려준다.)", "kneighbors",
        code="distances, indexes = kn.㉠([[25, 150]])\nprint(indexes.shape)",
        why="`kneighbors()` 는 (거리, 인덱스)를 돌려주는 메서드입니다. 기본 이웃 5개라 shape 이 `(1, 5)` 입니다.", tags=['kneighbors'])
    b.W("훈련 세트에서 무게의 평균이 450, 표준편차가 300이다. 무게가 150인 생선의 표준점수를 구하시오.", "-1.0", accept=['-1', '−1', '−1.0', '-1.00'],
        chk="print((150 - 450) / 300)", pre='',
        why="(150 − 450) ÷ 300 = −1.0 입니다. 평균보다 표준편차 1배만큼 작다는 뜻입니다.", tags=['표준점수'])

    # ── 서술형 ──
    b.E("도미와 빙어의 [길이, 무게] 데이터로 훈련한 K-최근접 이웃 모델의 테스트 정확도는 1.0이었다. 그런데 산점도에서 도미 쪽에 가까워 보이는 길이 25, 무게 150인 생선을 이 모델은 빙어로 예측했다. 그 이유와 해결 방법을 쓰시오.",
        "길이는 10~40 정도인데 무게는 0~1000 정도로 값의 범위(스케일)가 훨씬 크다. 그래서 거리를 계산할 때 무게 차이가 대부분을 차지하고 길이는 거의 반영되지 않아, 무게가 가까운 빙어들이 이웃으로 뽑혔다. 두 특성을 표준점수 등으로 바꾸어 스케일을 맞춘 뒤 훈련하고 예측하면 된다.",
        "필수 요소(모두 있어야 정답): (1) 두 특성의 값 범위(스케일)가 다르다는 점, 구체적으로 무게의 범위가 훨씬 크다는 점. (2) 그래서 거리 계산이 무게에 좌우된다(길이가 반영되지 않는다)는 점. (3) 해결: 표준화(표준점수)/정규화/스케일 맞추기 중 하나. 이유 없이 해결 방법만 쓰거나 해결 방법이 없으면 오답.",
        ['스케일', '표준점수'], chk="print(kn.predict([[25, 150]]), int(train_target[kn.kneighbors([[25, 150]])[1]].sum()))")
    b.E("훈련 세트를 표준점수로 바꾼 뒤, 테스트 세트와 새로운 샘플을 변환할 때에도 **훈련 세트의 평균과 표준편차**를 사용한다. 테스트 세트 자체의 평균과 표준편차를 쓰면 안 되는 이유를 설명하시오.",
        "모델은 훈련 세트의 평균과 표준편차를 기준으로 바뀐 값의 공간에서 학습했다. 테스트 세트나 새 샘플을 다른 기준으로 변환하면 같은 원래 값이 다른 위치로 옮겨져 훈련 데이터와 올바르게 비교(거리 계산)할 수 없다. 따라서 같은 기준인 훈련 세트의 평균과 표준편차를 써야 한다.",
        "필수 요소: 훈련 세트와 '같은 기준(같은 척도)'으로 변환해야 비교가 가능하다는 취지. 기준이 다르면 같은 값이 다른 위치가 된다/거리 계산이 어긋난다는 설명이면 정답. 단순히 '그렇게 정해져 있어서', '훈련 세트가 더 많아서'는 오답.",
        ['표준점수', '테스트 세트'])
    b.E("훈련 세트에서 길이의 평균은 27, 표준편차는 10이고, 무게의 평균은 450, 표준편차는 300이라고 하자. 길이 25, 무게 150인 생선의 길이와 무게를 각각 표준점수로 바꾸는 식과 값을 쓰시오.",
        "표준점수 = (값 − 평균) ÷ 표준편차\n길이: (25 − 27) ÷ 10 = −0.2\n무게: (150 − 450) ÷ 300 = −1.0",
        "필수 요소(모두 있어야 정답): (1) 길이의 표준점수 −0.2. (2) 무게의 표준점수 −1.0(−1 도 정답). 식이 (값 − 평균) ÷ 표준편차 꼴로 드러나야 하며, 부호가 틀리면 오답. 식 없이 두 값만 정확히 써도 정답으로 인정한다.",
        ['표준점수', '계산'], chk="print((25 - 27) / 10, (150 - 450) / 300)", pre='')
    return b
