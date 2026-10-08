#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""sys_parser: .sys(btor2 变体) 的词法+语法分析器。

正确的 tokenizer + 递归下降表达式解析, 保证结点名完全匹配。
替代 parse_cex.parse_sys 的逐行正则方案。

语法:
  file        := statement*
  statement   := header | transition
  header      := kind name ':' type ('=' expr)?
  transition  := '[' ('init'|'next') ']' expr
  kind        := 'input' | 'state' | 'node' | 'output' | 'constraint' | 'bad'
  expr        := IDENT | CONSTANT | FUNC '(' expr (',' expr)* ')'
  FUNC        := 'and'|'or'|'not'|'ite'|'eq'|'neq'|'concat'|'add'|'sub'|'mul'
               | 'ult'|'ule'|'ugt'|'uge'|'slt'|'sle'|'sgt'|'sge'|'shl'|'shr'
               | 'sra'|'srl'|'sll'|'xor'|'xnor'|'nand'|'nor'|'zext'|'uext'
               | 'sext'|'msb'|'implies'|'udiv'|'urem'
  CONSTANT    := NUM "'" BASE DIGITS   (如 6'b111111, 32'x0)
               | NUM                   (纯数字)

Tokenizer 保证: 标识符 = [A-Za-z_][A-Za-z0-9_.]* 的连续 token,
  不会把 a.b.c 拆碎, 也不会把 6'b 中的 b 误认为标识符。
