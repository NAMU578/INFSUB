"""기말.10 CNN을 이용한 패션 MNIST 분류
텐서플로를 실행할 수 없는 환경이라, 합성곱·풀링·파라미터 수는 넘파이와 산술로 검증하고
학습 결과는 노트북에 저장된 출력을 근거(ref)로 둔다."""
from lib import Bank

SRC = '기말.10.CNN을이용한패션MNIST분류'
EXTRA_SOURCE = ['CNN 확인 문제.pdf (출제 유형 참고, 문항은 신규 작성)']
PRE = '''
import numpy as np
import math
def conv(x, k):
    """패딩 없이(valid) 한 칸씩 이동하는 합성곱"""
    kh, kw = k.shape
    return np.array([[int((x[i:i + kh, j:j + kw] * k).sum()) for j in range(x.shape[1] - kw + 1)]
                     for i in range(x.shape[0] - kh + 1)])
def pool(x, s=2):
    """(s, s) 최대 풀링"""
    return x.reshape(x.shape[0] // s, s, x.shape[1] // s, s).max(axis=(1, 3))
'''


def arr(name, rows):
    pad = ' ' * (len(name) + 12)
    return f"{name} = np.array([" + (",\n" + pad).join(str(r) for r in rows) + "])"


XA = arr('x', [[1, 2, 0, 1], [0, 1, 3, 2], [2, 1, 0, 1], [1, 0, 2, 3]])
KA = arr('k', [[1, 0], [0, 1]])
XB = arr('x', [[1, 0, 2, 1], [0, 1, 1, 0], [2, 1, 0, 1], [1, 0, 1, 2]])
KB = arr('k', [[1, 0, 1], [0, 1, 0], [1, 0, 1]])
FC = arr('f', [[1, 3, 2, 0], [5, 2, 1, 4], [0, 1, 7, 2], [3, 6, 2, 8]])
FD = arr('g', [[4, 1, 0, 2], [3, 9, 5, 1], [2, 0, 6, 6], [1, 7, 3, 8]])
XE = arr('x', [[1, 0, 2, 1, 0], [2, 1, 0, 0, 3], [0, 3, 1, 2, 1], [1, 0, 0, 4, 2], [2, 2, 1, 0, 1]])
KE = arr('k', [[1, 1], [0, 1]])
XG = arr('x', [[2, 1, 0], [1, 3, 1], [0, 2, 4]])
KG = arr('k', [[1, 2], [0, 1]])
XH = arr('x', [[3, 1, 2, 0], [0, 2, 1, 4], [1, 5, 0, 2], [2, 0, 3, 1]])
KH = arr('k', [[0, 1], [1, 0]])

CONV1 = "model.add(keras.layers.Conv2D(32, kernel_size=3, activation='relu',\n                              padding='same', input_shape=(28,28,1)))"
CONV2 = "model.add(keras.layers.Conv2D(64, kernel_size=(3,3), activation='relu',\n                              padding='same'))"
MODEL = ("model = keras.Sequential()\n" + CONV1 + "\nmodel.add(keras.layers.MaxPooling2D(2))\n" + CONV2 + "\nmodel.add(keras.layers.MaxPooling2D(2))\n"
         "model.add(keras.layers.Flatten())\nmodel.add(keras.layers.Dense(100, activation='relu'))\nmodel.add(keras.layers.Dropout(0.4))\n"
         "model.add(keras.layers.Dense(10, activation='softmax'))")
VAL = "val_loss = [0.3184, 0.2785, 0.2464, 0.2437, 0.2363, 0.2301, 0.2335, 0.2285, 0.2434, 0.2440]"
LOG = ('\n검증 손실(val_loss)은 1~10 에포크 차례로 0.3184, 0.2785, 0.2464, 0.2437, 0.2363, 0.2301, 0.2335, 0.2285, 0.2434, 0.2440 이었고 '
       '훈련은 10번째 에포크에서 멈췄다.')
CV = '합성곱은 패딩 없이(valid) 커널을 한 칸씩 이동하며 계산한다.'
REF_SUM = '셀 [13] model.summary() 출력'
REF_LOG = '셀 [17], [20] 학습 기록과 검증 세트 평가 출력'


