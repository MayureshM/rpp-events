from voluptuous import All, Any, Length, Optional, Required, Schema, Url, ALLOW_EXTRA


def get_eventer_event_validator():
    return Schema(
        {
            "href": Url(str),
            Required("eventType"): Any(str),
            Required("body"): Any(dict),
            "createdOn": Any(str),
        },
        extra=True,
    )


def get_inspection_repair_event_validator():
    return Schema(
        {
            Required("eventType"): Any(str),
            Required("body"): Any(dict),
            "createdOn": Any(str),
        },
        extra=True,
    )


def get_pe_event_validator():
    return Schema(
        {
            Required("eventType"): Any(str),
        },
        extra=True,
    )


def get_rpp_event_validator():
    return Schema(
        {
            Required("event_type"): Any(str),
        },
        extra=True,
    )


def get_subscription_cfn_validator():
    default = {"ALL": ["root"]}
    source_keys = Schema(
        {
            Required(
                Any("Eventer", "Inspection", "PE", "RPP"),
                msg="Must specify at least one of \
                     ['Eventer','Inspection', 'PE', 'RPP']",
            ): object
        },
        extra=True,
    )

    source_dict = Schema(
        {
            Optional("Eventer"): All(
                Schema(
                    {
                        Required("Events"): Any(list),
                        Optional("Expansions", default=default): Schema(
                            {Required(Any(str)): Any(list)}
                        ),
                        Optional("Filter", default={"ALL": " "}): Schema(
                            {Required(Any(str)): Any(str)}
                        ),
                    }
                )
            ),
            Optional("Inspection"): All(Schema({Required("Events"): Any(list)})),
            Optional("PE"): All(Schema({Required("Events"): Any(list)})),
            Optional("RPP"): All(Schema({Required("Events"): Any(list)})),
        }
    )

    return Schema(
        {
            Required("Source"): All(source_keys, source_dict),
            Required("Targets"): All(
                Schema({Required(Any("SQS", "Lambda")): Any(str)})
            ),
        },
        extra=True,
    )


def get_subscriber_cfn_validator():
    return Schema(
        {
            "Source": All(
                Schema(
                    {
                        Required("Eventer"): All(
                            Schema(
                                {
                                    Required("CallbackUrl"): Url(str),
                                    Required("Emails"): Any(list),
                                    "Headers": Any(dict),
                                    "Inactive": Any("true", "false"),
                                }
                            )
                        )
                    }
                )
            )
        },
        extra=True,
    )


def get_config_validator() -> Schema:
    schema = Schema(
        {
            "application_name": All(str, Length(min=1)),
            "environment_name": All(str, Length(min=1)),
            "configuration_name": All(str, Length(min=1)),
            "transform": ["json", "base64", None],
        },
        required=True,
        extra=ALLOW_EXTRA,
    )

    return schema


def validate_config_event(properties):
    event_validator = get_config_validator()
    return event_validator(properties)


def validate_eventer_event(properties):
    event_validator = get_eventer_event_validator()
    return event_validator(properties)


def validate_inspection_repair_event(properties):
    event_validator = get_inspection_repair_event_validator()
    return event_validator(properties)


def validate_pe_event(properties):
    event_validator = get_pe_event_validator()
    return event_validator(properties)


def validate_rpp_event(properties):
    event_validator = get_rpp_event_validator()
    return event_validator(properties)


def validate_subscription_cfn(properties):
    request_validator = get_subscription_cfn_validator()
    return request_validator(properties)


def validate_subscriber_cfn(properties):
    request_validator = get_subscriber_cfn_validator()
    return request_validator(properties)
