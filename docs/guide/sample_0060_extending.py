class debug_logging:
    # logger_name = log_level
    traffic = 'debug'
    engine = 'debug'
class analysis_debug_logging(debug_logging):
    analyzer = 'debug'  # adding a new param
    traffic = 'warning'  # overshadowing base's traffic param
