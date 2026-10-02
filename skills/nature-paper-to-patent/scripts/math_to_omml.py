#!/usr/bin/env python3
"""Convert a LaTeX equation into editable Word Office Math (OMML)."""

from copy import deepcopy
from xml.etree import ElementTree

from docx.oxml import OxmlElement
from docx.oxml.ns import qn


MATHML_NS = "{http://www.w3.org/1998/Math/MathML}"


def _element(name: str):
    return OxmlElement(f"m:{name}")


def _text_run(text: str):
    run = _element("r")
    properties = _element("rPr")
    style = _element("sty")
    style.set(qn("m:val"), "p")
    properties.append(style)
    run.append(properties)
    value = _element("t")
    value.text = text
    run.append(value)
    return run


def _append_children(target, source) -> None:
    if source.text and source.text.strip():
        target.append(_text_run(source.text.strip()))
    for child in source:
        _append_mathml(target, child)
        if child.tail and child.tail.strip():
            target.append(_text_run(child.tail.strip()))


def _script(target, node, kind: str) -> None:
    result = _element(kind)
    expression = _element("e")
    sub = _element("sub")
    sup = _element("sup")
    children = list(node)
    if children:
        _append_mathml(expression, children[0])
    if len(children) > 1:
        _append_mathml(sup if kind == "sSup" else sub, children[1])
    if len(children) > 2:
        _append_mathml(sup, children[2])
    result.append(expression)
    if kind in {"sSub", "sSubSup"}:
        result.append(sub)
    if kind in {"sSup", "sSubSup"}:
        result.append(sup)
    target.append(result)


def _append_mathml(target, node) -> None:
    tag = node.tag.removeprefix(MATHML_NS)
    children = list(node)

    if tag in {"math", "mrow", "mstyle", "semantics", "annotation"}:
        _append_children(target, node)
    elif tag in {"mi", "mn", "mo", "mtext"}:
        target.append(_text_run("".join(node.itertext())))
    elif tag == "mfrac":
        fraction = _element("f")
        numerator = _element("num")
        denominator = _element("den")
        if children:
            _append_mathml(numerator, children[0])
        if len(children) > 1:
            _append_mathml(denominator, children[1])
        fraction.extend((numerator, denominator))
        target.append(fraction)
    elif tag == "msub":
        _script(target, node, "sSub")
    elif tag == "msup":
        _script(target, node, "sSup")
    elif tag in {"msubsup", "munderover"}:
        _script(target, node, "sSubSup")
    elif tag == "munder":
        _script(target, node, "sSub")
    elif tag == "mover":
        _script(target, node, "sSup")
    elif tag == "msqrt":
        radical = _element("rad")
        properties = _element("radPr")
        hide_degree = _element("degHide")
        hide_degree.set(qn("m:val"), "1")
        properties.append(hide_degree)
        degree = _element("deg")
        expression = _element("e")
        _append_children(expression, node)
        radical.extend((properties, degree, expression))
        target.append(radical)
    elif tag == "mroot":
        radical = _element("rad")
        degree = _element("deg")
        expression = _element("e")
        if children:
            _append_mathml(expression, children[0])
        if len(children) > 1:
            _append_mathml(degree, children[1])
        radical.extend((degree, expression))
        target.append(radical)
    elif tag == "mfenced":
        delimiter = _element("d")
        properties = _element("dPr")
        begin = _element("begChr")
        begin.set(qn("m:val"), node.attrib.get("open", "("))
        end = _element("endChr")
        end.set(qn("m:val"), node.attrib.get("close", ")"))
        properties.extend((begin, end))
        expression = _element("e")
        _append_children(expression, node)
        delimiter.extend((properties, expression))
        target.append(delimiter)
    elif tag == "mtable":
        matrix = _element("m")
        for row_node in children:
            row = _element("mr")
            for cell_node in list(row_node):
                cell = _element("e")
                _append_children(cell, cell_node)
                row.append(cell)
            matrix.append(row)
        target.append(matrix)
    elif tag in {"mtr", "mtd"}:
        _append_children(target, node)
    elif tag == "mspace":
        target.append(_text_run(" "))
    else:
        _append_children(target, node)


def latex_to_omml(latex: str):
    try:
        from latex2mathml.converter import convert
    except ImportError as error:
        raise RuntimeError(
            "Native equations require latex2mathml: py -3 -m pip install latex2mathml"
        ) from error

    mathml = ElementTree.fromstring(convert(latex))
    paragraph = _element("oMathPara")
    math = _element("oMath")
    _append_mathml(math, mathml)
    paragraph.append(math)
    return paragraph


def clone_omml(element):
    return deepcopy(element)
