import io
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from django.contrib.auth import get_user_model
from files.models import UserFile

User = get_user_model()

SEED_USERS = [
    {
        "email": "alice@example.com",
        "password": "Password123!",
        "full_name": "Alice Nakamura",
        "display_name": "alice",
        "bio": "Product designer who likes clean UIs.",
        "files": [
            {"file_name": "resume_alice.pdf", "mime_type": "application/pdf"},
            {"file_name": "profile_photo.jpg", "mime_type": "image/jpeg"},
        ],
    },
    {
        "email": "bob@example.com",
        "password": "Password123!",
        "full_name": "Bob Alvarez",
        "display_name": "bob",
        "bio": "Backend engineer, coffee enthusiast.",
        "files": [
            {"file_name": "project_notes.txt", "mime_type": "text/plain"},
            {"file_name": "invoice_march.pdf", "mime_type": "application/pdf"},
        ],
    },
    {
        "email": "carol@example.com",
        "password": "Password123!",
        "full_name": "Carol Whitfield",
        "display_name": "carol",
        "bio": "QA lead focused on security testing.",
        "files": [
            {"file_name": "test_plan.docx", "mime_type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document"},
            {"file_name": "vacation.png", "mime_type": "image/png"},
        ],
    },
]


class Command(BaseCommand):
    help = "Seeds 3 test users with sample files"

    def handle(self, *args, **options):
        for entry in SEED_USERS:
            user, created = User.objects.get_or_create(
                email=entry["email"],
                defaults={
                    "full_name": entry["full_name"],
                    "display_name": entry["display_name"],
                    "bio": entry["bio"],
                },
            )
            if created:
                user.set_password(entry["password"])
                user.save()
                self.stdout.write(self.style.SUCCESS(f"Created user: {user.email}"))
            else:
                self.stdout.write(f"User already exists: {user.email}")

            for f in entry["files"]:
                if UserFile.objects.filter(owner=user, file_name=f["file_name"]).exists():
                    continue
                dummy_content = ContentFile(
                    f"Dummy content for {f['file_name']}".encode(),
                    name=f["file_name"],
                )
                UserFile.objects.create(
                    owner=user,
                    file=dummy_content,
                    file_name=f["file_name"],
                    mime_type=f["mime_type"],
                    size_bytes=dummy_content.size,
                )
                self.stdout.write(f"  -> added file: {f['file_name']}")