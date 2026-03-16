#!/usr/bin/env python3
"""
C/C++ code augmentation framework using libclang-backed AST analysis.

All transforms discover candidates from libclang cursors and rewrite exact source
spans from the original code instead of scanning with regexes.
"""

from __future__ import annotations

import argparse
import json
import random
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, Optional

from pydantic import BaseModel, ConfigDict, Field

try:
    import clang.cindex as ci
    from clang.cindex import CursorKind, TokenKind, TypeKind
except ImportError as exc:
    raise ImportError(
        "libclang Python bindings not found. Install with: pip install libclang"
    ) from exc


PARSE_ARGS = [
    "-xc++",
    "-std=c++17",
    "-D__global__=",
    "-D__device__=",
    "-D__host__=",
    "-D__shared__=",
    "-D__constant__=",
    "-D__kernel__=",
    "-D__syncthreads()=",
    "-D__launch_bounds__(x)=",
    "-D__restrict__=",
    "-isystem", "/opt/sycl/lib/clang/23/include",
    "-isystem", "/usr/include/c++/11",
    "-isystem", "/usr/include/x86_64-linux-gnu/c++/11",
    "-isystem", "/usr/include/c++/11/backward",
    "-isystem", "/usr/lib/gcc/x86_64-linux-gnu/11/include",
    "-isystem", "/usr/local/include",
    "-isystem", "/usr/include/x86_64-linux-gnu",
    "-isystem", "/usr/include",
]
PARSE_OPTIONS = (
    ci.TranslationUnit.PARSE_DETAILED_PROCESSING_RECORD
    | getattr(ci.TranslationUnit, "PARSE_INCOMPLETE", 0)
)
BASELINE_ERROR_THRESHOLD = 100
UNWRAP_KINDS = {
    CursorKind.UNEXPOSED_EXPR,
    getattr(CursorKind, "PAREN_EXPR", CursorKind.UNEXPOSED_EXPR),
}
COMPARISON_OPERATORS = {"<", ">", "<=", ">=", "==", "!="}
COMPOUND_OPERATORS = {
    "+=": "+",
    "-=": "-",
    "*=": "*",
    "/=": "/",
    "%=": "%",
    "&=": "&",
    "|=": "|",
    "^=": "^",
    "<<=": "<<",
    ">>=": ">>",
}
INTEGER_TYPE_KINDS = {
    TypeKind.BOOL,
    TypeKind.CHAR_U,
    TypeKind.UCHAR,
    TypeKind.CHAR16,
    TypeKind.CHAR32,
    TypeKind.USHORT,
    TypeKind.UINT,
    TypeKind.ULONG,
    TypeKind.ULONGLONG,
    TypeKind.UINT128,
    TypeKind.CHAR_S,
    TypeKind.SCHAR,
    TypeKind.WCHAR,
    TypeKind.SHORT,
    TypeKind.INT,
    TypeKind.LONG,
    TypeKind.LONGLONG,
    TypeKind.INT128,
}
ARRAY_LIKE_TYPE_KINDS = {
    TypeKind.POINTER,
    TypeKind.CONSTANTARRAY,
    TypeKind.INCOMPLETEARRAY,
    TypeKind.VARIABLEARRAY,
    TypeKind.DEPENDENTSIZEDARRAY,
}


@dataclass
class TransformResult:
    """Result of attempting a transform."""

    applied: bool
    code: str
    description: str = ""


class TextEdit(BaseModel):
    start_offset: int
    end_offset: int
    replacement: str


