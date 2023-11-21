from speech_sample import get_assessment_results_with_json_config, get_content_results, get_continuous_results
from chatting_sample import chatting_from_file


while True:
    funs = [
        get_assessment_results_with_json_config,
        get_content_results,
        get_continuous_results,
        chatting_from_file
    ]
    for idx, fun in enumerate(funs):
        print("{}: {}\n\t{}".format(idx, fun.__name__, fun.__doc__))
    try:
        num = int(input())
        selected_fun = funs[num]
    except EOFError:
        raise
    except Exception as e:
        print(e)
    selected_fun()
