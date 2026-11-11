"""기말.7 특성공학과 규제 (과대적합, 과소적합)"""
from lib import Bank
from data import PERCH

SRC = '기말.7.특성공학과규제(과대적합,과소적합)'
IMP = PERCH + '''
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.preprocessing import PolynomialFeatures, StandardScaler
'''
# 길이 한 가지 특성
PRE_RAW = IMP + '''
train_input, test_input, train_target, test_target = train_test_split(perch_length, perch_weight, random_state=42)
'''
PRE_1 = PRE_RAW + '''
train_input = train_input.reshape(-1, 1)
test_input = test_input.reshape(-1, 1)
'''
PRE_LIN = PRE_1 + '''
lr = LinearRegression()
lr.fit(train_input, train_target)
'''
PRE_POLY = PRE_1 + '''
train_poly = np.column_stack((train_input ** 2, train_input))
test_poly = np.column_stack((test_input ** 2, test_input))
lr = LinearRegression()
lr.fit(train_poly, train_target)
'''
# 길이, 높이, 두께 세 가지 특성
PRE_3 = IMP + '''
perch_full = pd.read_csv('perch_full.csv').to_numpy()
train_input, test_input, train_target, test_target = train_test_split(perch_full, perch_weight, random_state=42)
'''
PRE_D5 = PRE_3 + '''
poly = PolynomialFeatures(degree=5, include_bias=False)
poly.fit(train_input)
train_poly = poly.transform(train_input)
test_poly = poly.transform(test_input)
'''
PRE_SS = PRE_D5 + '''
ss = StandardScaler()
ss.fit(train_poly)
train_scaled = ss.transform(train_poly)
test_scaled = ss.transform(test_poly)
'''
ONE = '(`train_input`, `test_input` 은 농어 56마리의 길이를 기본 비율로 나눈 뒤 `reshape(-1, 1)` 한 배열이고, 정답은 무게이다)'
THREE = '(`train_input`, `test_input` 은 농어의 길이, 높이, 두께 3개 특성을 기본 비율로 나눈 훈련 42개, 테스트 14개이다)'
SC = '(`train_scaled`, `test_scaled` 는 3개 특성을 `degree=5` 로 늘린 55개 특성을 `StandardScaler` 로 표준화한 훈련 42개, 테스트 14개이다)'
POLY2 = "train_poly = np.column_stack((train_input ** 2, train_input))\ntest_poly = np.column_stack((test_input ** 2, test_input))\nlr = LinearRegression()\nlr.fit(train_poly, train_target)"
PF2 = "poly = PolynomialFeatures(include_bias=False)\npoly.fit(train_input)\ntrain_poly = poly.transform(train_input)\ntest_poly = poly.transform(test_input)"
PF5 = PF2.replace("include_bias=False", "degree=5, include_bias=False") + "\nlr = LinearRegression()\nlr.fit(train_poly, train_target)"


