{
    "InferenceName": "CopierMenu",
    "Sequence": [
        {
            "Name": "Select one submenu in Copier menu",
            "KeyBody": [
                {
                    "Name": "Select Copier Submenu",
                    "Conditions": {
                            "Jobs": {"Bookname": "CopierSubmenu"},
                            "Allow": {"Tags": ["CopierOff"]}
                    },
                    "Actions": { "Command": "Click" }
                }
            ]
        },
        {
            "Name": "Go and do jobs in Copier Submenu",
            "KeyBody": {
                    "Name": "Goto Copier Submenu",
                    "Conditions": { 
                            "Allow": { "Tags": [ "CopierOn" ] } 
                        },
                    "Actions": {
                            "Command": "Goto",
                            "BookName": "CopierSubmenu"
                        }
                }
        }
    ]
}


