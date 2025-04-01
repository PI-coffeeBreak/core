from sqlalchemy import Column, String
from dependencies.database import Base

class ColorTheme(Base):
    __tablename__ = "color_themes"

    base_100 = Column(String)
    base_200 = Column(String)
    base_300 = Column(String)
    base_content = Column(String)
    primary = Column(String)
    primary_content = Column(String)
    secondary = Column(String)
    secondary_content = Column(String)
    accent = Column(String)
    accent_content = Column(String)
    neutral = Column(String)
    neutral_content = Column(String)
    info = Column(String)
    info_content = Column(String)
    success = Column(String)
    success_content = Column(String)
    warning = Column(String)
    warning_content = Column(String)
    error = Column(String)
    error_content = Column(String)

    def __repr__(self):
        return f"<ColorTheme(id={self.id}, primary={self.primary}, secondary={self.secondary}, accent={self.accent})>"

# Example of how to populate this model with your provided data
color_data = {
    "base_100": "#f3faff",
    "base_200": "#d6d6d3",
    "base_300": "#d6d6d3",
    "base_content": "#726d65",
    "primary": "#4f2b1d",
    "primary_content": "#f3faff",
    "secondary": "#c6baa2",
    "secondary_content": "#f1fbfb",
    "accent": "#faa275",
    "accent_content": "#f3fbf6",
    "neutral": "#caa751",
    "neutral_content": "#f3faff",
    "info": "#00b2dd",
    "info_content": "#f2fafd",
    "success": "#0cae00",
    "success_content": "#f5faf4",
    "warning": "#fbad00",
    "warning_content": "#221300",
    "error": "#ff1300",
    "error_content": "#fff6f4",
}

# Example: Creating and adding the theme to the database
color_theme = ColorTheme(id="default", **color_data)
