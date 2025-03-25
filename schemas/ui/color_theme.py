from pydantic import BaseModel

class ColorThemeBase(BaseModel):
    base_100: str
    base_200: str
    base_300: str
    base_content: str
    primary: str
    primary_content: str
    secondary: str
    secondary_content: str
    accent: str
    accent_content: str
    neutral: str
    neutral_content: str
    info: str
    info_content: str
    success: str
    success_content: str
    warning: str
    warning_content: str
    error: str
    error_content: str

class ColorThemeCreate(ColorThemeBase):
    pass

class ColorTheme(ColorThemeBase):
    pass

    class Config:
        from_attributes = True
