from pathlib import Path

path = Path("dashboard/templates/dashboard/home.html")
content = path.read_text(encoding="utf-8")

sidebar_old = '''            <a href="{% url 'dashboard:event_list' %}">Events</a>
            <a href="{% url 'appointment' %}" target="_blank">Appointments Page</a>'''

sidebar_new = '''            <a href="{% url 'dashboard:event_list' %}">Events</a>
            <a href="{% url 'dashboard:homepage_content_edit' %}">Homepage Content</a>
            <a href="{% url 'appointment' %}" target="_blank">Appointments Page</a>'''

card_old = '''            <article class="management-card">
                <h3>Appointments</h3>'''

card_new = '''            <article class="management-card">
                <h3>Homepage Content</h3>
                <p>Update the homepage headings, clinic information, mission, vision and values.</p>
                <a href="{% url 'dashboard:homepage_content_edit' %}">Manage Homepage Content</a>
            </article>

            <article class="management-card">
                <h3>Appointments</h3>'''

if content.count(sidebar_old) != 1:
    raise SystemExit("STOP: Sidebar insertion point was not found exactly once.")

if content.count(card_old) != 1:
    raise SystemExit("STOP: Card insertion point was not found exactly once.")

content = content.replace(sidebar_old, sidebar_new, 1)
content = content.replace(card_old, card_new, 1)

path.write_text(content, encoding="utf-8")
print("SUCCESS: Homepage Content links added.")