def build():
    b = Bank('07', SRC, PRE_1)

    # ── 개념 분류 ──
    b.C(stem='과대적합과 과소적합에 대한 설명으로 옳은 것만 <보기>에서 모두 고른 것은?',
        items=[("훈련 세트의 점수는 좋은데 테스트 세트의 점수가 낮으면 과대적합이다.", True),
               ("테스트 세트의 점수가 훈련 세트보다 높거나 두 점수가 모두 낮으면 과소적합이다.", True),
               ("과대적합은 모델이 너무 단순해서 훈련이 제대로 되지 않은 경우이다.", False)],
        why="모델이 너무 단순해서 훈련이 제대로 되지 않은 것은 **과소적합**입니다. 과대적합은 모델이 훈련 세트에 너무 집착해서 전체적인 패턴을 놓친 경우입니다.",
        tags=['과대적합', '과소적합'], ref='셀 [1] 과대적합, 과소적합')
    b.C(code="train_input = train_input.reshape(-1, 1)", pre=PRE_RAW,
        stem='`train_input` 은 농어의 길이 42개가 든 1차원 배열(shape `(42,)`)이다. 다음 코드를 실행한 뒤의 설명으로 옳은 것만 <보기>에서 모두 고른 것은?',
        items=[("`train_input.shape` 은 `(42, 1)` 이다.", "train_input.shape == (42, 1)"),
               ("`train_input.size` (전체 원소 수)는 84 가 된다.", "train_input.size == 84"),
               ("`-1` 은 나머지 차원에 맞춰 크기를 자동으로 정하라는 뜻이다.", True)],
        why="사이킷런의 입력은 2차원이어야 해서 `(42,)` 를 `(42, 1)` 로 바꿉니다. 모양만 바뀌고 원소 수 42 는 그대로이며, `-1` 자리는 자동으로 42 가 됩니다.",
        tags=['reshape', '2차원 입력'])
    b.C(code="lr = LinearRegression()\nlr.fit(train_input, train_target)", stem=f'다음 코드에 대한 설명으로 옳은 것만 <보기>에서 모두 고른 것은? {ONE}',
        items=[("`lr.predict([[50]])` 의 값은 약 1574 이다.", "round(float(lr.predict([[50]])[0])) == 1574"),
               ("`lr.coef_` 에는 값이 1개 들어 있다.", "len(lr.coef_) == 1"),
               ("`lr.intercept_` 는 음수이다.", "lr.intercept_ < 0")],
        why="특성이 길이 하나라서 계수도 하나(약 39.02)이고 절편은 약 −709.02 입니다. 50cm 의 예측값은 39.02 × 50 − 709.02 ≈ 1241.8 입니다. 1574 는 2차식(다항회귀) 모델의 예측값입니다.",
        tags=['LinearRegression', 'coef_', 'intercept_'])
    b.C(code=POLY2, stem=f'다음 코드에 대한 설명으로 옳은 것만 <보기>에서 모두 고른 것은? {ONE}',
        items=[("`train_poly.shape` 은 `(42, 2)` 이다.", "train_poly.shape == (42, 2)"),
               ("`train_poly` 의 첫 번째 열은 길이의 제곱이다.", "bool(np.allclose(train_poly[:, 0], train_input[:, 0] ** 2))"),
               ("50cm 농어는 `lr.predict([[50, 50**2]])` 로 예측해야 한다.", False)],
        why="`column_stack` 에 제곱을 먼저 넣었으므로 열 순서는 [길이², 길이] 입니다. 예측할 때도 같은 순서인 `[[50**2, 50]]` 으로 넣어야 합니다.",
        tags=['다항회귀', 'column_stack'])
    b.C(code=PF2, pre=PRE_3, stem=f'다음 코드에 대한 설명으로 옳은 것만 <보기>에서 모두 고른 것은? {THREE}',
        items=[("`train_poly.shape` 은 `(42, 9)` 이다.", "train_poly.shape == (42, 9)"),
               ("`include_bias=False` 를 지우면 특성이 8개로 줄어든다.", "PolynomialFeatures().fit_transform(train_input).shape[1] == 8"),
               ("`poly.get_feature_names_out()` 에는 `'x0 x1'` 이 들어 있다.", "'x0 x1' in poly.get_feature_names_out()")],
        why="특성 3개에서 원래 특성 3개, 제곱 3개, 서로 곱한 것 3개로 9개가 만들어집니다. `include_bias=False` 를 지우면 값이 1인 특성이 하나 **추가**되어 10개가 됩니다.",
        tags=['PolynomialFeatures', '특성 공학'])
    b.C(code=PF5, pre=PRE_3, stem=f'다음 코드를 노트북에서 실행한 결과에 대한 설명으로 옳은 것만 <보기>에서 모두 고른 것은? {THREE}',
        ref='셀 [34]~[38] degree=5 실험 (저장된 출력: 훈련 0.9999999999996433, 테스트 -144.40579436844948)',
        items=[("만들어진 특성은 55개이다.", "train_poly.shape[1] == 55"),
               ("`lr.score(test_poly, test_target)` 도 0.9 이상이다.", False),
               ("`lr.score(train_poly, train_target)` 은 0.99 보다 크다.", True)],
        why="5제곱 항까지 만들면 특성이 55개로 훈련 샘플 42개보다 많아집니다. 훈련 세트는 거의 완벽하게 맞히지만(0.9999…) 테스트 점수는 −144 로, 극단적인 과대적합입니다.",
        tags=['과대적합', 'degree'])
    b.C(stem='규제에 대한 설명으로 옳은 것만 <보기>에서 모두 고른 것은?',
        items=[("`alpha` 값이 클수록 규제가 약해진다.", False),
               ("릿지는 계수를 작게 만들어 여러 특성의 영향력을 줄인다.", True),
               ("라쏘는 일부 특성의 계수를 0 으로 만들어 아예 쓰지 않게 할 수 있다.", True)],
        why="`alpha` 가 **클수록 규제가 강해져** 계수가 더 작아지고 과소적합 쪽으로 갑니다. 릿지는 '여러 특성을 유지하되 영향력을 줄이자', 라쏘는 '일부 특성은 아예 사용하지 말자'입니다.",
        tags=['규제', '릿지', '라쏘', 'alpha'], ref='셀 [40]~[52] 규제, 릿지 회귀, 라쏘 회귀')
    b.C(code="ridge = Ridge(alpha=0.1)\nridge.fit(train_scaled, train_target)\nlasso = Lasso(alpha=10)\nlasso.fit(train_scaled, train_target)", pre=PRE_SS,
        stem=f'다음 코드에 대한 설명으로 옳은 것만 <보기>에서 모두 고른 것은? {SC}',
        items=[("`lasso.coef_` 에는 0 인 계수가 있다.", "int(np.sum(lasso.coef_ == 0)) > 0"),
               ("`ridge.coef_` 에는 0 인 계수가 없다.", "int(np.sum(ridge.coef_ == 0)) == 0"),
               ("`ridge.score(test_scaled, test_target)` 은 음수이다.", "ridge.score(test_scaled, test_target) < 0")],
        why="라쏘는 일부 계수를 정확히 0 으로 만들고, 릿지는 계수를 작게 줄일 뿐 0 으로 만들지는 않습니다. 규제를 적용하자 55개 특성을 쓰면서도 테스트 점수가 약 0.98 로 회복됩니다.",
        tags=['릿지', '라쏘', 'coef_'])
    b.C(code="ss = StandardScaler()\nss.fit(train_poly)\ntrain_scaled = ss.transform(train_poly)\ntest_scaled = ss.transform(test_poly)", pre=PRE_D5,
        stem='`train_poly`, `test_poly` 는 `PolynomialFeatures` 로 만든 훈련 세트와 테스트 세트이다. 다음 코드에 대한 설명으로 옳은 것만 <보기>에서 모두 고른 것은?',
        items=[("`train_scaled` 는 열마다 평균이 0 에 가깝다.", "bool(np.allclose(train_scaled.mean(axis=0), 0))"),
               ("`test_scaled` 도 열마다 평균이 정확히 0 이다.", "bool(np.allclose(test_scaled.mean(axis=0), 0))"),
               ("테스트 세트는 훈련 세트에서 구한 평균과 표준편차로 변환되었다.", True)],
        why="`ss.fit(train_poly)` 로 훈련 세트의 평균과 표준편차를 구하고, 그 기준으로 두 세트를 모두 변환합니다. 테스트 세트는 자기 평균으로 변환한 것이 아니므로 평균이 정확히 0 이 되지는 않습니다.",
        tags=['StandardScaler', '표준화'])

    # ── 빈칸 ──
    b.B("train_input = train_input.㉠(-1, ㉡)\nprint(train_input.shape)", ('reshape', '1'), [('reshape', '2'), ('resize', '0'), ('shape', '1'), ('reshape', '42')], pre=PRE_RAW,
        stem='`train_input` 은 shape 이 `(42,)` 인 1차원 배열이다. ㉠, ㉡에 들어갈 것으로 알맞은 것은?',
        why="`reshape(-1, 1)` 은 열을 1개로 고정하고 행 수를 자동으로 맞춰 `(42, 1)` 을 만듭니다.", tags=['reshape'])
    b.B("lr = ㉠()\nlr.fit(train_input, train_target)\nprint(lr.㉡.round(2), lr.intercept_.round(2))", ('LinearRegression', 'coef_'),
        [('LinearRegression', 'coef'), ('LinearRegression', 'weight_'), ('LogisticRegression', 'coef_'), ('LinearRegression', 'intercept_')], stem=f'㉠, ㉡에 들어갈 것으로 알맞은 것은? {ONE}',
        why="선형회귀 모델은 `LinearRegression`, 학습으로 찾은 기울기(계수)는 끝에 밑줄이 붙은 `coef_` 에 들어 있습니다. 식은 무게 = 39.02 × 길이 − 709.02 입니다.", tags=['LinearRegression', 'coef_'])
    b.B(POLY2 + "\nprint(lr.predict([[㉠, ㉡]]).round(1))", ('50**2', '50'), [('50', '50**2'), ('50', '50'), ('50*2', '50'), ('2500', '2500')],
        stem=f'길이 50cm 인 농어의 무게를 예측하려고 한다. ㉠, ㉡에 들어갈 것으로 알맞은 것은? {ONE}',
        why="훈련할 때 열 순서가 [길이², 길이] 였으므로 예측할 때도 `[[50**2, 50]]` 순서로 넣습니다.", tags=['다항회귀', 'predict'])
    b.B("poly = PolynomialFeatures(㉠=False)\npoly.fit(train_input)\ntrain_poly = poly.㉡(train_input)\nprint(train_poly.shape)", ('include_bias', 'transform'),
        [('include_bias', 'fit'), ('bias', 'transform'), ('include_bias', 'predict'), ('intercept', 'transform')], pre=PRE_3, stem=f'㉠, ㉡에 들어갈 것으로 알맞은 것은? {THREE}',
        why="절편용 항(값이 1인 특성)을 넣지 않는 옵션은 `include_bias=False` 이고, 변환기는 `fit` 다음에 `transform` 으로 데이터를 바꿉니다.", tags=['PolynomialFeatures', 'transform'])
    b.B("ss = ㉠()\nss.fit(train_poly)\ntrain_scaled = ss.transform(train_poly)\ntest_scaled = ss.㉡(test_poly)\nprint(train_scaled.shape, test_scaled.shape)", ('StandardScaler', 'transform'),
        [('StandardScaler', 'fit'), ('MinMaxScaler', 'transform'), ('StandardScaler', 'predict'), ('Standard', 'transform')], pre=PRE_D5,
        stem='규제를 적용하기 전에 특성을 표준화하려고 한다. ㉠, ㉡에 들어갈 것으로 알맞은 것은?',
        why="표준점수로 바꾸는 변환기는 `StandardScaler` 입니다. 훈련 세트로 `fit` 한 변환기로 테스트 세트는 `transform` 만 합니다.", tags=['StandardScaler'])
    b.B("ridge = Ridge(㉠=0.1)\nridge.fit(train_scaled, train_target)\nprint(round(ridge.㉡(test_scaled, test_target), 4))", ('alpha', 'score'),
        [('C', 'score'), ('alpha', 'predict'), ('rate', 'score'), ('alpha', 'fit')], pre=PRE_SS, stem=f'㉠, ㉡에 들어갈 것으로 알맞은 것은? {SC}',
        why="릿지와 라쏘의 규제 강도는 `alpha` 로 조절합니다. `score(입력, 정답)` 이 R² 를 돌려줍니다.", tags=['Ridge', 'alpha'])
    b.B("train_score = []\nalpha_list = [0.001, 0.01, 0.1, 1, 10, 100]\nfor alpha in alpha_list:\n    ridge = Ridge(alpha=㉠)\n    ridge.fit(train_scaled, train_target)\n    train_score.append(ridge.score(train_scaled, train_target))\n"
        "print(np.㉡(alpha_list).tolist(), round(train_score[-1], 2))", ('alpha', 'log10'), [('alpha_list', 'log10'), ('alpha', 'log'), ('alpha', 'sqrt'), ('0.1', 'log10')], pre=PRE_SS,
        stem=f'alpha 값을 바꿔 가며 점수를 기록하고, 그래프의 가로축에 쓸 값을 출력한다. ㉠, ㉡에 들어갈 것으로 알맞은 것은? {SC}',
        why="반복문에서 꺼낸 `alpha` 를 그대로 모델에 넣습니다. alpha 가 10배씩 커지므로 `np.log10` 으로 바꿔 −3, −2, …, 2 처럼 같은 간격으로 만듭니다.", tags=['alpha', 'log10'])

    # ── 경계값 ──
    b.D("a, b, c, d = train_test_split(perch_length, perch_weight, random_state=42)\nprint(len(a), len(b))", ['43 13', '41 15', '14 42', '45 11'], pre=IMP,
        stem='`perch_length`, `perch_weight` 는 농어 56마리의 길이와 무게이다. 다음 코드를 실행했을 때 출력되는 것은?',
        why="기본 테스트 비율 25%이므로 56 × 0.25 = 14개가 테스트 세트, 42개가 훈련 세트입니다.", tags=['train_test_split'])
    b.D("print(PolynomialFeatures(include_bias=False).fit_transform(train_input).shape,\n      PolynomialFeatures().fit_transform(train_input).shape)", ['(42, 9) (42, 9)', '(42, 9) (42, 8)', '(42, 6) (42, 7)', '(42, 3) (42, 4)'], pre=PRE_3,
        stem=f'다음 코드를 실행했을 때 출력되는 것은? {THREE}',
        why="특성 3개를 2차까지 조합하면 9개이고, `include_bias` 의 기본값은 True 라서 값이 1인 특성이 하나 더 붙어 10개가 됩니다.", tags=['include_bias'])
    b.D("poly = PolynomialFeatures(include_bias=False)\nprint(poly.fit_transform([[2, 3]]))", ['[[1. 2. 3. 4. 6. 9.]]', '[[2. 3. 4. 9.]]', '[[4. 6. 9.]]', '[[2. 3. 5. 6.]]'], pre=IMP,
        why="샘플 [2, 3] 에서 원래 값 2, 3 과 2² = 4, 2 × 3 = 6, 3² = 9 가 만들어집니다. `include_bias=False` 라서 맨 앞의 1 은 없습니다.", tags=['PolynomialFeatures'])
    b.D("poly = PolynomialFeatures()\nprint(poly.fit_transform([[2, 3]]))", ['[[2. 3. 4. 6. 9.]]', '[[0. 2. 3. 4. 6. 9.]]', '[[1. 2. 3. 4. 9.]]', '[[1. 2. 3. 6.]]'], pre=IMP,
        why="`include_bias` 를 지정하지 않으면 절편용 항 1 이 맨 앞에 추가됩니다. 그 뒤로 2, 3, 2², 2×3, 3² 입니다.", tags=['PolynomialFeatures', 'include_bias'])
    b.D("poly = PolynomialFeatures(degree=5, include_bias=False)\nprint(poly.fit_transform(train_input).shape)", ['(42, 15)', '(42, 243)', '(42, 9)', '(55, 42)'], pre=PRE_3,
        stem=f'다음 코드를 실행했을 때 출력되는 것은? {THREE}',
        why="5제곱 항까지 만들면 특성이 55개가 됩니다. 샘플 수 42 는 그대로이고, 특성 수가 샘플 수보다 많아집니다.", tags=['degree'])
    b.D("a = np.arange(6)\nprint(a.reshape(-1, 1).shape, a.reshape(2, -1).shape)", ['(6, 1) (2, 6)', '(1, 6) (2, 3)', '(6,) (2, 3)', '(5, 1) (2, 2)'], pre='import numpy as np',
        why="원소가 6개이므로 열을 1로 고정하면 행이 6, 행을 2로 고정하면 열이 3 으로 자동 계산됩니다.", tags=['reshape'])

    # ── 상태 예측 ──
    b.R("print(train_input.shape, test_input.shape)", ['(42,) (14,)', '(1, 42) (1, 14)', '(56, 1) (56, 1)', '(42, 2) (14, 2)'], stem=f'다음 코드를 실행했을 때 출력되는 것은? {ONE}',
        why="56개가 42개와 14개로 나뉘고, `reshape(-1, 1)` 로 열이 1개인 2차원 배열이 됩니다.", tags=['reshape', 'shape'])
    b.R("print(lr.predict([[50]]).round(1))", ['[1574.]', '[1950.9]', '[39.]', '1241.8'], pre=PRE_LIN,
        stem=f'`lr` 은 길이 한 가지 특성으로 훈련한 `LinearRegression` 모델이고 `lr.coef_` 는 약 39.02, `lr.intercept_` 는 약 −709.02 이다. 다음 코드를 실행했을 때 출력되는 것은?',
        why="39.02 × 50 − 709.02 ≈ 1241.8 입니다. `predict` 는 값 하나짜리 배열을 돌려줍니다.", tags=['선형식', 'predict'])
    b.R(PF2 + "\nprint(poly.get_feature_names_out().tolist()[3:6])", ["['x0', 'x1', 'x2']", "['x0^2', 'x1^2', 'x2^2']", "['x0 x1', 'x0 x2', 'x1 x2']", "['1', 'x0', 'x1']"], pre=PRE_3,
        stem=f'다음 코드를 실행했을 때 출력되는 것은? {THREE}',
        why="특성 이름은 x0, x1, x2, x0^2, x0 x1, x0 x2, x1^2, x1 x2, x2^2 순서입니다. 인덱스 3~5 는 x0^2, x0 x1, x0 x2 입니다.", tags=['get_feature_names_out'])
    b.R("print(round(lr.score(train_poly, train_target), 2), round(lr.score(test_poly, test_target), 2))", ['0.94 0.82', '0.98 0.97', '1.0 -144.41', '0.97 0.82'], pre=PRE_POLY,
        stem='길이 한 가지 특성을 [길이², 길이] 로 늘려 훈련한 다항회귀 모델이다. 직선 모델(훈련 0.94, 테스트 0.82)보다 두 점수가 모두 올랐다. 다음 코드를 실행했을 때 출력되는 것은?',
        why="다항회귀 모델의 점수는 훈련 0.97, 테스트 0.98 입니다. 테스트 점수가 조금 더 높아서 과소적합이 약간 남아 있습니다.", tags=['다항회귀', '점수'])
    b.R(PF5 + "\nprint(lr.score(train_poly, train_target) > 0.99, lr.score(test_poly, test_target) < 0)", ['True False', 'False True', 'False False', 'True None'], pre=PRE_3,
        ans='True True', ref='셀 [34]~[38] degree=5 실험 (저장된 출력: 훈련 0.9999999999996433, 테스트 -144.40579436844948)',
        stem=f'노트북에서 다음 코드를 실행했을 때 출력되는 것은? {THREE}',
        why="특성을 55개로 늘리면 훈련 점수는 0.9999… 로 거의 완벽하지만 테스트 점수는 −144 로 음수입니다. 훈련 세트에 지나치게 맞춰진 과대적합입니다.", tags=['과대적합'])
    b.R("a = np.array([[2], [3]])\nprint(np.column_stack((a ** 2, a)).tolist())", ['[[2, 4], [3, 9]]', '[[4, 9], [2, 3]]', '[[4, 2, 9, 3]]', '[[4], [9], [2], [3]]'], pre='import numpy as np',
        why="제곱한 열이 앞, 원래 열이 뒤에 붙습니다. 행마다 [길이², 길이] 순서입니다.", tags=['column_stack'])
    b.R("print(np.log10([0.001, 0.1, 10]).tolist())", ['[0.001, 0.1, 10.0]', '[-3.0, -1.0, 10.0]', '[3.0, 1.0, -1.0]', '[-6.9, -2.3, 2.3]'], pre='import numpy as np',
        why="0.001 = 10⁻³, 0.1 = 10⁻¹, 10 = 10¹ 이므로 −3, −1, 1 입니다. alpha 그래프의 가로축이 이렇게 만들어집니다.", tags=['log10'])
    b.R("print(round(1.01 * 10**2 - 21.6 * 10 + 116.05, 2))", ['117.05', '-98.95', '10.15', '1.5'], pre='',
        stem='다항회귀로 학습한 식이 **무게 = 1.01 × 길이² − 21.6 × 길이 + 116.05** 이다. 길이 10 을 넣은 다음 코드를 실행했을 때 출력되는 것은?',
        why="1.01 × 100 − 216 + 116.05 = 101 − 216 + 116.05 = 1.05 입니다.", tags=['다항식 계산'])

    # ── 대조 ──
    b.X("# 방법1: 직선 모델\nlr1 = LinearRegression()\nlr1.fit(train_input, train_target)\nprint(lr1.predict([[50]]).round(1))\n\n# 방법2: 2차식 모델\nlr2 = LinearRegression()\nlr2.fit(np.column_stack((train_input ** 2, train_input)), train_target)\nprint(lr2.predict([[50**2, 50]]).round(1))",
        [('[1574.]', '[1241.8]'), ('[1241.8]', '[1241.8]'), ('[1574.]', '[1574.]'), ('[1241.8]', '[2500.]')], stem=f'50cm 농어의 무게를 두 모델로 예측한다. ㉠, ㉡에 출력되는 값으로 알맞은 것은? {ONE}',
        why="직선 모델은 약 1241.8g, 길이의 제곱을 특성으로 추가한 모델은 약 1574g 으로 예측합니다. 농어의 무게는 길이가 길수록 더 가파르게 늘어나서 곡선 모델의 예측이 더 큽니다.", tags=['선형회귀', '다항회귀'])
    b.X("# 방법1\nprint(PolynomialFeatures(include_bias=False).fit_transform([[2, 3]]).shape)\n\n# 방법2\nprint(PolynomialFeatures().fit_transform([[2, 3]]).shape)",
        [('(1, 6)', '(1, 5)'), ('(1, 5)', '(1, 5)'), ('(1, 4)', '(1, 5)'), ('(2, 5)', '(2, 6)')], pre=IMP,
        why="[2, 3] 에서 2, 3, 4, 6, 9 다섯 개가 만들어지고, `include_bias` 를 끄지 않으면 맨 앞에 1 이 추가되어 여섯 개가 됩니다.", tags=['include_bias'])
    b.X("# 방법1\nprint(PolynomialFeatures(degree=2, include_bias=False).fit_transform(train_input).shape[1])\n\n# 방법2\nprint(PolynomialFeatures(degree=5, include_bias=False).fit_transform(train_input).shape[1])",
        [('6', '15'), ('9', '45'), ('9', '243'), ('10', '56')], pre=PRE_3, stem=f'㉠, ㉡에 출력되는 값(만들어진 특성의 수)으로 알맞은 것은? {THREE}',
        why="특성 3개를 2차까지 조합하면 9개, 5차까지 조합하면 55개입니다.", tags=['degree'])
    b.X("ridge = Ridge(alpha=0.1).fit(train_scaled, train_target)\nlasso = Lasso(alpha=10).fit(train_scaled, train_target)\n# 방법1: 릿지\nprint(int(np.sum(ridge.coef_ == 0)))\n\n# 방법2: 라쏘\nprint(int(np.sum(lasso.coef_ == 0)))",
        [('40', '0'), ('0', '0'), ('40', '40'), ('55', '55')], pre=PRE_SS, stem=f'55개 계수 중 값이 0 인 것의 개수를 출력한다. ㉠, ㉡에 출력되는 값으로 알맞은 것은? {SC}',
        why="릿지는 계수를 작게 줄이기만 해서 0 인 계수가 없습니다. 라쏘는 55개 중 40개의 계수를 0 으로 만들어 15개 특성만 사용합니다.", tags=['릿지', '라쏘'])
    b.X("ss = StandardScaler()\nss.fit(train_poly)\n# 방법1\nprint(bool(np.allclose(ss.transform(test_poly).mean(axis=0), 0)))\n\n# 방법2\nprint(bool(np.allclose(StandardScaler().fit_transform(test_poly).mean(axis=0), 0)))",
        [('True', 'False'), ('True', 'True'), ('False', 'False'), ('None', 'True')], pre=PRE_D5,
        stem='테스트 세트를 표준화한 뒤 열마다 평균이 0 인지 확인한다. ㉠, ㉡에 출력되는 값으로 알맞은 것은?',
        why="방법1은 훈련 세트의 평균과 표준편차로 변환해서 테스트 세트의 평균이 정확히 0 이 되지 않습니다(올바른 방법). 방법2는 테스트 세트만으로 기준을 새로 잡아서 평균이 0 이 되지만, 훈련 세트와 기준이 달라져 쓰면 안 됩니다.",
        tags=['StandardScaler', 'fit', 'transform'])

    # ── 조건 매핑 ──
    b.S(["shape 이 `(42,)` 인 `train_input` 을 사이킷런 입력에 맞게 2차원으로 바꾼다.", "결과의 shape 은 `(42, 1)` 이다."], "train_input.reshape(-1, 1)",
        ["train_input.reshape(1, -1)", "train_input.reshape(-1)", "train_input.reshape(42)", "train_input.reshape(1, 1)"],
        code="train_input = ____", chk="print(train_input.shape)", pre=PRE_RAW,
        why="열을 1개로 고정하고 행은 `-1` 로 자동 계산합니다. `reshape(1, -1)` 은 `(1, 42)` 가 됩니다.", tags=['reshape'])
    b.S(["길이의 제곱과 길이를 나란히 붙여 특성 2개짜리 훈련 세트를 만든다.", "첫 번째 열이 길이의 제곱이다."], "np.column_stack((train_input ** 2, train_input))",
        ["np.column_stack((train_input, train_input ** 2))", "np.column_stack((train_input * 2, train_input))", "np.concatenate((train_input ** 2, train_input))", "train_input ** 2"],
        code="train_poly = ____", chk="print(train_poly.shape, bool(np.isclose(train_poly[0][0], train_poly[0][1] ** 2)))",
        why="`** 2` 가 제곱이고, `column_stack` 에 넣은 순서대로 열이 됩니다. `* 2` 는 두 배입니다.", tags=['다항회귀', 'column_stack'])
    b.S(["특성 3개를 2차 항까지 조합해 9개로 늘리는 변환기를 만든다.", "값이 1인 절편용 특성은 넣지 않는다."], "PolynomialFeatures(include_bias=False)",
        ["PolynomialFeatures()", "PolynomialFeatures(degree=5, include_bias=False)", "PolynomialFeatures(degree=1, include_bias=False)", "StandardScaler()"],
        code="poly = ____", chk="poly.fit(train_input)\nprint(poly.transform(train_input).shape)", pre=PRE_3,
        why="`degree` 의 기본값이 2 이므로 `include_bias=False` 만 주면 됩니다.", tags=['PolynomialFeatures'])
    b.S(["릿지 회귀 모델 객체를 만든다.", "규제 강도를 0.1 로 한다."], "Ridge(alpha=0.1)", ["Ridge(C=0.1)", "Lasso(alpha=0.1)", "Ridge(alpha=10)", "LinearRegression(alpha=0.1)"],
        code="model = ____", chk="print(type(model).__name__, model.alpha)", pre=IMP,
        why="릿지는 `Ridge`, 규제 강도는 `alpha` 입니다. `C` 는 로지스틱 회귀에서 쓰는 매개변수입니다.", tags=['Ridge', 'alpha'])
    b.S(["`lr` 은 [길이², 길이] 순서의 특성으로 훈련한 모델이다.", "길이 50cm 인 농어 한 마리의 무게를 예측한다."], "lr.predict([[50**2, 50]])",
        ["lr.predict([[50, 50**2]])", "lr.predict([[50]])", "lr.predict([50**2, 50])", "lr.predict([[50*2, 50]])"],
        code="pred = ____", chk="print(pred.round(1))", pre=PRE_POLY,
        why="훈련할 때와 같은 열 순서, 같은 개수의 특성을 2차원으로 넣어야 합니다.", tags=['predict', '다항회귀'])

    # ── 서답형 ──
    b.W("빈칸 ㉠ 에 들어갈 메서드 이름을 쓰시오.", "reshape", pre=PRE_RAW, code="train_input = train_input.㉠(-1, 1)\nprint(train_input.shape)",
        why="배열의 모양을 바꾸는 메서드는 `reshape` 입니다.", tags=['reshape'])
    b.W("선형회귀로 학습한 식이 **무게 = 39 × 길이 − 709** 이다. 길이 30cm 인 농어의 무게 예측값을 구하시오.", "461", accept=['461g', '461.0', '461 g'], chk="print(39 * 30 - 709)", pre='',
        why="39 × 30 − 709 = 1170 − 709 = 461 입니다.", tags=['선형식 계산'])
    b.W("빈칸 ㉠ 에 들어갈 매개변수 이름을 쓰시오. (절편용 특성 1 을 넣지 않는다.)", "include_bias", pre=IMP, code="poly = PolynomialFeatures(㉠=False)\nprint(poly.fit_transform([[2, 3]]))",
        why="`include_bias=False` 로 값이 1인 특성을 빼면 2, 3, 4, 6, 9 만 남습니다.", tags=['include_bias'])
    b.W("특성이 2개인 데이터를 `PolynomialFeatures(include_bias=False)` 로 변환하면 특성은 모두 몇 개가 되는지 쓰시오.", "5", accept=['5개', '다섯', '다섯 개'], pre=IMP,
        chk="print(PolynomialFeatures(include_bias=False).fit_transform([[2, 3]]).shape[1])",
        why="원래 특성 2개(x0, x1), 제곱 2개(x0², x1²), 서로 곱한 것 1개(x0·x1)로 5개입니다.", tags=['PolynomialFeatures'])
    b.W("어떤 모델의 훈련 세트 점수가 0.99999, 테스트 세트 점수가 −144.4 였다. 이 모델의 상태를 무엇이라고 하는지 쓰시오.", "과대적합", accept=['과대 적합', 'overfitting', '오버피팅', '과적합', '과대적합(overfitting)'],
        why="훈련 세트는 거의 완벽하게 맞히지만 테스트 세트에서는 형편없는 것은 훈련 세트에 지나치게 맞춰진 과대적합입니다.", tags=['과대적합'])
    b.W("빈칸 ㉠ 에 들어갈 매개변수 이름을 쓰시오. (릿지와 라쏘에서 규제의 강도를 정한다.)", "alpha", pre=PRE_SS, code="ridge = Ridge(㉠=0.1)\nridge.fit(train_scaled, train_target)\nprint(round(ridge.score(test_scaled, test_target), 4))",
        why="`alpha` 가 클수록 규제가 강해집니다.", tags=['alpha'])
    b.W("`lr.coef_` 가 `[39.02]`, `lr.intercept_` 가 `-709.02` 인 선형회귀 모델로 길이 20cm 인 농어의 무게를 예측한 값을 소수 둘째 자리까지 구하시오.", "71.38", accept=['71.4', '71.38g'],
        chk="print(round(39.02 * 20 - 709.02, 2))", pre='', why="39.02 × 20 − 709.02 = 780.4 − 709.02 = 71.38 입니다.", tags=['선형식 계산'])

    # ── 서술형 ──
    b.E("농어의 길이로 무게를 예측할 때 길이의 제곱을 특성으로 추가해 **무게 = a × 길이² + b × 길이 + c** 꼴의 식을 학습했다. 식에 2차항이 있는데도 이 모델을 선형회귀라고 부를 수 있는 이유를 설명하시오.",
        "길이²을 '왕길이' 같은 새로운 변수 하나로 바꿔 생각하면 식이 무게 = a × 왕길이 + b × 길이 + c 가 된다. 즉 무게는 두 특성(왕길이, 길이)에 계수를 곱해 더한 선형 관계로 표현되므로 선형회귀이다.",
        "필수 요소: 길이의 제곱을 새로운 변수(특성) 하나로 치환하면 특성들의 선형식(계수×특성의 합)이 된다는 취지. '그래프가 직선이라서'는 오답(그래프는 곡선).",
        ['다항회귀', '선형'])
    b.E("농어의 길이, 높이, 두께 3개 특성을 `PolynomialFeatures(degree=5, include_bias=False)` 로 55개로 늘려 선형회귀 모델을 훈련했더니 훈련 세트 점수는 0.9999, 테스트 세트 점수는 −144.4 가 나왔다(훈련 샘플 42개). 이 결과가 뜻하는 것과 그 원인을 쓰고, 해결 방법을 한 가지 쓰시오.",
        "훈련 세트는 거의 완벽하게 맞히지만 테스트 세트는 전혀 맞히지 못하는 과대적합이다. 특성이 55개로 훈련 샘플 수(42개)보다 많아 모델이 훈련 세트에 지나치게 맞춰졌기 때문이다. 해결하려면 특성 수를 줄이거나(degree 를 낮춤), 릿지·라쏘 같은 규제를 적용한다.",
        "필수 요소(모두 있어야 정답): (1) 과대적합이라는 판정. (2) 원인: 특성이 너무 많다/모델이 훈련 세트에 지나치게 맞춰졌다는 취지. (3) 해결: 규제(릿지, 라쏘) 적용 또는 특성 수(차수) 줄이기 중 하나.",
        ['과대적합', '규제'], chk=PF5 + "\nprint(train_poly.shape)", pre=PRE_3)
    b.E("릿지 회귀와 라쏘 회귀는 모두 선형회귀에 규제를 더한 모델이다. 두 모델이 계수를 규제하는 방식의 차이를 설명하시오.",
        "릿지는 계수의 제곱을 기준으로 규제해서 모든 특성의 계수를 작게 줄이지만 0 으로 만들지는 않는다(여러 특성을 유지하되 영향력을 줄임). 라쏘는 계수의 절댓값을 기준으로 규제해서 일부 특성의 계수를 정확히 0 으로 만들 수 있다(일부 특성을 아예 사용하지 않음).",
        "필수 요소(모두 있어야 정답): (1) 릿지: 계수를 작게 줄인다(0 이 되지는 않는다) 또는 계수의 제곱 기준. (2) 라쏘: 일부 계수를 0 으로 만들 수 있다(일부 특성을 쓰지 않는다) 또는 계수의 절댓값 기준. 두 모델의 설명이 서로 바뀌면 오답.",
        ['릿지', '라쏘'])
    b.E("릿지 회귀에서 `alpha` 값을 크게 할 때와 작게 할 때 모델이 각각 어떻게 달라지는지 과대적합, 과소적합과 관련지어 설명하고, 적절한 `alpha` 값은 어떻게 찾는지 쓰시오.",
        "alpha 가 크면 규제가 강해져 계수가 더 작아지고 모델이 단순해져 과소적합 쪽으로 간다. alpha 가 작으면 규제가 약해져 훈련 세트에 더 잘 맞게 되어 과대적합 쪽으로 간다. 여러 alpha 값으로 모델을 훈련해 훈련 세트와 테스트 세트의 점수를 그래프로 그리고, 두 점수가 가장 가깝고 테스트 세트 점수가 가장 높은 alpha 를 고른다.",
        "필수 요소(모두 있어야 정답): (1) alpha 가 크면 규제가 강해져 과소적합 쪽. (2) alpha 가 작으면 규제가 약해져 과대적합 쪽. (3) 여러 alpha 로 훈련·테스트 점수를 비교해(그래프) 테스트 점수가 가장 높은(두 점수가 가까운) 값을 고른다는 취지. 방향이 반대면 오답.",
        ['alpha', '규제'])
    b.E("릿지나 라쏘 같은 규제를 적용하기 전에는 `StandardScaler` 로 특성을 표준화해야 한다. 그 이유를 설명하시오.",
        "규제는 계수의 크기를 기준으로 벌점을 준다. 특성마다 값의 범위(스케일)가 다르면 계수의 크기도 그에 따라 제각각이 되어, 스케일 때문에 계수가 큰 특성만 더 심하게 규제받는 등 공정하게 규제되지 않는다. 표준화로 스케일을 맞추면 모든 특성의 계수가 같은 기준에서 규제된다.",
        "필수 요소: (1) 규제가 계수의 크기에 벌점을 준다는 점. (2) 특성의 스케일이 다르면 계수의 크기가 달라져 공정하게 규제되지 않는다는 점. 두 취지가 드러나야 정답. '점수가 좋아져서'만 쓰면 오답.",
        ['표준화', '규제'])
    b.E("농어의 길이 한 가지 특성으로 훈련한 선형회귀 모델의 식이 **무게 = 39 × 길이 − 709** 였다. 이 식으로 길이 5cm 인 농어의 무게를 계산하고, 그 결과에서 알 수 있는 이 모델의 문제점을 쓰시오.",
        "39 × 5 − 709 = −514. 무게가 음수로 예측된다. 무게는 음수가 될 수 없으므로, 직선 하나로는 길이가 짧은 농어의 무게를 제대로 예측하지 못한다. (실제 데이터는 길이가 길수록 무게가 더 가파르게 늘어나는 곡선 모양이라 직선으로는 한계가 있다.)",
        "필수 요소(모두 있어야 정답): (1) 계산 결과 −514 (음수). (2) 무게가 음수가 되는 것은 현실과 맞지 않는다/직선 모델로는 짧은 농어의 무게를 제대로 예측하지 못한다는 문제점.",
        ['선형회귀', '한계'], chk="print(39 * 5 - 709)", pre='')
    b.E("`PolynomialFeatures(include_bias=False)` 로 샘플 `[2, 3]` 을 변환한 결과를 쓰고, 결과의 각 값이 어떻게 만들어졌는지 설명하시오.",
        "[2, 3, 4, 6, 9]\n2 와 3 은 원래 특성, 4 는 첫 번째 특성의 제곱(2²), 6 은 두 특성의 곱(2 × 3), 9 는 두 번째 특성의 제곱(3²)이다.",
        "필수 요소(모두 있어야 정답): (1) 결과 [2, 3, 4, 6, 9] (순서 포함, 2. 3. 처럼 실수 표기도 정답). (2) 4 = 2², 6 = 2×3, 9 = 3² 이라는 설명. 맨 앞에 1 을 넣으면 오답(include_bias=False).",
        ['PolynomialFeatures'], chk="print(PolynomialFeatures(include_bias=False).fit_transform([[2, 3]]))", pre=IMP)
    return b