"""

from typing import Dict, List, Set, Tuple
import re

# ------------------------------------------------------------------
# 词法分析
# ------------------------------------------------------------------

_TOKEN_SPEC = [
    ('CONSTANT',  re.compile(r"\d+'\w[0-9a-fA-FxXzZ_]*")),  # 6'b111, 32'x0
    ('NUMBER',    re.compile(r"\d+")),
    ('IDENT',     re.compile(r"[A-Za-z_][A-Za-z0-9_.]*")),   # 含点标识符
    ('LBRACKET',  re.compile(r"\[")),
    ('RBRACKET',  re.compile(r"\]")),
    ('COLON',     re.compile(r":")),
    ('EQ',        re.compile(r"=")),
    ('LPAREN',    re.compile(r"\(")),
    ('RPAREN',    re.compile(r"\)")),
    ('COMMA',     re.compile(r",")),
    ('SLICE',     re.compile(r"\[")),                         # 数组切片 [h:l]
    ('WS',        re.compile(r"\s+")),
]

_FUNCS = {
    'and', 'or', 'not', 'ite', 'eq', 'neq', 'concat', 'add', 'sub', 'mul',
    'ult', 'ule', 'ugt', 'uge', 'slt', 'sle', 'sgt', 'sge', 'shl', 'shr',
    'sra', 'srl', 'sll', 'xor', 'xnor', 'nand', 'nor', 'zext', 'uext',
    'sext', 'msb', 'implies', 'udiv', 'urem',
}

_KINDS = {'input', 'state', 'node', 'output', 'constraint', 'bad'}


def tokenize(text: str) -> List[Tuple[str, str]]:
    """文本 → [(token_type, value)] 列表"""
    tokens = []
    pos = 0
    while pos < len(text):
        matched = False
        for ttype, pattern in _TOKEN_SPEC:
            m = pattern.match(text, pos)
            if m:
                val = m.group()
                if ttype != 'WS':
                    tokens.append((ttype, val))
                pos = m.end()
                matched = True
                break
        if not matched:
            pos += 1  # 跳过无法识别的字符
    return tokens


# ------------------------------------------------------------------
# 语法分析: 表达式 → 引用的标识符集合
# ------------------------------------------------------------------

class ExprParser:
    """递归下降解析表达式, 提取引用的标识符(非函数名/非常量)。

    ite 条件边的语义区分:
    - 自保持选通 y = ite(cond, new, y)(y 出现在数据分支)是寄存器
      使能更新模式, cond 只决定"何时更新" → 不产生依赖边;
    - 其余 ite 的 cond 直接影响输出取值 → 保留依赖边。
    target: 正在被定义的变量名(用于识别自保持), None 时全部保留。
    """

    def __init__(self, tokens: List[Tuple[str, str]], start: int,
                 target: str = None):
        self.toks = tokens
        self.pos = start
        self.ids: Set[str] = set()
        self.target = target

    def peek(self) -> Tuple[str, str]:
        if self.pos < len(self.toks):
            return self.toks[self.pos]
        return ('EOF', '')

    def advance(self):
        self.pos += 1

    def parse(self) -> Set[str]:
        return self._expr()

    def _expr(self) -> Set[str]:
        """返回本子树的 id 集合"""
        ttype, val = self.peek()
        if ttype == 'CONSTANT' or ttype == 'NUMBER':
            self.advance()
            return set()
        elif ttype == 'IDENT':
            # 函数调用 or 普通标识符
            if val in _FUNCS and self.pos + 1 < len(self.toks) \
                    and self.toks[self.pos + 1] == ('LPAREN', '('):
                self.advance()  # func name
                self.advance()  # (
                if val == 'ite':
                    args = []
                    while self.peek()[0] != 'RPAREN' \
                            and self.peek()[0] != 'EOF':
                        args.append(self._expr())
                        if self.peek() == ('COMMA', ','):
                            self.advance()
                    if self.peek()[0] == 'RPAREN':
                        self.advance()
                    cond_ids = args[0] if args else set()
                    data_ids = set().union(*args[1:]) if len(args) > 1 else set()
                    # 自保持选通: 目标自身出现在数据分支 → 条件只是使能
                    if self.target and self.target in data_ids:
                        return data_ids
                    return cond_ids | data_ids
                acc: Set[str] = set()
                while self.peek()[0] != 'RPAREN' and self.peek()[0] != 'EOF':
                    acc |= self._expr()
                    if self.peek() == ('COMMA', ','):
                        self.advance()
                if self.peek()[0] == 'RPAREN':
                    self.advance()
                return acc
            else:
                self.advance()
                # 后缀切片: IDENT[hi:lo]
                while self.peek()[0] == 'LBRACKET':
                    self.advance()
                    while self.peek()[0] != 'RBRACKET' and self.peek()[0] != 'EOF':
                        self.advance()
                    if self.peek()[0] == 'RBRACKET':
                        self.advance()
                return {val}
        else:
            self.advance()  # 跳过未知 token
            return set()


# ------------------------------------------------------------------
# 主解析: .sys 文件 → 图
# ------------------------------------------------------------------

def parse_sys_proper(sys_path: str,
                     fold: bool = True) -> Tuple[Dict[str, Set[str]], Dict[str, Set[str]], Set[str]]:
    """.sys → (正向邻接 driver→{driven}, 反向邻接, input/state 名集合)。
    正式的词法+语法分析, 结点名完全匹配。"""
    fwd: Dict[str, Set[str]] = {}
    bwd: Dict[str, Set[str]] = {}
    keep: Set[str] = set()

    def add(a, b):
        fwd.setdefault(a, set()).add(b)
        bwd.setdefault(b, set()).add(a)

    lines = open(sys_path, encoding='utf-8', errors='ignore').readlines()
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        i += 1
        if not line:
            continue

        tokens = tokenize(line)
        if not tokens:
            continue

        # [init]/[next] 行
        if tokens[0][0] == 'LBRACKET' and len(tokens) > 1 \
                and tokens[1][1] in ('init', 'next'):
            if cur_state:
                # 找到表达式起始: 跳过 [ next ] 或 [ init ]
                expr_start = 2
                while expr_start < len(tokens) and tokens[expr_start][0] == 'RBRACKET':
                    expr_start += 1
                p = ExprParser(tokens, expr_start, target=cur_state)
                for rid in p.parse():
                    add(rid, cur_state)
            continue

        # 定义行: kind name : type = expr
        if tokens[0][1] in _KINDS and len(tokens) > 1:
            kind = tokens[0][1]
            name = tokens[1][1]
            cur_state = name if kind == 'state' else None

            if kind in ('input', 'state'):
                keep.add(name)
                continue

            # 找 '=' 后的表达式起始
            eq_pos = None
            for j, (tt, vv) in enumerate(tokens):
                if tt == 'EQ':
                    eq_pos = j + 1
                    break
            if eq_pos is not None and eq_pos < len(tokens):
                p = ExprParser(tokens, eq_pos, target=name)
                for rid in p.parse():
                    add(rid, name)
        else:
            cur_state = None

    # 存储器阵列折叠(编号单元 → base[*])
    if fold:
        fwd, bwd, keep, _ = fold_memory_arrays(fwd, bwd, keep)
    return fwd, bwd, keep


if __name__ == '__main__':
    import sys as _sys
    fwd, bwd, keep = parse_sys_proper(_sys.argv[1])
    print(f"节点: {len(fwd)+len(bwd)}, input/state: {len(keep)}")
    # 抽查关键边
    for check in [('icache_metaMem_tag.rmeta.data', 'icache_metaMem_tag_rmeta_data'),
                  ('icache_ren_reg', 'icache__GEN_5')]:
        a, b = check
        print(f"  {a} → {b}: {'✓' if b in fwd.get(a,set()) else '✗'}")


# ------------------------------------------------------------------
# 存储器阵列折叠
# ------------------------------------------------------------------

import re as _re

_BASE_FROM_PORT = _re.compile(r'^(.+?)[._](?:MPORT|rdata)[._]')
_ARRAY_1D = _re.compile(r'^(.+?)_(\d+)$')
_ARRAY_2D = _re.compile(r'^(.+?)_(\d+)_(\d+)$')


def extract_memory_bases(names) -> set:
    """从端口引用(MPORT/rdata)提取存储器基名"""
    bases = set()
    for n in names:
        m = _BASE_FROM_PORT.match(n)
        if m:
            bases.add(m.group(1))
    return bases


def normalize_name(name: str, bases: set) -> str:
    """编号阵列单元 → 折叠为 base[*]"""
    for base in sorted(bases, key=len, reverse=True):
        if name.startswith(base + '_'):
            suffix = name[len(base) + 1:]
            # 纯数字(一维: _N)
            if _re.match(r'^\d+$', suffix):
                return base + '[*]'
            # 二维: _W_S — base 可能含一级索引
            m2 = _re.match(r'^(\d+)_(\d+)$', suffix)
            if m2:
                # dataMem_0_0 → dataMem[*] (去掉 way 索引)
                base_2d = _re.sub(r'_\d+$', '', base)
                return base_2d + '[*]'
            # dataMem_0_0_MPORT_1_addr 类端口不折叠(已有前缀匹配但后缀非纯数字)
            break
    return name


def fold_memory_arrays(fwd, bwd, keep):
    """折叠存储器阵列: 编号单元归一为 base[*], 重建去重后的图"""
    all_names = set(list(fwd.keys()) + list(bwd.keys()))
    bases = extract_memory_bases(all_names)
    if not bases:
        return fwd, bwd, keep, 0

    # 名字映射
    remap = {}
    folded_count = 0
    for n in all_names:
        new = normalize_name(n, bases)
        if new != n:
            remap[n] = new
            folded_count += 1

    # 重建图
    new_fwd = {}
    new_bwd = {}
    for a, targets in fwd.items():
        na = remap.get(a, a)
        for b in targets:
            nb = remap.get(b, b)
            if na != nb:  # 去自环(折叠产生的)
                new_fwd.setdefault(na, set()).add(nb)
                new_bwd.setdefault(nb, set()).add(na)
    new_keep = {remap.get(k, k) for k in keep}

    # 去重后的节点数
    return new_fwd, new_bwd, new_keep, folded_count
