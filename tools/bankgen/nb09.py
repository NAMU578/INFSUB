"""기말.9 인공신경망을 이용한 MNIST 손글씨 분류
텐서플로를 실행할 수 없는 환경이라, 숫자 계산은 넘파이·산술로 검증하고
실행 결과는 노트북에 저장된 출력을 근거(ref)로 둔다."""
from lib import Bank

SRC = '기말.9.인공신경망을이용한MNIST손글씨분류'
NP = "import numpy as np\nimport math\n"
PRE_X = NP + "X_train = np.zeros((60000, 28, 28), dtype=np.uint8)\nX_test = np.zeros((10000, 28, 28), dtype=np.uint8)\n"
MODEL1 = ("model = Sequential()\nmodel.add(Dense(100, activation='relu', input_shape=(784, ), name='hidden'))\n"
          "model.add(Dense(10, activation='softmax', name='output'))")
MODEL2 = ("model = Sequential()\nmodel.add(Dense(200, activation='relu', input_shape=(784, ), name='hidden1'))\n"
          "model.add(Dense(100, activation='relu', name='hidden2'))\nmodel.add(Dense(10, activation='softmax', name='output'))")
COMPILE = "model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])"
FIT = "model.fit(X_train, y_train, epochs=100, batch_size=128, verbose=2)"
MN = '(MNIST 는 28×28 크기의 손글씨 숫자 이미지로, 훈련 데이터 60000장과 테스트 데이터 10000장이다)'


