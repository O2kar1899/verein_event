from authapp.models import Organization, UserProfile
from django.contrib.auth.models import User

# Ihren User finden (ersetzen Sie 'ihr_username' mit dem echten Namen)
user = User.objects.get(username='Heiner')  # <-- Ihren echten Username einsetzen
print(f"User: {user.username}")

try:
    profile = UserProfile.objects.get(user=user)
    print(f"UserProfile gefunden: {profile}")
    orgs = profile.organizations.all()
    print(f"Organisationen: {list(orgs)}")
    for org in orgs:
        print(f"  - {org.name}")
except UserProfile.DoesNotExist:
    print("PROBLEM: Kein UserProfile gefunden!")

print("\nAlle verfügbaren Organisationen:")
for org in Organization.objects.all():
    print(f"  - {org.name} (ID: {org.id})")

exit()