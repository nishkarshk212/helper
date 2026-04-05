"""
Database models for storing group settings
"""
from sqlalchemy import create_engine, Column, Integer, String, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


class GroupSettings(Base):
    __tablename__ = 'group_settings'
    
    id = Column(Integer, primary_key=True)
    chat_id = Column(String, unique=True, nullable=False)
    welcome_enabled = Column(Boolean, default=False)
    welcome_message = Column(Text, default="Welcome {user} to the group!")
    welcome_type = Column(String, default="text")  # text, photo, video, document
    welcome_media_file_id = Column(Text, nullable=True)
    welcome_buttons = Column(Text, default="[]")  # JSON string of buttons
    goodbye_enabled = Column(Boolean, default=False)
    goodbye_message = Column(Text, default="Goodbye {user}! We'll miss you.")
    goodbye_type = Column(String, default="text")  # text, photo, video, document
    goodbye_media_file_id = Column(Text, nullable=True)
    goodbye_buttons = Column(Text, default="[]")  # JSON string of buttons
    anti_spam_enabled = Column(Boolean, default=False)
    anti_flood_enabled = Column(Boolean, default=False)
    flood_limit = Column(Integer, default=5)  # messages per time window
    auto_delete_enabled = Column(Boolean, default=False)
    allowed_links = Column(Boolean, default=False)
    captcha_enabled = Column(Boolean, default=False)
    self_destruct_enabled = Column(Boolean, default=False)
    self_destruct_hours = Column(Integer, default=0)
    self_destruct_minutes = Column(Integer, default=0)
    self_destruct_seconds = Column(Integer, default=30)
    clean_join_messages = Column(Boolean, default=False)
    clean_leave_messages = Column(Boolean, default=False)
    clean_invite_messages = Column(Boolean, default=False)
    clean_voice_chat_messages = Column(Boolean, default=False)
    custom_admin_roles = Column(Text, default="{}")  # JSON: {user_id: {role: "admin", tag: "@Admin"}}
    user_warns = Column(Text, default="{}")  # JSON: {user_id: warn_count}
    muted_users = Column(Text, default="[]")  # JSON: [user_ids]
    chat_filters = Column(Text, default="{}")  # JSON: {trigger: {type: "text/sticker/photo/video", content: "...", file_id: "..."}}
    blocked_words = Column(Text, default="[]")  # JSON: [blocked words/phrases]
    
    def __repr__(self):
        return f"<GroupSettings(chat_id={self.chat_id})>"


# Database setup
engine = create_engine('sqlite:///group_bot.db')

# Add new columns if they don't exist (for database migration)
from sqlalchemy import text
def migrate_database():
    """Add new columns for welcome/goodbye messages with media and buttons"""
    with engine.connect() as conn:
        try:
            # Check and add welcome_type column
            conn.execute(text("ALTER TABLE group_settings ADD COLUMN welcome_type VARCHAR DEFAULT 'text'"))
        except:
            pass  # Column already exists
        
        try:
            conn.execute(text("ALTER TABLE group_settings ADD COLUMN welcome_media_file_id TEXT"))
        except:
            pass
        
        try:
            conn.execute(text("ALTER TABLE group_settings ADD COLUMN welcome_buttons TEXT DEFAULT '[]'"))
        except:
            pass
        
        try:
            conn.execute(text("ALTER TABLE group_settings ADD COLUMN goodbye_enabled BOOLEAN DEFAULT 0"))
        except:
            pass
        
        try:
            conn.execute(text("ALTER TABLE group_settings ADD COLUMN goodbye_message TEXT DEFAULT 'Goodbye {user}! We\'ll miss you.'"))
        except:
            pass
        
        try:
            conn.execute(text("ALTER TABLE group_settings ADD COLUMN goodbye_type VARCHAR DEFAULT 'text'"))
        except:
            pass
        
        try:
            conn.execute(text("ALTER TABLE group_settings ADD COLUMN goodbye_media_file_id TEXT"))
        except:
            pass
        
        try:
            conn.execute(text("ALTER TABLE group_settings ADD COLUMN goodbye_buttons TEXT DEFAULT '[]'"))
        except:
            pass
        
        try:
            conn.execute(text("ALTER TABLE group_settings ADD COLUMN self_destruct_enabled BOOLEAN DEFAULT 0"))
        except:
            pass
        
        try:
            conn.execute(text("ALTER TABLE group_settings ADD COLUMN self_destruct_hours INTEGER DEFAULT 0"))
        except:
            pass
        
        try:
            conn.execute(text("ALTER TABLE group_settings ADD COLUMN self_destruct_minutes INTEGER DEFAULT 0"))
        except:
            pass
        
        try:
            conn.execute(text("ALTER TABLE group_settings ADD COLUMN self_destruct_seconds INTEGER DEFAULT 30"))
        except:
            pass
        
        try:
            conn.execute(text("ALTER TABLE group_settings ADD COLUMN clean_join_messages BOOLEAN DEFAULT 0"))
        except:
            pass
        
        try:
            conn.execute(text("ALTER TABLE group_settings ADD COLUMN clean_leave_messages BOOLEAN DEFAULT 0"))
        except:
            pass
        
        try:
            conn.execute(text("ALTER TABLE group_settings ADD COLUMN clean_invite_messages BOOLEAN DEFAULT 0"))
        except:
            pass
        
        try:
            conn.execute(text("ALTER TABLE group_settings ADD COLUMN clean_voice_chat_messages BOOLEAN DEFAULT 0"))
        except:
            pass
        
        try:
            conn.execute(text("ALTER TABLE group_settings ADD COLUMN custom_admin_roles TEXT DEFAULT '{}'"))
        except:
            pass
        
        try:
            conn.execute(text("ALTER TABLE group_settings ADD COLUMN user_warns TEXT DEFAULT '{}'"))
        except:
            pass
        
        try:
            conn.execute(text("ALTER TABLE group_settings ADD COLUMN muted_users TEXT DEFAULT '[]'"))
        except:
            pass
        
        try:
            conn.execute(text("ALTER TABLE group_settings ADD COLUMN chat_filters TEXT DEFAULT '{}'"))
        except:
            pass
        
        try:
            conn.execute(text("ALTER TABLE group_settings ADD COLUMN blocked_words TEXT DEFAULT '[]'"))
        except:
            pass
        
        conn.commit()

# Run migration
migrate_database()

Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)


def get_session():
    """Get a new database session"""
    return Session()


def get_or_create_group(chat_id):
    """Get existing group settings or create new ones"""
    session = get_session()
    try:
        settings = session.query(GroupSettings).filter_by(chat_id=str(chat_id)).first()
        if not settings:
            settings = GroupSettings(chat_id=str(chat_id))
            session.add(settings)
            session.commit()
        return settings
    finally:
        session.close()


def update_group_setting(chat_id, **kwargs):
    """Update group settings"""
    session = get_session()
    try:
        settings = session.query(GroupSettings).filter_by(chat_id=str(chat_id)).first()
        if not settings:
            settings = GroupSettings(chat_id=str(chat_id))
            session.add(settings)
        
        for key, value in kwargs.items():
            if hasattr(settings, key):
                setattr(settings, key, value)
        
        session.commit()
        return settings
    finally:
        session.close()
