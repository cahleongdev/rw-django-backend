import json
from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.db import transaction

from app.models.users import User


class Command(BaseCommand):
    help = "Seed super admin user from seed.json file"

    def validate_super_admin_data(self, data):
        """Validate required fields for super admin"""
        required_fields = ['first_name', 'last_name', 'title', 'email', 'password']
        
        for field in required_fields:
            if field not in data or not data[field]:
                raise ValueError(f"Required field '{field}' is missing or empty")
        
        # Validate email format
        try:
            validate_email(data['email'])
        except ValidationError:
            raise ValueError(f"Invalid email format: {data['email']}")
        
        # Validate password length
        if len(data['password']) < 8:
            raise ValueError("Password must be at least 8 characters long")

    @transaction.atomic
    def handle(self, *args, **options):
        file_path = './app/seeds/SuperAdmin.json'
        
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)

        # Validate the data
        self.validate_super_admin_data(data)

        # Set default values
        data['role'] = 'Super_Admin'
        data['username'] = data.get('username', data['email'])
        data['is_active'] = True
        data['is_staff'] = True
        data['is_superuser'] = True
        data['password'] = make_password(data['password'])
        
        # Create new user
        super_admin = User.objects.create(**data)
        
        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully created super admin user: {data['email']}"
            )
        )
            