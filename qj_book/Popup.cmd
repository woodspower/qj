{
    "Name":"Popup",
    "InferenceName": "Movie",
    "Sequence": {
        "Name": "One of Confirm->dNext->Cancel->Reject",
        "KeyBody": [
            {
                "Conditions": {
                    "Allow": {
                        "Percent":0.1,
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
