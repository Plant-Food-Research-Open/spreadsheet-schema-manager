from dataclasses import dataclass, field


@dataclass
class ReleaseNote:
    version: str
    date: str
    changes: list[str] = field(default_factory=list)


# Newest release first.
RELEASE_NOTES: list[ReleaseNote] = [
    ReleaseNote(
        version="0.24",
        date="2026-07-29",
        changes=[
            "Settings: added a \"Preferred date format\" option, used when standardising Date fields and when exporting Workbooks",
            "Datasets: standardising a Date field now detects ambiguous day/month formats and lets you choose, and blocks Finish for columns with unreliable date data",
            "Datasets: standardised Workbook now include a StandardisationLog sheet recording the field/value mapping decisions made during standardisation",
            "Workbooks: fixed Category values containing a quote corrupting the data validation dropdown in downloaded Workbooks",
        ],
    ),
    ReleaseNote(
        version="0.23",
        date="2026-07-20",
        changes=[
            "Fields: added Export and Delete All buttons",
            "Datasets: Date fields are now standardised to ISO format (YYYY-MM-DD) when finishing standardisation",
        ],
    ),
    ReleaseNote(
        version="0.22",
        date="2026-04-24",
        changes=[
            "Fields: added Import button",
            "Workbooks: added Field ordering before download",
        ],
    ),
]
