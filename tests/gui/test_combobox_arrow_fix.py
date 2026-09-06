from expense_tracker.app import _use_visible_downarrow


def sample_layout():
    # Shape of ttkbootstrap 1.18's TCombobox layout
    return [
        ("Combobox.downarrow", {"side": "right", "sticky": "s"}),
        (
            "Combobox.field",
            {
                "sticky": "nswe",
                "children": [
                    (
                        "Combobox.padding",
                        {
                            "expand": "1",
                            "sticky": "nswe",
                            "children": [("Combobox.textarea", {"sticky": "nswe"})],
                        },
                    )
                ],
            },
        ),
    ]


def test_replaces_downarrow_and_centers_it():
    fixed = _use_visible_downarrow(sample_layout())
    name, opts = fixed[0]
    assert name == "Combobox.downarrow.visible"
    assert opts["sticky"] == "e"
    assert opts["side"] == "right"  # other options preserved


def test_leaves_nested_elements_untouched():
    fixed = _use_visible_downarrow(sample_layout())
    field_name, field_opts = fixed[1]
    assert field_name == "Combobox.field"
    padding_name, padding_opts = field_opts["children"][0]
    assert padding_name == "Combobox.padding"
    assert padding_opts["children"] == [("Combobox.textarea", {"sticky": "nswe"})]


def test_handles_downarrow_nested_in_children():
    layout = [
        (
            "Combobox.field",
            {"children": [("Combobox.downarrow", {"sticky": "s"})]},
        )
    ]
    fixed = _use_visible_downarrow(layout)
    child_name, child_opts = fixed[0][1]["children"][0]
    assert child_name == "Combobox.downarrow.visible"
    assert child_opts["sticky"] == "e"
