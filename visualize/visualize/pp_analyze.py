WEBSITES_BY_CONFLICTS__50 = {
    0: [
        "amazonaws.com",
        "googleusercontent.com",
        "mozilla.org",
        "opera.com",
        "europa.eu",
    ],
    1: [
        "google.com",
        "googleapis.com",
        "youtube.com",
        "gstatic.com",
        "googlevideo.com",
        "googletagmanager.com",
        "wordpress.org",
        "github.com",
        "digicert.com",
        "goo.gl",
        "bit.ly",
        "gandi.net",
        "reddit.com",
        "snapchat.com",
        "comcast.net",
    ],
    2: ["yahoo.com", "samsung.com"],
    3: ["azure.com", "tiktok.com"],
    4: ["office.net"],
    5: ["fastly.net", "netflix.com", "adobe.com", "dropbox.com"],
    6: [
        "linkedin.com",
        "amazon.com",
        "bing.com",
        "wikipedia.org",
        "pinterest.com",
        "spotify.com",
        "vimeo.com",
        "unity3d.com",
    ],
    7: ["icloud.com", "intuit.com"],
    8: ["zoom.us"],
    9: ["facebook.com", "cloudflare.com", "instagram.com", "tumblr.com"],
    10: ["apple.com"],
    12: ["wordpress.com"],
    13: ["office.com", "microsoftonline.com", "windows.net", "roblox.com"],
}


PERSONAS_BY_CONFLICTS__50 = {
    0: [
        "comm-internal-1st-allow",
        "comm-internal-1st-no",
        "contact-ad-no",
        "picture-pubsec-no",
        "social-sns-allow",
        "social-sns-no",
        "identifying-pubsec-no",
    ],
    1: [
        "location-ad-3rd-no",
        "location-ad-no",
    ],
    2: [
        "contact-analytics-no"
    ],
    4: [
        "picture-pubsec-allow"
    ],
    5: [
        "health-research-allow"
    ],
    12: [
        "contact-analytics-all-allow",
        "location-analytics-no",
    ],
    13: [
        "contact-ad-allow",
        "contact-analytics-1st-allow",
    ],
    17: ["contact-1st-only"],
    20: ["data-ad-3rd-no"],
    21: [
        "location-analytics-all-allow"
    ],
    23: [
        "location-analytics-1st-allow",
        "location-internal-1st-allow",
        "location-ad-allow",
    ],
    39: ["location-3rd-no"],
}


