from openhealthkit.i18n import i18n


def test_i18n_translation_keys():
    # Test English
    assert i18n.gettext("app_name", locale="en") == "OpenHealthKit"
    assert i18n.gettext("status_open", locale="en") == "Open"

    # Test Hindi
    assert i18n.gettext("app_name", locale="hi") == "ओपनहेल्थकिट"
    assert i18n.gettext("status_open", locale="hi") == "खुला है (Open)"

    # Test Fallback for unknown key
    assert i18n.gettext("non_existent_key", locale="en") == "non_existent_key"
