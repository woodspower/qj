{
    "Name":"Popup",
    "InferenceName": "Movie",
    "Sequence": {
        "Name": "One of Confirm->dNext->Cancel->Reject",
        "KeyBody": [
            {
                "Conditions": {
                    "Allow": {
                        "Tags": [
                            "Confirm",
                            "dNext",
                            "Cancel",
                            "Reject"
                        ]
                    }
                },
                "Actions": {
                    "Command": "Click"
                }
            }
        ]
    }
}
