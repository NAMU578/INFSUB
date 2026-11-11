"""기말.4 선형회귀 (보험료 예측)"""
from lib import Bank

SRC = '기말.4.선형회귀'
IMP = '''
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler, StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
'''
# 판다스 버전에 따라 replace 뒤의 자료형이 달라서, 검증용 준비 코드는 map 으로 같은 값을 만든다.
PRE_DF = IMP + '''
raw = pd.read_csv('insurance.csv')
df = raw.drop('region', axis=1)
df['sex'] = df['sex'].map({'male': 0, 'female': 1})
df['smoker'] = df['smoker'].map({'no': 0, 'yes': 1})
'''
PRE_XY = PRE_DF + '''
X = df[['age', 'bmi', 'smoker']]
y = df['charges']
'''
PRE_MODEL = PRE_XY + '''
scaler = MinMaxScaler()
normalized_data = scaler.fit_transform(X.values)
X = pd.DataFrame(normalized_data, columns=X.columns)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=10)
linear_model = LinearRegression()
linear_model.fit(X_train, y_train)
'''
DF = '(`df` 는 보험 데이터 1338행. 열은 age, sex, bmi, children, smoker, charges 이고 sex 와 smoker 는 0/1 로 바꾼 상태)'
MD = ('(`X` 는 age, bmi, smoker 를 Min-Max 정규화한 데이터프레임(1338행), `y` 는 charges. '
      '`scaler` 는 정규화에 쓴 `MinMaxScaler` 객체)')


