"""Publish Electric Eye email templates to the newsletter website."""

from pathlib import Path

from newsletter.page_publish import publish_page

TEMPLATE_DIRECTORY = Path(__file__).resolve().parent / "email_templates"


def publish_email_template(frequency, *, token=None, session=None):
    """Publish an approved HTML template to the public newsletter site."""
    if frequency not in ("weekly", "monthly"):
        raise ValueError("Unsupported email template frequency")

    path = TEMPLATE_DIRECTORY / f"{frequency}.html"

    if not path.is_file():
        raise FileNotFoundError(f"Email template not found: {path}")

    html = path.read_text(encoding="utf-8")

    return publish_page(
        f"templates/{frequency}.html",
        html,
        token=token,
        session=session,
    )


if __name__ == "__main__":
    print(publish_email_template("weekly"))
