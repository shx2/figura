# Say we want to poll A every X seconds, B every 2*X seconds, and C
# every 8*X seconds.
# We sometimes change X, and rarely change the ratios between A, B, and C.
# Written this way, when we want to change X, we only need to change the value
# of _basic_polling_interval_seconds.
# The rules about the default ratios are encoded here and not in the code
# dealing with params, thus keeping it simple.
_basic_polling_interval_seconds = 5 * 60  # every 5 minutes (more readable than _basic_polling_interval_seconds=300)
class A:
    polling_interval = _basic_polling_interval_seconds
class B:
    polling_interval = _basic_polling_interval_seconds * 2
class C:
    polling_interval = _basic_polling_interval_seconds * 8
