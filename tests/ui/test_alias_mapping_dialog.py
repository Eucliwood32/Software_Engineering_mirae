"""FR-1.3 — AliasMappingDialog UI (L3)."""
from __future__ import annotations

from qce.view.dialogs.alias_mapping_dialog import PLACEHOLDER, AliasMappingDialog


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


def test_apply_suggested_preselects_clustered_alias(qtbot):    # FR-1.3 자동 추천
    dlg = AliasMappingDialog()
    qtbot.addWidget(dlg)
    dlg.set_members(["이대한", "조원희"])
    dlg.populate(_identifiers())
    # 대표명 "이대한"으로 별칭 군집을 추천 → 해당 행만 미리 선택됨
    dlg.apply_suggested({"dh-lee": "이대한", "daehan.lee": "이대한", "이대한": "이대한"})
    assert dlg.combo_for("dh-lee").currentText() == "이대한"
    assert dlg.combo_for("daehan.lee").currentText() == "이대한"
    # 대표명==raw_id(자기 자신)인 행은 강제 선택하지 않는다 → (미지정) 유지.
    assert dlg.combo_for("이대한").currentText() == PLACEHOLDER


def test_apply_suggested_ignores_unknown_member(qtbot):
    dlg = AliasMappingDialog()
    qtbot.addWidget(dlg)
    dlg.set_members(["조원희"])
    dlg.populate(_identifiers())
    # 추천 대표명이 멤버 목록에 없으면 무시(미지정 유지)
    dlg.apply_suggested({"dh-lee": "이대한"})
    assert "dh-lee" not in dlg.current_mapping()


def test_mapping_confirmed_signal(qtbot):
    dlg = AliasMappingDialog()
    qtbot.addWidget(dlg)
    dlg.set_members(["이대한"])
    dlg.populate(_identifiers())
    dlg.combo_for("dh-lee").setCurrentText("이대한")
    with qtbot.waitSignal(dlg.mapping_confirmed, timeout=1000) as blocker:
        dlg._confirm()
    assert blocker.args[0] == {"dh-lee": "이대한"}

def test_cancel_resets_mapping(qtbot):
    dlg = AliasMappingDialog()
    qtbot.addWidget(dlg)
    dlg.set_members(["이대한"])
    dlg.populate(_identifiers())
    dlg.combo_for("dh-lee").setCurrentText("이대한")
    
    # Cancel 버튼 클릭
    dlg._reset_mapping()
    
    # 모두 PLACEHOLDER로 초기화되었는지 확인
    assert dlg.combo_for("dh-lee").currentText() == PLACEHOLDER
    assert "dh-lee" not in dlg.current_mapping()
