# Ontology definitions: Activities & Data Categories

DATA_LEXICON = {

    # -----------------------
    # 1. Identifiers
    # -----------------------
    "identifier": [
        "name", "full name", "email", "phone", "telephone", "username",
        "ip address", "user id", "account id", "identifier",
        "contact information", "profile picture",
        "is identified", "identifiable"
    ],

    # -----------------------
    # 2. Location Data
    # -----------------------
    "location": [
        "location", "geolocation", "gps", "locational",
        "precise location", "approximate location",
        "where you are", "city", "country", "zip code",
        "location is collected", "location data"
    ],

    # -----------------------
    # 3. Audio Data
    # -----------------------
    "audio": [
        "audio", "voice recording", "microphone", "sound",
        "voice command", "voice interactions",
        # Passive/nominal
        "audio is collected", "audio data", "voice data"
    ],

    # -----------------------
    # 4. Image / Video Data
    # -----------------------
    "video_image": [
        "photo", "photos", "picture", "video", "image",
        "visual information", "camera", "recording",
        "live stream", "media you capture",
        "image is collected", "video is collected", "video data",
        "photo data"
    ],

    # -----------------------
    # 5. Device Information
    # -----------------------
    "device_info": [
        "device information", "device info", "hardware",
        "software version", "browser", "operating system",
        "device identifiers", "cookie", "cookies",
        "battery level", "signal strength", "storage", "model",
        # Passive/nominal
        "device data", "device logs"
    ],

    # -----------------------
    # 6. Usage & Event Logs
    # -----------------------
    "usage_events": [
        "app usage", "log data", "events", "clicks",
        "interactions", "how you use", "performance data",
        "crash reports",
        "usage data", "event logs", "analytics data"
    ],

    # -----------------------
    # 7. Payment Information
    # -----------------------
    "payment": [
        "credit card", "transaction info", "payment details",
        "billing address", "purchase history", "payment information",
        "financial data"
    ],

    # -----------------------
    # 8. Biometric Information
    # -----------------------
    "biometrics": [
        "facial geometry", "voiceprint", "retinal scan",
        "biometric", "face recognition", "biometric identifier",
        "biometric data"
    ],

    # -----------------------
    # 9. Health Information
    # -----------------------
    "health": [
        "prescription data", "medical info", "health data",
        "eyesight check", "health related", "vision information",
        "medical data"
    ]
}



# ================================================================
# Activities
# ================================================================

ACTIVITY_LEXICON = {

    # Smart-glasses capture
    "take_photo_with_glasses": [
        "take photos", "take a photo", "capture photos", "use the camera",
        "taking a photo", "take a picture", "capture a photo",
        "when you take photos"
    ],

    "record_video_with_glasses": [
        "record video", "capture videos", "recording video",
        "record a video", "when you record video", "capture video"
    ],

    # Voice / Meta AI
    "use_voice_assistant": [
        "voice commands", "voice assistant", "hey meta",
        "use meta ai", "voice services", "when you say",
        "interact with the assistant"
    ],

    # Media consumption
    "stream_media": [
        "listen to music", "stream media", "play audio",
        "listening to", "stream content"
    ],

    # Sharing content
    "share_to_facebook": [
        "share to facebook", "post to social",
        "share content", "upload to fb", "upload to facebook"
    ],

    "share_to_social": [
        "share", "post", "upload to facebook", "upload to instagram",
        "share on social media", "post content"
    ],

    # Companion App
    "use_companion_app": [
        "view app", "companion app", "meta view",
        "use the app", "use our app", "open the app"
    ],

    # Website usage
    "visit_rayban_website": [
        "visit our website", "browse our site",
        "use the website", "visit ray-ban.com",
        "browse our webpage"
    ],

    # Account creation
    "create_account": [
        "create an account", "sign up", "register",
        "account creation", "set up your account"
    ],

    # Purchases
    "purchase_glasses": [
        "purchase", "buy", "order", "transaction",
        "buying", "checkout"
    ],

    # Support
    "contact_support": [
        "contact support", "customer service",
        "help center", "contact us", "customer support"
    ],

    # Location services
    "enable_location_services": [
        "location services", "enable location",
        "turn on location", "activate location"
    ],

    # Device pairing
    "pair_device": [
        "pair", "bluetooth", "connect", "link",
        "pair the glasses", "pair your device"
    ]
}


# ================================================================
# Collection verbs (active, passive, nominal)
# ================================================================

COLLECTION_VERBS = [
    # Active  
    "collect", "process", "store", "use", "retain",
    "obtain", "receive", "access", "gather",
    "record", "capture", "provide", "share",

    # Passive  
    "is collected", "are collected", "is processed",
    "is stored", "is used", "is obtained", "is received",
    "is accessed", "is gathered", "is recorded",
    "is captured", "is shared",

    # Nominal forms  
    "collection of", "processing of", "storage of",
    "use of data", "retention of data", "gathering of data",
    "recording of", "capture of", "sharing of"
]
