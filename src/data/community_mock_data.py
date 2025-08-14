json_str = """
[
  {
    "#": 1,
    "N": "Alice",
    "TT": 20,
    "TC": 19,
    "CE": 150,
    "R": 4.9
  },
  {
    "#": 2,
    "N": "Bob",
    "TT": 18,
    "TC": 16,
    "CE": 130,
    "R": 4.7
  },
  {
    "#": 3,
    "N": "Charlie",
    "TT": 17,
    "TC": 15,
    "CE": 120,
    "R": 4.5
  },
  {
    "#": 4,
    "N": "Diana",
    "TT": 15,
    "TC": 13,
    "CE": 110,
    "R": 4.3
  },
  {
    "#": 5,
    "N": "Ethan",
    "TT": 14,
    "TC": 12,
    "CE": 100,
    "R": 4.1
  }
]
"""

json_data_broadcast_project_insert = [{
      "Task": "audio",
      "Cat": "static",
      "Language": "Yoruba",
      "Count": 4
   }]

json_data_broadcast_policy_insert = """
    [
    {
      "announcement_title": "Upcoming Security Policy Update",
      "body": "To enhance account protection, we're introducing a mandatory two-factor authentication policy starting August 15. Please ensure your mobile number is up to date in your profile settings."
    },
    {
      "announcement_title": "Payment Policy Update",
      "body": "We're adding additional forms of payment including - PayPal, Venmo, CashApp, & Zelle."
    }
    ]
"""  # noqa: E501

json_data_broadcast_trainings_insert = """
    [
    {
      "announcement_title": "New User Onboarding Course Available",
      "body":  "We've launched an updated onboarding training for new users. This 45-minute course walks through the core features and best practices for getting started quickly."
    },
    {
      "announcement_title": "Interface Training Available",
      "body": "To allow better transition into the platform we've provided a new training to allow a new user to become more comfortable. The training is 1-hour and self-paced."
    }
    ]
"""  # noqa: E501