WEBSITES_AND_CONFLICT_SEGMENTS_BY_CONFLICTS__50 = {
    0: {
        "amazonaws.com": {},
        "europa.eu": {},
        "googleusercontent.com": {},
        "mozilla.org": {},
        "opera.com": {},
    },
    1: {
        "bit.ly": {
            "data-ad-3rd-no": 8
        },
        "comcast.net": {
            "data-ad-3rd-no": 8
        },
        "digicert.com": {
            "data-ad-3rd-no": 5
        },
        "gandi.net": {
            "location-3rd-no": 3
        },
        "github.com": {
            "health-research-allow": 1
        },
        "goo.gl": {
            "location-3rd-no": 1
        },
        "google.com": {
            "location-3rd-no": 1
        },
        "googleapis.com": {
            "location-3rd-no": 1
        },
        "googletagmanager.com": {
            "location-3rd-no": 1
        },
        "googlevideo.com": {
            "location-3rd-no": 1
        },
        "gstatic.com": {
            "location-3rd-no": 1
        },
        "reddit.com": {
            "location-3rd-no": 1
        },
        "snapchat.com": {
            "location-3rd-no": 1
        },
        "wordpress.org": {
            "data-ad-3rd-no": 2
        },
        "youtube.com": {
            "location-3rd-no": 1
        },
    },
    2: {
        "samsung.com": {
            "data-ad-3rd-no": 7,
            "location-3rd-no": 1,
        },
        "yahoo.com": {
            "data-ad-3rd-no": 3,
            "location-3rd-no": 1,
        },
    },
    3: {
        "azure.com": {
            "contact-1st-only": 1,
            "health-research-allow": 1,
            "location-3rd-no": 1,
        },
        "tiktok.com": {
            "contact-1st-only": 3,
            "data-ad-3rd-no": 5,
            "location-3rd-no": 1,
        },
    },
    4: {
        "office.net": {
            "contact-1st-only": 1,
            "contact-ad-allow": 1,
            "contact-analytics-1st-allow": 1,
            "contact-analytics-all-allow": 1,
        }
    },
    5: {
        "adobe.com": {
            "location-3rd-no": 2,
            "location-ad-allow": 1,
            "location-analytics-1st-allow": 1,
            "location-analytics-all-allow": 1,
            "location-internal-1st-allow": 1,
        },
        "dropbox.com": {
            "location-3rd-no": 2,
            "location-ad-allow": 1,
            "location-analytics-1st-allow": 2,
            "location-analytics-no": 2,
            "location-internal-1st-allow": 2,
        },
        "fastly.net": {
            "contact-1st-only": 2,
            "contact-ad-allow": 1,
            "contact-analytics-1st-allow": 1,
            "contact-analytics-all-allow": 1,
            "location-3rd-no": 1,
        },
        "netflix.com": {
            "location-3rd-no": 1,
            "location-ad-allow": 1,
            "location-analytics-1st-allow": 1,
            "location-analytics-all-allow": 1,
            "location-internal-1st-allow": 1,
        },
    },
    6: {
        "amazon.com": {
            "data-ad-3rd-no": 2,
            "location-3rd-no": 1,
            "location-ad-allow": 1,
            "location-analytics-1st-allow": 1,
            "location-analytics-all-allow": 1,
            "location-internal-1st-allow": 1,
        },
        "bing.com": {
            "data-ad-3rd-no": 8,
            "location-3rd-no": 1,
            "location-ad-allow": 1,
            "location-analytics-1st-allow": 1,
            "location-analytics-all-allow": 1,
            "location-internal-1st-allow": 1,
        },
        "linkedin.com": {
            "contact-1st-only": 1,
            "location-3rd-no": 1,
            "location-ad-allow": 1,
            "location-analytics-1st-allow": 1,
            "location-analytics-all-allow": 1,
            "location-internal-1st-allow": 1,
        },
        "pinterest.com": {
            "data-ad-3rd-no": 6,
            "location-3rd-no": 2,
            "location-ad-allow": 1,
            "location-analytics-1st-allow": 1,
            "location-analytics-all-allow": 1,
            "location-internal-1st-allow": 2,
        },
        "spotify.com": {
            "data-ad-3rd-no": 7,
            "location-3rd-no": 1,
            "location-ad-allow": 1,
            "location-analytics-1st-allow": 1,
            "location-analytics-all-allow": 1,
            "location-internal-1st-allow": 1,
        },
        "unity3d.com": {
            "contact-1st-only": 1,
            "contact-ad-allow": 1,
            "contact-analytics-1st-allow": 1,
            "contact-analytics-no": 1,
            "data-ad-3rd-no": 19,
            "location-3rd-no": 3,
        },
        "vimeo.com": {
            "data-ad-3rd-no": 10,
            "location-3rd-no": 1,
            "location-ad-allow": 1,
            "location-analytics-1st-allow": 1,
            "location-analytics-all-allow": 1,
            "location-internal-1st-allow": 1,
        },
        "wikipedia.org": {
            "location-3rd-no": 5,
            "location-ad-allow": 3,
            "location-analytics-1st-allow": 5,
            "location-analytics-all-allow": 2,
            "location-analytics-no": 5,
            "location-internal-1st-allow": 5,
        },
    },
    7: {
        "icloud.com": {
            "contact-1st-only": 1,
            "location-3rd-no": 4,
            "location-ad-allow": 4,
            "location-analytics-1st-allow": 4,
            "location-analytics-all-allow": 4,
            "location-analytics-no": 4,
            "location-internal-1st-allow": 4,
        },
        "intuit.com": {
            "data-ad-3rd-no": 8,
            "location-3rd-no": 2,
            "location-ad-allow": 2,
            "location-analytics-1st-allow": 2,
            "location-analytics-all-allow": 2,
            "location-analytics-no": 2,
            "location-internal-1st-allow": 2,
        },
    },
    8: {
        "zoom.us": {
            "data-ad-3rd-no": 17,
            "location-3rd-no": 4,
            "location-ad-allow": 3,
            "location-analytics-1st-allow": 4,
            "location-analytics-all-allow": 2,
            "location-analytics-no": 4,
            "location-internal-1st-allow": 4,
            "picture-pubsec-allow": 1,
        }
    },
    9: {
        "cloudflare.com": {
            "contact-1st-only": 1,
            "contact-ad-allow": 1,
            "contact-analytics-1st-allow": 1,
            "contact-analytics-all-allow": 1,
            "location-3rd-no": 1,
            "location-ad-allow": 1,
            "location-analytics-1st-allow": 1,
            "location-analytics-all-allow": 1,
            "location-internal-1st-allow": 1,
        },
        "facebook.com": {
            "contact-1st-only": 1,
            "contact-ad-allow": 1,
            "contact-analytics-1st-allow": 1,
            "contact-analytics-all-allow": 1,
            "location-3rd-no": 2,
            "location-ad-allow": 1,
            "location-analytics-1st-allow": 1,
            "location-analytics-all-allow": 1,
            "location-internal-1st-allow": 2,
        },
        "instagram.com": {
            "contact-1st-only": 1,
            "contact-ad-allow": 1,
            "contact-analytics-1st-allow": 1,
            "contact-analytics-all-allow": 1,
            "location-3rd-no": 1,
            "location-ad-allow": 1,
            "location-analytics-1st-allow": 1,
            "location-analytics-no": 1,
            "location-internal-1st-allow": 1,
        },
        "tumblr.com": {
            "contact-1st-only": 1,
            "contact-ad-allow": 1,
            "contact-analytics-1st-allow": 1,
            "contact-analytics-all-allow": 1,
            "location-3rd-no": 2,
            "location-ad-allow": 1,
            "location-analytics-1st-allow": 1,
            "location-analytics-all-allow": 1,
            "location-internal-1st-allow": 2,
        },
    },
    10: {
        "apple.com": {
            "contact-1st-only": 1,
            "contact-ad-allow": 1,
            "contact-analytics-1st-allow": 1,
            "contact-analytics-all-allow": 1,
            "location-3rd-no": 4,
            "location-ad-allow": 4,
            "location-analytics-1st-allow": 4,
            "location-analytics-all-allow": 4,
            "location-analytics-no": 4,
            "location-internal-1st-allow": 4,
        }
    },
    12: {
        "wordpress.com": {
            "contact-1st-only": 2,
            "contact-ad-allow": 2,
            "contact-analytics-1st-allow": 2,
            "contact-analytics-all-allow": 2,
            "contact-analytics-no": 2,
            "data-ad-3rd-no": 6,
            "location-3rd-no": 3,
            "location-ad-allow": 3,
            "location-analytics-1st-allow": 3,
            "location-analytics-all-allow": 2,
            "location-analytics-no": 3,
            "location-internal-1st-allow": 3,
        }
    },
    13: {
        "microsoftonline.com": {
            "contact-1st-only": 7,
            "contact-ad-allow": 4,
            "contact-analytics-1st-allow": 4,
            "contact-analytics-all-allow": 4,
            "data-ad-3rd-no": 34,
            "health-research-allow": 2,
            "location-3rd-no": 12,
            "location-ad-allow": 12,
            "location-analytics-1st-allow": 12,
            "location-analytics-all-allow": 12,
            "location-analytics-no": 12,
            "location-internal-1st-allow": 12,
            "picture-pubsec-allow": 1,
        },
        "office.com": {
            "contact-1st-only": 6,
            "contact-ad-allow": 4,
            "contact-analytics-1st-allow": 4,
            "contact-analytics-all-allow": 4,
            "data-ad-3rd-no": 38,
            "health-research-allow": 9,
            "location-3rd-no": 9,
            "location-ad-allow": 9,
            "location-analytics-1st-allow": 9,
            "location-analytics-all-allow": 9,
            "location-analytics-no": 9,
            "location-internal-1st-allow": 9,
            "picture-pubsec-allow": 5,
        },
        "roblox.com": {
            "contact-1st-only": 3,
            "contact-ad-allow": 3,
            "contact-analytics-1st-allow": 3,
            "contact-analytics-all-allow": 3,
            "data-ad-3rd-no": 4,
            "location-3rd-no": 3,
            "location-ad-3rd-no": 3,
            "location-ad-allow": 3,
            "location-ad-no": 3,
            "location-analytics-1st-allow": 3,
            "location-analytics-all-allow": 3,
            "location-analytics-no": 3,
            "location-internal-1st-allow": 3,
        },
        "windows.net": {
            "contact-1st-only": 7,
            "contact-ad-allow": 5,
            "contact-analytics-1st-allow": 5,
            "contact-analytics-all-allow": 5,
            "data-ad-3rd-no": 37,
            "health-research-allow": 1,
            "location-3rd-no": 11,
            "location-ad-allow": 11,
            "location-analytics-1st-allow": 11,
            "location-analytics-all-allow": 11,
            "location-analytics-no": 11,
            "location-internal-1st-allow": 11,
            "picture-pubsec-allow": 5,
        },
    },
}