def build():
    b = Bank('10', SRC, PRE)

    # ── 개념 분류 ──
    b.C(stem='합성곱 신경망(CNN)에 대한 설명으로 옳은 것만 <보기>에서 모두 고른 것은?',
        items=[("이미지를 1차원으로 펼치지 않고 2차원 그대로 입력받는다.", True),
               ("풀링 층에는 학습할 가중치가 없다.", True),
               ("Flatten 층은 과대적합을 막기 위해 일부 값을 0 으로 만든다.", False)],
        why="일부 값을 무작위로 0 으로 만들어 과대적합을 막는 것은 **Dropout** 층입니다. Flatten 은 3차원 특성 맵을 1차원으로 펼쳐 Dense 층에 넣을 수 있게 합니다.",
        tags=['CNN', '풀링', 'Flatten', 'Dropout'], ref='셀 [8]~[11] 합성곱 신경망 만들기')
    b.C(stem='패션 MNIST 는 28×28 흑백 이미지로 훈련 데이터가 60000장이다. 다음 코드에 대한 설명으로 옳은 것만 <보기>에서 모두 고른 것은?',
        show="train_scaled = train_input.reshape(-1, 28, 28, 1) / 255.0\ntrain_scaled, val_scaled, train_target, val_target = train_test_split(\n    train_scaled, train_target, test_size=0.2, random_state=42)",
        code="n_val = int(60000 * 0.2)\nn_train = 60000 - n_val",
        items=[("나눈 뒤 `train_scaled` 는 48000장이다.", "n_train == 48000"),
               ("`val_scaled` 는 12000장의 검증 세트이다.", "n_val == 12000"),
               ("`reshape` 의 마지막 1 은 이미지의 장수를 뜻한다.", False)],
        why="마지막 1 은 **채널 수**(흑백이라 1)입니다. Conv2D 는 (높이, 너비, 채널) 입력을 받습니다. 60000장의 20%인 12000장이 검증 세트, 나머지 48000장이 훈련 세트입니다.",
        tags=['reshape', '검증 세트', '채널'])
    b.C(stem='다음 모델의 `model.summary()` 에 나오는 출력 크기에 대한 설명으로 옳은 것만 <보기>에서 모두 고른 것은?', show=MODEL, code="flat = 7 * 7 * 64",
        items=[("첫 번째 Conv2D 층의 출력은 `(28, 28, 32)` 이다.", True),
               ("두 번째 MaxPooling2D 층의 출력은 `(7, 7, 32)` 이다.", False),
               ("Flatten 층의 출력은 값 3136개이다.", "flat == 3136")],
        why="same 패딩이라 합성곱 뒤에도 가로세로는 그대로이고 깊이만 필터 수로 바뀝니다. 풀링은 가로세로를 절반으로 줄이고 깊이는 그대로 둡니다. 28 → 14 → 7 이고 두 번째 풀링 뒤는 `(7, 7, 64)`, 펼치면 7 × 7 × 64 = 3136 입니다.",
        tags=['출력 크기', 'summary'], ref=REF_SUM)
    b.C(stem='다음 모델의 파라미터 수에 대한 설명으로 옳은 것만 <보기>에서 모두 고른 것은?', show=MODEL, code="c1 = (3 * 3 * 1 + 1) * 32\nc2 = (3 * 3 * 32 + 1) * 64",
        items=[("첫 번째 Conv2D 층의 파라미터는 320개이다.", "c1 == 320"),
               ("두 번째 Conv2D 층의 파라미터는 18,496개이다.", "c2 == 18496"),
               ("MaxPooling2D 층의 파라미터 수는 필터 수와 같다.", False)],
        why="합성곱 층의 파라미터 수는 (커널 높이 × 커널 너비 × 입력 채널 수 + 1) × 필터 수입니다. (3×3×1+1)×32 = 320, (3×3×32+1)×64 = 18,496 입니다. 풀링 층은 파라미터가 0 입니다.",
        tags=['파라미터 수', 'Conv2D'])
    b.C(stem='패딩에 대한 설명으로 옳은 것만 <보기>에서 모두 고른 것은?', code="out = conv(np.zeros((5, 5)), np.zeros((3, 3))).shape",
        show="keras.layers.Conv2D(32, kernel_size=3, padding='same')",
        items=[("`padding='same'` 은 출력의 가로세로 크기가 입력과 같아지도록 둘레를 0 으로 채운다.", True),
               ("패딩을 쓰지 않고 (5, 5) 입력에 (3, 3) 커널을 한 칸씩 이동하면 출력도 (5, 5) 이다.", "out == (5, 5)"),
               ("`padding` 을 지정하지 않으면 패딩을 하지 않는다(밸리드 패딩).", True)],
        why="패딩이 없으면 출력 크기는 입력 − 커널 + 1 이라 5 − 3 + 1 = 3, 즉 (3, 3) 으로 줄어듭니다. same 패딩은 둘레를 0 으로 채워 크기를 유지합니다.",
        tags=['패딩', '출력 크기'])
    b.C(stem='다음 코드에 대한 설명으로 옳은 것만 <보기>에서 모두 고른 것은? (`train_target` 은 0~9 의 정수이다.)',
        show="model.compile(optimizer='adam', loss='sparse_categorical_crossentropy',\n              metrics=['accuracy'])\nearly_stopping_cb = keras.callbacks.EarlyStopping(patience=2,\n                                                  restore_best_weights=True)\n"
             "history = model.fit(train_scaled, train_target, epochs=20,\n                    validation_data=(val_scaled, val_target),\n                    callbacks=[early_stopping_cb])",
        items=[("정답을 원-핫 인코딩하지 않은 정수 그대로 써서 `sparse_categorical_crossentropy` 를 쓴다.", True),
               ("`EarlyStopping(patience=2)` 는 2 에포크만 학습하고 멈춘다는 뜻이다.", False),
               ("`validation_data` 를 주면 에포크마다 검증 세트의 손실과 정확도도 계산된다.", True)],
        why="`patience=2` 는 검증 손실이 **2번 연속으로 좋아지지 않으면** 멈춘다는 뜻입니다. 정답이 정수면 `sparse_categorical_crossentropy`, 원-핫 인코딩했으면 `categorical_crossentropy` 를 씁니다.",
        tags=['compile', 'EarlyStopping', 'validation_data'], ref='셀 [17] 모델 컴파일과 훈련')
    b.C(stem='`EarlyStopping(patience=2, restore_best_weights=True)` 를 쓰고 `epochs=20` 으로 학습한 기록이다. 설명으로 옳은 것만 <보기>에서 모두 고른 것은?',
        code=VAL + "\nbest = val_loss.index(min(val_loss)) + 1", show=VAL + "   # 1~10 에포크, 10번째에서 훈련이 멈춤",
        items=[("검증 손실이 가장 낮은 것은 8번째 에포크이다.", "best == 8"),
               ("훈련이 끝난 뒤 모델에는 10번째 에포크의 가중치가 남아 있다.", False),
               ("9번째와 10번째 에포크에서 연속으로 검증 손실이 나아지지 않아 멈췄다.", "val_loss[8] > val_loss[7] and val_loss[9] > val_loss[7]")],
        why="8번째(0.2285)가 가장 낮았고 그 뒤 두 번 연속(0.2434, 0.2440) 나아지지 않아 10번째에서 멈췄습니다. `restore_best_weights=True` 라서 가장 좋았던 8번째 에포크의 가중치로 되돌아갑니다.",
        tags=['EarlyStopping', '검증 손실'])
    b.C(code="preds = np.array([[0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0]])\nclasses = ['티셔츠', '바지', '스웨터', '드레스', '코트', '샌달', '셔츠', '스니커즈', '가방', '앵클 부츠']",
        stem='`preds` 는 `model.predict(val_scaled[0:1])` 의 결과를 반올림해 옮긴 것이다. 설명으로 옳은 것만 <보기>에서 모두 고른 것은?',
        items=[("`np.argmax(preds)` 는 8 이다.", "int(np.argmax(preds)) == 8"),
               ("`classes[np.argmax(preds)]` 는 '가방' 이다.", "classes[np.argmax(preds)] == '가방'"),
               ("`preds.shape` 은 `(10,)` 이다.", "preds.shape == (10,)")],
        why="샘플 1개에 대한 10개 클래스의 확률이라 shape 은 `(1, 10)` 입니다. `np.argmax` 가 가장 큰 값의 인덱스 8 을 돌려주고 `classes[8]` 이 가방입니다.",
        tags=['predict', 'argmax'])
    b.C(stem='다음 모델의 뒷부분에 대한 설명으로 옳은 것만 <보기>에서 모두 고른 것은? (Flatten 의 출력은 값 3136개이다.)', code="d = 3136 * 100 + 100\ntotal = 320 + 18496 + d + 1010",
        show="model.add(keras.layers.Flatten())\nmodel.add(keras.layers.Dense(100, activation='relu'))\nmodel.add(keras.layers.Dropout(0.4))\nmodel.add(keras.layers.Dense(10, activation='softmax'))",
        items=[("`Dense(100)` 층의 파라미터는 313,700개이다.", "d == 313700"),
               ("`Dropout(0.4)` 는 훈련할 때 약 40%의 값을 무작위로 0 으로 만든다.", True),
               ("이 모델에서 파라미터가 가장 많은 층은 두 번째 Conv2D 층이다.", "18496 > d")],
        why="Dense(100) 층은 3136 × 100 + 100 = 313,700 개로 전체 333,526 개의 대부분을 차지합니다. 합성곱 층(320, 18,496)보다 훨씬 많습니다.",
        tags=['Dense', 'Dropout', '파라미터 수'])

    # ── 빈칸 ──
    b.B("train_scaled = train_input.㉠(-1, 28, 28, ㉡) / 255.0\nprint(train_scaled.shape)", ('reshape', '1'), [('reshape', '3'), ('resize', '1'), ('reshape', '28'), ('flatten', '1')],
        exec_=False, result="(60000, 28, 28, 1)", stem='`train_input` 은 shape 이 `(60000, 28, 28)` 인 흑백 이미지이다. ㉠, ㉡에 들어갈 것으로 알맞은 것은?',
        why="Conv2D 에 넣으려면 채널 차원이 필요합니다. 흑백은 채널이 1 이므로 `reshape(-1, 28, 28, 1)` 입니다.", tags=['reshape', '채널'])
    b.B("model.add(keras.layers.Conv2D(32, ㉠=3, activation='relu',\n                              ㉡='same', input_shape=(28,28,1)))", ('kernel_size', 'padding'),
        [('filters', 'padding'), ('kernel_size', 'pooling'), ('padding', 'kernel_size'), ('size', 'mode')], exec_=False, result=False,
        stem='필터 32개, 커널 크기 3×3, 출력 크기가 입력과 같아지는 패딩을 쓴다. ㉠, ㉡에 들어갈 것으로 알맞은 것은?',
        why="커널의 크기는 `kernel_size`, 패딩 방식은 `padding` 으로 정합니다.", tags=['Conv2D'])
    b.B("model.add(keras.layers.Conv2D(64, kernel_size=(3,3), activation='relu', padding='same'))\nmodel.add(keras.layers.㉠(2))\nmodel.add(keras.layers.㉡())\nmodel.add(keras.layers.Dense(100, activation='relu'))",
        ('MaxPooling2D', 'Flatten'), [('Flatten', 'MaxPooling2D'), ('Dropout', 'Flatten'), ('MaxPooling2D', 'Dropout'), ('Conv2D', 'Flatten')], exec_=False, result=False,
        stem='합성곱 뒤에 가로세로를 절반으로 줄이고, Dense 층에 넣기 위해 1차원으로 펼친다. ㉠, ㉡에 들어갈 것으로 알맞은 것은?',
        why="크기를 줄이는 층은 `MaxPooling2D`, 1차원으로 펼치는 층은 `Flatten` 입니다.", tags=['MaxPooling2D', 'Flatten'])
    b.B("model.compile(optimizer='adam', loss='㉠', metrics=['accuracy'])\nhistory = model.fit(train_scaled, train_target, epochs=20,\n                    ㉡=(val_scaled, val_target))",
        ('sparse_categorical_crossentropy', 'validation_data'), [('categorical_crossentropy', 'validation_data'), ('sparse_categorical_crossentropy', 'test_data'), ('accuracy', 'validation_data'), ('sparse_categorical_crossentropy', 'callbacks')],
        exec_=False, result=False, stem='정답 `train_target` 은 원-핫 인코딩하지 않은 0~9 의 정수이다. 검증 세트로 에포크마다 점검한다. ㉠, ㉡에 들어갈 것으로 알맞은 것은?',
        why="정답이 정수 그대로면 `sparse_categorical_crossentropy` 를 씁니다. 검증 세트는 `validation_data=(입력, 정답)` 으로 넘깁니다.", tags=['compile', 'validation_data'])
    b.B("early_stopping_cb = keras.callbacks.㉠(㉡=2,\n                                    restore_best_weights=True)", ('EarlyStopping', 'patience'),
        [('ModelCheckpoint', 'patience'), ('EarlyStopping', 'epochs'), ('EarlyStopping', 'save_best_only'), ('Dropout', 'patience')], exec_=False, result=False,
        stem='검증 손실이 2번 연속으로 좋아지지 않으면 훈련을 멈추게 한다. ㉠, ㉡에 들어갈 것으로 알맞은 것은?',
        why="조기 종료 콜백은 `EarlyStopping`, 몇 번까지 참을지는 `patience` 로 정합니다. `ModelCheckpoint` 는 모델을 파일로 저장하는 콜백입니다.", tags=['EarlyStopping'])
    b.B("preds = np.array([[0.01, 0.03, 0.9, 0.06]])\nclasses = ['티셔츠', '바지', '스웨터', '드레스']\nprint(classes[np.㉠(preds)], preds.㉡)", ('argmax', 'shape'),
        [('max', 'shape'), ('argmin', 'shape'), ('argmax', 'size'), ('sum', 'shape')],
        why="가장 큰 확률의 **위치**는 `np.argmax` 로 찾습니다. 샘플 1개, 클래스 4개라 shape 은 `(1, 4)` 입니다.", tags=['argmax'])
    b.B("model.add(keras.layers.Dense(100, activation='㉠'))\nmodel.add(keras.layers.㉡(0.4))\nmodel.add(keras.layers.Dense(10, activation='softmax'))", ('relu', 'Dropout'),
        [('softmax', 'Dropout'), ('relu', 'Flatten'), ('relu', 'MaxPooling2D'), ('sigmoid', 'Dense')], exec_=False, result=False,
        stem='은닉층에는 렐루 함수를 쓰고, 그 뒤에 과대적합을 막기 위해 값의 약 40%를 무작위로 0 으로 만드는 층을 둔다. ㉠, ㉡에 들어갈 것으로 알맞은 것은?',
        why="은닉층의 활성화 함수는 `relu`, 일부 값을 0 으로 만드는 층은 `Dropout` 입니다.", tags=['Dropout', 'ReLU'])

    # ── 경계값 (출력 크기) ──
    b.D("", ['(5, 5)', '(2, 2)', '(4, 4)', '(7, 7)'], chk="print(conv(np.zeros((5, 5)), np.zeros((3, 3))).shape)",
        stem='(5, 5) 크기의 입력에 (3, 3) 커널을 패딩 없이 한 칸씩 이동하며 합성곱했을 때 출력의 크기는?',
        why="패딩이 없으면 출력 크기는 입력 − 커널 + 1 입니다. 5 − 3 + 1 = 3 이므로 (3, 3) 입니다.", tags=['출력 크기', 'valid'])
    b.D(CONV1, ['(26, 26, 32)', '(28, 28, 1)', '(14, 14, 32)', '(32, 28, 28)'], ans='(28, 28, 32)', ref=REF_SUM,
        stem='(28, 28, 1) 이미지가 다음 층을 지난 뒤의 출력 크기는?',
        why="same 패딩이라 가로세로 28 은 그대로이고, 깊이는 필터 수인 32 가 됩니다.", tags=['출력 크기', 'same'])
    b.D("model.add(keras.layers.MaxPooling2D(2))", ['(7, 7, 32)', '(14, 14, 32)', '(12, 12, 64)', '(28, 28, 64)'], ans='(7, 7, 64)', ref=REF_SUM,
        stem='(14, 14, 64) 크기의 특성 맵이 다음 층을 지난 뒤의 출력 크기는?',
        why="(2, 2) 풀링은 가로세로를 절반(14 → 7)으로 줄이고 깊이 64 는 그대로 둡니다.", tags=['출력 크기', '풀링'])
    b.D("model.add(keras.layers.Conv2D(16, kernel_size=5, activation='relu', input_shape=(28,28,1)))", ['(28, 28, 16)', '(23, 23, 16)', '(24, 24, 1)', '(14, 14, 16)'],
        ans='(24, 24, 16)', chk="print((28 - 5 + 1, 28 - 5 + 1, 16))", stem='(28, 28, 1) 이미지가 다음 층을 지난 뒤의 출력 크기는? (`padding` 을 지정하지 않았다.)',
        why="패딩을 지정하지 않으면 밸리드 패딩이라 28 − 5 + 1 = 24 로 줄어듭니다. 깊이는 필터 수 16 입니다.", tags=['출력 크기', 'valid'])
    b.D("model.add(keras.layers.Flatten())", ['49', '448', '78', '6272'], ans='3136', chk="print(7 * 7 * 64)", stem='(7, 7, 64) 크기의 특성 맵이 다음 층을 지나면 값이 몇 개인 1차원 배열이 되는가?',
        why="모든 값을 한 줄로 펼치므로 7 × 7 × 64 = 3136 개입니다.", tags=['Flatten'])
    b.D("", ['(10, 10, 8)', '(5, 5, 1)', '(12, 12, 1)', '(10, 10, 3)'], ans='(10, 10, 1)', chk="print((5 * 2, 5 * 2, 1))",
        stem='흑백 이미지를 **same 패딩**, 필터 8개, 커널 (3, 3) 인 합성곱 층에 넣고 (2, 2) 최대 풀링을 했더니 (5, 5, 8) 크기의 특성 맵이 나왔다. 합성곱 층에 넣은 입력의 크기는?',
        why="풀링 전은 가로세로가 두 배인 (10, 10, 8) 이고, same 패딩이라 합성곱 입력의 가로세로도 10 입니다. 입력의 깊이는 필터 수가 아니라 이미지의 채널 수로, 흑백은 1 입니다.",
        tags=['출력 크기', '거꾸로 구하기'])
    b.D("print(int(60000 * 0.8), int(60000 * 0.2), 48000 // 32)", ['48000 12000 469', '45000 15000 1500', '54000 6000 1875', '48000 12000 150'],
        stem='훈련 데이터 60000장을 `test_size=0.2` 로 나누고, 기본 `batch_size` 인 32 로 학습한다. 훈련 세트 수, 검증 세트 수, 한 에포크의 갱신 횟수를 계산한 다음 코드의 출력은?',
        why="60000 의 80%인 48000장이 훈련 세트, 20%인 12000장이 검증 세트입니다. 48000 ÷ 32 = 1500 이라 학습 출력에 1500/1500 이 나옵니다.", tags=['검증 세트', 'batch_size'])

    # ── 상태 예측 (합성곱·풀링 계산) ──
    b.R(XA + "\n" + KA, ['[[1, 2, 0], [0, 1, 3], [2, 1, 0]]', '[[2, 5, 2], [1, 1, 4]]', '[[3, 3, 3], [3, 5, 6], [4, 3, 6]]', '[[2, 5], [1, 1]]'], chk=XA + "\n" + KA + "\nprint(conv(x, k).tolist())",
        stem=f'입력 `x` 에 커널 `k` 로 합성곱한 결과(특성 맵)로 알맞은 것은? {CV}',
        why="출력은 4 − 2 + 1 = 3 이라 3×3 입니다. 왼쪽 위 칸은 겹친 [[1, 2], [0, 1]] 에 커널을 곱해 더한 1×1 + 2×0 + 0×0 + 1×1 = 2, 그 오른쪽은 [[2, 0], [1, 3]] 이라 2 + 3 = 5 입니다.",
        tags=['합성곱 계산'])
    b.R(XB + "\n" + KB, ['[[4, 6], [3, 4]]', '[[6, 4, 4, 3]]', '[[5, 5], [5, 4]]', '[[6, 4], [4, 3], [2, 1]]'], chk=XB + "\n" + KB + "\nprint(conv(x, k).tolist())",
        stem=f'입력 `x` 에 커널 `k` 로 합성곱한 결과(특성 맵)로 알맞은 것은? {CV}',
        why="출력은 4 − 3 + 1 = 2 라 2×2 입니다. 커널의 1 이 있는 다섯 자리(네 모서리와 가운데)의 값만 더하면 됩니다. 왼쪽 위: 1 + 2 + 1 + 2 + 0 = 6, 오른쪽 위: 0 + 1 + 1 + 1 + 1 = 4 입니다.",
        tags=['합성곱 계산'])
    b.R(FC, ['[[1, 0], [0, 2]]', '[[5, 4], [3, 8]]', '[[3, 4], [6, 8]]', '[[11, 7], [10, 19]]'], chk=FC + "\nprint(pool(f).tolist())",
        stem='특성 맵 `f` 에 (2, 2) 최대 풀링을 한 결과로 알맞은 것은?',
        why="겹치지 않게 2×2 영역 네 개로 나누고 각 영역의 최댓값만 남깁니다. 왼쪽 위 [[1, 3], [5, 2]] → 5, 오른쪽 위 [[2, 0], [1, 4]] → 4, 왼쪽 아래 [[0, 1], [3, 6]] → 6, 오른쪽 아래 [[7, 2], [2, 8]] → 8 입니다.",
        tags=['최대 풀링'])
    b.R(FC + "\n" + FD, ['[[5, 4], [6, 8]] [[4, 5], [7, 8]]', '[[9, 5], [7, 8]] [[5, 4], [6, 8]]', '[[5, 4], [6, 8]] [[9, 6], [7, 8]]', '[[9, 5], [7, 8]]'],
        chk=FC + "\n" + FD + "\nprint(pool(f).tolist(), pool(g).tolist())",
        stem='`f` 와 `g` 는 (4, 4, 2) 크기 특성 맵의 첫 번째 장과 두 번째 장이다. (2, 2) 최대 풀링을 한 결과를 첫 번째 장, 두 번째 장 순서로 쓴 것은?',
        why="풀링은 특성 맵을 **한 장씩 따로** 계산하고 깊이(2장)는 그대로 유지합니다. 결과의 크기는 (2, 2, 2) 입니다.", tags=['최대 풀링', '깊이'])
    b.R(XE + "\n" + KE, ['[[2, 2], [6, 2]]', '[[6, 4], [4, 4]]', '[[2, 3], [3, 7]]', '[[7, 7], [7, 7]]'], chk=XE + "\n" + KE + "\nprint(pool(conv(x, k)).tolist())",
        stem=f'입력 `x` 에 커널 `k` 로 합성곱한 다음, 그 결과에 (2, 2) 최대 풀링을 한 최종 결과로 알맞은 것은? {CV}',
        why="합성곱 결과는 5 − 2 + 1 = 4 라 4×4 인 [[2, 2, 3, 4], [6, 2, 2, 4], [3, 4, 7, 5], [3, 1, 4, 7]] 입니다. 여기에 최대 풀링을 하면 [[6, 4], [4, 7]] 입니다.", tags=['합성곱 계산', '최대 풀링'])
    b.R(CONV1, ['288', '9', '10', '32'], ans='320', chk="print((3 * 3 * 1 + 1) * 32)", stem='(28, 28, 1) 이미지를 받는 다음 합성곱 층의 파라미터 수는?',
        why="(커널 높이 × 커널 너비 × 입력 채널 수 + 1) × 필터 수 = (3 × 3 × 1 + 1) × 32 = 320 입니다. 필터마다 편향이 하나씩 있어 +1 을 합니다.", tags=['파라미터 수', 'Conv2D'])
    b.R(CONV2, ['18,432', '640', '576', '18,560'], ans='18,496', chk="print(f'{(3 * 3 * 32 + 1) * 64:,}')", stem='(14, 14, 32) 크기의 특성 맵을 받는 다음 합성곱 층의 파라미터 수는?',
        why="입력 채널이 앞 층의 필터 수인 32 입니다. (3 × 3 × 32 + 1) × 64 = 289 × 64 = 18,496 입니다.", tags=['파라미터 수', 'Conv2D'])
    b.R(MODEL + "\nmodel.summary()", ['333,206', '313,700', '19,826', '352,022'], ans='333,526', chk="print(f'{320 + 18496 + 3136 * 100 + 100 + 100 * 10 + 10:,}')",
        stem='다음 모델 요약의 Total params 값은? (두 Conv2D 층의 파라미터는 320, 18,496 이고 Flatten 의 출력은 3136개이다.)',
        why="320 + 18,496 + (3136 × 100 + 100) + (100 × 10 + 10) = 320 + 18,496 + 313,700 + 1,010 = 333,526 입니다. 풀링, Flatten, Dropout 은 0 입니다.", tags=['파라미터 수'])
    b.R("model.evaluate(val_scaled, val_target)", ['0.2440', '0.2434', '0.3184', '0.2301'], ans='0.2285', chk=VAL + "\nprint('%.4f' % min(val_loss))", ref=REF_LOG,
        stem='`EarlyStopping(patience=2, restore_best_weights=True)` 로 학습했다.' + LOG + ' 훈련이 끝난 뒤 다음 코드가 돌려주는 손실값은? (소수 넷째 자리까지)',
        why="`restore_best_weights=True` 라서 검증 손실이 가장 낮았던 8번째 에포크의 가중치로 되돌아갑니다. 그래서 검증 세트의 손실은 8번째 에포크의 0.2285 입니다.",
        tags=['EarlyStopping', 'evaluate'])

    # ── 대조 ──
    b.X("# 방법1\nkeras.layers.Conv2D(8, kernel_size=3, padding='same')\n\n# 방법2\nkeras.layers.Conv2D(8, kernel_size=3)", [('(4, 4)', '(6, 6)'), ('(6, 6)', '(6, 6)'), ('(6, 6)', '(3, 3)'), ('(8, 8)', '(4, 4)')],
        ans=('(6, 6)', '(4, 4)'), chk="print((6, 6))\nprint(conv(np.zeros((6, 6)), np.zeros((3, 3))).shape)",
        stem='(6, 6, 1) 입력을 각 층에 넣었을 때 출력의 **가로세로 크기** ㉠, ㉡으로 알맞은 것은?',
        why="same 패딩은 크기를 유지해 (6, 6), 패딩을 지정하지 않으면 6 − 3 + 1 = 4 라 (4, 4) 가 됩니다.", tags=['패딩', '출력 크기'])
    b.X("# 방법1: 입력이 (28, 28, 1)\nkeras.layers.Conv2D(64, kernel_size=3, padding='same')\n\n# 방법2: 입력이 (14, 14, 32)\nkeras.layers.Conv2D(64, kernel_size=3, padding='same')",
        [('576', '18,432'), ('640', '640'), ('18,496', '640'), ('64', '2,048')], ans=('640', '18,496'), chk="print(f'{(3 * 3 * 1 + 1) * 64:,}')\nprint(f'{(3 * 3 * 32 + 1) * 64:,}')",
        stem='같은 합성곱 층에 깊이가 다른 입력을 넣는다. 각 경우의 파라미터 수 ㉠, ㉡으로 알맞은 것은?',
        why="파라미터 수는 **입력 채널 수**에 따라 달라집니다. 채널 1 이면 (9 × 1 + 1) × 64 = 640, 채널 32 면 (9 × 32 + 1) × 64 = 18,496 입니다.", tags=['파라미터 수', '입력 채널'])
    b.X("# 방법1\nkeras.layers.MaxPooling2D(2)\n\n# 방법2\nkeras.layers.Conv2D(16, kernel_size=3, padding='same')", [('(4, 4, 8)', '(8, 8, 16)'), ('(8, 8, 16)', '(8, 8, 16)'), ('(4, 4, 16)', '(6, 6, 16)'), ('(4, 4, 16)', '(4, 4, 16)')],
        ans=('(4, 4, 16)', '(8, 8, 16)'), chk="print((8 // 2, 8 // 2, 16))\nprint((8, 8, 16))", stem='(8, 8, 16) 크기의 특성 맵을 각 층에 넣었을 때의 출력 크기 ㉠, ㉡으로 알맞은 것은?',
        why="풀링은 가로세로를 절반으로 줄이고 깊이는 그대로 둡니다. same 패딩 합성곱은 가로세로를 유지하고 깊이는 필터 수(16)가 됩니다.", tags=['풀링', '합성곱', '출력 크기'])
    b.X("preds = np.array([[0.01, 0.03, 0.9, 0.06]])\n# 방법1\nprint(np.argmax(preds))\n\n# 방법2\nprint(np.max(preds))", [('0.9', '2'), ('2', '2'), ('3', '0.9'), ('0.9', '0.9')],
        why="`np.argmax` 는 가장 큰 값의 **인덱스**(2), `np.max` 는 가장 큰 **값**(0.9)을 돌려줍니다. 클래스 이름을 찾을 때는 인덱스가 필요합니다.", tags=['argmax'])
    b.X("# 방법1: Flatten 의 입력이 (7, 7, 64)\nkeras.layers.Dense(100, activation='relu')\n\n# 방법2: Flatten 의 입력이 (14, 14, 32)\nkeras.layers.Dense(100, activation='relu')",
        [('313,600', '627,200'), ('313,700', '313,700'), ('627,300', '313,700'), ('3,236', '6,372')], ans=('313,700', '627,300'),
        chk="print(f'{7 * 7 * 64 * 100 + 100:,}')\nprint(f'{14 * 14 * 32 * 100 + 100:,}')", stem='Flatten 뒤에 오는 Dense(100) 층의 파라미터 수 ㉠, ㉡으로 알맞은 것은?',
        why="7 × 7 × 64 = 3136 이라 3136 × 100 + 100 = 313,700, 14 × 14 × 32 = 6272 라 6272 × 100 + 100 = 627,300 입니다. 풀링으로 크기를 줄이면 뒤쪽 Dense 층의 파라미터도 줄어듭니다.",
        tags=['파라미터 수', 'Flatten'])

    # ── 조건 매핑 ──
    b.S(["첫 번째 합성곱 층을 만든다.", "필터 32개, 커널 3×3, 활성화 함수는 렐루이다.", "출력의 가로세로가 입력 (28, 28, 1) 과 같게 한다."],
        "keras.layers.Conv2D(32, kernel_size=3, activation='relu', padding='same', input_shape=(28,28,1))",
        ["keras.layers.Conv2D(3, kernel_size=32, activation='relu', padding='same', input_shape=(28,28,1))", "keras.layers.Conv2D(32, kernel_size=3, activation='relu', padding='valid', input_shape=(28,28,1))",
         "keras.layers.Conv2D(32, kernel_size=3, activation='relu', padding='same', input_shape=(28,28))", "keras.layers.Dense(32, kernel_size=3, activation='relu', padding='same', input_shape=(28,28,1))"],
        code="model.add(____)", why="`Conv2D` 의 첫 인자가 필터 수이고, 크기를 유지하려면 `padding='same'`, 입력은 채널까지 포함한 `(28,28,1)` 입니다.", tags=['Conv2D'])
    b.S(["특성 맵의 가로세로를 절반으로 줄인다.", "영역마다 가장 큰 값만 남긴다."], "keras.layers.MaxPooling2D(2)",
        ["keras.layers.Conv2D(2)", "keras.layers.Flatten()", "keras.layers.Dropout(0.5)", "keras.layers.MaxPooling2D(1)"],
        code="model.add(____)", why="`MaxPooling2D(2)` 가 (2, 2) 영역마다 최댓값만 남겨 가로세로를 절반으로 줄입니다. 1 을 주면 크기가 줄지 않습니다.", tags=['MaxPooling2D'])
    b.S(["검증 손실이 2번 연속으로 좋아지지 않으면 훈련을 멈춘다.", "멈춘 뒤 가장 좋았던 때의 가중치로 되돌린다."], "keras.callbacks.EarlyStopping(patience=2, restore_best_weights=True)",
        ["keras.callbacks.ModelCheckpoint(patience=2, restore_best_weights=True)", "keras.callbacks.EarlyStopping(patience=2, restore_best_weights=False)",
         "keras.callbacks.EarlyStopping(epochs=2, restore_best_weights=True)", "keras.layers.Dropout(patience=2, restore_best_weights=True)"],
        code="early_stopping_cb = ____", why="조기 종료는 `EarlyStopping`, 참는 횟수는 `patience`, 가장 좋은 가중치로 되돌리는 옵션은 `restore_best_weights=True` 입니다.", tags=['EarlyStopping'])
    b.S(["흑백 이미지 배열 `train_input` (shape `(N, 28, 28)`)에 채널 차원 1 을 추가한다.", "픽셀값(0~255)을 0~1 로 바꾼다."], "train_input.reshape(-1, 28, 28, 1) / 255.0",
        ["train_input.reshape(-1, 784) / 255.0", "train_input.reshape(-1, 28, 28, 1) * 255.0", "train_input.reshape(28, 28, 1) / 255.0", "train_input.reshape(-1, 28, 28, 3) / 255.0"],
        code="train_scaled = ____", chk="print(train_scaled.shape, train_scaled.max())", pre="import numpy as np\ntrain_input = np.full((10, 28, 28), 255, dtype=np.uint8)",
        why="`reshape(-1, 28, 28, 1)` 로 채널 차원을 붙이고 255.0 으로 나눕니다. `reshape(-1, 784)` 는 Dense 층용 1차원 변환입니다.", tags=['reshape', '정규화'])
    b.S(["`preds` 는 샘플 1개에 대한 클래스별 확률, `classes` 는 클래스 이름 리스트이다.", "확률이 가장 큰 클래스의 **이름**을 구한다."], "classes[np.argmax(preds)]",
        ["classes[np.max(preds)]", "np.argmax(classes)", "preds[np.argmax(classes)]", "classes[np.argmin(preds)]"],
        code="name = ____", chk="print(name)", pre="import numpy as np\npreds = np.array([[0.01, 0.03, 0.9, 0.06]])\nclasses = ['티셔츠', '바지', '스웨터', '드레스']",
        why="`np.argmax(preds)` 로 가장 큰 확률의 인덱스를 구해 `classes` 에서 이름을 꺼냅니다.", tags=['argmax'])

    # ── 서답형 ──
    b.W("(28, 28, 1) 이미지를 받는 `Conv2D(32, kernel_size=3)` 층의 파라미터 수를 구하시오.", "320", accept=['320개'], chk="print((3 * 3 * 1 + 1) * 32)",
        why="(3 × 3 × 1 + 1) × 32 = 10 × 32 = 320 입니다.", tags=['파라미터 수'])
    b.W("(14, 14, 32) 특성 맵을 받는 `Conv2D(64, kernel_size=(3,3))` 층의 파라미터 수를 구하시오.", "18496", accept=['18,496', '18496개', '18,496개'], chk="print((3 * 3 * 32 + 1) * 64)",
        why="(3 × 3 × 32 + 1) × 64 = 289 × 64 = 18,496 입니다.", tags=['파라미터 수'])
    b.W("(7, 7) 크기의 입력에 (3, 3) 커널을 패딩 없이 한 칸씩 이동하며 합성곱하면 출력의 한 변의 길이는 얼마인지 쓰시오.", "5", accept=['5칸', '(5, 5)', '5x5', '5×5'],
        chk="print(conv(np.zeros((7, 7)), np.zeros((3, 3))).shape[0])", why="7 − 3 + 1 = 5 입니다.", tags=['출력 크기'])
    b.W("커널이 [[1, 0, 1], [0, 1, 0], [1, 0, 1]] 이고, 입력에서 커널과 겹친 부분이 [[2, 0, 1], [1, 3, 0], [0, 1, 2]] 일 때 이 위치의 합성곱 값을 구하시오.", "8",
        chk="print(int((np.array([[2, 0, 1], [1, 3, 0], [0, 1, 2]]) * np.array([[1, 0, 1], [0, 1, 0], [1, 0, 1]])).sum()))",
        why="같은 자리끼리 곱해서 더합니다. 커널이 1 인 자리의 값 2, 1, 3, 0, 2 를 더하면 8 입니다.", tags=['합성곱 계산'])
    b.W("(7, 7, 64) 크기의 특성 맵을 Flatten 한 뒤 `Dense(100)` 층에 연결했다. 이 Dense 층의 파라미터 수를 구하시오.", "313700", accept=['313,700', '313700개', '313,700개'],
        chk="print(7 * 7 * 64 * 100 + 100)", why="7 × 7 × 64 = 3136 개의 입력이므로 3136 × 100 + 100 = 313,700 입니다.", tags=['파라미터 수', 'Flatten'])
    b.W("빈칸 ㉠ 에 들어갈 값을 쓰시오. (출력의 가로세로 크기가 입력과 같아지도록 둘레를 0 으로 채운다.)", "same", accept=["'same'", '"same"'],
        code="model.add(keras.layers.Conv2D(32, kernel_size=3, activation='relu',\n                              padding='㉠', input_shape=(28,28,1)))", exec_=False, result=False,
        why="`padding='same'` 이 세임 패딩입니다. 지정하지 않으면 패딩이 없는 밸리드 패딩입니다.", tags=['패딩'])
    b.W("(28, 28, 32) 크기의 특성 맵에 `MaxPooling2D(2)` 를 적용한 출력의 크기를 (높이, 너비, 깊이) 형식으로 쓰시오.", "(14, 14, 32)", accept=['14, 14, 32', '(14,14,32)', '14,14,32', '14x14x32', '14×14×32'],
        chk="print((28 // 2, 28 // 2, 32))", why="가로세로는 절반인 14 가 되고 깊이 32 는 그대로입니다.", tags=['풀링', '출력 크기'])
    b.W("훈련할 때 일부 값을 무작위로 0 으로 만들어 과대적합을 막는 층의 이름을 쓰시오. (노트북에서는 0.4 를 인자로 주었다.)", "Dropout", accept=['드롭아웃', 'dropout', 'DropOut', 'Dropout 층', '드롭아웃 층'],
        why="`Dropout(0.4)` 는 훈련할 때 입력값 중 약 40%를 무작위로 0 으로 만듭니다.", tags=['Dropout'])
    b.W("특성 맵의 2×2 영역 [[1, 3], [5, 2]] 에 최대 풀링을 적용하면 남는 값을 쓰시오.", "5", chk="print(int(np.array([[1, 3], [5, 2]]).max()))", why="최대 풀링은 영역에서 가장 큰 값 5 만 남깁니다.", tags=['최대 풀링'])

    # ── 서술형 ──
    b.E(f"다음 입력 `x` 에 커널 `k` 로 합성곱한 결과를 구하고, 출력의 크기가 그렇게 되는 이유와 첫 번째 칸(왼쪽 위)의 계산 과정을 쓰시오. {CV}",
        "결과: [[7, 2], [9, 9]]\n출력 크기: 3 − 2 + 1 = 2 이므로 2×2.\n왼쪽 위 칸: 겹친 부분 [[2, 1], [1, 3]] 에 커널 [[1, 2], [0, 1]] 을 같은 자리끼리 곱해 더하면 2×1 + 1×2 + 1×0 + 3×1 = 7.",
        "필수 요소(모두 있어야 정답): (1) 결과 [[7, 2], [9, 9]] (네 값이 모두 맞아야 함). (2) 출력이 2×2 인 이유(3 − 2 + 1 = 2 또는 커널이 가로·세로로 두 번씩만 놓인다는 설명). (3) 첫 칸 7 의 계산 과정. 값이 하나라도 틀리면 오답.",
        ['합성곱 계산'], code=XG + "\n" + KG, chk=XG + "\n" + KG + "\nprint(conv(x, k).tolist())")
    b.E("다음 특성 맵 `x` 에 (2, 2) 최대 풀링을 한 결과를 구하고, 풀링 층이 하는 역할을 설명하시오.",
        "결과: [[3, 4], [5, 3]]\n겹치지 않게 2×2 영역으로 나누어 각 영역의 최댓값만 남긴다. 풀링은 특성 맵의 가로세로 크기를 줄여 계산량과 뒤쪽 층의 파라미터 수를 줄이며, 학습할 가중치는 없다.",
        "필수 요소(모두 있어야 정답): (1) 결과 [[3, 4], [5, 3]]. (2) 풀링의 역할: 특성 맵의 크기를 줄인다(영역의 대표값만 남긴다)는 취지. 값이 하나라도 틀리면 오답.",
        ['최대 풀링'], code=XH, chk=XH + "\nprint(pool(x).tolist())")
    b.E("(28, 28, 1) 이미지를 다음 층에 차례로 통과시킨다. 각 층을 지난 뒤의 출력 크기를 쓰고 그렇게 되는 이유를 설명하시오.\n① Conv2D(32, kernel_size=3, padding='same')  ② MaxPooling2D(2)  ③ Conv2D(64, kernel_size=3, padding='same')  ④ MaxPooling2D(2)  ⑤ Flatten()",
        "① (28, 28, 32): same 패딩이라 가로세로는 그대로이고 깊이는 필터 수 32.\n② (14, 14, 32): 풀링으로 가로세로가 절반, 깊이는 그대로.\n③ (14, 14, 64): same 패딩이라 가로세로 그대로, 깊이는 필터 수 64.\n④ (7, 7, 64): 가로세로가 다시 절반.\n⑤ 3136: 7 × 7 × 64 개의 값을 1차원으로 펼침.",
        "필수 요소(모두 있어야 정답): 다섯 출력 크기 (28,28,32), (14,14,32), (14,14,64), (7,7,64), 3136 이 모두 맞아야 한다. 이유로 same 패딩은 크기 유지·깊이는 필터 수, 풀링은 절반이라는 설명이 드러나야 한다.",
        ['출력 크기'], chk="print((28, 28, 32), (14, 14, 32), (14, 14, 64), (7, 7, 64), 7 * 7 * 64)")
    b.E("(28, 28, 1) 이미지를 받는 첫 번째 층 `Conv2D(32, kernel_size=3)` 과, 그 출력을 풀링한 (14, 14, 32) 를 받는 두 번째 층 `Conv2D(64, kernel_size=3)` 의 파라미터 수를 각각 계산 과정과 함께 쓰시오.",
        "파라미터 수 = (커널 높이 × 커널 너비 × 입력 채널 수 + 1) × 필터 수\n첫 번째: (3 × 3 × 1 + 1) × 32 = 10 × 32 = 320\n두 번째: (3 × 3 × 32 + 1) × 64 = 289 × 64 = 18,496",
        "필수 요소(모두 있어야 정답): (1) 첫 번째 320. (2) 두 번째 18,496. (3) 계산식에서 입력 채널 수(1, 32)와 편향 +1 이 드러나야 한다. 편향을 빼서 288, 18,432 로 쓰면 오답.",
        ['파라미터 수'], chk="print((3 * 3 * 1 + 1) * 32, (3 * 3 * 32 + 1) * 64)")
    b.E("`EarlyStopping(patience=2, restore_best_weights=True)` 를 쓰고 `epochs=20` 으로 학습했다." + LOG + " 20 에포크를 다 돌지 않고 10번째에서 멈춘 이유와, 훈련이 끝난 뒤 모델이 몇 번째 에포크의 가중치를 갖게 되는지 설명하시오.",
        "검증 손실은 8번째 에포크(0.2285)에서 가장 낮았고, 9번째(0.2434)와 10번째(0.2440)에 2번 연속으로 그보다 나아지지 않았다. patience=2 이므로 10번째에서 훈련을 멈췄다. restore_best_weights=True 이므로 검증 손실이 가장 낮았던 8번째 에포크의 가중치로 되돌아간다.",
        "필수 요소(모두 있어야 정답): (1) 8번째가 최저이고 그 뒤 2번 연속(9, 10번째) 개선되지 않았다는 점. (2) patience=2 라서 멈췄다는 점. (3) 최종 가중치는 8번째 에포크의 것이라는 점. 10번째 가중치라고 쓰면 오답.",
        ['EarlyStopping'], chk=VAL + "\nprint(val_loss.index(min(val_loss)) + 1)")
    b.E("손글씨나 옷 사진 같은 이미지를 분류할 때, 이미지를 한 줄로 펼쳐 Dense 층에 넣는 인공신경망과 비교해 합성곱 신경망(CNN)이 갖는 장점을 설명하시오.",
        "이미지를 1차원으로 펼치면 어떤 픽셀이 어떤 픽셀의 옆이나 위아래에 있었는지 같은 위치(공간) 정보가 사라진다. 합성곱 신경망은 이미지를 2차원 그대로 입력받아 작은 커널이 이미지를 훑으며 주변 픽셀들의 관계에서 특징을 뽑아내므로 공간 정보를 살릴 수 있어 이미지 분류에 유리하다.",
        "필수 요소: (1) 1차원으로 펼치면 픽셀의 위치(공간, 2차원 구조) 정보가 사라진다는 점. (2) CNN 은 2차원 그대로 입력받아(커널로) 그 정보를 활용한다는 점. 두 취지가 드러나야 정답.",
        ['CNN'])
    b.E("컬러 이미지를 **same 패딩**, 필터 6개, 커널 (3, 3) 인 합성곱 층에 넣고 (2, 2) 최대 풀링을 했더니 (8, 8, 6) 크기의 특성 맵이 나왔다. 합성곱 층에 넣은 입력의 크기를 구하고 풀이 과정을 쓰시오.",
        "(16, 16, 3)\n(2, 2) 풀링은 가로세로를 절반으로 줄이므로 풀링 전의 특성 맵은 (16, 16, 6) 이다. same 패딩은 가로세로를 유지하므로 합성곱 층의 입력도 가로세로가 16 이다. 입력의 깊이는 필터 수(6)가 아니라 이미지의 채널 수이고 컬러 이미지는 3 이다.",
        "필수 요소(모두 있어야 정답): (1) 답 (16, 16, 3). (2) 풀링 전이 (16, 16, …) 라는 점. (3) same 패딩이라 가로세로가 유지된다는 점 또는 컬러 이미지의 채널이 3 이라는 점. (16, 16, 6) 은 오답.",
        ['출력 크기', '거꾸로 구하기'], chk="print((8 * 2, 8 * 2, 3))")
    b.E("에포크가 진행될수록 훈련 손실(loss)은 0.5113 에서 0.1548 까지 계속 줄어들었지만, 검증 손실(val_loss)은 8번째 에포크의 0.2285 까지 줄었다가 그 뒤로 0.2434, 0.2440 으로 다시 커졌다. 이 현상이 뜻하는 것을 설명하고, 이 노트북의 모델에서 이를 줄이기 위해 사용한 방법을 한 가지 쓰시오.",
        "훈련 세트에는 점점 더 잘 맞지만 검증 세트에서는 오히려 나빠지기 시작한 것으로, 모델이 훈련 세트에 과대적합되기 시작했다는 뜻이다. 이를 줄이기 위해 Dropout 층으로 훈련 중 일부 값을 0 으로 만들었고, 조기 종료(EarlyStopping)로 검증 손실이 나빠지면 훈련을 멈추고 가장 좋았던 가중치로 되돌렸다.",
        "필수 요소(모두 있어야 정답): (1) 과대적합(훈련 세트에만 지나치게 맞춰짐)이라는 해석. (2) 방법: Dropout 또는 조기 종료(EarlyStopping) 중 하나 이상.",
        ['과대적합', 'Dropout', 'EarlyStopping'])
    return b