class RewriteCandidate(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    description: str
    edits: list[TextEdit] = Field(default_factory=list)


class Transform(ABC):
    """Base class for code transforms."""

    name: str = "BaseTransform"

    def __init__(self, level: int = 4):
        self.level = level

    @abstractmethod
    def is_applicable(self, code: str, index: ci.Index) -> bool:
        """Check if this transform can be applied to the code."""

    @abstractmethod
    def apply(self, code: str, index: ci.Index) -> TransformResult:
        """Apply the transform to the code."""


def _parse_translation_unit(
    code: str,
    index: ci.Index,
    filename: str = "tmp.cpp",
) -> ci.TranslationUnit:
    return index.parse(
        path=filename,
        args=PARSE_ARGS,
        unsaved_files=[(filename, code)],
        options=PARSE_OPTIONS,
    )


def _is_low_quality_tu(tu: ci.TranslationUnit) -> bool:
    """Return True if the TU has fatal errors or too many diagnostics."""
    error_count = 0
    for d in tu.diagnostics:
        if d.severity >= ci.Diagnostic.Fatal:
            return True
        if d.severity >= ci.Diagnostic.Error:
            error_count += 1
    return error_count > 50


def _iter_cursors(cursor: ci.Cursor) -> Iterable[ci.Cursor]:
    yield cursor
    for child in cursor.get_children():
        yield from _iter_cursors(child)


def _cursor_in_main_file(cursor: ci.Cursor, filename: str) -> bool:
    try:
        location = cursor.location
        return bool(location.file) and location.file.name == filename
    except Exception:
        return False


def _is_macro_expansion(cursor: ci.Cursor) -> bool:
    """Check if the cursor is part of a macro expansion."""
    try:
        loc = cursor.location
        if not loc or not loc.file:
            return False
        # get_instantiation returns (file, line, column, offset) of the expansion site.
        # If it differs from the physical location, it is likely inside a macro.
        # Also check if any parent is a MACRO_EXPANSION/INSTANTIATION.
        s_file, s_line, s_col, s_off = loc._get_instantiation()
        if s_line != loc.line or s_col != loc.column or s_off != loc.offset:
            return True

        # Fallback: check parents for macro instantiation
        curr = cursor
        while curr:
            if curr.kind == ci.CursorKind.MACRO_INSTANTIATION:
                return True
            # Stop if we hit a function or translation unit
            if curr.kind in (ci.CursorKind.FUNCTION_DECL, ci.CursorKind.TRANSLATION_UNIT):
                break
            curr = curr.semantic_parent
        return False
    except Exception:
        return False


def _cursor_offsets(cursor: ci.Cursor) -> tuple[int, int]:
    return cursor.extent.start.offset, cursor.extent.end.offset


def _source_text(code: str, cursor: ci.Cursor) -> str:
    start, end = _cursor_offsets(cursor)
    return code[start:end]


def _unwrap_expr(cursor: ci.Cursor) -> ci.Cursor:
    current = cursor
    while current.kind in UNWRAP_KINDS:
        children = list(current.get_children())
        if len(children) != 1:
            break
        current = children[0]
    return current


def _children(cursor: ci.Cursor) -> list[ci.Cursor]:
    return [_unwrap_expr(child) for child in cursor.get_children()]


def _strip_outer_parens(text: str) -> str:
    stripped = text.strip()
    while stripped.startswith("(") and stripped.endswith(")"):
        depth = 0
        balanced = True
        for idx, ch in enumerate(stripped):
            if ch == "(":
                depth += 1
            elif ch == ")":
                depth -= 1
            if depth == 0 and idx != len(stripped) - 1:
                balanced = False
                break
        if not balanced or depth != 0:
            break
        stripped = stripped[1:-1].strip()
    return stripped


def _normalized_expr_text(text: str) -> str:
    return " ".join(_strip_outer_parens(text).split())


def _binary_operator_text(code: str, cursor: ci.Cursor) -> Optional[str]:
    children = _children(cursor)
    if len(children) != 2:
        return None
    left_end = children[0].extent.end.offset
    right_start = children[1].extent.start.offset
    between = code[left_end:right_start]
    for operator in sorted(COMPARISON_OPERATORS | set(COMPOUND_OPERATORS) | set(COMPOUND_OPERATORS.values()) | {"="}, key=len, reverse=True):
        if operator in between:
            return operator
    return None


def _unary_prefix_text(code: str, cursor: ci.Cursor) -> str:
    children = _children(cursor)
    if len(children) != 1:
        return ""
    start, _ = _cursor_offsets(cursor)
    child_start = children[0].extent.start.offset
    return code[start:child_start]


def _identifier_range(cursor: ci.Cursor, spelling: Optional[str] = None) -> Optional[tuple[int, int]]:
    target = spelling or cursor.spelling
    for token in cursor.get_tokens():
        if token.kind != TokenKind.IDENTIFIER:
            continue
        if token.spelling != target:
            continue
        return token.extent.start.offset, token.extent.end.offset
    return None


def _apply_candidate(code: str, candidate: RewriteCandidate) -> str:
    # libclang reports byte offsets (UTF-8). Operate on the encoded bytes so that
    # multi-byte Unicode characters (e.g. em-dashes in comments) do not cause a
    # mismatch between Python str character indices and libclang byte offsets.
    rewritten_bytes = code.encode("utf-8")
    seen_ranges: set[tuple[int, int]] = set()
    for edit in sorted(candidate.edits, key=lambda item: item.start_offset, reverse=True):
        key = (edit.start_offset, edit.end_offset)
        if key in seen_ranges:
            continue
        seen_ranges.add(key)
        replacement_bytes = edit.replacement.encode("utf-8")
        rewritten_bytes = (
            rewritten_bytes[: edit.start_offset]
            + replacement_bytes
            + rewritten_bytes[edit.end_offset :]
        )
    return rewritten_bytes.decode("utf-8")


def _fatal_diagnostics(tu: ci.TranslationUnit) -> int:
    return sum(
        1
        for diag in tu.diagnostics
        if diag.severity >= ci.Diagnostic.Error
    )


def _validate_rewrite(candidate: RewriteCandidate, code: str, index: ci.Index) -> bool:
    rewritten = _apply_candidate(code, candidate)
    try:
        baseline = _parse_translation_unit(code, index)
        updated = _parse_translation_unit(rewritten, index)
    except Exception:
        return False
    return _fatal_diagnostics(updated) <= _fatal_diagnostics(baseline)


class AstTransform(Transform):
    """Base class for transforms that produce AST-backed rewrite candidates."""

    def is_applicable(self, code: str, index: ci.Index) -> bool:
        return bool(self._find_candidates(code, index))

    def apply(self, code: str, index: ci.Index) -> TransformResult:
        tu = _parse_translation_unit(code, index)
        # Baseline check: if the TU is too broken, skip transformation
        if _fatal_diagnostics(tu) > BASELINE_ERROR_THRESHOLD:
            return TransformResult(False, code, f"{self.name}: too many baseline errors")

        candidates = self._find_candidates(code, index)
        if not candidates:
            return TransformResult(False, code, f"{self.name}: 0 changes")

        valid_candidates = [
            candidate
            for candidate in candidates
            if _validate_rewrite(candidate, code, index)
        ]
        if not valid_candidates:
            return TransformResult(False, code, f"{self.name}: 0 changes")

        # Based on level, determine how many non-overlapping edits to apply
        if self.level == 1:
            num_to_select = 1
        elif self.level == 2:
            num_to_select = max(1, int(len(valid_candidates) * 0.33))
        elif self.level == 3:
            num_to_select = max(1, int(len(valid_candidates) * 0.66))
        else:
            num_to_select = len(valid_candidates)
            
        selected_candidates = random.sample(valid_candidates, num_to_select)

        # Fix A: remove candidates whose edit ranges overlap with already-selected ones.
        def _edits_overlap(c1: RewriteCandidate, c2: RewriteCandidate) -> bool:
            for e1 in c1.edits:
                for e2 in c2.edits:
                    if not (e1.end_offset <= e2.start_offset or e2.end_offset <= e1.start_offset):
                        return True
            return False

        non_overlapping: list[RewriteCandidate] = []
        for c in selected_candidates:
            if not any(_edits_overlap(c, existing) for existing in non_overlapping):
                non_overlapping.append(c)
        selected_candidates = non_overlapping

        if not selected_candidates:
            return TransformResult(False, code, f"{self.name}: 0 changes")

        all_edits = []
        for c in selected_candidates:
            all_edits.extend(c.edits)

        # Re-validate the merged candidate before applying.
        merged = RewriteCandidate(
            description=f"{self.name}: {len(selected_candidates)} candidates applied",
            edits=all_edits
        )
        if not _validate_rewrite(merged, code, index):
            return TransformResult(False, code, f"{self.name}: merged candidate failed validation")

        rewritten = _apply_candidate(code, merged)
        return TransformResult(True, rewritten, merged.description)

    @abstractmethod
    def _find_candidates(self, code: str, index: ci.Index) -> list[RewriteCandidate]:
        """Collect AST-backed rewrite candidates."""


class ArithmeticTransform(AstTransform):
    """
    Converts augmented assignments to expanded form and vice versa.
    x += 1 <-> x = x + 1
    """

    name = "ArithmeticTransform"

    def _find_candidates(self, code: str, index: ci.Index) -> list[RewriteCandidate]:
        tu = _parse_translation_unit(code, index)
        filename = tu.spelling
        candidates: list[RewriteCandidate] = []
        reverse_ops = {value: key for key, value in COMPOUND_OPERATORS.items()}
        compound_kind = getattr(CursorKind, "COMPOUND_ASSIGNMENT_OPERATOR", None)

        for cursor in _iter_cursors(tu.cursor):
            if not _cursor_in_main_file(cursor, filename) or _is_macro_expansion(cursor):
                continue

            if compound_kind is not None and cursor.kind == compound_kind:
                children = _children(cursor)
                if len(children) != 2:
                    continue
                lhs, rhs = children
                operator = _binary_operator_text(code, cursor)
                if operator not in COMPOUND_OPERATORS:
                    continue
                lhs_text = _source_text(code, lhs).strip()
                rhs_text = _source_text(code, rhs).strip()
                start, end = _cursor_offsets(cursor)
                candidates.append(
                    RewriteCandidate(
                        description=f"{self.name}: 1 changes",
                        edits=[
                            TextEdit(
                                start_offset=start,
                                end_offset=end,
                                replacement=f"{lhs_text} = {lhs_text} {COMPOUND_OPERATORS[operator]} ({rhs_text})",
                            )
                        ],
                    )
                )
                continue

            if cursor.kind != CursorKind.BINARY_OPERATOR:
                continue

            operator = _binary_operator_text(code, cursor)
            if operator != "=":
                continue

            children = _children(cursor)
            if len(children) != 2:
                continue
            lhs, rhs = children
            rhs = _unwrap_expr(rhs)
            if rhs.kind != CursorKind.BINARY_OPERATOR:
                continue
            rhs_operator = _binary_operator_text(code, rhs)
            if rhs_operator not in reverse_ops:
                continue

            rhs_children = _children(rhs)
            if len(rhs_children) != 2:
                continue
            rhs_left, rhs_right = rhs_children
            lhs_text = _source_text(code, lhs).strip()
            rhs_left_text = _source_text(code, rhs_left).strip()
            rhs_right_text = _source_text(code, rhs_right).strip()
            if _normalized_expr_text(lhs_text) != _normalized_expr_text(rhs_left_text):
                continue

            start, end = _cursor_offsets(cursor)
            candidates.append(
                RewriteCandidate(
                    description=f"{self.name}: 1 changes",
                    edits=[
                        TextEdit(
                            start_offset=start,
                            end_offset=end,
                            replacement=f"{lhs_text} {reverse_ops[rhs_operator]} {rhs_right_text}",
                        )
                    ],
                )
            )

        return candidates


ASSIGNMENT_OPERATORS = {"="} | set(COMPOUND_OPERATORS)


def _contains_assignment(code: str, cursor: ci.Cursor) -> bool:
    """Return True if any node in the subtree performs an assignment."""
    if cursor.kind == CursorKind.BINARY_OPERATOR:
        op = _binary_operator_text(code, cursor)
        if op in ASSIGNMENT_OPERATORS:
            return True
    for child in cursor.get_children():
        if _contains_assignment(code, child):
            return True
    return False


class SwapCondition(AstTransform):
    """
    Swaps operands of comparison expressions.
    a < b -> b > a
    """

    name = "SwapCondition"
    SWAP_MAP = {
        "<": ">",
        ">": "<",
        "<=": ">=",
        ">=": "<=",
        "==": "==",
        "!=": "!=",
    }

    def _find_candidates(self, code: str, index: ci.Index) -> list[RewriteCandidate]:
        tu = _parse_translation_unit(code, index)
        filename = tu.spelling
        candidates: list[RewriteCandidate] = []

        for cursor in _iter_cursors(tu.cursor):
            if cursor.kind != CursorKind.BINARY_OPERATOR:
                continue
            if not _cursor_in_main_file(cursor, filename) or _is_macro_expansion(cursor):
                continue

            operator = _binary_operator_text(code, cursor)
            if operator not in self.SWAP_MAP:
                continue

            children = _children(cursor)
            if len(children) != 2:
                continue
            lhs, rhs = children
            # Fix C: skip comparisons where either operand contains an assignment.
            # Swapping would produce a non-lvalue or change program semantics.
            if _contains_assignment(code, lhs) or _contains_assignment(code, rhs):
                continue
            start, end = _cursor_offsets(cursor)
            lhs_text = _source_text(code, lhs).strip()
            rhs_text = _source_text(code, rhs).strip()
            candidates.append(
                RewriteCandidate(
                    description=f"{self.name}: 1 changes",
                    edits=[
                        TextEdit(
                            start_offset=start,
                            end_offset=end,
                            replacement=f"{rhs_text} {self.SWAP_MAP[operator]} {lhs_text}",
                        )
                    ],
                )
            )

        return candidates


def _is_array_like(cursor: ci.Cursor) -> bool:
    return cursor.type.kind in ARRAY_LIKE_TYPE_KINDS


def _is_integer_like(cursor: ci.Cursor) -> bool:
    return cursor.type.kind in INTEGER_TYPE_KINDS


class PointerArithmeticToArrayIndex(AstTransform):
    """
    Converts between pointer arithmetic and array indexing.
    *(arr + i) <-> arr[i]
    *(i + arr) <-> arr[i]
    """

    name = "PointerArithmeticToArrayIndex"

    def _pointer_addition_parts(
        self,
        code: str,
        cursor: ci.Cursor,
    ) -> Optional[tuple[str, str]]:
        if cursor.kind != CursorKind.UNARY_OPERATOR:
            return None
        if "*" not in _unary_prefix_text(code, cursor):
            return None

        children = _children(cursor)
        if len(children) != 1:
            return None
        child = _unwrap_expr(children[0])
        if child.kind != CursorKind.BINARY_OPERATOR:
            return None
        if _binary_operator_text(code, child) != "+":
            return None

        operands = _children(child)
        if len(operands) != 2:
            return None
        left, right = operands
        if _is_array_like(left) and _is_integer_like(right):
            return _source_text(code, left).strip(), _source_text(code, right).strip()
        if _is_array_like(right) and _is_integer_like(left):
            return _source_text(code, right).strip(), _source_text(code, left).strip()
        return None

    def _find_candidates(self, code: str, index: ci.Index) -> list[RewriteCandidate]:
        tu = _parse_translation_unit(code, index)
        filename = tu.spelling
        candidates: list[RewriteCandidate] = []

        for cursor in _iter_cursors(tu.cursor):
            if not _cursor_in_main_file(cursor, filename) or _is_macro_expansion(cursor):
                continue

            parts = self._pointer_addition_parts(code, cursor)
            if parts is None:
                continue
            base_text, idx_text = parts
            if not base_text or not idx_text:
                continue
            start, end = _cursor_offsets(cursor)
            candidates.append(
                RewriteCandidate(
                    description=f"{self.name}: 1 changes",
                    edits=[
                        TextEdit(
                            start_offset=start,
                            end_offset=end,
                            replacement=f"({base_text})[{idx_text}]",
                        )
                    ],
                )
            )

        return candidates


class TypedefExpansion(AstTransform):
    """Expands typedef aliases at AST-identified type-reference sites."""

    name = "TypedefExpansion"

    def _find_candidates(self, code: str, index: ci.Index) -> list[RewriteCandidate]:
        tu = _parse_translation_unit(code, index)
        filename = tu.spelling
        alias_by_usr: dict[str, tuple[str, str]] = {}

        for cursor in _iter_cursors(tu.cursor):
            if cursor.kind != CursorKind.TYPEDEF_DECL:
                continue
            if not _cursor_in_main_file(cursor, filename) or _is_macro_expansion(cursor):
                continue
            usr = cursor.get_usr()
            if not usr:
                continue
            alias_by_usr[usr] = (
                cursor.spelling,
                cursor.underlying_typedef_type.spelling,
            )

        candidates: list[RewriteCandidate] = []
        for cursor in _iter_cursors(tu.cursor):
            if cursor.kind != CursorKind.TYPE_REF:
                continue
            if not _cursor_in_main_file(cursor, filename) or _is_macro_expansion(cursor):
                continue
            referenced = cursor.referenced
            if referenced is None:
                continue
            entry = alias_by_usr.get(referenced.get_usr())
            if entry is None:
                continue
            alias, underlying = entry
            # Safety: avoid expanding complex types (like template instances) to 'int'
            # which often happens when libclang fails to resolve the full type.
            if underlying == "int" and alias != "int" and not any(x in alias.lower() for x in ["int", "count", "size", "offset", "id", "index"]):
                continue

            token_range = _identifier_range(cursor, alias)
            if token_range is None:
                continue
            start, end = token_range
            candidates.append(
                RewriteCandidate(
                    description=f"{self.name}: 1 changes",
                    edits=[
                        TextEdit(
                            start_offset=start,
                            end_offset=end,
                            replacement=underlying,
                        )
                    ],
                )
            )

        return candidates


class ChangeNames(Transform):
    """
    Consistently renames local variables and function parameters using symbol-aware
    reference collection from libclang.
    """

    name = "ChangeNames"
    RESERVED = {
        "auto",
        "break",
        "case",
        "char",
        "const",
        "continue",
        "default",
        "do",
        "double",
        "else",
        "enum",
        "extern",
        "float",
        "for",
        "goto",
        "if",
        "int",
        "long",
        "register",
        "return",
        "short",
        "signed",
        "sizeof",
        "static",
        "struct",
        "switch",
        "typedef",
        "union",
        "unsigned",
        "void",
        "volatile",
        "while",
        "bool",
        "true",
        "false",
        "nullptr",
        "class",
        "public",
        "private",
        "protected",
        "virtual",
        "template",
        "typename",
        "namespace",
        "using",
        "new",
        "delete",
        "this",
        "throw",
        "try",
        "catch",
        "printf",
        "scanf",
        "malloc",
        "free",
        "calloc",
        "realloc",
        "memcpy",
        "memset",
        "strlen",
        "strcmp",
        "strcpy",
        "strcat",
        "fopen",
        "fclose",
        "fprintf",
        "fscanf",
        "fread",
        "fwrite",
        "exit",
        "abort",
        "assert",
        "sqrt",
        "pow",
        "exp",
        "log",
        "log2",
        "log10",
        "sin",
        "cos",
        "tan",
        "asin",
        "acos",
        "atan",
        "atan2",
        "floor",
        "ceil",
        "fabs",
        "abs",
        "min",
        "max",
        "fmin",
        "fmax",
        "omp_get_thread_num",
        "omp_get_num_threads",
        "omp_set_num_threads",
        "size_t",
        "ptrdiff_t",
        "int8_t",
        "int16_t",
        "int32_t",
        "int64_t",
        "uint8_t",
        "uint16_t",
        "uint32_t",
        "uint64_t",
        "main",
        "argc",
        "argv",
    }
    NAME_PREFIXES = ["v", "x", "tmp", "val", "var", "data", "elem", "item"]

    def _owning_function(self, cursor: ci.Cursor) -> Optional[ci.Cursor]:
        current = cursor.semantic_parent
        while current is not None and current.kind != CursorKind.TRANSLATION_UNIT:
            if current.kind in {
                CursorKind.FUNCTION_DECL,
                getattr(CursorKind, "CXX_METHOD", CursorKind.FUNCTION_DECL),
                getattr(CursorKind, "CONSTRUCTOR", CursorKind.FUNCTION_DECL),
                getattr(CursorKind, "DESTRUCTOR", CursorKind.FUNCTION_DECL),
            }:
                return current
            current = current.semantic_parent
        return None

    def _macro_identifiers(self, tu: ci.TranslationUnit) -> set[str]:
        """Collect all identifiers that appear within macro definitions."""
        idents = set()
        for cursor in _iter_cursors(tu.cursor):
            if cursor.kind == CursorKind.MACRO_DEFINITION:
                for token in cursor.get_tokens():
                    if token.kind == TokenKind.IDENTIFIER:
                        idents.add(token.spelling)
        return idents

    def _renamable_decls(
        self,
        tu: ci.TranslationUnit,
    ) -> list[ci.Cursor]:
        if _is_low_quality_tu(tu):
            return []
        filename = tu.spelling
        decls: list[ci.Cursor] = []
        macro_idents = self._macro_identifiers(tu)
        for cursor in _iter_cursors(tu.cursor):
            if cursor.kind not in {CursorKind.VAR_DECL, CursorKind.PARM_DECL}:
                continue
            if not _cursor_in_main_file(cursor, filename) or _is_macro_expansion(cursor):
                continue
            if len(cursor.spelling) <= 1 or cursor.spelling in self.RESERVED or cursor.spelling in macro_idents:
                continue
            if self._owning_function(cursor) is None:
                continue
            decls.append(cursor)
        return decls

    def _existing_identifiers(self, tu: ci.TranslationUnit) -> set[str]:
        return {
            token.spelling
            for token in tu.get_tokens(extent=tu.cursor.extent)
            if token.kind == TokenKind.IDENTIFIER
        }

    def _fresh_name(self, used_names: set[str], counter: int) -> str:
        while True:
            candidate = f"{random.choice(self.NAME_PREFIXES)}_{counter}"
            counter += 1
            if candidate in used_names or candidate in self.RESERVED:
                continue
            used_names.add(candidate)
            return candidate

    def _symbol_edits(
        self,
        code: str,
        tu: ci.TranslationUnit,
        decl: ci.Cursor,
        new_name: str,
    ) -> list[TextEdit]:
        usr = decl.get_usr()
        if not usr:
            return []

        owner = self._owning_function(decl)
        if owner is None:
            return []

        edits: list[TextEdit] = []
        decl_range = _identifier_range(decl)
        if decl_range is not None:
            edits.append(
                TextEdit(
                    start_offset=decl_range[0],
                    end_offset=decl_range[1],
                    replacement=new_name,
                )
            )

        for cursor in _iter_cursors(owner):
            if cursor.kind != CursorKind.DECL_REF_EXPR:
                continue
            referenced = cursor.referenced
            if referenced is None or referenced.get_usr() != usr:
                continue
            token_range = _identifier_range(cursor)
            if token_range is None:
                continue
            edits.append(
                TextEdit(
                    start_offset=token_range[0],
                    end_offset=token_range[1],
                    replacement=new_name,
                )
            )

        # Fallback: scan all tokens in the owning function for identifier tokens
        # matching the declaration's spelling.  libclang does not emit DECL_REF_EXPR
        # for every reference site in CUDA code (e.g. cudaMemcpy arguments and
        # kernel-launch <<< >>> syntax are often opaque to the AST).  A pure token
        # scan catches those sites so the rename stays consistent.
        #
        # Safety: we only add sites that the AST walk missed; the result is still
        # validated by _validate_rewrite before it is accepted.
        spelling = decl.spelling
        if spelling:
            # Check if there are other renamable declarations with same spelling in same owner
            # to avoid mis-attributing an unresolved token.
            other_decls_with_same_spelling = [
                d for d in self._renamable_decls(tu)
                if d.spelling == spelling and d.get_usr() != usr
                and self._owning_function(d) == owner
            ]
            
            ast_offsets: set[int] = {e.start_offset for e in edits}
            for token in owner.get_tokens():
                if token.kind != TokenKind.IDENTIFIER:
                    continue
                if token.spelling != spelling:
                    continue
                start = token.extent.start.offset
                end = token.extent.end.offset
                if start not in ast_offsets:
                    # libclang has missed this site, but it is often still a known symbol
                    # in its database (e.g. a struct member with same name). Check it.
                    site_cursor = ci.Cursor.from_location(tu, token.extent.start)
                    if (
                        site_cursor.kind != CursorKind.INVALID_FILE
                        and site_cursor.referenced
                        and site_cursor.referenced.get_usr() != usr
                    ):
                        continue

                    if _is_macro_expansion(site_cursor):
                        continue

                    # If the site is unresolved (referenced is None), but we have other candidates
                    # with the same spelling in this function, we must skip to avoid a collision.
                    if not site_cursor.referenced and other_decls_with_same_spelling:
                        continue

                    edits.append(
                        TextEdit(
                            start_offset=start,
                            end_offset=end,
                            replacement=new_name,
                        )
                    )

        unique: dict[tuple[int, int], TextEdit] = {}
        for edit in edits:
            unique[(edit.start_offset, edit.end_offset)] = edit
        return sorted(unique.values(), key=lambda item: item.start_offset)

    def is_applicable(self, code: str, index: ci.Index) -> bool:
        tu = _parse_translation_unit(code, index)
        return bool(self._renamable_decls(tu))

    def apply(self, code: str, index: ci.Index) -> TransformResult:
        tu = _parse_translation_unit(code, index)
        decls = self._renamable_decls(tu)
        if not decls:
            return TransformResult(False, code, f"{self.name}: renamed_vars=0, replaced_occurrences=0")

        used_names = self._existing_identifiers(tu)
        counter = 0
        selected_edits: list[TextEdit] = []
        renamed_vars = 0

        for decl in decls:
            if self.level == 1 and renamed_vars >= 1:
                continue
            if self.level == 2 and random.random() > 0.33:
                continue
            if self.level == 3 and random.random() > 0.66:
                continue
            
            new_name = self._fresh_name(used_names, counter)
            counter += 1
            edits = self._symbol_edits(code, tu, decl, new_name)
            if not edits:
                continue
            selected_edits.extend(edits)
            renamed_vars += 1

        if not selected_edits:
            return TransformResult(False, code, f"{self.name}: renamed_vars=0, replaced_occurrences=0")

        candidate = RewriteCandidate(
            description=f"{self.name}: renamed_vars={renamed_vars}, replaced_occurrences={len(selected_edits)}",
            edits=selected_edits,
        )
        if not _validate_rewrite(candidate, code, index):
            return TransformResult(False, code, f"{self.name}: renamed_vars=0, replaced_occurrences=0")

        return TransformResult(True, _apply_candidate(code, candidate), candidate.description)


@dataclass
class AugmentationConfig:
    """Configuration for the augmentation process."""
    level: int = 4  # Aggressiveness level (1-4)
    seed: Optional[int] = None
    transforms: list[Transform] = field(default_factory=list)
    probability: float = 0.5  # Per-transform application probability


def load_jsonl(path: Path) -> list[dict]:
    """Load a JSONL file, skipping commented lines."""
    samples = []
    with open(path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('//'):
                continue
            try:
                samples.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return samples


def save_jsonl(samples: list[dict], path: Path) -> None:
    """Save samples to a JSONL file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w') as f:
        for sample in samples:
            f.write(json.dumps(sample) + '\n')


def augment_code(code: str, config: AugmentationConfig, index: ci.Index) -> tuple[str, list[str]]:
    """
    Apply augmentation transforms to code.
    
    Returns:
        Tuple of (augmented_code, list of applied transform names)
    """
    result = code
    applied_transforms = []
    
    transforms_to_try = list(config.transforms)
    random.shuffle(transforms_to_try)
    
    if config.level == 1:
        num_transforms = 1
    elif config.level == 2:
        num_transforms = max(1, int(len(transforms_to_try) * 0.33))
    elif config.level == 3:
        num_transforms = max(1, int(len(transforms_to_try) * 0.66))
    else:
        num_transforms = len(transforms_to_try)
        
    transforms_to_try = transforms_to_try[:num_transforms]
    
    for transform in config.transforms:
        # We enforce the limited pool by only running if not filtered out
        if transform not in transforms_to_try:
            continue
        if transform.is_applicable(result, index):
            transform_result = transform.apply(result, index)
            if transform_result.applied:
                result = transform_result.code
                applied_transforms.append(transform.name)
    
    return result, applied_transforms


def augment_sample(sample: dict, config: AugmentationConfig, index: ci.Index) -> dict:
    """Augment a single sample."""
    augmented = sample.copy()
    augmented_code = {}
    all_transforms = []
    
    code_dict = sample.get('code', {})
    for filename, code_content in code_dict.items():
        # Handle case where code_content is just a filename reference
        if code_content == filename or len(code_content) < 50:
            # This is just a reference, not actual code
            augmented_code[filename] = code_content
            continue
        
        aug_code, transforms = augment_code(code_content, config, index)
        augmented_code[filename] = aug_code
        all_transforms.extend(transforms)
    
    augmented['code'] = augmented_code
    augmented['augmentation'] = {
        'transforms_applied': all_transforms,
        'original_kernel': sample.get('kernel_name', 'unknown')
    }
    
    return augmented


def main():
    parser = argparse.ArgumentParser(
        description='Augment C/C++ code dataset with semantics-preserving transforms'
    )
    parser.add_argument(
        '--input', '-i',
        type=Path,
        required=True,
        help='Input JSONL file or directory containing JSONL files'
    )
    parser.add_argument(
        '--output', '-o',
        type=Path,
        required=True,
        help='Output directory for augmented dataset'
    )
    parser.add_argument(
        '--augment_level', '-l',
        type=int,
        choices=[1, 2, 3, 4],
        default=4,
        help='Aggressiveness level (1=light, 4=aggressive) (default: 4)'
    )
    parser.add_argument(
        '--seed', '-s',
        type=int,
        default=None,
        help='Random seed for reproducibility'
    )
    parser.add_argument(
        '--include-original',
        action='store_true',
        help='Include original samples alongside augmented ones'
    )
    
    args = parser.parse_args()
    
    if args.seed is not None:
        random.seed(args.seed)
    
    # Initialize libclang
    index = ci.Index.create()
    
    # Configure transforms
    config = AugmentationConfig(
        level=args.augment_level,
        seed=args.seed,
        transforms=[
            ArithmeticTransform(level=args.augment_level),
            SwapCondition(level=args.augment_level),
            PointerArithmeticToArrayIndex(level=args.augment_level),
            TypedefExpansion(level=args.augment_level),
            ChangeNames(level=args.augment_level),
        ]
    )
    
    # Process input
    input_path = args.input
    output_dir = args.output
    output_dir.mkdir(parents=True, exist_ok=True)
    
    if input_path.is_file():
        input_files = [input_path]
    else:
        input_files = list(input_path.glob('*.jsonl'))
    
    total_samples = 0
    total_augmented = 0
    
    for input_file in input_files:
        print(f"Processing {input_file}...")
        samples = load_jsonl(input_file)
        
        output_samples = []
        
        for sample in samples:
            total_samples += 1
            
            # Optionally include original
            if args.include_original:
                original = sample.copy()
                original['augmentation'] = {'transforms_applied': [], 'is_original': True}
                output_samples.append(original)
            
            # Create augmented version
            augmented = augment_sample(sample, config, index)
            
            # Only include if something was actually changed
            if augmented.get('augmentation', {}).get('transforms_applied'):
                output_samples.append(augmented)
                total_augmented += 1
            elif not args.include_original:
                # If nothing changed and we're not including originals, still include the sample
                augmented['augmentation'] = {'transforms_applied': [], 'no_applicable_transforms': True}
                output_samples.append(augmented)
        
        # Save output
        output_file = output_dir / input_file.name
        save_jsonl(output_samples, output_file)
        print(f"  Saved {len(output_samples)} samples to {output_file}")
    
    print(f"\nSummary:")
    print(f"  Total input samples: {total_samples}")
    print(f"  Samples with augmentation: {total_augmented}")
    print(f"  Output directory: {output_dir}")


if __name__ == '__main__':
    main()