PERSONA_AND_CONFLICG_SEGMENTS_BY_CONFLICTS__50 = {
    0: {
        "comm-internal-1st-allow": {},
        "comm-internal-1st-no": {},
        "contact-ad-no": {},
        "identifying-pubsec-no": {},
        "picture-pubsec-no": {},
        "social-sns-allow": {},
        "social-sns-no": {},
    },
    1: {
        "location-ad-3rd-no": {
            "roblox.com": 3
        },
        "location-ad-no": {
            "roblox.com": 3
        },
    },
    2: {
        "contact-analytics-no": {
            "unity3d.com": 1,
            "wordpress.com": 2,
        }
    },
    4: {
        "picture-pubsec-allow": {
            "microsoftonline.com": 1,
            "office.com": 5,
            "windows.net": 5,
            "zoom.us": 1,
        }
    },
    5: {
        "health-research-allow": {
            "azure.com": 1,
            "github.com": 1,
            "microsoftonline.com": 2,
            "office.com": 9,
            "windows.net": 1,
        }
    },
    12: {
        "contact-analytics-all-allow": {
            "apple.com": 1,
            "cloudflare.com": 1,
            "facebook.com": 1,
            "fastly.net": 1,
            "instagram.com": 1,
            "microsoftonline.com": 4,
            "office.com": 4,
            "office.net": 1,
            "roblox.com": 3,
            "tumblr.com": 1,
            "windows.net": 5,
            "wordpress.com": 2,
        },
        "location-analytics-no": {
            "apple.com": 4,
            "dropbox.com": 2,
            "icloud.com": 4,
            "instagram.com": 1,
            "intuit.com": 2,
            "microsoftonline.com": 12,
            "office.com": 9,
            "roblox.com": 3,
            "wikipedia.org": 5,
            "windows.net": 11,
            "wordpress.com": 3,
            "zoom.us": 4,
        },
    },
    13: {
        "contact-ad-allow": {
            "apple.com": 1,
            "cloudflare.com": 1,
            "facebook.com": 1,
            "fastly.net": 1,
            "instagram.com": 1,
            "microsoftonline.com": 4,
            "office.com": 4,
            "office.net": 1,
            "roblox.com": 3,
            "tumblr.com": 1,
            "unity3d.com": 1,
            "windows.net": 5,
            "wordpress.com": 2,
        },
        "contact-analytics-1st-allow": {
            "apple.com": 1,
            "cloudflare.com": 1,
            "facebook.com": 1,
            "fastly.net": 1,
            "instagram.com": 1,
            "microsoftonline.com": 4,
            "office.com": 4,
            "office.net": 1,
            "roblox.com": 3,
            "tumblr.com": 1,
            "unity3d.com": 1,
            "windows.net": 5,
            "wordpress.com": 2,
        },
    },
    17: {
        "contact-1st-only": {
            "apple.com": 1,
            "azure.com": 1,
            "cloudflare.com": 1,
            "facebook.com": 1,
            "fastly.net": 2,
            "icloud.com": 1,
            "instagram.com": 1,
            "linkedin.com": 1,
            "microsoftonline.com": 7,
            "office.com": 6,
            "office.net": 1,
            "roblox.com": 3,
            "tiktok.com": 3,
            "tumblr.com": 1,
            "unity3d.com": 1,
            "windows.net": 7,
            "wordpress.com": 2,
        }
    },
    20: {
        "data-ad-3rd-no": {
            "amazon.com": 2,
            "bing.com": 8,
            "bit.ly": 8,
            "comcast.net": 8,
            "digicert.com": 5,
            "intuit.com": 8,
            "microsoftonline.com": 34,
            "office.com": 38,
            "pinterest.com": 6,
            "roblox.com": 4,
            "samsung.com": 7,
            "spotify.com": 7,
            "tiktok.com": 5,
            "unity3d.com": 19,
            "vimeo.com": 10,
            "windows.net": 37,
            "wordpress.com": 6,
            "wordpress.org": 2,
            "yahoo.com": 3,
            "zoom.us": 17,
        }
    },
    21: {
        "location-analytics-all-allow": {
            "adobe.com": 1,
            "amazon.com": 1,
            "apple.com": 4,
            "bing.com": 1,
            "cloudflare.com": 1,
            "facebook.com": 1,
            "icloud.com": 4,
            "intuit.com": 2,
            "linkedin.com": 1,
            "microsoftonline.com": 12,
            "netflix.com": 1,
            "office.com": 9,
            "pinterest.com": 1,
            "roblox.com": 3,
            "spotify.com": 1,
            "tumblr.com": 1,
            "vimeo.com": 1,
            "wikipedia.org": 2,
            "windows.net": 11,
            "wordpress.com": 2,
            "zoom.us": 2,
        }
    },
    23: {
        "location-ad-allow": {
            "adobe.com": 1,
            "amazon.com": 1,
            "apple.com": 4,
            "bing.com": 1,
            "cloudflare.com": 1,
            "dropbox.com": 1,
            "facebook.com": 1,
            "icloud.com": 4,
            "instagram.com": 1,
            "intuit.com": 2,
            "linkedin.com": 1,
            "microsoftonline.com": 12,
            "netflix.com": 1,
            "office.com": 9,
            "pinterest.com": 1,
            "roblox.com": 3,
            "spotify.com": 1,
            "tumblr.com": 1,
            "vimeo.com": 1,
            "wikipedia.org": 3,
            "windows.net": 11,
            "wordpress.com": 3,
            "zoom.us": 3,
        },
        "location-analytics-1st-allow": {
            "adobe.com": 1,
            "amazon.com": 1,
            "apple.com": 4,
            "bing.com": 1,
            "cloudflare.com": 1,
            "dropbox.com": 2,
            "facebook.com": 1,
            "icloud.com": 4,
            "instagram.com": 1,
            "intuit.com": 2,
            "linkedin.com": 1,
            "microsoftonline.com": 12,
            "netflix.com": 1,
            "office.com": 9,
            "pinterest.com": 1,
            "roblox.com": 3,
            "spotify.com": 1,
            "tumblr.com": 1,
            "vimeo.com": 1,
            "wikipedia.org": 5,
            "windows.net": 11,
            "wordpress.com": 3,
            "zoom.us": 4,
        },
        "location-internal-1st-allow": {
            "adobe.com": 1,
            "amazon.com": 1,
            "apple.com": 4,
            "bing.com": 1,
            "cloudflare.com": 1,
            "dropbox.com": 2,
            "facebook.com": 2,
            "icloud.com": 4,
            "instagram.com": 1,
            "intuit.com": 2,
            "linkedin.com": 1,
            "microsoftonline.com": 12,
            "netflix.com": 1,
            "office.com": 9,
            "pinterest.com": 2,
            "roblox.com": 3,
            "spotify.com": 1,
            "tumblr.com": 2,
            "vimeo.com": 1,
            "wikipedia.org": 5,
            "windows.net": 11,
            "wordpress.com": 3,
            "zoom.us": 4,
        },
    },
    39: {
        "location-3rd-no": {
            "adobe.com": 2,
            "amazon.com": 1,
            "apple.com": 4,
            "azure.com": 1,
            "bing.com": 1,
            "cloudflare.com": 1,
            "dropbox.com": 2,
            "facebook.com": 2,
            "fastly.net": 1,
            "gandi.net": 3,
            "goo.gl": 1,
            "google.com": 1,
            "googleapis.com": 1,
            "googletagmanager.com": 1,
            "googlevideo.com": 1,
            "gstatic.com": 1,
            "icloud.com": 4,
            "instagram.com": 1,
            "intuit.com": 2,
            "linkedin.com": 1,
            "microsoftonline.com": 12,
            "netflix.com": 1,
            "office.com": 9,
            "pinterest.com": 2,
            "reddit.com": 1,
            "roblox.com": 3,
            "samsung.com": 1,
            "snapchat.com": 1,
            "spotify.com": 1,
            "tiktok.com": 1,
            "tumblr.com": 2,
            "unity3d.com": 3,
            "vimeo.com": 1,
            "wikipedia.org": 5,
            "windows.net": 11,
            "wordpress.com": 3,
            "yahoo.com": 1,
            "youtube.com": 1,
            "zoom.us": 4,
        }
    },
}


