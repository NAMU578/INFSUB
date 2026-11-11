"""기말.8 로지스틱 회귀"""
from lib import Bank

SRC = '기말.8.로지스틱회귀'
IMP = '''
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import KNeighborsClassifier
from sklearn.linear_model import LogisticRegression
from scipy.special import expit, softmax
'''
PRE_DATA = IMP + '''
fish = pd.read_csv('fish.csv')
fish_input = fish[['Weight', 'Length', 'Diagonal', 'Height', 'Width']].to_numpy()
fish_target = fish['Species'].to_numpy()
train_input, test_input, train_target, test_target = train_test_split(fish_input, fish_target, random_state=42)
ss = StandardScaler()
ss.fit(train_input)
train_scaled = ss.transform(train_input)
test_scaled = ss.transform(test_input)
'''
PRE_KN = PRE_DATA + '''
kn = KNeighborsClassifier(n_neighbors=3)
kn.fit(train_scaled, train_target)
'''
PRE_BS = PRE_DATA + '''
bream_smelt_indexes = (train_target == 'Bream') | (train_target == 'Smelt')
train_bream_smelt = train_scaled[bream_smelt_indexes]
target_bream_smelt = train_target[bream_smelt_indexes]
'''
PRE_BIN = PRE_BS + '''
lr = LogisticRegression()
lr.fit(train_bream_smelt, target_bream_smelt)
'''
PRE_MULTI = PRE_DATA + '''
lr = LogisticRegression(C=20, max_iter=1000)
lr.fit(train_scaled, train_target)
'''
DT = ('(`train_scaled`, `test_scaled` 는 물고기 7종의 특성 5개(Weight, Length, Diagonal, Height, Width)를 표준화한 훈련 119개, 테스트 40개이고 '
      '`train_target`, `test_target` 은 종 이름 문자열 배열이다)')
CLS = "클래스는 알파벳순으로 ['Bream' 'Parkki' 'Perch' 'Pike' 'Roach' 'Smelt' 'Whitefish'] 이다."
BS = '(`train_bream_smelt`, `target_bream_smelt` 는 훈련 세트에서 Bream 과 Smelt 만 골라낸 33개 샘플과 정답이다)'
BIN = f'`lr` 은 Bream 과 Smelt 두 종만으로 훈련한 `LogisticRegression()` 모델이고 `lr.classes_` 는 `[\'Bream\' \'Smelt\']` 이다. {BS}'
MUL = f'`lr` 은 7종 전체로 훈련한 `LogisticRegression(C=20, max_iter=1000)` 모델이다. {CLS}'
KNN = f'`kn` 은 `KNeighborsClassifier(n_neighbors=3)` 을 훈련한 모델이다. {CLS}'
BOOL = "bream_smelt_indexes = (train_target == 'Bream') | (train_target == 'Smelt')\ntrain_bream_smelt = train_scaled[bream_smelt_indexes]\ntarget_bream_smelt = train_target[bream_smelt_indexes]"


