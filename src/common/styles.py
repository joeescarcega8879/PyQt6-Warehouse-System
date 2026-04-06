from src.common.enums import StatusType

STATUSBAR_STYLES = {
    StatusType.SUCCESS: """
        .QStatusBar {
            background-color: #1a3d2a;
            color: #6fcf97;
            border-top: 1px solid #2a5c40;
            font-weight: bold;
            padding: 2px 8px;
        }
    """,
    StatusType.ERROR: """
        .QStatusBar {
            background-color: #3d1a1a;
            color: #ff7070;
            border-top: 1px solid #6b3030;
            font-weight: bold;
            padding: 2px 8px;
        }
    """,
    StatusType.WARNING: """
        .QStatusBar {
            background-color: #3d2e10;
            color: #f0c060;
            border-top: 1px solid #6b4e20;
            font-weight: bold;
            padding: 2px 8px;
        }
    """,
}