WEBSITES_WITH_SAME_POLICY = [
    ["googleapis.com", "google-analytics.com"],
    ["gstatic.com", "doubleclick.net"],
    [
        "office.com",
        "live.com",
        "sharepoint.com",
        "skype.com",
        "msn.com",
        "office365.com",
    ],
    ["googletagmanager.com", "youtu.be"],
]


# Average conflict rate for each number of conflicting profiles; denominator is the total number of segments in the privacy policy
# This measures how easy a website's privacy policy (based on the number of segments in the PP) is to conflict with a/some profile. Higher number implies that the website's privacy policy is more likely to conflict with a profile.
# More intuitively, at the same number of conflicts, this measures how detailed a privacy policy is -- a lower number means the privacy policy is more detailed (each segment is less likely to conflict with a profile).
# For across number of conflicts, when the number of conflicts is higher, if the detailing status is roughly the same, this ratio is expected to be higher in the same rate. If there is a sudden drop, it means that the privacy policy is more detailed.
# rate(website) = num_conflicting_profiles / num_segments_in_privacy_policy
# Grouping is the number of conflicting profiles, same from to_websites_by_num_conflicts()
AVERAGE_CONFLICT_RATE_0__50 = {
    0: 0.0,
    1: 0.010186640082404304,
    2: 0.022161172161172162,
    3: 0.04551282051282052,
    4: 0.05405405405405406,
    5: 0.06410283579727835,
    6: 0.06325853221270857,
    7: 0.08599033816425121,
    8: 0.0427807486631016,
    9: 0.09760510787387056,
    10: 0.1388888888888889,
    12: 0.06282722513089005,
    13: 0.030898352229157145,
}