def build():
    b = Bank('09', SRC, NP)

    # ── 개념 분류 ──
    b.C(stem='`keras.datasets.mnist.load_data()` 로 불러온 MNIST 데이터에 대한 설명으로 옳은 것만 <보기>에서 모두 고른 것은?',
        show="(X_train, y_train), (X_test, y_test) = mnist.load_data()",
        items=[("`X_train.shape` 은 `(60000, 28, 28)` 이다.", True),
               ("`y_train.shape` 은 `(60000, 10)` 이다.", False),
               ("불러온 직후의 픽셀값은 0 부터 255 사이의 정수이다.", True)],
        why="훈련 이미지는 28×28 크기 60000장이고 정답은 숫자 하나씩이라 `y_train.shape` 은 `(60000,)` 입니다. `(60000, 10)` 은 원-핫 인코딩을 한 **뒤**의 모양입니다. 픽셀값은 0~255 이고 255 로 나눠 정규화합니다.",
        tags=['MNIST', 'shape'], ref='셀 [6], [8] 데이터 탐색 출력')
    b.C(stem=f'다음 전처리 코드에 대한 설명으로 옳은 것만 <보기>에서 모두 고른 것은? {MN}',
        show="X_train = X_train.reshape(X_train.shape[0], 784)\nX_train = X_train / 255.0\ny_train = to_categorical(y_train, 10)",
        items=[("`X_train.shape` 은 `(60000, 784)` 가 된다.", True),
               ("`X_train` 의 값은 0 과 1 사이가 된다.", True),
               ("정답 5 는 `[0, 0, 0, 0, 1, 0, 0, 0, 0, 0]` 으로 바뀐다.", False)],
        why="원-핫 인코딩에서 1 의 위치는 **인덱스**입니다. 정답 5 는 0번부터 세어 5번 자리(여섯 번째 칸)가 1 인 `[0, 0, 0, 0, 0, 1, 0, 0, 0, 0]` 입니다.",
        tags=['reshape', '정규화', '원-핫 인코딩'], ref='셀 [12]~[16] 데이터 전처리 출력')
    b.C(stem='다음 인공신경망 모델에 대한 설명으로 옳은 것만 <보기>에서 모두 고른 것은?', show=MODEL1,
        items=[("입력은 28×28 의 2차원 이미지를 그대로 받는다.", False),
               ("은닉층의 노드는 100개이다.", True),
               ("출력층의 활성화 함수는 소프트맥스이다.", True)],
        why="`input_shape=(784, )` 이므로 784개의 값을 한 줄로 펼친 1차원 입력을 받습니다. 은닉층은 노드 100개에 렐루, 출력층은 노드 10개에 소프트맥스를 씁니다.",
        tags=['Sequential', 'Dense', '활성화 함수'], ref='셀 [19] 인공신경망 구조 만들기')
    b.C(stem='다음 모델의 `model.summary()` 에 대한 설명으로 옳은 것만 <보기>에서 모두 고른 것은?', show=MODEL1 + "\nmodel.summary()", code="h = 784 * 100 + 100\no = 100 * 10 + 10",
        items=[("`hidden` 층의 파라미터는 78,500개이다.", "h == 78500"),
               ("`output` 층의 파라미터는 1,000개이다.", "o == 1000"),
               ("전체 파라미터는 79,510개이다.", "h + o == 79510")],
        why="Dense 층의 파라미터 수는 (입력 수 × 노드 수) + 노드 수(편향)입니다. 은닉층 784 × 100 + 100 = 78,500, 출력층 100 × 10 + 10 = 1,010 으로 편향 10개를 빠뜨리면 안 됩니다.",
        tags=['파라미터 수', 'summary'])
    b.C(stem='다음 코드의 각 인자에 대한 설명으로 옳은 것만 <보기>에서 모두 고른 것은?', show=COMPILE,
        items=[("`loss` 는 예측과 정답의 차이를 계산하는 손실함수를 정한다.", True),
               ("`metrics=['accuracy']` 는 손실을 줄이도록 가중치를 고치는 방법을 정한다.", False),
               ("`optimizer` 는 최적화 함수를 정한다.", True)],
        why="손실을 줄이도록 가중치와 편향을 고치는 방법은 `optimizer`(최적화 함수)가 정합니다. `metrics` 는 학습 과정에서 함께 살펴볼 평가지표(여기서는 정확도)입니다.",
        tags=['compile', '손실함수', '최적화'], ref='셀 [22] 학습 과정 설정')
    b.C(stem=f'다음 코드에 대한 설명으로 옳은 것만 <보기>에서 모두 고른 것은? {MN}', show=FIT, code="steps = math.ceil(60000 / 128)",
        items=[("훈련 데이터 전체를 100번 반복해서 학습한다.", True),
               ("한 에포크 동안 가중치를 469번 갱신한다.", "steps == 469"),
               ("`batch_size` 를 256 으로 바꾸면 한 에포크의 갱신 횟수가 늘어난다.", "math.ceil(60000 / 256) > steps")],
        why="`epochs=100` 은 전체 데이터를 100번 반복한다는 뜻입니다. 128개씩 묶으면 60000 ÷ 128 = 468.75 를 올림한 469번 갱신합니다. 묶음을 256개로 키우면 갱신 횟수는 235번으로 **줄어듭니다**.",
        tags=['epochs', 'batch_size'])
    b.C(stem='학습을 마친 모델의 출력이 다음과 같다. 설명으로 옳은 것만 <보기>에서 모두 고른 것은? (훈련 마지막 에포크의 accuracy 는 1.0000 이었다.)',
        show="print(model.evaluate(X_test, y_test))\n# [0.13044600188732147, 0.9807000160217285]",
        items=[("첫 번째 값은 손실, 두 번째 값은 정확도이다.", True),
               ("정확도만 꺼내려면 `model.evaluate(X_test, y_test)[1]` 을 쓴다.", True),
               ("테스트 데이터의 정확도가 훈련 데이터의 정확도보다 높다.", False)],
        why="`evaluate` 는 [손실, 정확도] 를 돌려줍니다. 훈련 정확도는 1.0000 인데 테스트 정확도는 0.9807 로 더 낮습니다. 훈련 데이터에 더 잘 맞춰진 과대적합의 모습입니다.",
        tags=['evaluate', '과대적합'], ref='셀 [23], [25] 학습 및 평가 출력')
    b.C(stem='은닉층 1개(Dense 100, 100 에포크) 모델의 테스트 정확도는 0.9807, 은닉층 2개(Dense 200, Dense 100, 200 에포크) 모델은 0.9821 이었다. 설명으로 옳은 것만 <보기>에서 모두 고른 것은?',
        code="p2 = 784 * 200 + 200 + 200 * 100 + 100 + 100 * 10 + 10", show=MODEL2,
        items=[("은닉층 2개 모델의 전체 파라미터는 178,110개이다.", "p2 == 178110"),
               ("두 모델의 차이는 테스트 이미지 10000장 중 14장을 더 맞힌 정도이다.", "round((0.9821 - 0.9807) * 10000) == 14"),
               ("은닉층을 늘리면 정확도는 항상 크게 오른다.", False)],
        why="784 × 200 + 200 = 157,000, 200 × 100 + 100 = 20,100, 100 × 10 + 10 = 1,010 을 더하면 178,110 입니다. 파라미터와 학습 시간은 두 배 넘게 늘었지만 정확도 차이는 0.0014(14장)에 그칩니다.",
        tags=['은닉층', '파라미터 수', '성능 비교'])
    b.C(stem='활성화 함수에 대한 설명으로 옳은 것만 <보기>에서 모두 고른 것은?', code="relu = np.maximum(0, np.array([-3.0, 0.0, 2.0]))",
        show="model.add(Dense(100, activation='relu', input_shape=(784, )))\nmodel.add(Dense(10, activation='softmax'))",
        items=[("렐루(ReLU)는 입력이 0 이하면 0, 양수면 그대로 내보낸다.", "relu.tolist() == [0.0, 0.0, 2.0]"),
               ("이 모델은 은닉층에 소프트맥스, 출력층에 렐루를 썼다.", False),
               ("소프트맥스의 출력 10개를 모두 더하면 1 이다.", True)],
        why="렐루는 max(0, x) 입니다. 이 모델은 은닉층에 렐루, 출력층에 소프트맥스를 썼습니다. 소프트맥스는 10개 숫자 각각일 확률을 내고 그 합은 1 입니다.",
        tags=['ReLU', '소프트맥스'])

    # ── 빈칸 ──
    b.B("X_train = X_train.㉠(X_train.shape[0], ㉡)\nprint(X_train.shape)", ('reshape', '784'), [('reshape', '28'), ('resize', '784'), ('reshape', '10'), ('flatten', '784')], pre=PRE_X,
        stem='`X_train` 의 shape 은 `(60000, 28, 28)` 이다. ㉠, ㉡에 들어갈 것으로 알맞은 것은?',
        why="28 × 28 = 784 이므로 이미지 한 장을 784개의 값이 한 줄로 늘어선 1차원으로 바꿉니다. 모양을 바꾸는 메서드는 `reshape` 입니다.", tags=['reshape'])
    b.B("X_train = X_train / ㉠\ny_train = to_categorical(y_train, ㉡)\nprint(X_train.max(), y_train[0])", ('255.0', '10'), [('255.0', '5'), ('28.0', '10'), ('784.0', '10'), ('255.0', '9')],
        stem='픽셀값(0~255)을 0~1 로 정규화하고 정답(0~9)을 원-핫 인코딩한다. 첫 번째 정답은 5 이다. ㉠, ㉡에 들어갈 것으로 알맞은 것은?',
        exec_=False, result="1.0 [0. 0. 0. 0. 0. 1. 0. 0. 0. 0.]",
        why="픽셀의 최댓값 255 로 나누면 0~1 이 되고, 숫자가 0~9 의 10종류이므로 범주 수는 10 입니다.", tags=['정규화', '원-핫 인코딩'])
    b.B("model = Sequential()\nmodel.add(Dense(100, activation='㉠', input_shape=(784, ), name='hidden'))\nmodel.add(Dense(10, activation='㉡', name='output'))",
        ('relu', 'softmax'), [('softmax', 'relu'), ('relu', 'relu'), ('sigmoid', 'relu'), ('softmax', 'softmax')], exec_=False, result=False,
        stem='은닉층에는 렐루 함수를, 출력층에는 10개 숫자 각각의 확률을 내는 함수를 쓴다. ㉠, ㉡에 들어갈 것으로 알맞은 것은?',
        why="은닉층의 활성화 함수는 `relu`, 다중 분류 출력층의 활성화 함수는 합이 1 인 확률을 내는 `softmax` 입니다.", tags=['활성화 함수'])
    b.B("model.compile(loss='㉠',\n              optimizer='adam',\n              metrics=['㉡'])", ('categorical_crossentropy', 'accuracy'),
        [('accuracy', 'categorical_crossentropy'), ('categorical_crossentropy', 'adam'), ('relu', 'accuracy'), ('softmax', 'accuracy')], exec_=False, result=False,
        stem='정답을 원-핫 인코딩한 다중 분류 모델의 학습 과정을 설정한다. 평가지표는 정확도이다. ㉠, ㉡에 들어갈 것으로 알맞은 것은?',
        why="원-핫 인코딩한 다중 분류의 손실함수는 `categorical_crossentropy`, 정확도 평가지표는 `accuracy` 입니다. `relu`, `softmax` 는 활성화 함수이고 `adam` 은 최적화 함수입니다.", tags=['compile'])
    b.B("model.fit(X_train, y_train,\n          ㉠ = 100,\n          ㉡ = 128,\n          verbose = 2)", ('epochs', 'batch_size'), [('batch_size', 'epochs'), ('epoch', 'batch'), ('max_iter', 'batch_size'), ('epochs', 'steps')],
        exec_=False, result="Epoch 1/100\n469/469 - 3s - 7ms/step - accuracy: 0.8974 - loss: 0.3735\n...",
        stem='모든 데이터를 100번 반복하고 128개씩 묶어서 학습한다. ㉠, ㉡에 들어갈 것으로 알맞은 것은?',
        why="반복 횟수는 `epochs`, 한 번에 묶어 학습하는 샘플 수는 `batch_size` 입니다. 60000 ÷ 128 을 올림한 469 가 출력에 보입니다.", tags=['fit', 'epochs', 'batch_size'])
    b.B("from tensorflow.keras.㉠ import Sequential\nfrom tensorflow.keras.㉡ import Dense", ('models', 'layers'), [('layers', 'models'), ('models', 'models'), ('utils', 'layers'), ('datasets', 'layers')],
        exec_=False, result=False,
        why="모델 클래스 `Sequential` 은 `keras.models` 에, 층을 만드는 클래스 `Dense` 는 `keras.layers` 에 있습니다.", tags=['import'])
    b.B("print(f'정확도: {model.㉠(X_test, y_test)[㉡]: .4}')", ('evaluate', '1'), [('evaluate', '0'), ('score', '1'), ('predict', '1'), ('fit', '1')], exec_=False, result="정확도:  0.9807",
        stem='테스트 데이터로 평가한 결과는 `[0.1304, 0.9807]` 이다. ㉠, ㉡에 들어갈 것으로 알맞은 것은?',
        why="케라스 모델의 평가는 `evaluate` 이고 [손실, 정확도] 를 돌려주므로 정확도는 인덱스 1 입니다.", tags=['evaluate'])

    # ── 경계값 ──
    b.D("print(math.ceil(60000 / 128), math.ceil(10000 / 32))", ['468 312', '469 312', '468 313', '128 32'],
        stem='학습 출력의 `469/469` 는 훈련 데이터 60000개를 128개씩, 평가 출력의 `313/313` 은 테스트 데이터 10000개를 32개씩 묶어 처리한 횟수이다. `math.ceil` 은 올림 함수이다. 다음 코드를 실행했을 때 출력되는 것은?',
        why="60000 ÷ 128 = 468.75, 10000 ÷ 32 = 312.5 입니다. 마지막에 남는 샘플도 한 묶음으로 처리하므로 올림해서 469 와 313 입니다.", tags=['batch_size', '올림'])
    b.D("print(to_categorical(3, 5))", ['[0. 0. 1. 0. 0.]', '[0. 0. 0. 0. 1.]', '[1. 1. 1. 0. 0.]', '[3. 0. 0. 0. 0.]'], ans='[0. 0. 0. 1. 0.]', chk="print(np.eye(5)[3])",
        why="범주가 5개(0~4)이므로 길이 5인 배열이 되고, 인덱스 3 의 자리(네 번째 칸)만 1 입니다.", tags=['원-핫 인코딩'])
    b.D("X = np.zeros((100, 28, 28))\nprint(X.reshape(100, 784).shape, X.size)", ['(100, 784) 784', '(100, 28) 78400', '(784, 100) 78400', '(100, 784) 2800'],
        why="모양만 바뀌고 전체 원소 수는 100 × 28 × 28 = 78400 으로 같습니다. 28 × 28 = 784 가 한 줄이 됩니다.", tags=['reshape'])
    b.D("model = Sequential()\nmodel.add(Dense(50, activation='relu', input_shape=(20, )))\nmodel.add(Dense(3, activation='softmax'))\nmodel.summary()", ['1000 150', '1050 150', '1000 153', '70 53'],
        ans='1050 153', chk="print(20 * 50 + 50, 50 * 3 + 3)", stem='다음 모델의 `model.summary()` 에서 두 층의 Param # 을 차례로 쓴 것은?',
        why="첫 층은 20 × 50 + 50 = 1050, 둘째 층은 50 × 3 + 3 = 153 입니다. 가중치에 노드 수만큼의 편향을 더합니다.", tags=['파라미터 수'])
    b.D("print(0 / 255.0, 255 / 255.0, 51 / 255.0)", ['0 1 0.2', '0.0 255.0 51.0', '0.0 1.0 0.5', '0.0 0.1 0.02'],
        why="픽셀값을 255.0 으로 나누면 가장 어두운 0 은 0.0, 가장 밝은 255 는 1.0 이 됩니다. 51 은 0.2 입니다.", tags=['정규화'])
    b.D("x = np.array([-2.0, 0.0, 3.0])\nprint(np.maximum(0, x))", ['[-2. 0. 3.]', '[2. 0. 3.]', '[0. 1. 1.]', '[3. 3. 3.]'], ans=None,
        stem='렐루(ReLU) 함수는 `max(0, x)` 이다. 넘파이로 계산한 다음 코드를 실행했을 때 출력되는 것은?',
        why="음수는 0 으로 바뀌고, 0 과 양수는 그대로입니다.", tags=['ReLU'])

    # ── 상태 예측 ──
    b.R("(X_train, y_train), (X_test, y_test) = mnist.load_data()\nprint(X_train.shape, y_train.shape)", ['(60000, 784) (60000,)', '(60000, 28, 28) (60000, 10)', '(10000, 28, 28) (10000,)', '(28, 28, 60000) (60000,)'],
        ans='(60000, 28, 28) (60000,)', ref='셀 [6] 데이터 탐색 출력', stem=f'다음 코드를 실행했을 때 출력되는 것은? {MN}',
        why="불러온 직후의 이미지는 28×28 의 2차원 그대로이고, 정답은 이미지마다 숫자 하나라 1차원입니다.", tags=['MNIST', 'shape'])
    b.R("X_train = X_train.reshape(X_train.shape[0], 784)\nX_test = X_test.reshape(X_test.shape[0], 784)\nprint(X_train.shape, X_test.shape)", ['(60000, 28, 28) (10000, 28, 28)', '(784, 60000) (784, 10000)', '(60000, 784) (60000, 784)', '(47040000,) (7840000,)'],
        pre=PRE_X, stem=f'다음 코드를 실행했을 때 출력되는 것은? {MN}',
        why="`X_train.shape[0]` 은 60000, `X_test.shape[0]` 은 10000 입니다. 이미지 한 장이 784개의 값으로 펼쳐집니다.", tags=['reshape'])
    b.R("y_train = to_categorical(y_train, 10)\nprint(y_train[0])", ['[0. 0. 0. 0. 1. 0. 0. 0. 0. 0.]', '[5. 0. 0. 0. 0. 0. 0. 0. 0. 0.]', '[0. 0. 0. 0. 0. 0. 1. 0. 0. 0.]', '5'],
        ans='[0. 0. 0. 0. 0. 1. 0. 0. 0. 0.]', chk="print(np.eye(10)[5])", stem='`y_train` 의 첫 번째 값은 5 이다. 다음 코드를 실행했을 때 출력되는 것은?',
        why="인덱스 5 의 자리(여섯 번째 칸)만 1 입니다. 0번부터 센다는 점에 주의합니다.", tags=['원-핫 인코딩'])
    b.R(MODEL1 + "\nmodel.summary()", ['78,500', '79,400', '7,940', '80,510'], ans='79,510', chk="print(f'{784 * 100 + 100 + 100 * 10 + 10:,}')",
        stem='다음 코드를 실행했을 때 출력되는 요약의 Total params 값은?',
        why="은닉층 784 × 100 + 100 = 78,500 과 출력층 100 × 10 + 10 = 1,010 을 더한 79,510 입니다.", tags=['파라미터 수'])
    b.R(MODEL2 + "\nmodel.summary()", ['177,800', '178,000', '79,510', '157,000'], ans='178,110', chk="print(f'{784 * 200 + 200 + 200 * 100 + 100 + 100 * 10 + 10:,}')",
        stem='다음 코드를 실행했을 때 출력되는 요약의 Total params 값은?',
        why="784 × 200 + 200 = 157,000, 200 × 100 + 100 = 20,100, 100 × 10 + 10 = 1,010 을 모두 더한 178,110 입니다.", tags=['파라미터 수', '은닉층'])
    b.R("result = [0.13044600188732147, 0.9807000160217285]\nprint(f'{result[1]:.4f}', round(result[0], 2))", ['0.1304 0.98', '0.9807 0.1304', '0.98 0.13', '0.9807000160217285 0.13'],
        stem='`result` 는 `model.evaluate(X_test, y_test)` 가 돌려준 값이다. 다음 코드를 실행했을 때 출력되는 것은?',
        why="`result[1]` 은 정확도이고 소수 넷째 자리까지 0.9807, `result[0]` 은 손실이고 둘째 자리까지 반올림하면 0.13 입니다.", tags=['evaluate', '출력 서식'])
    b.R("out = np.array([0.01, 0.02, 0.9, 0.07])\nprint(np.argmax(out), round(float(out.sum()), 2))", ['0.9 1.0', '3 1.0', '2 0.9', '2 4.0'],
        stem='`out` 은 4종류를 분류하는 모델의 소프트맥스 출력이다. 다음 코드를 실행했을 때 출력되는 것은?',
        why="`np.argmax` 는 가장 큰 값의 **인덱스**(2)를 돌려줍니다. 소프트맥스 출력의 합은 1 입니다.", tags=['argmax', '소프트맥스'])

    # ── 대조 ──
    b.X("# 방법1\n" + MODEL1 + "\nmodel.summary()\n\n# 방법2\n" + MODEL2 + "\nmodel.summary()", [('78,500', '157,000'), ('79,510', '159,020'), ('79,400', '177,800'), ('1,010', '1,010')],
        ans=('79,510', '178,110'), chk="print(f'{784 * 100 + 100 + 100 * 10 + 10:,}')\nprint(f'{784 * 200 + 200 + 200 * 100 + 100 + 100 * 10 + 10:,}')",
        stem='은닉층의 구성만 다른 두 모델이다. 각 요약의 Total params 값 ㉠, ㉡으로 알맞은 것은?',
        why="방법1은 78,500 + 1,010 = 79,510, 방법2는 157,000 + 20,100 + 1,010 = 178,110 입니다. 층과 노드가 늘면 파라미터가 두 배 넘게 늘어납니다.", tags=['파라미터 수', '은닉층'])
    b.X("# 방법1\nprint(to_categorical(2, 4))\n\n# 방법2\nprint(to_categorical(2, 3))", [('[0. 1. 0. 0.]', '[0. 1. 0.]'), ('[0. 0. 1. 0.]', '[0. 0. 1. 0.]'), ('[0. 0. 2. 0.]', '[0. 0. 2.]'), ('[1. 1. 0. 0.]', '[1. 1. 0.]')],
        ans=('[0. 0. 1. 0.]', '[0. 0. 1.]'), chk="print(np.eye(4)[2])\nprint(np.eye(3)[2])",
        why="두 번째 인자는 범주의 개수라서 배열의 길이가 됩니다. 값 2 는 두 경우 모두 인덱스 2 의 자리가 1 입니다.", tags=['원-핫 인코딩'])
    b.X("# 방법1: batch_size=128\nprint(math.ceil(60000 / 128))\n\n# 방법2: batch_size=32\nprint(math.ceil(60000 / 32))", [('468', '1875'), ('469', '469'), ('128', '32'), ('1875', '469')],
        stem='훈련 데이터 60000개로 학습할 때 한 에포크의 갱신 횟수를 계산한다. ㉠, ㉡에 출력되는 값으로 알맞은 것은?',
        why="묶음이 작을수록 한 에포크에 더 여러 번 갱신합니다. 128개씩이면 469번, 32개씩이면 1875번입니다.", tags=['batch_size'])
    b.X("X = np.zeros((2, 28, 28))\n# 방법1\nprint(X.reshape(2, 784).shape)\n\n# 방법2\nprint(X.reshape(-1, 28).shape)", [('(2, 784)', '(2, 28)'), ('(784, 2)', '(56, 28)'), ('(2, 784)', '(28, 56)'), ('(1568,)', '(56, 28)')],
        why="방법1은 이미지마다 784개 값을 한 줄로 펼칩니다. 방법2는 열을 28로 고정하고 행을 자동 계산해 1568 ÷ 28 = 56 행이 됩니다.", tags=['reshape'])

    # ── 조건 매핑 ──
    b.S(["shape 이 `(60000, 28, 28)` 인 `X_train` 을 이미지마다 1차원으로 펼친다.", "결과의 shape 은 `(60000, 784)` 이다."], "X_train.reshape(X_train.shape[0], 784)",
        ["X_train.reshape(784, X_train.shape[0])", "X_train.reshape(28, 28)", "X_train.reshape(X_train.shape[0], 28)", "X_train.reshape(784)"],
        code="X_train = ____", chk="print(X_train.shape)", pre=PRE_X,
        why="첫 번째 차원(이미지 수)은 그대로 두고 28 × 28 을 784 로 합칩니다.", tags=['reshape'])
    b.S(["은닉층을 만든다.", "노드는 100개, 활성화 함수는 렐루이다.", "입력은 784개의 값이다."], "Dense(100, activation='relu', input_shape=(784, ))",
        ["Dense(784, activation='relu', input_shape=(100, ))", "Dense(100, activation='softmax', input_shape=(784, ))", "Dense(10, activation='relu', input_shape=(784, ))", "Dense(100, activation='relu', input_shape=(28, 28))"],
        code="model.add(____)", why="`Dense` 의 첫 인자가 노드 수이고, `input_shape` 에 입력의 모양을 튜플로 줍니다.", tags=['Dense'])
    b.S(["0~9 의 10개 숫자를 분류하는 출력층을 만든다.", "각 숫자일 확률(합이 1)을 출력한다."], "Dense(10, activation='softmax')",
        ["Dense(1, activation='softmax')", "Dense(10, activation='relu')", "Dense(100, activation='softmax')", "Dense(9, activation='softmax')"],
        code="model.add(____)", why="출력층의 노드 수는 분류할 범주의 수(10)와 같고, 합이 1 인 확률은 소프트맥스가 만듭니다.", tags=['출력층', '소프트맥스'])
    b.S(["0~9 의 정수로 된 정답 `y_train` 을 원-핫 인코딩한다."], "to_categorical(y_train, 10)", ["to_categorical(y_train, 9)", "to_categorical(X_train, 10)", "y_train / 10", "y_train.reshape(-1, 10)"],
        code="y_train = ____", why="`to_categorical(정답, 범주 수)` 입니다. 0~9 는 10종류이므로 범주 수는 10 입니다.", tags=['원-핫 인코딩'])
    b.S(["원-핫 인코딩한 정답으로 다중 분류 모델을 학습시킬 준비를 한다.", "최적화 함수는 adam, 평가지표는 정확도이다."],
        "model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])",
        ["model.compile(loss='accuracy', optimizer='adam', metrics=['categorical_crossentropy'])", "model.fit(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])",
         "model.compile(loss='adam', optimizer='categorical_crossentropy', metrics=['accuracy'])", "model.compile(loss='categorical_crossentropy', optimizer='accuracy', metrics=['adam'])"],
        code="____", why="학습 과정 설정은 `compile` 이고 손실함수는 `loss`, 최적화 함수는 `optimizer`, 평가지표는 `metrics` 에 넣습니다.", tags=['compile'])

    # ── 서답형 ──
    b.W("입력이 784개이고 노드가 100개인 Dense 은닉층의 파라미터(가중치 + 편향) 수를 구하시오.", "78500", accept=['78,500', '78500개', '78,500개'], chk="print(784 * 100 + 100)",
        why="가중치 784 × 100 = 78,400 개에 편향 100개를 더해 78,500 개입니다.", tags=['파라미터 수'])
    b.W("입력 784개 → Dense(200) → Dense(100) → Dense(10) 으로 이루어진 모델의 전체 파라미터 수를 구하시오.", "178110", accept=['178,110', '178110개', '178,110개'],
        chk="print(784 * 200 + 200 + 200 * 100 + 100 + 100 * 10 + 10)", why="157,000 + 20,100 + 1,010 = 178,110 입니다.", tags=['파라미터 수'])
    b.W("0~9 를 분류하는 문제에서 정답 3 을 원-핫 인코딩한 결과를 쓰시오. (예: [0, 1, 0, …] 형식, 길이 10)", "[0, 0, 0, 1, 0, 0, 0, 0, 0, 0]",
        accept=['0001000000', '[0. 0. 0. 1. 0. 0. 0. 0. 0. 0.]', '0 0 0 1 0 0 0 0 0 0', '0,0,0,1,0,0,0,0,0,0', '[0 0 0 1 0 0 0 0 0 0]'],
        chk="print(np.eye(10, dtype=int)[3].tolist())", why="인덱스 3 의 자리(네 번째 칸)만 1 이고 나머지는 0 입니다.", tags=['원-핫 인코딩'])
    b.W("훈련 데이터 60000개를 `batch_size=100` 으로 학습하면 한 에포크 동안 가중치를 몇 번 갱신하는지 쓰시오.", "600", accept=['600번', '600회'], chk="print(math.ceil(60000 / 100))",
        why="60000 ÷ 100 = 600 번입니다.", tags=['batch_size'])
    b.W("빈칸 ㉠ 에 들어갈 함수 이름을 쓰시오. (정답을 원-핫 인코딩한다.)", "to_categorical", code="from tensorflow.keras.utils import ㉠\ny_train = ㉠(y_train, 10)\nprint(y_train[0])", exec_=False, result="[0. 0. 0. 0. 0. 1. 0. 0. 0. 0.]",
        why="케라스의 `to_categorical(정답, 범주 수)` 가 원-핫 인코딩을 해 줍니다.", tags=['원-핫 인코딩'])
    b.W("입력이 0 이하이면 0 을, 양수이면 입력을 그대로 출력하는 활성화 함수의 이름을 쓰시오. (이 노트북의 은닉층에서 사용)", "relu", accept=['ReLU', '렐루', '렐루 함수', 'relu 함수', 'ReLU 함수', '렐루(ReLU)'],
        chk="print(np.maximum(0, np.array([-1.0, 2.0])).tolist())", eq=False, why="렐루(ReLU)는 max(0, x) 입니다.", tags=['ReLU'])
    b.W("노드가 500개인 입력층, 200개인 첫 번째 은닉층, 50개인 두 번째 은닉층이 차례로 연결되어 있다. 두 은닉층의 가중치와 편향을 모두 더한 파라미터 수를 구하시오.", "110250",
        accept=['110,250', '110250개', '110,250개'], chk="print(500 * 200 + 200 + 200 * 50 + 50)",
        why="첫 은닉층: 가중치 500 × 200 = 100,000, 편향 200. 둘째 은닉층: 가중치 200 × 50 = 10,000, 편향 50. 합은 110,250 입니다.", tags=['파라미터 수'])
    b.W("28×28 크기의 이미지 한 장을 1차원으로 펼치면 값이 몇 개인지 쓰시오.", "784", accept=['784개'], chk="print(28 * 28)", why="28 × 28 = 784 입니다.", tags=['reshape'])

    # ── 서술형 ──
    b.E("MNIST 손글씨 이미지를 Dense 층으로 이루어진 인공신경망에 넣기 전에 한 전처리 세 가지를 쓰고, 각각 왜 필요한지 설명하시오.",
        "① 1차원 배열로 변환: 28×28 의 2차원 이미지를 784개의 값으로 펼친다. Dense 층은 1차원 입력을 받기 때문이다.\n② 정규화: 0~255 의 픽셀값을 255 로 나눠 0~1 사이로 만든다. 값의 범위를 줄여 학습이 잘되게 하기 위해서이다.\n③ 원-핫 인코딩: 정답 0~9 를 길이 10 의 배열로 바꾼다. 0~9 는 크기를 비교하는 수가 아니라 서로 다른 범주이고, 출력층 노드 10개와 형태를 맞추기 위해서이다.",
        "필수 요소(모두 있어야 정답): (1) 1차원 변환(reshape, 784)과 그 이유. (2) 정규화(255 로 나눔, 0~1)와 그 이유. (3) 원-핫 인코딩(to_categorical)과 그 이유. 세 가지 이름이 모두 나오고 이유가 두 가지 이상 타당하면 정답.",
        ['전처리'])
    b.E("입력 784개, 은닉층 Dense(100), 출력층 Dense(10) 으로 이루어진 모델의 각 층의 파라미터 수와 전체 파라미터 수를 계산 과정과 함께 쓰시오.",
        "은닉층: 가중치 784 × 100 = 78,400 개 + 편향 100개 = 78,500 개\n출력층: 가중치 100 × 10 = 1,000 개 + 편향 10개 = 1,010 개\n전체: 78,500 + 1,010 = 79,510 개",
        "필수 요소(모두 있어야 정답): (1) 은닉층 78,500. (2) 출력층 1,010. (3) 전체 79,510. 편향을 빠뜨려 78,400 / 1,000 / 79,400 으로 쓰면 오답. 계산식이 드러나야 한다.",
        ['파라미터 수'], chk="print(784 * 100 + 100, 100 * 10 + 10, 784 * 100 + 100 + 100 * 10 + 10)")
    b.E("은닉층이 1개(노드 100, 100 에포크)인 모델의 테스트 정확도는 0.9807, 은닉층이 2개(노드 200, 100, 200 에포크)인 모델은 0.9821 이었다. 이 차이를 유의미한 성능 향상이라고 볼 수 있는지 자신의 판단과 근거를 쓰시오.",
        "유의미한 차이라고 보기 어렵다. 차이는 0.0014 로 테스트 이미지 10000장 중 14장에 해당하는 작은 값이다. 반면 파라미터 수는 79,510 개에서 178,110 개로 두 배 넘게 늘었고 에포크도 두 배라 학습 시간이 훨씬 많이 든다. 또 신경망은 가중치의 초기값이 무작위라서 실행할 때마다 결과가 조금씩 달라지는데 그 범위 안의 차이일 수 있다.",
        "판단(유의미하다/아니다)과 근거가 함께 있어야 한다. 근거로 인정: 차이가 0.0014(14장)로 작다 / 파라미터·학습 시간 증가에 비해 이득이 작다 / 실행마다 달라질 수 있는 범위다 중 하나 이상. '유의미하다'고 답해도 정확도가 실제로 올랐다는 점과 그 한계를 근거와 함께 논리적으로 쓰면 정답. 근거 없이 판단만 쓰면 오답.",
        ['성능 비교', '은닉층'])
    b.E("학습 마지막 에포크에서 훈련 데이터의 정확도는 1.0000 이었는데, `model.evaluate(X_test, y_test)` 로 구한 테스트 데이터의 정확도는 0.9807 이었다. 두 값의 차이가 의미하는 것을 설명하시오.",
        "모델이 훈련 데이터는 완벽하게 맞히지만 학습에 쓰지 않은 테스트 데이터는 그만큼 맞히지 못한다는 뜻이다. 훈련 데이터에 지나치게 맞춰진 과대적합 경향이 있다.",
        "필수 요소: 훈련 데이터에는 잘 맞지만 새(테스트) 데이터에는 덜 맞는다는 점과, 이것이 과대적합(훈련 데이터에 지나치게 맞춰짐)이라는 취지. '과대적합'이라는 용어가 없어도 뜻이 분명하면 정답.",
        ['과대적합', 'evaluate'])
    b.E("0~9 의 숫자를 분류할 때 정답을 원-핫 인코딩한다. 정답 7 을 원-핫 인코딩한 결과를 쓰고, 정답을 숫자 그대로 쓰지 않고 이렇게 바꾸는 이유를 설명하시오.",
        "[0, 0, 0, 0, 0, 0, 0, 1, 0, 0]\n0~9 는 크기나 순서를 비교하는 값이 아니라 서로 다른 범주를 구별하는 이름표이다. 출력층의 노드 10개가 각 숫자일 확률을 하나씩 내므로, 정답도 같은 길이 10 의 배열로 만들어 해당 숫자의 자리만 1 로 표시한다.",
        "필수 요소(모두 있어야 정답): (1) 인덱스 7 의 자리(여덟 번째)가 1 인 길이 10 의 배열. (2) 숫자가 범주(종류)를 나타내는 것이라는 점 또는 출력층 10개 노드(확률)와 형태를 맞춘다는 점 중 하나.",
        ['원-핫 인코딩'], chk="print(np.eye(10, dtype=int)[7].tolist())")
    b.E("`model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])` 에서 세 인자 `loss`, `optimizer`, `metrics` 가 각각 무엇을 정하는지 설명하시오.",
        "loss 는 손실함수로, 예측값과 정답의 차이(오차)를 계산하는 방법을 정한다. optimizer 는 최적화 함수로, 손실이 줄어들도록 가중치와 편향을 고쳐 나가는 방법을 정한다. metrics 는 평가지표로, 학습과 평가에서 성능을 확인할 기준(여기서는 정확도)을 정한다.",
        "필수 요소(모두 있어야 정답): (1) loss = 손실함수(예측과 정답의 차이 계산). (2) optimizer = 최적화(손실을 줄이도록 가중치를 갱신하는 방법). (3) metrics = 평가지표(정확도). 셋 중 둘의 설명이 서로 바뀌면 오답.",
        ['compile'])
    b.E("훈련 데이터 60000개를 `model.fit(X_train, y_train, epochs=100, batch_size=128)` 로 학습하면 출력에 `469/469` 가 나타난다. `epochs` 와 `batch_size` 의 뜻을 쓰고 469 가 어떻게 나온 값인지 설명하시오.",
        "epochs 는 전체 훈련 데이터를 몇 번 반복해서 학습할지(100번)이고, batch_size 는 한 번에 묶어서 학습하는 샘플 수(128개)이다. 60000 ÷ 128 = 468.75 이므로 한 에포크에 469 묶음(마지막 묶음은 남은 샘플)을 처리하고, 그 횟수가 469 이다.",
        "필수 요소(모두 있어야 정답): (1) epochs = 전체 데이터 반복 횟수. (2) batch_size = 한 번에 묶어 학습하는 샘플 수. (3) 60000 ÷ 128 을 올림해서 469 라는 계산.",
        ['epochs', 'batch_size'], chk="print(math.ceil(60000 / 128))")
    return b
