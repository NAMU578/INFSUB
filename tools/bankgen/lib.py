"""기말 문항 은행 생성 도구.
문항을 짧게 적으면 (1) 코드를 실제로 실행해 정답과 verifyExpect 를 만들고
(2) 보기 상자 HTML 을 붙이고 (3) 정답 위치를 고르게 배치한다."""
import io, os, re, json, random, contextlib, warnings, itertools

os.environ.setdefault('MPLBACKEND', 'Agg')
DATA_DIR = '/home/claude/INFSUB/data'
BOX = ('<span style="display:block;margin-top:9px;padding:9px 12px;background:rgba(22,35,58,.045);'
       'border-left:2px solid var(--rule);border-radius:2px">')
MARK = ['(가)', '(나)', '(다)', '(라)']
BLANKS = ['㉠', '㉡', '㉢']

TYPES = [
    {"key": "classify", "label": "개념 분류", "pick": [1, 2], "note": "코드를 보고 <보기>에서 옳은 설명을 모두 고르는 문항"},
    {"key": "blank2", "label": "빈칸", "pick": [1, 2], "note": "㉠, ㉡ 두 빈칸을 짝으로 고르는 문항"},
    {"key": "boundary", "label": "경계값", "pick": [1, 2], "note": "포함/미포함, 개수·크기의 경계를 판별하는 문항"},
    {"key": "trace", "label": "상태 예측", "pick": [1, 2], "note": "출력값·shape 등 실행 결과를 예측하는 문항"},
    {"key": "contrast", "label": "대조", "pick": [1, 2], "note": "거의 같은 두 코드의 결정적 차이를 묻는 문항"},
    {"key": "spec", "label": "조건 매핑", "pick": [1, 1], "note": "[조건]을 만족하는 코드를 고르는 문항"},
    {"key": "short", "label": "서답형", "pick": [1, 1], "note": "빈칸에 들어갈 코드나 계산 결과를 직접 쓰는 문항"},
    {"key": "essay", "label": "서술형", "pick": [1, 1], "note": "이유 설명·계산 과정을 서술하는 문항 (AI 채점)"},
]
LABEL = {t['key']: t['label'] for t in TYPES}


def esc(s):
    return str(s).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def fmt(s):
    """`코드` → 고정폭, **굵게** → <b>, 줄바꿈 → <br>"""
    s = esc(s)
    s = re.sub(r'`([^`]+)`', r'<span class="mono">\1</span>', s)
    s = re.sub(r'\*\*([^*]+)\*\*', r'<b>\1</b>', s)
    return s.replace('\n', '<br>')


def box(title, body_html):
    return f'{BOX}<b>{esc(title)}</b><br>{body_html}</span>'


def resbox(text, title='<실행결과>'):
    return box(title, '<span class="mono" style="white-space:pre-wrap">' + esc(text).replace('\n', '<br>') + '</span>')


def run(code):
    """코드를 새 이름공간에서 실행하고 (표준출력, 이름공간)을 돌려준다."""
    buf = io.StringIO()
    ns = {'__name__': '__main__'}
    cwd = os.getcwd()
    os.chdir(DATA_DIR)
    try:
        with contextlib.redirect_stdout(buf), warnings.catch_warnings():
            warnings.simplefilter('ignore')
            exec(compile(code, '<q>', 'exec'), ns)
    finally:
        os.chdir(cwd)
        try:
            import matplotlib.pyplot as plt
            plt.close('all')
        except Exception:
            pass
    return buf.getvalue().rstrip('\n'), ns