# Average conflict rate for each number of conflicting profiles; denominator is the number of conflicting segments
# This also measures how easy a website's privacy policy is to conflict with a profile. But different from above, this emphasis more on how more likely each conflicting segment invokes a conflict (rather than the whole privacy policy document).
# More intuitively, at the same number of conflicts, this number indicates how complex/controversal a segment is (average in the group), if the segment is in conflict with some profile.
# For across number of conflicts, this number is expected to be the same, if the privacy-respecting level is the same. If there is a sudden increase, it means that the privacy policy is more complex/controversal; if there is a sudden drop, it means that the privacy policy is more privacy-respecting.
# This number aims to reduce the impact of the length of the privacy policy document, such as because of more contextual description or more new lines (thus more segments).
# The implication is that if only a few segments are in conflict in a long document, this ratio will be higher (i.e. more sensitive).
AVERAGE_CONFLICT_RATE_1__50 = {
    0: 0.0,
    1: 0.7522222222222222,
    2: 0.375,
    3: 0.6666666666666666,
    4: 1.0,
    5: 0.8055555555555556,
    6: 0.5188736263736263,
    7: 0.315,
    8: 0.20512820512820512,
    9: 0.9090909090909092,
    10: 0.35714285714285715,
    12: 0.36363636363636365,
    13: 0.15765946272469836,
}


AVERAGE_CONFLICT_RATE_2__50 = {
    0: 0.0,
    1: 0.7522222222222222,
    2: 0.375,
    3: 0.6666666666666666,
    4: 4.0,
    5: 2.9166666666666665,
    6: 1.1466238471673253,
    7: 1.225,
    8: 0.36363636363636365,
    9: 3.75,
    10: 2.5,
    12: 1.2,
    13: 0.48757765973090217,
}