def build():
    b = Bank('08', SRC, PRE_DATA)

    # ── 개념 분류 ──
    b.C(stem='로지스틱 회귀에 대한 설명으로 옳은 것만 <보기>에서 모두 고른 것은?',
        items=[("이름은 회귀이지만 분류 모델이다.", True),
               ("시그모이드 함수의 출력은 0 과 1 사이의 값이다.", True),
               ("소프트맥스 함수의 출력을 모두 더하면 클래스의 수와 같다.", False)],
        why="로지스틱 회귀는 선형식으로 z 를 계산한 뒤 함수를 거쳐 확률로 바꾸는 분류 모델입니다. 소프트맥스의 출력은 각각 0~1 사이이고 모두 더하면 **1** 입니다.",
        tags=['로지스틱 회귀', '시그모이드', '소프트맥스'], ref='셀 [16], [24] 로지스틱 회귀, 다중분류')
    b.C(code="kn = KNeighborsClassifier(n_neighbors=3)\nkn.fit(train_scaled, train_target)\nproba = kn.predict_proba(test_scaled[:5])",
        stem=f'다음 코드에 대한 설명으로 옳은 것만 <보기>에서 모두 고른 것은? {DT}',
        items=[("`kn.classes_` 는 알파벳 순서로 정렬되어 있다.", "list(kn.classes_) == sorted(kn.classes_)"),
               ("`proba` 에는 0.5 인 값이 있다.", "bool(np.isclose(proba, 0.5).any())"),
               ("`proba` 의 각 행을 더하면 1 이다.", "bool(np.allclose(proba.sum(axis=1), 1))")],
        why="`predict_proba` 의 열 순서는 알파벳순인 `classes_` 의 순서입니다. 이웃이 3개라 확률은 0, 1/3, 2/3, 1 만 나올 수 있어 0.5 는 나오지 않습니다. 한 행은 한 샘플의 클래스별 확률이라 합이 1 입니다.",
        tags=['predict_proba', 'classes_', 'KNN'])
    b.C(code=BOOL, stem=f'다음 코드에 대한 설명으로 옳은 것만 <보기>에서 모두 고른 것은? {DT}',
        items=[("`bream_smelt_indexes` 는 True/False 로 이루어진 배열이다.", "bream_smelt_indexes.dtype == bool"),
               ("`target_bream_smelt` 에는 'Perch' 도 들어 있다.", "'Perch' in set(target_bream_smelt)"),
               ("`train_bream_smelt` 의 샘플 수는 `bream_smelt_indexes` 의 True 개수와 같다.", "len(train_bream_smelt) == int(bream_smelt_indexes.sum())")],
        why="비교식은 원소마다 True/False 를 만들고, 그 배열을 인덱스로 넣으면 True 인 행만 뽑힙니다(불리언 인덱싱). Bream 또는 Smelt 인 행만 남으므로 다른 종은 없습니다.",
        tags=['불리언 인덱싱'])
    b.C(code="lr = LogisticRegression()\nlr.fit(train_bream_smelt, target_bream_smelt)", pre=PRE_BS, stem=f'다음 코드에 대한 설명으로 옳은 것만 <보기>에서 모두 고른 것은? {BS}',
        items=[("`lr.classes_` 는 `['Bream' 'Smelt']` 이다.", "list(lr.classes_) == ['Bream', 'Smelt']"),
               ("`lr.coef_.shape` 은 `(5, 1)` 이다.", "lr.coef_.shape == (5, 1)"),
               ("`lr.predict_proba()` 의 두 번째 열은 Smelt 일 확률이다.", "bool(np.allclose(lr.predict_proba(train_bream_smelt[:5])[:, 1], expit(lr.decision_function(train_bream_smelt[:5]))))")],
        why="이진 분류에서는 `classes_` 의 두 번째 클래스(Smelt)가 양성 클래스이고, `predict_proba` 의 열은 [Bream 확률, Smelt 확률] 순서입니다. 식(z)이 하나이고 특성이 5개라 `coef_` 의 shape 은 `(1, 5)` 입니다.",
        tags=['이진 분류', 'classes_', 'coef_'])
    b.C(code="decisions = lr.decision_function(train_bream_smelt[:5])\npred = lr.predict(train_bream_smelt[:5])", pre=PRE_BIN, stem=f'다음 코드에 대한 설명으로 옳은 것만 <보기>에서 모두 고른 것은? {BIN}',
        items=[("z 값(`decisions`)이 양수인 샘플은 Smelt 로 예측된다.", "all((d > 0) == (p == 'Smelt') for d, p in zip(decisions, pred))"),
               ("`expit(decisions)` 는 각 샘플이 Bream 일 확률이다.", False),
               ("`expit(0)` 은 0.5 이다.", "expit(0) == 0.5")],
        why="`decision_function` 은 z 값을 돌려주고, 이를 시그모이드(`expit`)에 넣으면 **양성 클래스(Smelt)** 일 확률이 됩니다. z = 0 이면 0.5, z 가 양수면 0.5 보다 커서 Smelt 로 예측합니다.",
        tags=['decision_function', '시그모이드'])
    b.C(code="lr = LogisticRegression(C=20, max_iter=1000)\nlr.fit(train_scaled, train_target)", stem=f'다음 코드에 대한 설명으로 옳은 것만 <보기>에서 모두 고른 것은? {DT}',
        items=[("`C` 를 20 보다 작게 하면 규제가 약해진다.", False),
               ("`lr.coef_.shape` 은 `(7, 5)` 이다.", "lr.coef_.shape == (7, 5)"),
               ("`lr.decision_function(test_scaled[:5]).shape` 은 `(5, 7)` 이다.", "lr.decision_function(test_scaled[:5]).shape == (5, 7)")],
        why="다중 분류에서는 클래스마다 z 를 하나씩 계산하므로 `coef_` 가 7행(클래스) 5열(특성)이고, 샘플 5개의 z 는 5행 7열입니다. `C` 는 **작을수록 규제가 강해집니다**.",
        tags=['다중 분류', 'C', 'coef_'])
    b.C(code="decision = lr.decision_function(test_scaled[:5])\nproba = softmax(decision, axis=1)", pre=PRE_MULTI, stem=f'다음 코드에 대한 설명으로 옳은 것만 <보기>에서 모두 고른 것은? {MUL}',
        items=[("`proba` 는 `lr.predict_proba(test_scaled[:5])` 와 같은 값이다.", "bool(np.allclose(proba, lr.predict_proba(test_scaled[:5])))"),
               ("`proba` 의 각 행을 더하면 1 이다.", "bool(np.allclose(proba.sum(axis=1), 1))"),
               ("`axis=1` 을 `axis=0` 으로 바꿔도 결과는 같다.", "bool(np.allclose(softmax(decision, axis=0), proba))")],
        why="샘플마다(행마다) 7개의 z 를 소프트맥스에 넣어야 하므로 `axis=1` 입니다. 이렇게 계산한 값이 `predict_proba` 의 결과와 같고, 행의 합은 1 입니다.",
        tags=['소프트맥스', 'axis'])
    b.C(stem='`LogisticRegression` 의 매개변수에 대한 설명으로 옳은 것만 <보기>에서 모두 고른 것은?',
        items=[("기본적으로 릿지 회귀처럼 계수의 제곱을 규제한다(L2 규제).", True),
               ("`max_iter` 는 참고할 이웃의 수이다.", False),
               ("`C` 의 값이 작을수록 규제가 강해진다.", True)],
        why="`C` 는 `alpha` 와 반대로 작을수록 규제가 커지고 기본값은 1 입니다. `max_iter` 는 반복 횟수이며, 부족하면 경고가 떠서 노트북은 1000 으로 늘렸습니다.",
        tags=['C', 'max_iter', '규제'], ref='셀 [24] 다중분류 설명')

    # ── 빈칸 ──
    b.B("fish = pd.read_csv('fish.csv')\nfish_input = fish[['Weight', 'Length', 'Diagonal', 'Height', 'Width']].㉠()\nfish_target = fish['㉡'].to_numpy()\nprint(fish_input.shape, fish_target.shape, fish_target[0])",
        ('to_numpy', 'Species'), [('to_numpy', 'Weight'), ('numpy', 'Species'), ('to_array', 'Species'), ('values', 'Species')], pre=IMP,
        why="데이터프레임을 넘파이 배열로 바꾸는 메서드는 `to_numpy()` 이고, 정답은 종 이름이 든 `Species` 열입니다.", tags=['to_numpy', '타깃'])
    b.B("kn = KNeighborsClassifier(n_neighbors=3)\nkn.fit(train_scaled, train_target)\nproba = kn.㉠(test_scaled[3:4])\nprint(np.round(proba, 4), kn.㉡[2])",
        ('predict_proba', 'classes_'), [('predict', 'classes_'), ('predict_proba', 'classes'), ('proba', 'classes_'), ('predict_proba', 'labels_')], stem=f'㉠, ㉡에 들어갈 것으로 알맞은 것은? {DT}',
        why="클래스별 확률은 `predict_proba()`, 클래스 목록은 `classes_` 입니다. 세 번째 클래스(인덱스 2)인 Perch 의 확률이 0.6667 입니다.", tags=['predict_proba', 'classes_'])
    b.B("bream_smelt_indexes = (train_target == 'Bream') ㉠ (train_target == 'Smelt')\ntrain_bream_smelt = train_scaled[㉡]\nprint(train_bream_smelt.shape)",
        ('|', 'bream_smelt_indexes'), [('or', 'bream_smelt_indexes'), ('&', 'bream_smelt_indexes'), ('|', 'train_target'), ('and', 'bream_smelt_indexes')], stem=f'㉠, ㉡에 들어갈 것으로 알맞은 것은? {DT}',
        why="배열끼리의 '또는'은 `or` 가 아니라 `|` 입니다. True/False 배열을 인덱스로 넣어 해당 행만 뽑습니다. `&` 를 쓰면 두 종에 동시에 속하는 샘플은 없으므로 0개가 됩니다.", tags=['불리언 인덱싱'])
    b.B("decisions = lr.㉠(train_bream_smelt[:5])\nprint(np.round(㉡(decisions), 3))", ('decision_function', 'expit'),
        [('predict_proba', 'expit'), ('decision_function', 'softmax'), ('predict', 'expit'), ('decision_function', 'np.exp')], pre=PRE_BIN, stem=f'㉠, ㉡에 들어갈 것으로 알맞은 것은? {BIN}',
        why="`decision_function` 이 z 값을 돌려주고, 시그모이드 함수 `expit` 가 이를 Smelt 일 확률로 바꿉니다. 두 번째 샘플만 0.973 으로 Smelt 입니다.", tags=['decision_function', 'expit'])
    b.B("lr = LogisticRegression(㉠=20, ㉡=1000)\nlr.fit(train_scaled, train_target)\nprint(round(lr.score(test_scaled, test_target), 3))", ('C', 'max_iter'),
        [('alpha', 'max_iter'), ('C', 'epochs'), ('n_neighbors', 'max_iter'), ('C', 'iter')], stem=f'규제를 약하게 풀고 반복 횟수를 1000 으로 늘리려고 한다. ㉠, ㉡에 들어갈 것으로 알맞은 것은? {DT}',
        why="로지스틱 회귀의 규제는 `C` 로 조절하고(클수록 약함), 반복 횟수는 `max_iter` 로 정합니다.", tags=['C', 'max_iter'])
    b.B("decision = lr.decision_function(test_scaled[:5])\nproba = ㉠(decision, axis=㉡)\nprint(np.round(proba.sum(axis=1), 2))", ('softmax', '1'),
        [('softmax', '0'), ('expit', '1'), ('sigmoid', '1'), ('np.exp', '1')], pre=PRE_MULTI, stem=f'㉠, ㉡에 들어갈 것으로 알맞은 것은? {MUL}',
        why="다중 분류의 z 값들을 확률로 바꾸는 함수는 `softmax` 이고, 샘플(행)마다 계산해야 하므로 `axis=1` 입니다. 그래야 행의 합이 모두 1 이 됩니다.", tags=['softmax', 'axis'])

    # ── 경계값 ──
    b.D("proba = kn.predict_proba(test_scaled[:5])\nprint(sorted(set(np.round(proba, 4).ravel().tolist())))", ['[0.0, 0.5, 1.0]', '[0.0, 0.25, 0.5, 0.75, 1.0]', '[0.0, 1.0]', '[0.0, 0.2, 0.4, 0.6, 0.8, 1.0]'], pre=PRE_KN,
        stem=f'확률에 나타난 값을 중복 없이 크기순으로 출력한다. 다음 코드를 실행했을 때 출력되는 것은? {KNN}',
        why="이웃이 3개이므로 확률은 이웃 중 그 클래스의 비율인 0/3, 1/3, 2/3, 3/3 만 가능합니다.", tags=['KNN', '확률'])
    b.D("print(fish_input.shape, train_input.shape, test_input.shape)", ['(159, 5) (120, 5) (39, 5)', '(159, 6) (119, 6) (40, 6)', '(159, 5) (111, 5) (48, 5)', '(5, 159) (5, 119) (5, 40)'],
        stem='fish.csv 는 159행이고 입력으로 특성 5개를 골랐다. `train_test_split` 의 기본 비율로 나눈 뒤 다음 코드를 실행했을 때 출력되는 것은?',
        why="159 × 0.25 = 39.75 를 올림해 테스트 세트가 40개, 훈련 세트가 119개입니다. 특성은 5개입니다.", tags=['train_test_split', 'shape'])
    b.D("print(expit(0), bool(expit(100) > 0.99), bool(expit(-100) < 0.01))", ['0 True True', '0.5 False True', '1.0 True False', '0.5 True False'], pre=IMP,
        stem='`expit` 는 시그모이드 함수이다. 다음 코드를 실행했을 때 출력되는 것은?',
        why="시그모이드는 z = 0 에서 0.5 이고, z 가 아주 크면 1 에, 아주 작으면(큰 음수) 0 에 가까워집니다.", tags=['시그모이드'])
    b.D("z = np.array([-2.0, 0.5, 3.0])\np = 1 / (1 + np.exp(-z))\nprint((p > 0.5).tolist())", ['[True, True, True]', '[False, False, True]', '[True, False, False]', '[False, True, False]'], pre=IMP,
        why="시그모이드 값이 0.5 보다 큰 것은 z 가 양수일 때입니다. −2.0 은 0.5 보다 작고, 0.5 와 3.0 은 0.5 보다 큽니다.", tags=['시그모이드', '0.5 기준'])
    b.D("kn5 = KNeighborsClassifier(n_neighbors=5)\nkn5.fit(train_scaled, train_target)\nproba = kn5.predict_proba(test_scaled)\nprint(len(set(np.round(proba, 4).ravel().tolist())) <= 6, proba.shape)",
        ['True (40, 5)', 'False (40, 7)', 'True (5, 7)', 'True (119, 7)'], stem=f'이웃 수를 5로 바꿨다. 다음 코드를 실행했을 때 출력되는 것은? {DT}',
        why="이웃이 5개면 확률은 0, 0.2, 0.4, 0.6, 0.8, 1 의 여섯 가지뿐입니다. 테스트 샘플 40개, 클래스 7개라 shape 은 `(40, 7)` 입니다.", tags=['KNN', '확률'])

    # ── 상태 예측 ──
    b.R("print(kn.classes_)", ["['Bream' 'Roach' 'Whitefish' 'Parkki' 'Perch' 'Pike' 'Smelt']", "['Whitefish' 'Smelt' 'Roach' 'Pike' 'Perch' 'Parkki' 'Bream']", "[0 1 2 3 4 5 6]", "['Bream' 'Smelt']"], pre=PRE_KN,
        stem='fish.csv 에는 종이 Bream, Roach, Whitefish, Parkki, Perch, Pike, Smelt 순서로 처음 나온다. 7종 전체로 `kn` 을 훈련한 뒤 다음 코드를 실행했을 때 출력되는 것은?',
        why="`classes_` 는 데이터에 나온 순서가 아니라 **알파벳 순서**로 정렬됩니다. `predict_proba` 의 열 순서가 이 순서입니다.", tags=['classes_'])
    b.R("print(kn.predict(test_scaled[3:4]))", ["['Roach']", "['Pike']", "['Parkki']", "[0.6667]"], pre=PRE_KN,
        stem=f'테스트 세트의 네 번째 샘플에 대한 `kn.predict_proba()` 결과가 `[0, 0, 0.6667, 0, 0.3333, 0, 0]` 이다. 다음 코드를 실행했을 때 출력되는 것은? {KNN}',
        why="확률의 열 순서는 `classes_` 순서입니다. 0.6667 은 세 번째 클래스 Perch, 0.3333 은 다섯 번째 클래스 Roach 의 확률이므로 확률이 가장 큰 Perch 로 예측합니다.", tags=['predict_proba', 'classes_'])
    b.R("print(lr.predict(train_bream_smelt[:5]))", ["['Smelt' 'Bream' 'Smelt' 'Smelt' 'Smelt']", "[0 1 0 0 0]", "['Bream' 'Bream' 'Bream' 'Bream' 'Bream']", "[0.998 0.027 0.995 0.986 0.998]"], pre=PRE_BIN,
        stem=f'처음 5개 샘플의 `lr.predict_proba()` 결과에서 첫 번째 열(Bream 확률)이 차례로 0.998, 0.027, 0.995, 0.986, 0.998 이다. 다음 코드를 실행했을 때 출력되는 것은? {BIN}',
        why="Bream 확률이 0.5 보다 큰 샘플은 Bream, 작은 샘플(두 번째)은 Smelt 입니다. `predict` 는 정답과 같은 형태인 종 이름을 돌려줍니다.", tags=['predict', '이진 분류'])
    b.R("print(np.round(lr.predict_proba(train_bream_smelt[:2]), 3).tolist())", ['[[0.002, 0.998], [0.973, 0.027]]', '[[0.998], [0.027]]', '[[0.998, 0.998], [0.027, 0.027]]', '[[-6.03, 3.57]]'], pre=PRE_BIN,
        stem=f'처음 두 샘플의 z 값은 −6.03, 3.57 이고 시그모이드 값은 0.002, 0.973 이다. 다음 코드를 실행했을 때 출력되는 것은? {BIN}',
        why="시그모이드 값은 양성 클래스(Smelt)일 확률이고 **두 번째 열**에 들어갑니다. 첫 번째 열(Bream 확률)은 1 에서 뺀 값입니다.", tags=['predict_proba', '시그모이드'])
    b.R("print(softmax(np.array([[1.0, 1.0, 1.0, 1.0]]), axis=1).tolist())", ['[[1.0, 1.0, 1.0, 1.0]]', '[[0.5, 0.5, 0.5, 0.5]]', '[[4.0]]', '[[0.0, 0.0, 0.0, 1.0]]'], pre=IMP,
        why="z 값이 모두 같으면 소프트맥스는 확률을 똑같이 나눕니다. 4개이므로 각각 0.25 이고 합은 1 입니다.", tags=['소프트맥스'])
    b.R("print(lr.predict(test_scaled[:5]))", ["['Perch' 'Smelt' 'Pike' 'Perch' 'Perch']", "['Bream' 'Smelt' 'Bream' 'Bream' 'Bream']", "[2 5 3 4 2]", "['Perch' 'Smelt' 'Pike' 'Whitefish' 'Perch']"], pre=PRE_MULTI,
        stem=f'테스트 세트 처음 5개 샘플에서 확률이 가장 큰 열의 인덱스가 차례로 2, 5, 3, 4, 2 이다. 다음 코드를 실행했을 때 출력되는 것은? {MUL}',
        why="열 인덱스를 `classes_` 에 대응시키면 2 는 Perch, 5 는 Smelt, 3 은 Pike, 4 는 Roach 입니다.", tags=['predict', 'classes_'])
    b.R("proba = lr.predict_proba(test_scaled[:1])\nprint(proba.shape, lr.classes_[np.argmax(proba)])", ['(7,) Perch', '(1, 7) 2', '(7, 1) Perch', '(1, 5) Perch'], pre=PRE_MULTI,
        stem=f'첫 번째 테스트 샘플은 세 번째 열의 확률이 가장 크다. 다음 코드를 실행했을 때 출력되는 것은? {MUL}',
        why="샘플 1개, 클래스 7개라 `(1, 7)` 입니다. `np.argmax` 는 가장 큰 값의 인덱스 2 를 돌려주고 `classes_[2]` 는 Perch 입니다.", tags=['argmax', 'classes_'])

    # ── 대조 ──
    b.X("# 방법1: K-최근접 이웃\nkn = KNeighborsClassifier(n_neighbors=3).fit(train_scaled, train_target)\nprint(kn.predict(test_scaled[3:4]))\n\n# 방법2: 로지스틱 회귀\nlr = LogisticRegression(C=20, max_iter=1000).fit(train_scaled, train_target)\nprint(lr.predict(test_scaled[3:4]))",
        [("['Roach']", "['Perch']"), ("['Perch']", "['Perch']"), ("['Roach']", "['Roach']"), ("['Perch']", "['Pike']")],
        stem=f'테스트 세트의 네 번째 샘플에 대해 KNN 은 Perch 0.6667, Roach 0.3333 을, 로지스틱 회귀는 Roach 약 0.57, Perch 약 0.30 을 가장 큰 두 확률로 냈다. ㉠, ㉡에 출력되는 값으로 알맞은 것은? {DT}',
        why="각 모델은 자기가 계산한 확률이 가장 큰 클래스로 예측합니다. KNN 은 Perch, 로지스틱 회귀는 Roach 로, 같은 샘플도 모델에 따라 예측이 달라질 수 있습니다.", tags=['KNN', '로지스틱 회귀'])
    b.X("# 방법1\nprint(test_scaled[3:4].shape)\n\n# 방법2\nprint(test_scaled[3].shape)", [('(5,)', '(1, 5)'), ('(1, 5)', '(1, 5)'), ('(5,)', '(5,)'), ('(1, 5)', '(5, 1)')], stem=f'㉠, ㉡에 출력되는 값으로 알맞은 것은? {DT}',
        why="슬라이싱 `[3:4]` 는 행 하나짜리 2차원 배열 `(1, 5)` 을, 인덱싱 `[3]` 은 1차원 배열 `(5,)` 을 돌려줍니다. `predict` 나 `kneighbors` 에는 2차원을 넣어야 해서 `[3:4]` 를 씁니다.", tags=['슬라이싱', '2차원 입력'])
    b.X("# 방법1: Bream, Smelt 두 종으로 훈련\nlr2 = LogisticRegression().fit(train_bream_smelt, target_bream_smelt)\nprint(lr2.coef_.shape)\n\n# 방법2: 7종 전체로 훈련\nlr7 = LogisticRegression(C=20, max_iter=1000).fit(train_scaled, train_target)\nprint(lr7.coef_.shape)",
        [('(2, 5)', '(7, 5)'), ('(1, 5)', '(5, 7)'), ('(5,)', '(7, 5)'), ('(1, 5)', '(1, 5)')], pre=PRE_BS, stem=f'특성은 5개이다. ㉠, ㉡에 출력되는 값으로 알맞은 것은? {BS}',
        why="이진 분류는 z 를 하나만 계산해서 계수가 1행 5열, 다중 분류는 클래스마다 z 를 계산해서 7행 5열입니다.", tags=['coef_', '이진 분류', '다중 분류'])
    b.X("# 방법1\nprint(expit(0.0))\n\n# 방법2\nprint(softmax([0.0, 0.0]).tolist())", [('0.0', '[0.0, 0.0]'), ('0.5', '[1.0, 1.0]'), ('1.0', '[0.5, 0.5]'), ('0.5', '[0.5]')], pre=IMP,
        why="시그모이드는 값 하나를 0~1 사이 값 하나로 바꾸며 z = 0 이면 0.5 입니다. 소프트맥스는 여러 값을 합이 1 인 확률들로 바꾸며, 두 값이 같으면 0.5 씩입니다.", tags=['시그모이드', '소프트맥스'])
    b.X("# 방법1\nprint(int(((train_target == 'Bream') | (train_target == 'Smelt')).sum()))\n\n# 방법2\nprint(int(((train_target == 'Bream') & (train_target == 'Smelt')).sum()))",
        [('0', '33'), ('33', '33'), ('119', '0'), ('33', '119')], stem=f'훈련 세트 119개 중 Bream 과 Smelt 는 모두 33개이다. ㉠, ㉡에 출력되는 값으로 알맞은 것은? {DT}',
        why="`|` 는 '또는'이라 Bream 이거나 Smelt 인 33개가 True 입니다. `&` 는 '그리고'인데 한 샘플이 두 종에 동시에 속할 수 없으므로 0개입니다.", tags=['불리언 인덱싱'])

    # ── 조건 매핑 ──
    b.S(["`train_target` 에서 값이 'Bream' **이거나** 'Smelt' 인 위치만 True 인 배열을 만든다."], "(train_target == 'Bream') | (train_target == 'Smelt')",
        ["(train_target == 'Bream') or (train_target == 'Smelt')", "(train_target == 'Bream') & (train_target == 'Smelt')", "train_target == 'Bream' | train_target == 'Smelt'", "train_target == ['Bream', 'Smelt']"],
        code="bream_smelt_indexes = ____", chk="print(int(bream_smelt_indexes.sum()))",
        why="배열의 '또는'은 `|` 이고, 연산 순서 때문에 각 비교식을 괄호로 감싸야 합니다.", tags=['불리언 인덱싱'])
    b.S(["테스트 세트 처음 5개 샘플에 대해 **클래스별 확률**을 구한다.", "결과는 5행 7열이고 각 행의 합은 1 이다."], "lr.predict_proba(test_scaled[:5])",
        ["lr.predict(test_scaled[:5])", "lr.decision_function(test_scaled[:5])", "lr.score(test_scaled[:5])", "lr.proba(test_scaled[:5])"],
        code="proba = ____", chk="print(proba.shape, bool(np.allclose(proba.sum(axis=1), 1)))", pre=PRE_MULTI,
        why="확률은 `predict_proba()` 입니다. `decision_function()` 도 5행 7열이지만 z 값이라 행의 합이 1 이 아닙니다.", tags=['predict_proba'])
    b.S(["로지스틱 회귀 모델 객체를 만든다.", "규제를 기본값(1)보다 **약하게** 한다.", "반복 횟수를 1000 으로 늘린다."], "LogisticRegression(C=20, max_iter=1000)",
        ["LogisticRegression(C=0.01, max_iter=1000)", "LogisticRegression(alpha=20, max_iter=1000)", "LogisticRegression(C=20, epochs=1000)", "LogisticRegression(max_iter=1000)"],
        code="lr = ____", chk="print(lr.C > 1, lr.max_iter)", pre=IMP,
        why="`C` 는 클수록 규제가 약해집니다. 기본값 1 보다 큰 20 을 줍니다. `alpha` 는 릿지와 라쏘의 매개변수입니다.", tags=['C', 'max_iter'])
    b.S(["넘파이로 시그모이드 함수 φ(z) = 1 ÷ (1 + e^(−z)) 를 계산한다."], "1 / (1 + np.exp(-z))", ["1 / (1 + np.exp(z))", "np.exp(-z) / (1 + z)", "1 / (1 - np.exp(-z))", "1 + np.exp(-z)"],
        code="phi = ____", chk="print(np.round(phi, 3))", pre="import numpy as np\nz = np.array([0.0, 2.0])",
        why="`np.exp(-z)` 가 e 의 −z 제곱입니다. z = 0 이면 1 ÷ 2 = 0.5 가 나와야 합니다.", tags=['시그모이드'])
    b.S(["테스트 세트의 네 번째 샘플 **하나**를 고른다.", "모델에 바로 넣을 수 있게 2차원 배열로 유지한다."], "test_scaled[3:4]", ["test_scaled[3]", "test_scaled[:3]", "test_scaled[4]", "test_scaled[3:5]"],
        code="x = ____", chk="print(x.shape, bool((x[0] == test_scaled[3]).all()))",
        why="네 번째 샘플의 인덱스는 3 이고, 슬라이싱 `[3:4]` 로 뽑아야 `(1, 5)` 의 2차원이 유지됩니다.", tags=['슬라이싱'])

    # ── 서답형 ──
    b.W("시그모이드 함수에 z = 0 을 넣었을 때의 값을 쓰시오.", "0.5", accept=['0.50', '1/2', '.5'], chk="print(expit(0))", pre=IMP, why="1 ÷ (1 + e⁰) = 1 ÷ 2 = 0.5 입니다.", tags=['시그모이드'])
    b.W("`KNeighborsClassifier(n_neighbors=3)` 모델에서 어떤 샘플의 이웃 3개가 Perch 2개, Roach 1개였다. 이 샘플이 Perch 일 확률을 소수 넷째 자리까지 쓰시오.", "0.6667",
        accept=['2/3', '0.667', '0.67', '0.6666', '0.666'], chk="print(round(2/3, 4))", pre='', why="이웃 3개 중 Perch 가 2개이므로 2/3 ≈ 0.6667 입니다.", tags=['KNN', '확률'])
    b.W("빈칸 ㉠ 에 들어갈 메서드 이름을 쓰시오. (클래스별 확률을 돌려준다.)", "predict_proba", pre=PRE_MULTI, code="proba = lr.㉠(test_scaled[:5])\nprint(proba.shape)",
        why="`predict_proba()` 가 샘플마다 클래스별 확률을 돌려줍니다. 샘플 5개, 클래스 7개라 `(5, 7)` 입니다.", tags=['predict_proba'])
    b.W("특성이 5개인 데이터로 7종을 분류하는 로지스틱 회귀 모델을 훈련했다. `lr.coef_.shape` 을 쓰시오.", "(7, 5)", accept=['7, 5', '(7,5)', '7,5', '7x5', '7×5', '7 5'],
        chk="print(lr.coef_.shape)", pre=PRE_MULTI, why="클래스마다 z 식이 하나씩 있어 7행, 식마다 특성 5개의 계수가 있어 5열입니다.", tags=['coef_', '다중 분류'])
    b.W("소프트맥스 함수가 출력한 클래스별 확률을 모두 더하면 얼마인지 쓰시오.", "1", accept=['1.0', '1.00', '100%'], chk="print(int(round(softmax([2.0, 1.0, 0.0]).sum())))", pre=IMP,
        why="소프트맥스는 각 값을 전체의 합으로 나누므로 출력의 합이 항상 1 입니다.", tags=['소프트맥스'])
    b.W("`LogisticRegression` 에서 규제의 강도를 조절하는 매개변수의 이름을 쓰시오. (작을수록 규제가 강하다.)", "C", accept=['c'], why="`C` 는 릿지·라쏘의 `alpha` 와 반대로 작을수록 규제가 강해지며 기본값은 1 입니다.", tags=['C'])
    b.W("빈칸 ㉠ 에 들어갈 함수 이름을 쓰시오. (사이파이의 시그모이드 함수)", "expit", pre='', code="from scipy.special import ㉠\nprint(㉠(0))", why="`scipy.special.expit` 가 시그모이드 함수입니다. z = 0 이면 0.5 입니다.", tags=['expit'])
    b.W("`KNeighborsClassifier(n_neighbors=5)` 모델의 `predict_proba()` 가 낼 수 있는 서로 다른 확률 값은 모두 몇 가지인지 쓰시오.", "6", accept=['6가지', '6개', '여섯', '여섯 가지'],
        chk="print(len({k / 5 for k in range(6)}))", pre='', why="이웃 5개 중 해당 클래스가 0~5개일 수 있으므로 0, 0.2, 0.4, 0.6, 0.8, 1 의 6가지입니다.", tags=['KNN', '확률'])

    # ── 서술형 ──
    b.E("이웃 수를 3으로 한 K-최근접 이웃 분류기의 `predict_proba()` 결과에는 0, 0.3333, 0.6667, 1 만 나타났다. 그 이유를 설명하고, 이것이 왜 한계인지 쓰시오.",
        "K-최근접 이웃의 확률은 이웃 중 그 클래스가 차지하는 비율이다. 이웃이 3개뿐이므로 가능한 값이 0/3, 1/3, 2/3, 3/3 네 가지밖에 없다. 확률이 띄엄띄엄한 몇 개의 값으로만 나와서 세밀한 확률을 알 수 없다는 것이 한계이다.",
        "필수 요소(모두 있어야 정답): (1) 확률이 이웃 중 해당 클래스의 비율(개수 ÷ 3)로 계산된다는 점. (2) 그래서 가능한 값이 네 가지뿐/세밀한(연속적인) 확률을 얻지 못한다는 한계.",
        ['KNN', '확률'], chk="print(sorted(set(np.round(kn.predict_proba(test_scaled[:5]), 4).ravel().tolist())))", pre=PRE_KN)
    b.E("시그모이드 함수와 소프트맥스 함수의 차이를 (1) 사용하는 분류의 종류, (2) 입력과 출력의 개수, (3) 출력값의 성질 측면에서 설명하시오.",
        "시그모이드 함수는 이진 분류에 쓰며, z 값 하나를 받아 0~1 사이의 값 하나(양성 클래스일 확률)를 낸다. 소프트맥스 함수는 다중 분류에 쓰며, 클래스 수만큼의 z 값을 받아 같은 개수의 0~1 사이 값을 내고 그 합은 1 이다.",
        "필수 요소(모두 있어야 정답): (1) 시그모이드는 이진 분류, 소프트맥스는 다중 분류. (2) 시그모이드는 값 하나 → 하나, 소프트맥스는 여러 개 → 여러 개. (3) 소프트맥스 출력의 합이 1 (또는 시그모이드 출력이 0~1 사이의 확률). 두 함수의 설명이 서로 바뀌면 오답.",
        ['시그모이드', '소프트맥스'])
    b.E("Bream 과 Smelt 를 구분하는 로지스틱 회귀 모델에서 `lr.classes_` 는 `['Bream' 'Smelt']` 이다. 어떤 샘플의 `decision_function()` 값(z)이 −6.03 이었고 `predict_proba()` 결과는 `[0.9976, 0.0024]` 였다. 이 샘플을 어느 종으로 예측하는지와, z 값과 두 확률의 관계를 설명하시오.",
        "Bream 으로 예측한다. z 를 시그모이드 함수에 넣은 값 0.0024 가 양성 클래스(classes_ 의 두 번째인 Smelt)일 확률이고 predict_proba 의 두 번째 열에 들어간다. 첫 번째 열 0.9976 은 1 − 0.0024 로 Bream 일 확률이다. z 가 음수라서 Smelt 확률이 0.5 보다 작으므로 Bream 이 된다.",
        "필수 요소(모두 있어야 정답): (1) Bream 으로 예측. (2) z 를 시그모이드에 넣은 값이 Smelt(양성 클래스, 두 번째 열)의 확률 0.0024 라는 점. (3) Bream 확률은 나머지(1 − 0.0024) 이거나, z 가 음수이면 양성 확률이 0.5 미만이라는 설명 중 하나.",
        ['시그모이드', 'predict_proba'], chk="print(lr.classes_, np.round(lr.predict_proba(train_bream_smelt[:1]), 4), np.round(lr.decision_function(train_bream_smelt[:1]), 2))", pre=PRE_BIN)
    b.E("릿지 회귀의 `alpha` 와 로지스틱 회귀의 `C` 는 모두 규제의 강도를 조절한다. 두 매개변수의 값과 규제 강도의 관계가 어떻게 다른지 설명하고, 노트북에서 `C=20` 으로 설정한 것은 규제를 어떻게 한 것인지 쓰시오.",
        "alpha 는 값이 클수록 규제가 강해지고, C 는 반대로 값이 작을수록 규제가 강해진다(클수록 약해진다). C 의 기본값은 1 이므로 C=20 은 규제를 기본보다 약하게 풀어 준 것이다.",
        "필수 요소(모두 있어야 정답): (1) alpha 는 클수록 규제가 강하다. (2) C 는 작을수록 규제가 강하다(클수록 약하다). (3) C=20 은 규제를 약하게 한 것. 방향이 하나라도 반대면 오답.",
        ['C', 'alpha', '규제'])
    b.E("로지스틱 회귀는 선형회귀와 같은 선형식을 학습하지만 회귀가 아니라 분류에 쓰인다. 로지스틱 회귀가 샘플의 클래스를 정하는 과정을 '선형식', '시그모이드(또는 소프트맥스)', '확률'이라는 말을 넣어 설명하시오.",
        "먼저 특성에 계수를 곱하고 절편을 더한 선형식으로 z 값을 계산한다. 이 z 를 시그모이드 함수(다중 분류에서는 소프트맥스 함수)에 넣어 0~1 사이의 확률로 바꾼다. 그 확률이 가장 큰 클래스(이진 분류에서는 0.5 를 기준)로 샘플을 분류한다.",
        "필수 요소(모두 있어야 정답): (1) 선형식으로 z 를 계산. (2) 시그모이드 또는 소프트맥스로 확률(0~1)로 변환. (3) 확률이 가장 큰 클래스(또는 0.5 기준)로 분류.",
        ['로지스틱 회귀'])
    b.E("7종을 분류하는 모델의 `classes_` 가 `['Bream' 'Parkki' 'Perch' 'Pike' 'Roach' 'Smelt' 'Whitefish']` 이고, 어떤 샘플의 `predict_proba()` 결과가 `[0, 0, 0.6667, 0, 0.3333, 0, 0]` 이다. 이 결과가 뜻하는 것을 설명하고 모델이 예측하는 종을 쓰시오.",
        "predict_proba 의 값은 classes_ 의 순서대로 각 종일 확률이다. 세 번째 값 0.6667 은 Perch 일 확률, 다섯 번째 값 0.3333 은 Roach 일 확률이고 나머지 종의 확률은 0 이다. 확률이 가장 큰 Perch 로 예측한다.",
        "필수 요소(모두 있어야 정답): (1) 열 순서가 classes_ 순서와 같다는 점 또는 0.6667 이 Perch, 0.3333 이 Roach 의 확률이라는 대응. (2) 예측 결과 Perch.",
        ['predict_proba', 'classes_'], chk="print(kn.classes_[np.argmax(kn.predict_proba(test_scaled[3:4]))])", pre=PRE_KN)
    b.E("`train_scaled` 는 훈련 세트의 입력(2차원 배열), `train_target` 은 종 이름이 든 배열이다. 훈련 세트에서 'Bream' 과 'Smelt' 인 샘플의 입력만 골라 `train_bream_smelt` 에 저장하는 코드를 쓰시오. (불리언 인덱싱 사용)",
        "bream_smelt_indexes = (train_target == 'Bream') | (train_target == 'Smelt')\ntrain_bream_smelt = train_scaled[bream_smelt_indexes]",
        "필수 요소(모두 있어야 정답): (1) (train_target == 'Bream') | (train_target == 'Smelt') 형태의 조건. 각 비교식에 괄호가 있어야 하고 or 가 아닌 | 를 써야 한다. (2) 그 조건으로 train_scaled 를 인덱싱. 한 줄로 합쳐 써도 정답. np.isin(train_target, ['Bream','Smelt']) 같은 같은 결과의 코드도 정답.",
        ['불리언 인덱싱'], chk=BOOL + "\nprint(train_bream_smelt.shape)")
    return b