def build():
    b = Bank('04', SRC, PRE_MODEL)

    # ── 개념 분류 ──
    b.C(code='df = pd.read_csv("insurance.csv")', pre=IMP,
        stem='insurance.csv 에는 age, sex, bmi, children, smoker, region, charges 열이 있고 sex, smoker, region 은 문자열이다. 다음 코드를 실행한 뒤의 설명으로 옳은 것만 <보기>에서 모두 고른 것은?',
        items=[("`df.shape` 은 `(1338, 7)` 이다.", "df.shape == (1338, 7)"),
               ("`df.describe()` 의 결과에는 `sex`, `smoker`, `region` 열이 나오지 않는다.", "set(df.describe().columns) == {'age', 'bmi', 'children', 'charges'}"),
               ("`df.isna().sum()` 은 결측치가 있는 행의 수를 숫자 하나로 돌려준다.", False)],
        why="`describe()` 는 수치형 열의 통계만 보여 주므로 문자열 열 세 개는 빠집니다. `isna().sum()` 은 숫자 하나가 아니라 **열마다** 결측치 개수를 돌려줍니다.",
        tags=['read_csv', 'describe', 'isna'])
    b.C(code="df = pd.DataFrame({'age': [19, 18], 'sex': ['female', 'male'], 'region': ['sw', 'se']})\ndf2 = df.drop('region', axis=1)\ndf2['sex'] = df2['sex'].replace({'male': 0, 'female': 1})", pre=IMP,
        items=[("`df` 에서도 `region` 열이 사라진다.", "'region' not in df.columns"),
               ("`df2` 의 열은 `age`, `sex` 두 개이다.", "list(df2.columns) == ['age', 'sex']"),
               ("`df2['sex']` 의 값은 차례로 1, 0 이다.", "df2['sex'].tolist() == [1, 0]")],
        why="`drop()` 은 원본을 바꾸지 않고 열을 뺀 **새 데이터프레임**을 돌려주므로 `df` 에는 `region` 이 그대로 있습니다. `replace` 는 딕셔너리의 짝대로 female → 1, male → 0 으로 바꿉니다.",
        tags=['drop', 'replace'])
    b.C(code="X = df[['age', 'bmi', 'smoker']]\ny = df['charges']", pre=PRE_DF, stem=f'다음 코드에 대한 설명으로 옳은 것만 <보기>에서 모두 고른 것은? {DF}',
        items=[("`X` 는 데이터프레임, `y` 는 시리즈이다.", "type(X).__name__ == 'DataFrame' and type(y).__name__ == 'Series'"),
               ("`X.shape` 은 `(1338, 4)` 이다.", "X.shape == (1338, 4)"),
               ("`y` 는 모델이 맞혀야 하는 값(종속변수)이다.", True)],
        why="대괄호를 두 겹으로 쓰면 여러 열을 고른 데이터프레임, 한 겹이면 열 하나인 시리즈입니다. 고른 열이 3개이므로 `X.shape` 은 `(1338, 3)` 입니다. 보험료 `charges` 가 예측 대상입니다.",
        tags=['독립변수', '종속변수', '열 선택'])
    b.C(code="scaler = MinMaxScaler()\nnormalized_data = scaler.fit_transform(X.values)", pre=PRE_XY,
        stem='`X` 는 age, bmi, smoker 세 열로 된 데이터프레임(1338행)이다. 다음 코드에 대한 설명으로 옳은 것만 <보기>에서 모두 고른 것은?',
        items=[("`normalized_data` 의 각 열은 최솟값이 0, 최댓값이 1이다.", "bool(np.allclose(normalized_data.min(axis=0), 0) and np.allclose(normalized_data.max(axis=0), 1))"),
               ("`normalized_data` 의 각 열은 평균이 0이다.", "bool(np.allclose(normalized_data.mean(axis=0), 0))"),
               ("`normalized_data.shape` 은 `(1338, 3)` 이다.", "normalized_data.shape == (1338, 3)")],
        why="Min-Max 정규화는 열마다 최솟값을 0, 최댓값을 1로 맞춥니다. 평균을 0으로 맞추는 것은 표준화(표준점수)입니다. 값만 바뀌고 모양은 그대로입니다.",
        tags=['MinMaxScaler', '정규화'])
    b.C(stem='결정계수 R² 에 대한 설명으로 옳은 것만 <보기>에서 모두 고른 것은?',
        items=[("R² = 0.8 은 예측 정확도가 80%라는 뜻이다.", False),
               ("R² 의 최댓값은 1이다.", True),
               ("평균으로 예측하는 것보다 오차가 크면 R² 는 음수가 된다.", True)],
        why="R² 는 '평균으로 예측하는 기준 모델보다 제곱오차 합을 얼마나 줄였는가'를 나타냅니다. 모든 예측이 맞으면 1, 평균 예측과 같으면 0, 그보다 나쁘면 음수입니다. 정확도(맞힌 비율)와는 다른 지표입니다.",
        tags=['R²', '결정계수'], ref='셀 [35] R² Score 설명')
    b.C(code="linear_model = LinearRegression()\nlinear_model.fit(X_train, y_train)\nlinear_predict = linear_model.predict(X_test)",
        stem=f'`train_test_split(X, y, test_size=0.3, random_state=10)` 으로 나눈 뒤 다음 코드를 실행했다. 설명으로 옳은 것만 <보기>에서 모두 고른 것은? {MD}',
        items=[("`linear_model.score(X_test, y_test)` 와 `r2_score(y_test, linear_predict)` 는 같은 값이다.", "bool(np.isclose(linear_model.score(X_test, y_test), r2_score(y_test, linear_predict)))"),
               ("`len(linear_predict)` 는 402이다.", "len(linear_predict) == 402"),
               ("`linear_predict` 의 값은 모두 0 이상이다.", "bool((linear_predict >= 0).all())")],
        why="회귀 모델의 `score()` 는 결정계수 R² 를 돌려주므로 `r2_score(실제값, 예측값)` 과 같습니다. 테스트 세트는 1338 × 0.3 을 올림한 402개입니다. 선형 모델의 출력에는 범위 제한이 없어 예측값 중에 음수(−596.89)도 있습니다.",
        tags=['score', 'r2_score', 'predict'])
    b.C(code="corr = df.corr()", pre=PRE_DF, stem=f'다음 코드에 대한 설명으로 옳은 것만 <보기>에서 모두 고른 것은? {DF}',
        items=[("`corr` 는 속성 쌍마다 상관계수를 담은 6행 6열 표이다.", "corr.shape == (6, 6)"),
               ("보험료(`charges`)와 상관계수가 가장 큰 속성은 `age` 이다.", "corr['charges'].drop('charges').idxmax() == 'age'"),
               ("`sns.heatmap(corr, annot=True)` 의 `annot=True` 는 칸마다 숫자를 표시한다.", True)],
        why="보험료와 상관계수가 가장 큰 속성은 흡연 여부 `smoker` (약 0.79)입니다. `age` 는 약 0.30, `bmi` 는 약 0.20 입니다. 그래서 노트북은 age, bmi, smoker 를 학습 속성으로 골랐습니다.",
        tags=['corr', 'heatmap', '상관계수'])

    # ── 빈칸 ──
    b.B('df = pd.㉠("insurance.csv")\nprint(df.㉡)', ('read_csv', 'shape'), [('read_csv', 'size'), ('read', 'shape'), ('load_csv', 'shape'), ('read_csv', 'shape()')], pre=IMP,
        why="csv 파일은 `pd.read_csv()` 로 읽고, (행 수, 열 수)는 괄호 없이 `df.shape` 으로 봅니다.", tags=['read_csv', 'shape'])
    b.B("df = pd.DataFrame({'age': [19, 18], 'bmi': [27.9, 33.8], 'region': ['sw', 'se']})\ndf = df.㉠('region', axis=㉡)\nprint(list(df.columns))",
        ('drop', '1'), [('drop', '0'), ('delete', '1'), ('remove', '1'), ('dropna', '0')], pre=IMP,
        why="행이나 열을 지우는 메서드는 `drop` 이고, **열**을 지울 때는 `axis=1` 입니다. `axis=0` 은 행을 지웁니다.", tags=['drop', 'axis'])
    b.B("X = df[㉠]\ny = df[㉡]\nprint(X.shape, y.shape)", ("['age', 'bmi', 'smoker']", "'charges'"),
        [("'age', 'bmi', 'smoker'", "'charges'"), ("['age', 'bmi', 'smoker']", "['charges']"), ("['charges']", "'age'"), ("['age', 'bmi']", "'charges'")], pre=PRE_DF,
        stem=f'㉠, ㉡에 들어갈 것으로 알맞은 것은? {DF}',
        why="열을 여러 개 고를 때는 열 이름의 **리스트**를 넣어 대괄호가 두 겹이 됩니다. `y` 는 shape 이 `(1338,)` 인 시리즈이므로 열 이름 하나만 넣습니다.", tags=['열 선택'])
    b.B("scaler = ㉠()\nnormalized_data = scaler.㉡(X.values)\nprint(normalized_data.min(), normalized_data.max())", ('MinMaxScaler', 'fit_transform'),
        [('MinMaxScaler', 'transform'), ('StandardScaler', 'fit_transform'), ('MinMaxScaler', 'fit'), ('Normalizer', 'fit_transform')], pre=PRE_XY,
        why="0~1 로 맞추는 변환기는 `MinMaxScaler` 이고, 기준 계산과 변환을 한 번에 하는 메서드는 `fit_transform` 입니다. `fit` 을 하지 않고 `transform` 만 부르면 오류가 납니다.",
        tags=['MinMaxScaler', 'fit_transform'])
    b.B("X_train, X_test, y_train, y_test = train_test_split(X, y, ㉠=0.3, random_state=10)\nprint(len(X_train), len(㉡))", ('test_size', 'X_test'),
        [('train_size', 'X_test'), ('test_size', 'y_train'), ('size', 'X_test'), ('test_size', 'X')], stem=f'㉠, ㉡에 들어갈 것으로 알맞은 것은? {MD}',
        why="`test_size=0.3` 이면 1338개 중 30%(올림해서 402개)가 테스트 세트, 나머지 936개가 훈련 세트입니다.", tags=['test_size'])
    b.B("linear_model = ㉠()\nlinear_model.fit(X_train, y_train)\nprint(round(linear_model.㉡(X_test, y_test), 3))", ('LinearRegression', 'score'),
        [('LinearRegression', 'predict'), ('LinearRegression', 'r2_score'), ('LinearModel', 'score'), ('Regression', 'score')],
        why="선형회귀 모델은 `LinearRegression` 이고, `score(입력, 정답)` 이 결정계수 R² 를 돌려줍니다.", tags=['LinearRegression', 'score'])

    # ── 경계값 ──
    b.D("X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=10)\nprint(len(X_train), len(X_test))",
        ['937 401', '1003 335', '402 936', '1338 402'], stem=f'다음 코드를 실행했을 때 출력되는 것은? {MD}',
        why="1338 × 0.3 = 401.4 를 올림해 테스트 세트가 402개, 나머지 936개가 훈련 세트입니다.", tags=['test_size', '올림'])
    b.D("data = np.array([[10.0], [20.0], [50.0]])\nprint(MinMaxScaler().fit_transform(data).ravel().tolist())", ['[0.2, 0.4, 1.0]', '[0.0, 0.5, 1.0]', '[0.0, 0.2, 1.0]', '[-1.0, 0.0, 1.0]'], pre=IMP,
        why="(x − 최솟값) ÷ (최댓값 − 최솟값) 입니다. 20은 (20 − 10) ÷ (50 − 10) = 0.25 입니다. 단순히 최댓값으로 나눈 0.4 가 아닙니다.", tags=['MinMaxScaler'])
    b.D("scaler = MinMaxScaler()\nscaler.fit(np.array([[10.0], [20.0], [50.0]]))\nprint(scaler.transform(np.array([[60.0], [0.0]])).ravel().tolist())", ['[1.0, 0.0]', '[1.2, 0.0]', '[1.0, -0.25]', '[60.0, 0.0]'], pre=IMP,
        why="`transform` 은 `fit` 때 정해진 최솟값 10, 최댓값 50 을 그대로 씁니다. 60은 (60 − 10) ÷ 40 = 1.25, 0은 (0 − 10) ÷ 40 = −0.25 로, 기준 범위를 벗어난 새 데이터는 0~1 밖의 값이 됩니다.", tags=['transform', '범위'])
    b.D("df = pd.DataFrame({'a': [1, None, 3], 'b': [None, None, 6]})\nprint(df.isna().sum().tolist())", ['[2, 1]', '[1, 1]', '[3]', '[2, 2, 0]'], pre=IMP,
        why="`isna()` 는 결측이면 True 이고 `sum()` 은 열마다 True 의 개수를 셉니다. a 열에 1개, b 열에 2개입니다.", tags=['isna', '결측치'])
    b.D('df = pd.read_csv("insurance.csv")\nprint(len(df.head()), len(df.head(3)), len(df))', ['5 3 7', '10 3 1338', '5 4 1338', '1 3 1338'], pre=IMP,
        stem='insurance.csv 는 데이터가 1338행인 파일이다. 다음 코드를 실행했을 때 출력되는 것은?',
        why="`head()` 는 기본으로 앞 5행, `head(3)` 은 앞 3행을 보여 줍니다. `len(df)` 는 전체 행 수입니다.", tags=['head'])

    # ── 상태 예측 ──
    b.R("X = df[['age', 'bmi', 'smoker']]\ny = df['charges']\nprint(X.shape, y.shape)", ['(1338, 3) (1338, 1)', '(3, 1338) (1338,)', '(1338, 6) (1338,)', '(1338,) (1338,)'], pre=PRE_DF,
        stem=f'다음 코드를 실행했을 때 출력되는 것은? {DF}',
        why="열 3개를 고른 데이터프레임은 `(1338, 3)`, 열 하나인 시리즈는 1차원이라 `(1338,)` 입니다.", tags=['shape', '열 선택'])
    b.R("s = pd.Series(['no', 'yes', 'no'])\nprint(s.replace({'no': 0, 'yes': 1}).tolist())", ["[1, 0, 1]", "['no', 'yes', 'no']", "[0, 1]", "[False, True, False]"], pre=IMP,
        why="`replace` 에 딕셔너리를 넘기면 키를 값으로 바꿉니다. no → 0, yes → 1 입니다. 범주형 데이터를 수치형으로 바꾸는 전처리입니다.", tags=['replace'])
    b.R("print(scaler.transform([[35, 28.5, 1]]).round(4).tolist())", ['[[35.0, 28.5, 1.0]]', '[[0.5469, 0.5364, 1.0]]', '[[0.3696, 0.3374, 0.5]]', '[[0.0, 0.0, 0.0]]'],
        stem='`scaler` 는 age(최소 18, 최대 64), bmi(최소 15.96, 최대 53.13), smoker(최소 0, 최대 1) 로 `fit` 한 `MinMaxScaler` 이다. 다음 코드를 실행했을 때 출력되는 것은?',
        why="나이 (35 − 18) ÷ (64 − 18) = 0.3696, bmi (28.5 − 15.96) ÷ (53.13 − 15.96) = 0.3374, 흡연 (1 − 0) ÷ (1 − 0) = 1.0 입니다.", tags=['transform', '정규화 계산'])
    b.R("y_true = [1, 2, 3]\nprint(r2_score(y_true, [1, 2, 3]), r2_score(y_true, [2, 2, 2]))", ['1.0 0.5', '0.0 1.0', '100.0 0.0', '1.0 -1.0'], pre=IMP,
        why="모든 예측이 실제값과 같으면 R² = 1 입니다. 실제값의 평균인 2로만 예측하면 '평균으로 예측하는 기준 모델'과 같아서 R² = 0 입니다.", tags=['R²'])
    b.R("print(r2_score([1, 2, 3], [3, 2, 1]))", ['-1.0', '0.0', '1.0', '3.0'], pre=IMP,
        why="오차 제곱의 합은 4 + 0 + 4 = 8, 평균(2)으로 예측했을 때의 오차 제곱의 합은 1 + 0 + 1 = 2 입니다. R² = 1 − 8 ÷ 2 = −3 으로, 평균 예측보다 나쁘면 음수가 됩니다.", tags=['R²', '음수'])
    b.R("pred = linear_model.predict(X_test)\nprint(type(pred).__name__, pred.shape, bool((pred < 0).any()))", ['DataFrame (402, 1) False', 'ndarray (402,) False', 'ndarray (936,) True', 'list (402,) True'],
        stem=f'테스트 세트는 402개이고, 예측값 중에는 −596.89 가 있다. 다음 코드를 실행했을 때 출력되는 것은? {MD}',
        why="`predict` 는 샘플마다 예측값 하나씩을 담은 1차원 넘파이 배열을 돌려줍니다. 선형 모델은 출력 범위에 제한이 없어 음수 예측도 나옵니다.", tags=['predict'])

    # ── 대조 ──
    b.X("scaler = MinMaxScaler()\n# 방법1\nprint(scaler.fit_transform(np.array([[10.0], [20.0], [50.0]]))[1][0])\n\n# 방법2\nprint(scaler.transform(np.array([[30.0]]))[0][0])",
        [('0.4', '0.6'), ('0.25', '0.0'), ('0.25', '1.0'), ('0.5', '0.5')], pre=IMP,
        why="`fit_transform` 에서 최솟값 10, 최댓값 50 이 기준으로 정해져 20은 0.25 가 됩니다. 그 뒤의 `transform` 은 같은 기준을 써서 30을 (30 − 10) ÷ 40 = 0.5 로 바꿉니다.", tags=['fit_transform', 'transform'])
    b.X("# 방법1\nprint(df[['age']].shape)\n\n# 방법2\nprint(df['age'].shape)", [('(1338,)', '(1338, 1)'), ('(1338, 1)', '(1338, 1)'), ('(1338,)', '(1338,)'), ('(1, 1338)', '(1338,)')], pre=PRE_DF,
        stem=f'㉠, ㉡에 출력되는 값으로 알맞은 것은? {DF}',
        why="대괄호 두 겹은 열이 하나뿐이어도 2차원 데이터프레임 `(1338, 1)` 이고, 한 겹은 1차원 시리즈 `(1338,)` 입니다.", tags=['열 선택', 'shape'])
    b.X("df = pd.DataFrame({'a': [1, 2, 3], 'b': [4, 5, 6], 'c': [7, 8, 9]})\n# 방법1\nprint(df.drop('b', axis=1).shape)\n\n# 방법2\nprint(df.drop(1, axis=0).shape)",
        [('(2, 3)', '(3, 2)'), ('(3, 2)', '(3, 2)'), ('(3, 3)', '(3, 3)'), ('(3, 2)', '(3, 3)')], pre=IMP,
        why="`axis=1` 은 열을 지워서 3행 2열, `axis=0` 은 인덱스 1인 행을 지워서 2행 3열이 됩니다.", tags=['drop', 'axis'])
    b.X("d = np.array([[0.0], [10.0]])\n# 방법1\nprint(MinMaxScaler().fit_transform(d).ravel().tolist())\n\n# 방법2\nprint(StandardScaler().fit_transform(d).ravel().tolist())",
        [('[-1.0, 1.0]', '[0.0, 1.0]'), ('[0.0, 1.0]', '[0.0, 1.0]'), ('[0.0, 10.0]', '[-5.0, 5.0]'), ('[0.0, 1.0]', '[-0.5, 0.5]')], pre=IMP,
        why="Min-Max 정규화는 최솟값을 0, 최댓값을 1로 만듭니다. 표준화는 (값 − 평균) ÷ 표준편차라서 평균 5, 표준편차 5인 이 데이터는 −1 과 1 이 됩니다.", tags=['정규화', '표준화'])
    b.X("df = pd.DataFrame({'a': [1, 2], 'b': [3, 4], 'c': [5, 6]})\n# 방법1\ndf.drop('b', axis=1)\nprint(len(df.columns))\n\n# 방법2\ndf = df.drop('b', axis=1)\nprint(len(df.columns))",
        [('2', '2'), ('3', '3'), ('2', '1'), ('3', '1')], pre=IMP,
        why="`drop()` 은 원본을 바꾸지 않습니다. 결과를 다시 `df` 에 넣어야 열이 실제로 줄어듭니다.", tags=['drop', '대입'])

    # ── 조건 매핑 ──
    b.S(["`df` 에서 age, bmi, smoker 세 열만 골라 독립변수로 쓴다.", "결과는 shape 이 `(1338, 3)` 인 데이터프레임이다."], "df[['age', 'bmi', 'smoker']]",
        ["df['age', 'bmi', 'smoker']", "df[['charges']]", "df['age'] + df['bmi'] + df['smoker']", "df.drop('charges')"],
        code="X = ____", chk="print(X.shape, list(X.columns))", pre=PRE_DF,
        why="여러 열을 고를 때는 열 이름 리스트를 대괄호 안에 넣습니다.", tags=['열 선택'])
    b.S(["`region` **열**을 지운다.", "지운 결과가 `df` 에 반영된다."], "df.drop('region', axis=1)",
        ["df.drop('region', axis=0)", "df.drop('region')", "df.remove('region', axis=1)", "df['region'].drop()"],
        code="df = ____", chk="print(df.shape, 'region' in df.columns)", pre=IMP + "df = pd.read_csv('insurance.csv')",
        why="열을 지울 때는 `axis=1` 을 줍니다. `axis` 를 생략하면 행 인덱스에서 'region' 을 찾다가 오류가 납니다.", tags=['drop', 'axis'])
    b.S(["새 고객 데이터 `new_customer` (age 35, bmi 28.5, smoker 1)를 정규화한다.", "학습 때 `scaler` 가 정한 최솟값, 최댓값 기준을 **그대로** 쓴다."], "scaler.transform(new_customer.values)",
        ["scaler.fit_transform(new_customer.values)", "MinMaxScaler().fit_transform(new_customer.values)", "scaler.fit(new_customer.values)", "new_customer.values / 100"],
        code="new_customer_normalized = ____", chk="print(np.round(new_customer_normalized, 4).tolist())",
        pre=PRE_MODEL + "new_customer = pd.DataFrame([{'age': 35, 'bmi': 28.5, 'smoker': 1}])",
        why="`fit_transform` 을 다시 부르면 새 데이터 한 줄만으로 기준을 새로 잡아 버려 모든 값이 0이 됩니다. 이미 `fit` 한 `scaler` 의 `transform` 만 써야 합니다.", tags=['transform', '새 데이터'])
    b.S(["데이터의 30%를 테스트 세트로 쓴다.", "실행할 때마다 같은 결과가 나오게 한다."], "train_test_split(X, y, test_size=0.3, random_state=10)",
        ["train_test_split(X, y, test_size=30, random_state=10)", "train_test_split(X, y, train_size=0.3, random_state=10)", "train_test_split(X, y, random_state=10)", "train_test_split(X, y, test_size=0.7, random_state=10)"],
        code="X_train, X_test, y_train, y_test = ____", chk="print(len(X_train), len(X_test))",
        why="비율은 `test_size=0.3` 처럼 소수로 줍니다. `test_size=30` 은 테스트 샘플 30개라는 뜻이고, 생략하면 25%입니다.", tags=['test_size'])
    b.S(["`smoker` 열의 문자열 'no' 를 0으로, 'yes' 를 1로 바꾼다."], "df['smoker'].replace({'no': 0, 'yes': 1})",
        ["df['smoker'].replace({'yes': 0, 'no': 1})", "df['smoker'].replace('no', 'yes')", "df['smoker'].drop('no')", "df['smoker'].astype(int)"],
        code="df['smoker'] = ____", chk="print(df['smoker'].tolist())", pre=IMP + "df = pd.DataFrame({'smoker': ['yes', 'no', 'no']})",
        why="`replace` 에 {바꿀 값: 새 값} 딕셔너리를 넘깁니다. 문자열 'yes' 는 `astype(int)` 로 숫자가 되지 않습니다.", tags=['replace', '범주형'])

    # ── 서답형 ──
    b.W("나이 속성의 최솟값이 18, 최댓값이 64이다. 41세를 Min-Max 정규화한 값을 구하시오.", "0.5", accept=['0.50', '1/2', '.5', '23/46'], chk="print((41 - 18) / (64 - 18))", pre='',
        why="(41 − 18) ÷ (64 − 18) = 23 ÷ 46 = 0.5 입니다.", tags=['정규화 계산'])
    b.W("빈칸 ㉠ 에 들어갈 메서드 이름을 쓰시오. (값이 결측이면 True 로 표시한다.)", "isna", accept=['isnull'], pre=IMP,
        code="df = pd.DataFrame({'a': [1, None, 3], 'b': [4, 5, None]})\nprint(df.㉠().sum().tolist())",
        why="`isna()` 로 결측 여부를 표시하고 `sum()` 으로 열마다 개수를 셉니다. `isnull()` 도 같은 기능입니다.", tags=['isna', '결측치'])
    b.W("빈칸 ㉠ 에 들어갈 메서드 이름을 쓰시오. (학습 때 정한 기준을 바꾸지 않고 새 데이터를 변환한다.)", "transform",
        code="new_array = np.array([[35, 28.5, 1]])\nprint(scaler.㉠(new_array).round(4).tolist())",
        why="이미 `fit` 한 변환기로 새 데이터를 바꿀 때는 `transform` 만 씁니다.", tags=['transform'])
    b.W("빈칸 ㉠ 에 공통으로 들어갈 함수 이름을 쓰시오. (회귀 모델의 결정계수를 구한다.)", "r2_score", pre='',
        code="from sklearn.metrics import ㉠\nprint(㉠([1, 2, 3], [1, 2, 3]))",
        why="`r2_score(실제값, 예측값)` 이 결정계수를 구합니다. 예측이 모두 맞아서 1.0 입니다.", tags=['r2_score'])
    b.W("샘플 1000개를 `train_test_split(X, y, test_size=0.3)` 으로 나누면 테스트 세트는 몇 개인지 쓰시오.", "300", accept=['300개'],
        chk="print(len(train_test_split(np.zeros((1000, 1)), np.zeros(1000), test_size=0.3, random_state=0)[1]))", pre=IMP,
        why="1000 × 0.3 = 300개가 테스트 세트이고 나머지 700개가 훈련 세트입니다.", tags=['test_size'])
    b.W("빈칸 ㉠ 에 들어갈 매개변수 이름을 쓰시오.", "axis", pre=IMP,
        code="df = pd.DataFrame({'age': [19, 18], 'region': ['sw', 'se']})\ndf = df.drop('region', ㉠=1)\nprint(list(df.columns))",
        why="`axis=1` 이 열 방향입니다.", tags=['drop', 'axis'])

    # ── 서술형 ──
    b.E("선형회귀 모델의 `score()` 값이 0.72로 나왔다. 이 값의 이름과 의미를 쓰고, '예측 정확도가 72%'라고 말하면 안 되는 이유를 설명하시오.",
        "이 값은 결정계수(R²)이다. 모든 값을 평균으로 예측하는 기준 모델과 비교해 제곱오차의 합을 72% 줄였다는 뜻이다. 정확도는 분류에서 전체 중 맞힌 개수의 비율인데, 회귀는 연속적인 수치를 예측하므로 맞혔다/틀렸다로 셀 수 없고 R² 는 오차가 줄어든 정도를 나타내는 다른 지표이다.",
        "필수 요소(모두 있어야 정답): (1) 결정계수 또는 R² 라는 이름. (2) 평균으로 예측하는 것(기준 모델)과 비교해 오차(제곱오차 합)를 얼마나 줄였는지를 나타낸다는 의미. (3) 정확도(맞힌 비율)와는 다른 지표라는 점. '72%를 맞혔다'는 식의 설명은 오답.",
        ['R²', '결정계수'], chk="print(round(linear_model.score(X_test, y_test), 2))")
    b.E("학습 데이터는 `scaler.fit_transform()` 으로 정규화했다. 예측하려는 새 고객 데이터를 정규화할 때는 `scaler.fit_transform()` 이 아니라 `scaler.transform()` 을 써야 한다. 그 이유를 설명하시오.",
        "fit 은 최솟값과 최댓값 같은 변환 기준을 새로 계산한다. 새 데이터에 fit_transform 을 쓰면 새 데이터만으로 기준이 다시 정해져 학습 데이터와 다른 기준으로 변환된다. 모델은 학습 데이터의 기준으로 변환된 값으로 학습했으므로, 새 데이터도 같은 기준을 그대로 쓰는 transform 으로 변환해야 한다.",
        "필수 요소: (1) fit(또는 fit_transform)은 기준(최솟값·최댓값)을 새로 계산한다는 점. (2) 새 데이터도 학습 데이터와 같은 기준으로 변환해야 한다는 점. 두 가지 취지가 모두 드러나야 정답.",
        ['transform', 'fit_transform'])
    b.E("어떤 속성의 최솟값이 20, 최댓값이 60이다. 값 30과 50을 각각 Min-Max 정규화하는 식과 결과를 쓰시오.",
        "Min-Max 정규화 = (값 − 최솟값) ÷ (최댓값 − 최솟값)\n30: (30 − 20) ÷ (60 − 20) = 0.25\n50: (50 − 20) ÷ (60 − 20) = 0.75",
        "필수 요소(모두 있어야 정답): (1) 30의 정규화 값 0.25. (2) 50의 정규화 값 0.75. 식이 (값 − 최솟값) ÷ (최댓값 − 최솟값) 꼴이어야 하며 최댓값으로만 나눈 0.5, 0.83 은 오답. 식 없이 두 값만 정확히 써도 정답으로 인정한다.",
        ['정규화 계산'], chk="print((30 - 20) / (60 - 20), (50 - 20) / (60 - 20))", pre='')
    b.E("보험 데이터의 `sex` 열에는 'male', 'female', `smoker` 열에는 'yes', 'no' 가 문자열로 들어 있다. 모델을 학습시키기 전에 이 열들에 해 주어야 하는 전처리가 무엇인지 쓰고, `smoker` 열에 대해 그 전처리를 하는 코드를 한 줄 쓰시오. (no 는 0, yes 는 1)",
        "문자열로 된 범주형 데이터를 수치형 데이터로 바꿔야 한다. 모델은 숫자로 계산하기 때문이다.\ndf['smoker'] = df['smoker'].replace({'no': 0, 'yes': 1})",
        "필수 요소(모두 있어야 정답): (1) 범주형(문자열) 데이터를 수치형(숫자)으로 변환한다는 설명. (2) df['smoker'].replace({'no':0, 'yes':1}) 또는 map 등 같은 결과를 내는 코드. no→0, yes→1 방향이 반대면 오답. 결과를 df['smoker'] 에 다시 대입하지 않은 것은 감점하지 않는다.",
        ['replace', '범주형'], chk="s = pd.Series(['yes', 'no']).replace({'no': 0, 'yes': 1})\nprint(s.tolist())", pre=IMP)
    b.E("보험료를 예측하는 선형회귀 모델의 예측값 중에 −596.89 처럼 음수가 나왔다. 보험료는 음수가 될 수 없는데도 이런 값이 나오는 이유를 선형회귀 모델의 특징과 관련지어 설명하시오.",
        "선형회귀 모델은 입력에 계수를 곱하고 절편을 더한 일차식(직선·평면)으로 값을 예측한다. 이 식의 결과에는 범위 제한이 없어서 입력값에 따라 0보다 작은 값도 나올 수 있다. 모델은 보험료가 0 이상이어야 한다는 사실을 알지 못한다.",
        "필수 요소: 선형회귀는 일차식(직선, 계수×입력+절편)으로 예측하며 그 출력 범위에 제한이 없다는 취지. '데이터가 잘못되어서', '학습이 덜 되어서'만 쓰면 오답.",
        ['선형회귀', 'predict'], chk="print(bool((linear_model.predict(X_test) < 0).any()))")
    return b
