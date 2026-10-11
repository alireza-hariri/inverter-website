# Data model

- **User** is the custom Django authentication model. Email is the login identifier. **MobileLoginCode** stores one hashed, single-use mobile login code with its expiry and attempt count; the digits themselves are never stored or returned.

`apps.common` holds what every app builds on: a timestamped base model, the shared pagination class, and the exception handler that produces the `{ "error": ... }` envelope. Put this site's own models in new apps beside the existing ones and register them in `INSTALLED_APPS`.
