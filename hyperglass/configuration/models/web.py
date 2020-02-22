"""Validate branding configuration variables."""

# Standard Library
from typing import Optional

# Third Party
from pydantic import (
    HttpUrl,
    FilePath,
    StrictInt,
    StrictStr,
    StrictBool,
    constr,
    validator,
    root_validator,
)
from pydantic.color import Color

# Project
from hyperglass.constants import DNS_OVER_HTTPS, FUNC_COLOR_MAP
from hyperglass.configuration.models._utils import HyperglassModel, validate_image
from hyperglass.configuration.models.opengraph import OpenGraph


class HyperglassLevel3(HyperglassModel):
    """Automatic docs sorting subclass."""

    class Config:
        """Pydantic model configuration."""

        schema_extra = {"level": 3}


class HyperglassLevel4(HyperglassModel):
    """Automatic docs sorting subclass."""

    class Config:
        """Pydantic model configuration."""

        schema_extra = {"level": 4}


class Analytics(HyperglassLevel3):
    """Validation model for Google Analytics."""

    enable: StrictBool = False
    id: Optional[StrictStr]

    @validator("id")
    def validate_id(cls, value, values):
        """Ensure ID is set if analytics is enabled.

        Arguments:
            value {str|None} -- Google Analytics ID
            values {[type]} -- Already-validated model parameters

        Raises:
            ValueError: Raised if analytics is enabled but no ID is set.

        Returns:
            {str|None} -- Google Analytics ID if enabled.
        """
        if values["enable"] and value is None:
            raise ValueError("Analytics is enabled, but no ID is set.")
        return value


class Credit(HyperglassLevel3):
    """Validation model for developer credit."""

    enable: StrictBool = True


class ExternalLink(HyperglassLevel3):
    """Validation model for external link."""

    enable: StrictBool = True
    title: StrictStr = "PeeringDB"
    url: HttpUrl = "https://www.peeringdb.com/AS{primary_asn}"


class HelpMenu(HyperglassLevel3):
    """Validation model for generic help menu."""

    enable: StrictBool = True
    file: Optional[FilePath]
    title: StrictStr = "Help"


class Logo(HyperglassLevel3):
    """Validation model for logo configuration."""

    light: StrictStr = "images/hyperglass-light.png"
    dark: StrictStr = "images/hyperglass-dark.png"
    width: StrictInt = 384
    height: Optional[StrictInt]
    favicons: StrictStr = "ui/images/favicons/"

    @validator("favicons")
    def favicons_trailing_slash(cls, value):
        """If the favicons path does not end in a '/', append it."""
        chars = list(value)
        if chars[len(chars) - 1] != "/":
            chars.append("/")
        return "".join(chars)

    @validator("light", "dark")
    def validate_logos(cls, value):
        """Convert file path to URL path.

        Arguments:
            value {FilePath} -- Path to logo file.

        Returns:
            {str} -- Formatted logo path
        """
        return validate_image(value)

    class Config:
        """Override pydantic config."""

        fields = {"logo_path": "path"}


class Terms(HyperglassLevel3):
    """Validation model for terms & conditions."""

    enable: StrictBool = True
    file: Optional[FilePath]
    title: StrictStr = "Terms"


class Text(HyperglassLevel3):
    """Validation model for params.branding.text."""

    title_mode: constr(regex=("logo_only|text_only|logo_title|all")) = "logo_only"
    title: StrictStr = "hyperglass"
    subtitle: StrictStr = "AS{primary_asn}"
    query_location: StrictStr = "Location"
    query_type: StrictStr = "Query Type"
    query_target: StrictStr = "Target"
    query_vrf: StrictStr = "Routing Table"
    fqdn_tooltip: StrictStr = "Use {protocol}"  # Formatted by Javascript
    cache: StrictStr = "Results will be cached for {timeout} {period}."


class ThemeColors(HyperglassLevel4):
    """Validation model for theme colors."""

    black: Color = "#262626"
    white: Color = "#f7f7f7"
    gray: Color = "#c1c7cc"
    red: Color = "#d84b4b"
    orange: Color = "#ff6b35"
    yellow: Color = "#edae49"
    green: Color = "#35b246"
    blue: Color = "#314cb6"
    teal: Color = "#35b299"
    cyan: Color = "#118ab2"
    pink: Color = "#f2607d"
    purple: Color = "#8d30b5"
    primary: Optional[Color]
    secondary: Optional[Color]
    success: Optional[Color]
    warning: Optional[Color]
    error: Optional[Color]
    danger: Optional[Color]

    @validator(*FUNC_COLOR_MAP.keys(), pre=True, always=True)
    def validate_colors(cls, value, values, field):
        """Set default functional color mapping.

        Arguments:
            value {str|None} -- Functional color
            values {str} -- Already-validated colors
        Returns:
            {str} -- Mapped color.
        """
        if value is None:
            default_color = FUNC_COLOR_MAP[field.name]
            value = str(values[default_color])
        return value

    def dict(self, *args, **kwargs):
        """Return dict for colors only."""
        return {k: v.as_hex() for k, v in self.__dict__.items()}


class ThemeFonts(HyperglassLevel4):
    """Validation model for theme fonts."""

    body: StrictStr = "Nunito"
    mono: StrictStr = "Fira Code"


class Theme(HyperglassLevel3):
    """Validation model for theme variables."""

    colors: ThemeColors = ThemeColors()
    fonts: ThemeFonts = ThemeFonts()


class DnsOverHttps(HyperglassLevel3):
    """Validation model for DNS over HTTPS resolution."""

    name: constr(regex="|".join(DNS_OVER_HTTPS.keys())) = "cloudflare"

    @root_validator
    def validate_dns(cls, values):
        """Assign url field to model based on selected provider.

        Arguments:
            values {dict} -- Dict of selected provider

        Returns:
            {dict} -- Dict with url attribute
        """
        provider = values["name"]
        values["url"] = DNS_OVER_HTTPS[provider]
        return values


class Web(HyperglassModel):
    """Validation model for all web/browser-related configuration."""

    credit: Credit = Credit()
    dns_provider: DnsOverHttps = DnsOverHttps()
    external_link: ExternalLink = ExternalLink()
    help_menu: HelpMenu = HelpMenu()
    logo: Logo = Logo()
    opengraph: OpenGraph = OpenGraph()
    terms: Terms = Terms()
    text: Text = Text()
    theme: Theme = Theme()

    class Config:
        """Pydantic model configuration."""

        schema_extra = {"level": 2}