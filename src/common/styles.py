from src.common.enums import StatusType

STATUSBAR_STYLES = {
    StatusType.SUCCESS: """
        .QStatusBar {
            background-color: #dcfce7;
            color: #166534;
            border-top: 1px solid #bbf7d0;
            font-weight: bold;
            padding: 2px 8px;
        }
    """,
    StatusType.ERROR: """
        .QStatusBar {
            background-color: #fee2e2;
            color: #991b1b;
            border-top: 1px solid #fecaca;
            font-weight: bold;
            padding: 2px 8px;
        }
    """,
}