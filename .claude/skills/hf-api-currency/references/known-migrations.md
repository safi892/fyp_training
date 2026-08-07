# Known API migrations

Append one line per surprise discovered. Format:

    <date> | <library> <version> | old -> new | where it bit us

## Entries

(empty — add entries as they are found)
2026-08-07 | transformers 4.57.3 | include_num_input_tokens_seen: bool -> Union[str, bool] | enabling real tokens/sec in ThroughputAndMemoryCallback; True is still valid, but do not annotate it as bool
2026-08-07 | transformers 4.57.3 | evaluation_strategy -> eval_strategy | confirmed removed, not just deprecated; build_sft_config already uses eval_strategy
