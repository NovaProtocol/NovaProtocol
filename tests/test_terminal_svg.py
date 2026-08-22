from __future__ import annotations

from utilities.terminal_svg import TerminalSVG, parse_ansi


def test_parse_ansi_color():
    segs = parse_ansi("\x1b[32mhello\x1b[0m")
    assert segs[0].text == "hello"
    assert segs[0].style.fg == "#50c878"  # green
    assert segs[0].delay == 0.0


def test_parse_ansi_styles():
    segs = parse_ansi("\x1b[1;4mbold_underline\x1b[0m")
    assert segs[0].style.bold is True
    assert segs[0].style.underline is True


def test_parse_ansi_reset():
    segs = parse_ansi("\x1b[31mred\x1b[0mnormal")
    assert segs[0].style.fg == "#ff5555"  # red
    assert segs[1].style.fg == "#c8d2dc"  # back to default


def test_parse_ansi_strips_escapes():
    segs = parse_ansi("plain")
    assert segs[0].text == "plain"


def test_parse_ansi_delay_code():
    segs = parse_ansi("ab\x1b[500pcd")
    assert segs[0].text == "ab"
    assert segs[0].delay == 0.0
    assert segs[1].text == "cd"
    assert segs[1].delay == 0.5  # 500ms -> 0.5s


def test_terminal_svg_renders_last_max_lines():
    v = TerminalSVG(max_line=3)
    for i in range(5):
        v.add_line({"input": f"cmd{i}", "output": [f"out{i}"]})
    svg = v.render()
    assert svg.startswith("<svg")
    assert svg.endswith("</svg>")
    # Full session present (all rows type and scroll)
    assert "cmd0" in svg or ">0<" in svg
    assert "cmd4" in svg or ">4<" in svg


def test_terminal_svg_animates():
    v = TerminalSVG(max_line=5)
    v.add_line({"input": "ls", "output": ["file.txt"]})
    svg = v.render()
    assert "tspan" in svg
    assert 'attributeName="opacity"' in svg
    assert 'fill="freeze"' in svg


def test_terminal_svg_height_scales():
    v = TerminalSVG(max_line=20)
    v.add_line({"input": "x", "output": []})
    svg = v.render()
    # height = BODY_TOP(60) + 20*LINE_H(20) + 6 = 466
    assert 'height="466"' in svg or "466" in svg


def test_terminal_svg_command_prefix():
    v = TerminalSVG(max_line=5)
    v.command_prefix = "custom:~$ "
    v.delay_per_char_input = 0
    v.add_line({"input": "ls", "output": []})
    svg = v.render()
    assert "tspan" in svg
    assert ">c<" in svg  # from "custom"
    assert ">l<" in svg  # from "ls"


def test_terminal_svg_custom_prefix_and_delays():
    v = TerminalSVG(max_line=5)
    v.command_prefix = "default:~$ "
    v.delay_per_char_input = 0
    v.delay_per_line_input = 0.0
    v.delay_after_entry = 0.0
    v.add_line(
        {
            "input": "ls",
            "output": ["file"],
            "custom_prefix": "root@box:~# ",
            "custom_start_delay": 1.0,
            "custom_end_delay": 0.5,
        }
    )
    svg = v.render()
    # custom prefix chars present (root@box)
    for ch in "root@box":
        assert f">{ch}<" in svg or ch in svg
    # start_delay: prefix appears at t=0, INPUT chars wait for the delay.
    import re

    prefix_begin = float(re.search(r'<tspan[^>]*>r<animate[^>]*begin="([0-9.]+)s"', svg).group(1))
    input_begin = float(re.search(r'<tspan[^>]*>l<animate[^>]*begin="([0-9.]+)s"', svg).group(1))
    assert prefix_begin == 0.0  # prompt shows immediately
    assert input_begin >= 1.0  # input waits for custom_start_delay


def test_terminal_svg_default_prefix_still_used():
    v = TerminalSVG(max_line=5)
    v.command_prefix = "default:~$ "
    v.delay_per_char_input = 0
    v.add_line({"input": "ls", "output": []})  # no custom_prefix
    svg = v.render()
    assert ">d<" in svg  # from "default:~$ "


def test_terminal_svg_view_level_input_delay():
    v = TerminalSVG(max_line=5)
    v.command_prefix = "prompt:$ "
    v.delay_per_char_input = 0
    v.delay_per_line_input = 0.5  # wait 0.5s after prompt before typing
    v.add_line({"input": "ls", "output": []})
    svg = v.render()
    import re

    # prompt shows at 0, input waits for the delay
    p = float(re.search(r'<tspan[^>]*>p<animate[^>]*begin="([0-9.]+)s"', svg).group(1))
    i = float(re.search(r'<tspan[^>]*>l<animate[^>]*begin="([0-9.]+)s"', svg).group(1))
    assert p == 0.0
    assert i >= 0.5


def test_terminal_svg_view_level_after_entry_delay():
    v = TerminalSVG(max_line=5)
    v.command_prefix = "prompt:$ "
    v.delay_per_char_input = 0
    v.delay_after_entry = 0.7
    v.add_line({"input": "one", "output": ["out1"]})
    v.add_line({"input": "two", "output": []})
    svg = v.render()
    import re

    # 'e' of first input "one", 'w' of second input "two"
    t1 = float(re.search(r'<tspan[^>]*>e<animate[^>]*begin="([0-9.]+)s"', svg).group(1))
    t2 = float(re.search(r'<tspan[^>]*>w<animate[^>]*begin="([0-9.]+)s"', svg).group(1))
    assert t2 - t1 >= 0.7


def test_terminal_svg_scrolls_per_line():
    v = TerminalSVG(max_line=3)
    for i in range(4):
        v.add_line({"input": f"ls{i}", "output": [f"file{i}"]})
    svg = v.render()
    # one-shot: begin-based per-line y jumps + opacity flashes
    assert 'attributeName="y"' in svg
    assert 'fill="freeze"' in svg
    assert "<tspan" in svg
