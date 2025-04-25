form_schemas = {
    "swms": """{
                "ppeRequirements": {
                    "HardHat": false,
                    "SafetyBoots": true,
                    "HighVisVest": false,
                    "SafetyGlasses": false
                },
                "requiredPermits": {
                    "WorkingatHeights": false,
                    "HotWork": false,
                    "ConfinedSpace": false,
                    "Excavation": false
                },
                "_id": "680b16eecb2376a1c157ca18",
                "title": "newtest",
                "project": "680a2e93ccf78668455ece55",
                "workArea": "newlocation",
                "description": "hazards",
                "hazardsandControls": [
                    {
                        "hazardDescription": "h1",
                        "riskLevel": "Low",
                        "controlMeasures": "gtake c",
                        "_id": "680b16eecb2376a1c157ca19"
                    }
                ],
                "createdAt": "2025-04-25T05:00:30.963Z",
                "updatedAt": "2025-04-25T05:00:30.963Z",
                "__v": 0
            }
}""",

    "incidents": """{
                "_id": "680a1b73d7053a09e2cea4e3",
                "incidentType": "injury",
                "dateTime": "2025-04-15T15:06:00.000Z",
                "location": "dd",
                "description": "dd",
                "severityLevel": "low",
                "witnesses": [
                    "dd"
                ],
                "immediateActions": "dd",
                "image": [
                    "https://res.cloudinary.com/dkqcqrrbp/image/upload/v1745492851/uploads/msbajnyebbwpfcpbjhln.jpg"
                ],
                "createdAt": "2025-04-24T11:07:31.404Z",
                "updatedAt": "2025-04-24T11:07:31.404Z",
                "__v": 0
            }""",

    "itps": """ "_id": "680a274a26854eb4f9f18eae",
                "projectName": "Main Building Constructionj",
                "InspectionType": "Safety Inspectionj",
                "Inspector": "Ali Raz",
                "Date": "2025-04-22T00:00:00.000Z",
                "InspectionItems": [
                    {
                        "itemDescription": "Item 1",
                        "status": true,
                        "comments": "Pass",
                        "_id": "680a274a26854eb4f9f18eaf"
                    },
                    {
                        "itemDescription": "Item 1",
                        "status": true,
                        "comments": "Pass",
                        "_id": "680a274a26854eb4f9f18eb0"
                    }
                ],
                "additionalNotes": "File upload",
                "activity": "Concrete Pouring",
                "criteria": "75–100mm",
                "status": "Approved",
                "image": [
                    "https://res.cloudinary.com/dkqcqrrbp/image/upload/v1745495882/itp_uploads/gtoigjekwjthb4ople6r.jpg"
                ],
                "createdAt": "2025-04-24T11:58:02.252Z",
                "updatedAt": "2025-04-24T11:58:02.252Z",
                "__v": 0
            }""",

    "RFI": """{
  "subject": "",
  "priority": "",
  "due_date": "",
  "assignee": "",
  "department": "",
  "description": "",
  "attachments": []
}"""
}




compliance_json_template = """{
  "issue_summary": "",
  "compliance_issues": [
    {
      "standard": "",
      "section": "",
      "issue": "",
      "rectification": ""
    }
  ],
  "overall_status": ""
}"""
