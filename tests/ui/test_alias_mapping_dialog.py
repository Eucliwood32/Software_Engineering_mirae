"""FR-1.3 — AliasMappingDialog UI (L3)."""
from __future__ import annotations

from qce.view.dialogs.alias_mapping_dialog import AliasMappingDialog


def _identifiers():
    return [
        {"raw_id": "dh-lee", "source": "git", "activity": 30},
        {"raw_id": "daehan.lee", "source": "doc", "activity": 1500},
        {"raw_id": "이대한", "source": "messenger", "activity": 120},
        {"raw_id": "ghost", "source": "git", "activity": 5},
    ]


def test_populate_shows_all_identifiers(qtbot):                 # TC-FR-1.3-05
    dlg = AliasMappingDialog()
    qtbot.addWidget(dlg)
    dlg.set_members(["이대한", "조원희"])
    ids = _identifiers()
    dlg.populate(ids)
    assert dlg.row_count() == len(ids)


def test_n_to_1_mapping(qtbot):                                 # TC-FR-1.3-01
    dlg = AliasMappingDialog()
    qtbot.addWidget(dlg)
    dlg.set_members(["이대한", "조원희"])
    dlg.populate(_identifiers())
    dlg.combo_for("dh-lee").setCurrentText("이대한")
    dlg.combo_for("daehan.lee").setCurrentText("이대한")
    dlg.combo_for("이대한").setCurrentText("이대한")
    mapping = dlg.current_mapping()
    assert mapping["dh-lee"] == "이대한"
    assert mapping["daehan.lee"] == "이대한"
    assert mapping["이대한"] == "이대한"


def test_unmapped_excluded(qtbot):                              # TC-FR-1.3-02/03
    dlg = AliasMappingDialog()
    qtbot.addWidget(dlg)
    dlg.set_members(["이대한", "조원희"])
    dlg.populate(_identifiers())
    dlg.combo_for("dh-lee").setCurrentText("이대한")
    # ghost는 미선택 → 매핑 제외, 미매핑 목록에 포함
    assert "ghost" not in dlg.current_mapping()
    assert "ghost" in dlg.unmapped_ids()


def test_mapping_confirmed_signal(qtbot):
    dlg = AliasMappingDialog()
    qtbot.addWidget(dlg)
    dlg.set_members(["이대한"])
    dlg.populate(_identifiers())
    dlg.combo_for("dh-lee").setCurrentText("이대한")
    with qtbot.waitSignal(dlg.mapping_confirmed, timeout=1000) as blocker:
        dlg._confirm()
    assert blocker.args[0] == {"dh-lee": "이대한"}