class Bank:
    def __init__(self, num, src, pre=''):
        self.num, self.src, self.pre = num, src, pre.strip('\n')
        self.qs, self.cnt = [], {}

    # ── 내부 도구 ──────────────────────────────────────
    def _id(self, letter):
        n = self.cnt.get(letter, 0) + 1
        self.cnt[letter] = n
        return f'F{self.num}{letter}{n:02d}', n

    def _full(self, code, pre):
        pre = self.pre if pre is None else pre.strip('\n')
        return (pre + '\n' if pre else '') + code

    def _place(self, letter, n, ans, wrong):
        wrong = [str(w) for w in wrong]
        ans = str(ans)
        assert len(wrong) == 4, f'오답은 4개여야 함: {ans} / {wrong}'
        assert ans not in wrong and len(set(wrong)) == 4, f'보기 중복: {ans} / {wrong}'
        perm = list(range(5))
        random.Random(f'{self.num}{letter}').shuffle(perm)
        pos = perm[(n - 1) % 5]
        rnd = random.Random(f'{self.num}{letter}{n}')
        rnd.shuffle(wrong)
        return wrong[:pos] + [ans] + wrong[pos:]

    def _add(self, qid, key, mode, stem, code, answer, why, tags, **extra):
        q = {"id": qid, "type": LABEL[key], "typeKey": key, "mode": mode, "src": self.src,
             "stem": stem, "code": code, "answer": answer, "why": fmt(why), "tags": list(tags)}
        q.update({k: v for k, v in extra.items() if v is not None})
        assert why.strip(), f'{qid}: 해설 없음'
        self.qs.append(q)
        return q

    # ── 개념 분류: <보기>에서 옳은 것만 고르기 ─────────────
    def C(self, items, why, tags, code='', stem=None, pre=None, ref=None):
        qid, n = self._id('C')
        exprs = [t for _, t in items if isinstance(t, str)]
        truth, vcode, vexp = [], None, None
        if exprs:
            full = self._full(code, pre)
            out, ns = run(full)
            for _, t in items:
                truth.append(bool(eval(t, ns)) if isinstance(t, str) else bool(t))
            if exprs:
                vcode = full + '\nprint(' + ', '.join(exprs) + ')'
                vexp, _ = run(vcode)
                vexp = vexp.split('\n')[-1] if out else vexp
                vcode = full + '\nprint(' + ', '.join(exprs) + ')'
                if out:   # 본문 코드가 무언가 출력하면 검증 출력은 마지막 줄만 비교하도록 본문 출력을 끈다
                    vcode = ('import io, contextlib\nwith contextlib.redirect_stdout(io.StringIO()):\n'
                             + '\n'.join('    ' + ln for ln in full.split('\n'))
                             + '\nprint(' + ', '.join(exprs) + ')')
                    vexp, _ = run(vcode)
        else:
            truth = [bool(t) for _, t in items]
        right = tuple(i for i, t in enumerate(truth) if t)
        assert right, f'{qid}: 옳은 보기가 하나도 없음'
        name = lambda sub: ', '.join(MARK[i] for i in sub)
        subs = [s for r in range(1, len(items) + 1) for s in itertools.combinations(range(len(items)), r) if s != right]
        rnd = random.Random(qid)
        subs.sort(key=lambda s: (abs(len(s) - len(right)), rnd.random()))
        opts = self._place('C', n, name(right), [name(s) for s in subs[:4]])
        opts_sorted = sorted(opts, key=lambda o: (o.count(','), o))   # 수능식으로 짧은 것부터
        body = '<br>'.join(f'{MARK[i]} {fmt(t)}' for i, (t, _) in enumerate(items))
        stem = fmt(stem or '다음 코드에 대한 설명으로 옳은 것만 <보기>에서 모두 고른 것은?') + box('<보기>', body)
        return self._add(qid, 'classify', 'mc', stem, code, name(right), why, tags,
                         verifyCode=vcode, verifyExpect=vexp, ref=ref, options=opts_sorted)

    # ── 실행 결과를 고르는 문항 (상태 예측 / 경계값) ───────
    def _mc(self, letter, key, stem, code, opts, why, tags, ans=None, pre=None, chk=None, eq=True, ref=None):
        qid, n = self._id(letter)
        vcode = vexp = None
        if ans is None:
            vcode = self._full(code, pre)
            vexp, _ = run(vcode)
            ans = vexp
            assert '\n' not in ans and ans != '', f'{qid}: 출력이 한 줄이 아님 → {ans!r}'
        elif chk is not None:
            vcode = self._full(chk, pre)
            vexp, _ = run(vcode)
            assert (not eq) or vexp == str(ans), f'{qid}: 검증 출력 {vexp!r} != 정답 {ans!r}'
        return self._add(qid, key, 'mc', fmt(stem), code, str(ans), why, tags,
                         verifyCode=vcode, verifyExpect=vexp, ref=ref, options=self._place(letter, n, ans, opts))

    def R(self, code, opts, why, tags, stem='다음 코드를 실행했을 때 출력되는 것은?', **kw):
        return self._mc('R', 'trace', stem, code, opts, why, tags, **kw)

    def D(self, code, opts, why, tags, stem='다음 코드를 실행했을 때 출력되는 것은?', **kw):
        return self._mc('D', 'boundary', stem, code, opts, why, tags, **kw)

    # ── 빈칸: ㉠, ㉡ 짝 고르기 ─────────────────────────────
    def B(self, code, fill, opts, why, tags, stem=None, pre=None, result=True, exec_=True):
        qid, n = self._id('B')
        keys = BLANKS[:len(fill)]
        assert all(k in code for k in keys), f'{qid}: 빈칸 기호 누락'
        join = lambda vals: '  ·  '.join(f'{k} {v}' for k, v in zip(keys, vals))
        vcode = vexp = None
        filled = code
        for k, v in zip(keys, fill):
            filled = filled.replace(k, v)
        if exec_:
            vcode = self._full(filled, pre)
            vexp, _ = run(vcode)
            for o in opts:      # 오답 짝이 정답과 같은 출력을 내면 안 된다
                alt = code
                for k, v in zip(keys, o):
                    alt = alt.replace(k, v)
                try:
                    aout, _ = run(self._full(alt, pre))
                except Exception:
                    continue
                assert aout != vexp or not vexp, f'{qid}: 오답 {o} 도 같은 출력을 냄'
        shown = vexp if result is True else result
        stem = fmt(stem or f'{", ".join(keys)}에 들어갈 것으로 알맞은 것은?')
        if shown:
            stem += resbox(shown)
        return self._add(qid, 'blank2', 'mc', stem, code, join(fill), why, tags,
                         verifyCode=vcode, verifyExpect=vexp,
                         options=self._place('B', n, join(fill), [join(o) for o in opts]))

    # ── 대조: 두 코드의 출력 짝 ────────────────────────────
    def X(self, code, opts, why, tags, stem=None, pre=None, ans=None, labels=('방법1', '방법2')):
        qid, n = self._id('X')
        join = lambda p: f'㉠ {p[0]}  ·  ㉡ {p[1]}'
        vcode = vexp = None
        if ans is None:
            vcode = self._full(code, pre)
            vexp, _ = run(vcode)
            lines = vexp.split('\n')
            assert len(lines) == 2, f'{qid}: 출력이 두 줄이 아님 → {vexp!r}'
            ans = tuple(lines)
        stem = fmt(stem or '다음은 거의 같은 두 코드이다. ㉠, ㉡에 출력되는 값으로 알맞은 것은?')
        stem += resbox(f'{labels[0]} → ㉠\n{labels[1]} → ㉡')
        return self._add(qid, 'contrast', 'mc', stem, code, join(ans), why, tags,
                         verifyCode=vcode, verifyExpect=vexp,
                         options=self._place('X', n, join(ans), [join(o) for o in opts]))

    # ── 조건 매핑: [조건]을 만족하는 코드 ──────────────────
    def S(self, conds, ans, opts, why, tags, code='x = ____', chk=None, pre=None, stem=None):
        qid, n = self._id('S')
        vcode = vexp = None
        if chk is not None:
            vcode = self._full(code.replace('____', ans) + '\n' + chk, pre)
            vexp, _ = run(vcode)
            for o in opts:      # 오답 코드가 정답과 같은 검증 출력을 내면 안 된다
                try:
                    aout, _ = run(self._full(code.replace('____', o) + '\n' + chk, pre))
                except Exception:
                    continue
                assert aout != vexp, f'{qid}: 오답 {o!r} 도 조건을 만족함'
        stem = fmt(stem or '다음 [조건]을 모두 만족하는 코드로 알맞은 것은?')
        stem += box('[조건]', '<br>'.join('○ ' + fmt(c) for c in conds))
        return self._add(qid, 'spec', 'mc', stem, code, ans, why, tags,
                         verifyCode=vcode, verifyExpect=vexp, options=self._place('S', n, ans, opts))

    # ── 서답형 ─────────────────────────────────────────────
    def W(self, stem, ans, why, tags, accept=(), code='', pre=None, chk=None, result=True, eq=True):
        qid, n = self._id('W')
        vcode = vexp = None
        stem = fmt(stem)
        if '㉠' in code:
            vcode = self._full(code.replace('㉠', ans), pre)
            vexp, _ = run(vcode)
            if result is True and vexp:
                stem += resbox(vexp)
            elif isinstance(result, str):
                stem += resbox(result)
        elif chk is not None:
            vcode = self._full(chk, pre)
            vexp, _ = run(vcode)
            assert (not eq) or vexp == str(ans), f'{qid}: 검증 출력 {vexp!r} != 정답 {ans!r}'
        acc = [str(ans)] + [a for a in accept if a != ans]
        return self._add(qid, 'short', 'text', stem, code, str(ans), why, tags,
                         verifyCode=vcode, verifyExpect=vexp, accept=acc)

    # ── 서술형 (AI 채점) ───────────────────────────────────
    def E(self, stem, ans, rubric, tags, code='', chk=None, pre=None):
        qid, n = self._id('E')
        vcode = vexp = None
        if chk is not None:
            vcode = self._full(chk, pre)
            vexp, _ = run(vcode)
        q = self._add(qid, 'essay', 'essay', fmt(stem), code, ans, 'AI 채점 결과입니다.', list(tags) + ['서술형'],
                      verifyCode=vcode, verifyExpect=vexp, rubric=rubric)
        return q

    # ── 저장 ───────────────────────────────────────────────
    def dump(self, path, source, note):
        ids = [q['id'] for q in self.qs]
        assert len(ids) == len(set(ids))
        doc = {"version": 1, "generatedAt": "2026-11-11", "source": source, "verified": note,
               "types": TYPES, "questions": self.qs}
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(doc, f, ensure_ascii=False, indent=1)
        return doc


NOTE = ("verifyCode 가 있는 문항은 파이썬(numpy 2.5, pandas 3.0, scikit-learn 1.9)에서 실제로 실행해 정답을 확인함. "
        "ref 가 있는 문항은 코드로 검증할 수 없는 개념이나 텐서플로 실행 결과라서 노트북 본문(해당 셀)과 저장된 출력을 근거로 둠. "
        "서술형(essay)은 AI 가 rubric 으로 채점하며, 계산이 들어간 모범 답안은 verifyCode 로 실행 확인함.")


def report(bank):
    import collections
    by = collections.Counter(q['typeKey'] for q in bank.qs)
    pos = collections.Counter(q['options'].index(q['answer']) + 1 for q in bank.qs if q.get('options') and q['typeKey'] != 'classify')
    ver = sum(1 for q in bank.qs if q.get('verifyCode'))
    print(f"{bank.src}: {len(bank.qs)}문항 {dict(by)} | 정답 위치 {dict(sorted(pos.items()))} | 실행 검증 {ver}")
