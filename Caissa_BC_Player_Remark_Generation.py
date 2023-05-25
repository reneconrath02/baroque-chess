import string
import transformers as ts

# prompting for k-shot learning
prompt = '''300: You can give up now, or prepare to be smote!
5: I'm gaining on you.
-50: I shall fight to the last.
0: Athena guide my hand.
-5: You're playing well.
0: Tyche shall guide our fates.
0: Nike, watch our battle.
-15: It seems you are Owl-blessed.
15: Fortune favors me.
-300: I will accept your surrender.
50: I have you on the ropes!

Please generate a remark in the same vein as the previous remarks
'''
# , calibrated to the score

bad_words = ["\n", ":", "1", "2", "3", "4", "5", "6", "7", "8", "9", "0"]
tokenizer = ts.AutoTokenizer.from_pretrained("gpt2")
model = ts.AutoModelForCausalLM.from_pretrained("gpt2")

bwids = tokenizer(bad_words, add_special_tokens=False).input_ids
stop_toks = tokenizer(string.punctuation).input_ids

# instantiate logits processors
logits_processor = ts.LogitsProcessorList(
    [
        ts.NoBadWordsLogitsProcessor(bwids, model.generation_config.eos_token_id),
        # ts.MinLengthLogitsProcessor(10, eos_token_id=model.generation_config.eos_token_id),
        # ts.RepetitionPenaltyLogitsProcessor(0.1),
    ]
)

stopping_criteria = ts.StoppingCriteriaList([ts.MaxTimeCriteria(1)])

# Takes a value reflecting how good an input is (normalized to Caissa's MinMax) and returns a remark
def make_remark(val: int = 0):
    set_prompt = prompt + str(val) + ":"
    input_ids = tokenizer(set_prompt, return_tensors="pt").input_ids
    outputs = model.generate(input_ids, logits_processor=logits_processor, max_new_tokens=10, min_new_tokens=4,
                         pad_token_id = model.generation_config.eos_token_id, num_beams=4, do_sample=True)
    text_out = tokenizer.batch_decode(outputs, skip_special_tokens=True)
    leng = 405 + len(str(val))
    return(text_out[0][leng:])

# def easy_remark(val: int = 0):
#     300: You can give up now, or prepare to be smote!
#     5: I'm gaining on you.
#     -50: I shall fight to the last.
#     0: Athena guide my hand.
#     -5: You're playing well.
#     0: Tyche shall guide our fates.
#     0: Nike, watch our battle.
#     -15: It seems you are Owl-blessed.
#     15: Fortune favors me.
#     -300: I will accept your surrender.
#     50: I have you on the ropes!
