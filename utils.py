import moment

name_mapper = [
    {
        "eng":"aviram",
        "heb":"אבירם"
    },
    {
        "eng": "nadav",
        "heb": "נדב"
    },
    {
        "eng": "chen",
        "heb": "חן"
    },
    {
        "eng": "hen",
        "heb": "חן"
    },
    {
        "eng": "shiran",
        "heb": "שירן"
    },
    {
        "eng": "tomer",
        "heb": "תומר"
    },
    {
        "eng": "amit",
        "heb": "עמית"
    },
    {
        "eng": "amir",
        "heb": "אמיר"
    },
    {
        "eng": "daniel",
        "heb": "דניאל"
    },
    {
        "eng":"veronica",
        "heb":"ורוניקה"
    },
    {
        "eng":"noam",
        "heb":"נועם"
    }
]

dates = [
        {
            "timephrase":"last day of this week",
            "alt":[
                "the end of this week",
                "the end of the week",
                "last day of this week",
                "last day of the week"
            ],
            "phrase":moment.now().add(days=6-moment.now().weekday).format("YYYY-MM-DD HH:mm:ss")
        },
        {
            "timephrase": "first day of next week",
            "alt": [
                "the next week",
                "to next week",
                "next week",
                "upcoming week",
                "the upcoming week"
            ],
            "phrase":moment.now().add(days=7-moment.now().weekday).format("YYYY-MM-DD HH:mm:ss")
        },
        {
            "timephrase": "last day of next week",
            "alt":[
                "the end of next week",
                "the end of the next week"
            ],
            "phrase": moment.now().add(days=14-moment.now().weekday).format("YYYY-MM-DD HH:mm:ss")
        },
        {
            "timephrase": "two weeks",
            "alt":[
                "two weeks",
                "2 weeks",
                "upcoming weeks",
                "the upcoming weeks",
                "the next two weeks"
            ],
            "phrase": moment.now().add(days=14).format("YYYY-MM-DD HH:mm:ss")
        },
        {
            "timephrase":"next weekend",
            "alt":[
                "next weekend"
            ],
            "phrase": moment.now().add(days=(11-moment.now().weekday)).format("YYYY-MM-DD HH:mm:ss")
        },
        {
            "timephrase": "one day",
            "alt": [
                "tomorrow",
                "1 day",
                "one day"
            ],
            "phrase": moment.now().add(days=1).format("YYYY-MM-DD HH:mm:ss")
        },
        {
            "timephrase": "two days",
            "alt": [
                "day after tomorrow",
                "2 days",
                "two days"
            ],
            "phrase": moment.now().add(days=2).format("YYYY-MM-DD HH:mm:ss")
        },
        {
            "timephrase": "three days",
            "alt": [
                "3 days",
                "three days"
            ],
            "phrase": moment.now().add(days=3).format("YYYY-MM-DD HH:mm:ss")
        },
        {
            "timephrase": "four days",
            "alt": [
                "4 days",
                "four days"
            ],
            "phrase": moment.now().add(days=4).format("YYYY-MM-DD HH:mm:ss")
        },
        {
            "timephrase": "five days",
            "alt": [
                "5 days",
                "five days"
            ],
            "phrase": moment.now().add(days=5).format("YYYY-MM-DD HH:mm:ss")
        },
        {
            "timephrase": "six days",
            "alt": [
                "6 days",
                "six days"
            ],
            "phrase": moment.now().add(days=6).format("YYYY-MM-DD HH:mm:ss")
        },
        {
            "timephrase": "in a week",
            "alt": [
                "7 days",
                "seven days",
                "a week"
            ],
            "phrase": moment.now().add(days=7).format("YYYY-MM-DD HH:mm:ss")
        }
    ]

datesHeb = [
    {
        "timephrase": "מחר",
        "alt":[
            "מחר",
            "עד מחר",
            "למחר",
            "תוך יום",
            "ביום הקרוב"
        ],
        "phrase": moment.now().add(days=1).format("YYYY-MM-DD HH:mm:ss")
    },
    {
        "timephrase": "מחרתיים",
        "alt": [
            "מחרתיים",
            "עד מחרתיים",
            "למחרתיים",
            "תוך יומיים",
            "תוך 2 ימים",
            "ביומיים הקרובים",
            "ב2 ימים הקרובים"
        ],
        "phrase": moment.now().add(days=2).format("YYYY-MM-DD HH:mm:ss")
    },
    {
        "timephrase": "שלושה ימים",
        "alt": [
            "שלושה ימים",
            "עד שלושה ימים",
            "עד 3 ימים",
            "לעוד שלושה ימים",
            "לעוד 3 ימים",
            "תוך שלושה ימים",
            "תוך 3 ימים",
            "בשלושה ימים הקרובים",
            "ב3 ימים הקרובים",
            "ב3 ימים הבאים",
            "בשלושה ימים הבאים",
            "בשלושת הימים הבאים"
        ],
        "phrase": moment.now().add(days=3).format("YYYY-MM-DD HH:mm:ss")
    },
    {
        "timephrase": "ארבעה ימים",
        "alt": [
            "ארבעה ימים",
            "עד ארבעה ימים",
            "עד 4 ימים",
            "לעוד ארבעה ימים",
            "לעוד 4 ימים",
            "תוך ארבעה ימים",
            "תוך 4 ימים",
            "בארבעה ימים הקרובים",
            "ב4 ימים הקרובים",
            "ב4 ימים הבאים",
            "בארבעה ימים הבאים"
            "בארבעת הימים הבאים"
        ],
        "phrase": moment.now().add(days=3).format("YYYY-MM-DD HH:mm:ss")
    },
    {
        "timephrase": "שבוע",
        "alt": [
            "שבוע",
            "עד שבוע",
            "עד 7 ימים",
            "לעוד שבוע",
            "לעוד 7 ימים",
            "תוך שבוע",
            "תוך 7 ימים",
            "בשבוע הקרוב",
            "ב7 ימים הקרובים",
            "ב7 ימים הבאים",
            "בשבוע הזה"
            "השבוע",
            "עוד השבוע",
        ],
        "phrase": moment.now().add(days=7).format("YYYY-MM-DD HH:mm:ss")
    },
    {
        "timephrase": "סופש",
        "alt": [
            "סופש",
            "עד הסופש",
            "לסופש",
            "לסוף השבוע",
            "עד סוף השבוע",
            "עד הסוף שבוע",
        ],
        "phrase": moment.now().add(days=5-moment.now().weekday).format("YYYY-MM-DD HH:mm:ss")
    },{
        "timephrase": "יום ראשון",
        "alt": [
            "ליום ראשון",
            "לתחילת השבוע",
            "עד יום ראשון",
            "עד תחילת השבוע",
            "עד תחילת שבוע הבא",
            "עד תחילת השבוע הבא",
        ],
        "phrase": moment.now().add(days=7-moment.now().weekday).format("YYYY-MM-DD HH:mm:ss")
    },{
        "timephrase": "יום שני",
        "alt": [
            "ליום שני",
            "עד יום שני",
            "עד שני",
        ],
        "phrase": moment.now().add(days=8-moment.now().weekday).format("YYYY-MM-DD HH:mm:ss")
    },{
        "timephrase": "יום שלישי",
        "alt": [
            "ליום שלישי",
            "עד יום שלישי",
            "עד שלישי",
        ],
        "phrase": moment.now().add(days=9-moment.now().weekday).format("YYYY-MM-DD HH:mm:ss")
    }
    # -----------------------------------------------
]
