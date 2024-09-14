from app import db, app, Profile, User, TimelineEvent, ProfileForm, TimelineEventForm, CreateProfileForm, EditProfileForm, EditTimelineForm, DeleteProfileForm, RegistrationForm, LoginForm, TimelineForm, SettingsForm
import json

with app.app_context():
    db.create_all()