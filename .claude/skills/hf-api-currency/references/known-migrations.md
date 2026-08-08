# Known API migrations

Append one line per surprise discovered. Format:

    <date> | <library> <version> | old -> new | where it bit us

## Entries

(empty — add entries as they are found)
2026-08-07 | transformers 4.57.3 | include_num_input_tokens_seen: bool -> Union[str, bool] | enabling real tokens/sec in ThroughputAndMemoryCallback; True is still valid, but do not annotate it as bool
2026-08-07 | transformers 4.57.3 | evaluation_strategy -> eval_strategy | confirmed removed, not just deprecated; build_sft_config already uses eval_strategy
2026-08-07 | trl 0.25.0 | dataset_text_field -> prompt/completion columns + completion_only_loss=True | completion_only_loss is documented as "supported only for prompt-completion datasets"; with a single text column TRL supervises the WHOLE sequence and train_on_inputs silently did nothing for a full 12h run
2026-08-07 | trl 0.25.0 | packing=True implies padding_free under packing_strategy='bfd' | padding_free is documented as FlashAttention 2/3 only, so packing is unusable on a Turing T4; build_trainer now refuses packing without model.flash_attention
2026-08-07 | trl 0.25.0 | assistant_only_loss needs conversational datasets | not usable with a pre-rendered chat string; the prompt/completion route avoids depending on {% generation %} markers in the Qwen template
