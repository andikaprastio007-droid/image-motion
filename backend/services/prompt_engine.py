NEG_BASE = ("warping, morphing, flickering, melting objects, unstable geometry, duplicated objects, "
            "deformed faces, extra limbs, artificial camera shake, text distortion, sudden cuts")
NEG_STOCK = ", logo, watermark, trademark, unnecessary text, copyrighted characters, excessive camera movement"

VARIATIONS = [
 ("Cinematic Push In", "push_in", "slow cinematic push-in, 4-6% scale over the clip, smooth ease-in-out", "subject stays still, only natural micro-motion", "gentle drift of background elements", "stable lighting with faint highlight shimmer", "ease-in then hold, no loop"),
 ("Cinematic Pull Out", "pull_out", "slow pull-out revealing more of the scene, steady speed", "subject remains static", "background elements settle gently", "even light, slight warm falloff", "no loop"),
 ("Slow Parallax", "pan", "very slow lateral truck with foreground/background parallax", "subject static", "midground and background shift at different speeds for depth", "lighting constant", "no loop"),
 ("Camera Orbit", "pan", "subtle orbit of about 8 degrees around the subject, locked distance", "subject rigid, no deformation", "background reveals naturally by parallax", "specular highlights shift realistically", "no loop"),
 ("Environmental Motion", "minimal", "locked-off tripod, no camera movement", "subject static", "natural wind or water motion in organic elements only (leaves, grass, ripples, fabric)", "stable", "motion cycle designed to repeat"),
 ("Atmospheric Motion", "push_in", "very slow push-in", "subject static", "drifting mist, floating dust particles, soft haze layers moving left to right", "soft volumetric light through atmosphere", "particles wrap around for loop"),
 ("Luxury Commercial", "push_in", "smooth gimbal-like glide, premium commercial pacing", "subject static, polished", "minimal, clean surfaces untouched", "soft elegant highlight sweep across surfaces", "no loop"),
 ("Dramatic Lighting", "minimal", "locked-off or tiny push-in", "subject static", "background static", "light intensity and angle shift slowly, shadows move realistically", "light returns to start for loop"),
 ("Minimal Motion", "minimal", "almost static, 1-2% slow drift", "only tiny natural micro-movements (breathing, blinking light)", "one small element moves, rest frozen", "constant", "slow ping-pong friendly"),
 ("Seamless Loop", "minimal", "locked-off, no net camera travel", "subject static", "cyclic motion with identical first and last frame", "cyclic subtle variation", "first frame equals last frame, crossfade 1s"),
]

def _s(a, k, d=""):
    v = a.get(k, d)
    return ", ".join(map(str, v)) if isinstance(v, list) else str(v)

def build_variations(a, stock_safe=True, duration=8):
    out = []
    for i, (name, ff, cam, subj, env, light, loop) in enumerate(VARIATIONS, 1):
        sections = [
            f"SUBJECT: preserve the original subject and visual identity: {_s(a,'subject')}. Static: {_s(a,'static_elements')}.",
            f"ENVIRONMENT: {_s(a,'environment')}; foreground {_s(a,'foreground')}; midground {_s(a,'midground')}; background {_s(a,'background')}.",
            f"DEPTH: {_s(a,'depth')}; keep layer separation clean.",
            f"MOTION: {subj}. Environment: {env}. Only these elements move; everything else stays fixed. Speed: slow and realistic.",
            f"CAMERA: {cam}.",
            f"LIGHTING: {_s(a,'lighting')}; {light}.",
            f"ATMOSPHERE: soft atmospheric depth matching the source palette {_s(a,'colors')}.",
            "PHYSICS: natural, believable physics; no impossible movement.",
            "TEMPORAL CONSISTENCY: stable geometry, consistent textures, no flicker, same identity every frame.",
            f"COMPOSITION: keep original framing ({_s(a,'composition')}); {loop}.",
            f"QUALITY: photorealistic, sharp, clean {duration}s footage, subtle and realistic motion.",
        ]
        neg = NEG_BASE
        if stock_safe:
            sections.append("STOCK SAFETY: clean commercial footage, generic composition, no branding, no watermark, no unnecessary text.")
            neg += NEG_STOCK
        sections.append("NEGATIVE PROMPT: " + neg)
        out.append({
            "id": i, "name": name, "ffmpeg_motion": ff,
            "description": f"{name}: {cam}",
            "camera_motion": cam, "subject_motion": subj, "environment_motion": env,
            "lighting_motion": light, "duration": duration, "loop_strategy": loop,
            "prompt": "\n".join(sections[:-1] if False else [s for s in sections if not s.startswith("NEGATIVE")]),
            "negative_prompt": neg, "favorite": False,
        })
    return out
