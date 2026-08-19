import json
from pathlib import Path

from openhealthkit.config import settings
from openhealthkit.utils.logger import logger


class I18nEngine:
    """Translation manager for loading and serving localized strings."""

    def __init__(self, locales_dir: str | None = None):
        if locales_dir:
            self.locales_dir = Path(locales_dir)
        else:
            # Default to packages/openhealthkit/locales
            base_dir = Path(__file__).resolve().parent.parent.parent.parent
            self.locales_dir = base_dir / "locales"

        self.translations: dict[str, dict[str, str]] = {}
        self.default_locale = settings.DEFAULT_LOCALE
        self._load_locales()

    def _load_locales(self) -> None:
        if not self.locales_dir.exists():
            logger.warning(f"Locales directory not found at {self.locales_dir}")
            return

        for lang_dir in self.locales_dir.iterdir():
            if lang_dir.is_dir():
                lang_code = lang_dir.name
                trans_file = lang_dir / "translations.json"
                if trans_file.exists():
                    try:
                        with open(trans_file, encoding="utf-8") as f:
                            self.translations[lang_code] = json.load(f)
                    except Exception as exc:
                        logger.error(f"Failed to load translations for '{lang_code}': {exc}")

    def gettext(self, key: str, locale: str | None = None) -> str:
        lang = (locale or self.default_locale).lower()
        if lang in self.translations and key in self.translations[lang]:
            return self.translations[lang][key]

        # Fallback to default locale or raw key
        if (
            self.default_locale in self.translations
            and key in self.translations[self.default_locale]
        ):
            return self.translations[self.default_locale][key]

        return key

    t = gettext

    def get_all_translations(self, locale: str | None = None) -> dict[str, str]:
        lang = (locale or self.default_locale).lower()
        if lang in self.translations:
            return self.translations[lang]
        return self.translations.get(self.default_locale, {})


i18n = I18nEngine()
i18n_engine = i18n

