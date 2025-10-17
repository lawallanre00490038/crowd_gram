def format_agent_status(data: dict) -> str:
    status_msg = f"""
📋 <b>Submission Status Overview</b>

👤 <b>User:</b> {data['user_email']}

📦 <b>Overall Summary:</b>
✅ Approved: <b>{data['approved']}</b>
🕓 Pending: <b>{data['pending']}</b>
❌ Rejected: <b>{data['rejected']}</b>

─────────────────────────────
📁 <b>Project Breakdown</b>
"""
    for project in data.get("per_project", []):
        status_msg += f"""
📌 <b>{project['project_name'].upper()}</b>
• Assigned Tasks: <b>{project['number_assigned']}</b>
• Total Submissions: <b>{project['total_submissions']}</b>
• ✅ Approved: <b>{project['approved']}</b>
• 🕓 Pending: <b>{project['pending']}</b>
• ❌ Rejected: <b>{project['rejected']}</b>

💰 Coins Earned: <b>{project['total_coins_earned']}</b>
💵 Amount Earned: <b>{project['total_amount_earned']}</b>
─────────────────────────────
"""

    status_msg += "\n✨ Keep up the great work, agent!"
    return status_msg



def format_reviewer_status(data: dict) -> str:
    status_msg = f"""
📋 <b>Review Summary Overview</b>

👤 <b>Reviewer:</b> {data.get('reviewer_email', 'N/A')}

🧾 <b>Overall Summary:</b>
🪶 Total Reviewed: <b>{data.get('total_reviewed', 0)}</b>
✅ Approved: <b>{data.get('approved_reviews', 0)}</b>
❌ Rejected: <b>{data.get('rejected_reviews', 0)}</b>
🕓 Pending: <b>{data.get('pending_reviews', 0)}</b>

─────────────────────────────
📁 <b>Project Breakdown</b>
"""
    for project in data.get("per_project", []):
        status_msg += f"""
📌 <b>{project['project_name'].upper()}</b>
• Tasks Assigned: <b>{project.get('number_assigned', 0)}</b>
• Total Reviewed: <b>{project.get('total_reviewed', 0)}</b>
• ✅ Approved: <b>{project.get('approved', 0)}</b>
• 🕓 Pending: <b>{project.get('pending', 0)}</b>
• ❌ Rejected: <b>{project.get('rejected', 0)}</b>

💰 Coins Earned: <b>{project.get('total_coins_earned', 0)}</b>
💵 Amount Earned: <b>{project.get('total_amount_earned', 0)}</b>
─────────────────────────────
"""

    status_msg += "\n🎯 Keep maintaining review accuracy and consistency!"
    return status_msg
