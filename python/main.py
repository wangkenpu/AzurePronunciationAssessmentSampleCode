import difflib
import json
import math
import string
import sys
import time

try:
    import azure.cognitiveservices.speech as speechsdk
except ImportError:
    print("""
    Importing the Speech SDK for Python failed.
    Please run "pip install azure-cognitiveservices-speech" to install the SDK.
    """)
    sys.exit(1)


# Set up the subscription info for the Speech Service:
# Replace with your own subscription key and service region (e.g., "westus").
speech_key, service_region = "YourSubscriptionKey", "YourServiceRegion"


def get_assessment_results_with_scenario_id():
    """Performs pronunciation assessment asynchronously with input from an audio file and specified scenario ID.
        See more information at https://aka.ms/csspeech/pa"""

    # Specify the path to an audio file containing speech (mono WAV / PCM with a sampling rate of 16 kHz).
    wave_filename = "../resources/weather_audio.wav"
    script_filename = "../resources/weather_script.txt"
    scenario_id = "[scenario ID will be assigned by product team]"

    # Creates an instance of a speech config with specified subscription key and service region.
    # Replace with your own subscription key and service region (e.g., "westus").
    # Note: The sample is for en-US language.
    speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)
    audio_config = speechsdk.audio.AudioConfig(filename=wave_filename)

    with open(script_filename, "r", encoding="utf-8") as f:
        reference_text = f.read()
    json_string = {
        "GradingSystem": "HundredMark",
        "Granularity": "Phoneme",
        "EnableMiscue": "True",
        "ScenarioId": f"{scenario_id}",
    }
    # Create pronunciation assessment config, set grading system, granularity and if enable miscue
    # based on your requirement.
    pronunciation_config = speechsdk.PronunciationAssessmentConfig(json_string=json.dumps(json_string))
    pronunciation_config.reference_text = reference_text

    # Creates a speech recognizer using a file as audio input.
    language = 'en-US'
    speech_recognizer = speechsdk.SpeechRecognizer(
        speech_config=speech_config, language=language, audio_config=audio_config)
    # apply pronunciation assessment config to speech recognizer
    pronunciation_config.apply_to(speech_recognizer)

    result = speech_recognizer.recognize_once_async().get()

    # Check the result
    if result.reason == speechsdk.ResultReason.RecognizedSpeech:
        pronunciation_result_json = json.loads(
            result.properties.get(speechsdk.PropertyId.SpeechServiceResponse_JsonResult))
        print(pronunciation_result_json)
    elif result.reason == speechsdk.ResultReason.NoMatch:
        print("No speech could be recognized")
    elif result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = result.cancellation_details
        print("Speech Recognition canceled: {}".format(cancellation_details.reason))
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            print("Error details: {}".format(cancellation_details.error_details))


def get_content_results():
    """Performs pronunciation assessment asynchronously with input from an audio file and return content score.
        See more information at https://aka.ms/csspeech/pa"""

    # Specify the path to an audio file containing speech (mono WAV / PCM with a sampling rate of 16 kHz).
    wave_filename = "../resources/Lauren_audio.wav"
    topic_filename = "../resources/Lauren_topic.txt"

    speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)
    audio_config = speechsdk.audio.AudioConfig(filename=wave_filename)
    speech_recognizer = speechsdk.SpeechRecognizer(
        speech_config=speech_config, audio_config=audio_config, language="en-US")
    connection = speechsdk.Connection.from_recognizer(speech_recognizer)

    with open(topic_filename, "r", encoding="utf-8") as f:
        topic = f.read()

    phrase_detection_config = {
        "enrichment": {
            "pronunciationAssessment": {
                "referenceText": "",
                "gradingSystem": "HundredMark",
                "granularity": "Word",
                "dimension": "Comprehensive",
                "enableMiscue": "False",
            },
            "contentAssessment": {
                "topic": topic,
            },
        }
    }
    connection.set_message_property(
        "speech.context",
        "phraseDetection",
        (json.dumps(phrase_detection_config)))

    phrase_output_config = {
        "format": "Detailed",
        "detailed": {
            "options": [
                "WordTimings",
                "PronunciationAssessment",
                "ContentAssessment",
                "SNR",
            ]
        }
    }
    connection.set_message_property(
        "speech.context",
        "phraseOutput",
        (json.dumps(phrase_output_config)))

    # open the connection
    connection.open(for_continuous_recognition=False)

    # apply the pronunciation assessment configuration to the speech recognizer
    result = speech_recognizer.recognize_once()
    if result.reason == speechsdk.ResultReason.RecognizedSpeech:
        pronunciation_result_json = json.loads(
            result.properties.get(speechsdk.PropertyId.SpeechServiceResponse_JsonResult))
        print(pronunciation_result_json["NBest"][0]["ContentAssessment"])
    else:
        message = f">>> [ERROR] WaveName: {wave_filename}, Reason: {result.reason}"
        raise Exception(message)

    # close the connection
    connection.close()


def get_prosody_results():
    """Performs pronunciation assessment asynchronously with input from an audio file and enable prosody assessment.
        See more information at https://aka.ms/csspeech/pa"""

    # Specify the path to an audio file containing speech (mono WAV / PCM with a sampling rate of 16 kHz).
    wave_filename = "../resources/weather_audio.wav"
    script_filename = "../resources/weather_script.txt"

    # Creates an instance of a speech config with specified subscription key and service region.
    # Replace with your own subscription key and service region (e.g., "westus").
    # Note: The sample is for en-US language.
    speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)
    audio_config = speechsdk.audio.AudioConfig(filename=wave_filename)

    with open(script_filename, "r", encoding="utf-8") as f:
        reference_text = f.read()

    # create pronunciation assessment config, set grading system, granularity and if enable miscue
    # based on your requirement.
    json_string = {
        "GradingSystem": "HundredMark",
        "Granularity": "Phoneme",
        "EnableMiscue": "True",
        "EnableProsodyAssessment": "True",
    }
    pronunciation_config = speechsdk.PronunciationAssessmentConfig(json_string=json.dumps(json_string))
    pronunciation_config.reference_text = reference_text

    # Creates a speech recognizer using a file as audio input.
    language = 'en-US'
    speech_recognizer = speechsdk.SpeechRecognizer(
        speech_config=speech_config, language=language, audio_config=audio_config)
    # apply pronunciation assessment config to speech recognizer
    pronunciation_config.apply_to(speech_recognizer)

    result = speech_recognizer.recognize_once_async().get()

    # Check the result
    if result.reason == speechsdk.ResultReason.RecognizedSpeech:
        pronunciation_result_json = json.loads(
            result.properties.get(speechsdk.PropertyId.SpeechServiceResponse_JsonResult))
        print(pronunciation_result_json)
    elif result.reason == speechsdk.ResultReason.NoMatch:
        print("No speech could be recognized")
    elif result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = result.cancellation_details
        print("Speech Recognition canceled: {}".format(cancellation_details.reason))
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            print("Error details: {}".format(cancellation_details.error_details))


def get_prosody_continuous_results():
    """Performs pronunciation assessment asynchronously from an audio file and enable prosody assessment
        with continuous mode.
        See more information at https://aka.ms/csspeech/pa"""

    # Specify the path to an audio file containing speech (mono WAV / PCM with a sampling rate of 16 kHz).
    wave_filename = "../resources/weather_audio.wav"
    script_filename = "../resources/weather_script.txt"

    # Creates an instance of a speech config with specified subscription key and service region.
    # Replace with your own subscription key and service region (e.g., "westus").
    # Note: The sample is for en-US language.
    speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)
    audio_config = speechsdk.audio.AudioConfig(filename=wave_filename)

    with open(script_filename, "r", encoding="utf-8") as f:
        reference_text = f.read()

    # create pronunciation assessment config, set grading system, granularity and if enable miscue
    # based on your requirement.
    enable_miscue = True
    json_string = {
        "GradingSystem": "HundredMark",
        "Granularity": "Phoneme",
        "EnableMiscue": enable_miscue,
        "EnableProsodyAssessment": "True",
    }
    pronunciation_config = speechsdk.PronunciationAssessmentConfig(json_string=json.dumps(json_string))
    pronunciation_config.reference_text = reference_text

    # Creates a speech recognizer using a file as audio input.
    language = 'en-US'
    speech_recognizer = speechsdk.SpeechRecognizer(
        speech_config=speech_config, language=language, audio_config=audio_config)
    # apply pronunciation assessment config to speech recognizer
    pronunciation_config.apply_to(speech_recognizer)

    done = False
    recognized_words = []
    prosody_scores = []
    fluency_scores = []
    durations = []

    def stop_cb(evt):
        """callback that signals to stop continuous recognition upon receiving an event `evt`"""
        print("CLOSING on {}".format(evt))
        nonlocal done
        done = True

    def recognized(evt):
        print("pronunciation assessment for: {}".format(evt.result.text))
        pronunciation_result = speechsdk.PronunciationAssessmentResult(evt.result)
        print("    Accuracy score: {}, pronunciation score: {}, completeness score : {}, fluency score: {}".format(
            pronunciation_result.accuracy_score, pronunciation_result.pronunciation_score,
            pronunciation_result.completeness_score, pronunciation_result.fluency_score
        ), end="")
        nonlocal recognized_words, prosody_scores, fluency_scores, durations
        recognized_words += pronunciation_result.words
        fluency_scores.append(pronunciation_result.fluency_score)
        json_result = evt.result.properties.get(speechsdk.PropertyId.SpeechServiceResponse_JsonResult)
        jo = json.loads(json_result)
        nb = jo["NBest"][0]
        if "ProsodyScore" in nb["PronunciationAssessment"]:
            prosody_score = nb["PronunciationAssessment"]["ProsodyScore"]
            prosody_scores.append(prosody_score)
            print(", prosody score: {}".format(prosody_score))
        else:
            print()
        durations.append(sum([int(w["Duration"]) for w in nb["Words"]]))

    # Connect callbacks to the events fired by the speech recognizer
    speech_recognizer.recognized.connect(recognized)
    speech_recognizer.session_started.connect(lambda evt: print("SESSION STARTED: {}".format(evt)))
    speech_recognizer.session_stopped.connect(lambda evt: print("SESSION STOPPED {}".format(evt)))
    speech_recognizer.canceled.connect(lambda evt: print("CANCELED {}".format(evt)))
    speech_recognizer.session_started.connect(lambda evt: None)
    speech_recognizer.session_stopped.connect(lambda evt: None)
    speech_recognizer.canceled.connect(lambda evt: None)
    # stop continuous recognition on either session stopped or canceled events
    speech_recognizer.session_stopped.connect(stop_cb)
    speech_recognizer.canceled.connect(stop_cb)

    # Start continuous pronunciation assessment
    speech_recognizer.start_continuous_recognition()
    while not done:
        time.sleep(.5)

    speech_recognizer.stop_continuous_recognition()

    # we need to convert the reference text to lower case, and split to words, then remove the punctuations.
    if language == "zh-CN":
        # Use jieba package to split words for Chinese
        import jieba
        import zhon.hanzi
        jieba.suggest_freq([x.word for x in recognized_words], True)
        reference_words = [w for w in jieba.cut(reference_text) if w not in zhon.hanzi.punctuation]
    else:
        reference_words = [w.strip(string.punctuation) for w in reference_text.lower().split()]

    # For continuous pronunciation assessment mode, the service won"t return the words with `Insertion` or `Omission`
    # even if miscue is enabled.
    # We need to compare with the reference text after received all recognized words to get these error words.
    if enable_miscue:
        diff = difflib.SequenceMatcher(None, reference_words, [x.word for x in recognized_words])
        final_words = []
        for tag, i1, i2, j1, j2 in diff.get_opcodes():
            if tag in ["insert", "replace"]:
                for word in recognized_words[j1:j2]:
                    if word.error_type == "None":
                        word._error_type = "Insertion"
                    final_words.append(word)
            if tag in ["delete", "replace"]:
                for word_text in reference_words[i1:i2]:
                    word = speechsdk.PronunciationAssessmentWordResult({
                        "Word": word_text,
                        "PronunciationAssessment": {
                            "ErrorType": "Omission",
                        }
                    })
                    final_words.append(word)
            if tag == "equal":
                final_words += recognized_words[j1:j2]
    else:
        final_words = recognized_words

    # We can calculate whole accuracy by averaging
    final_accuracy_scores = []
    for word in final_words:
        if word.error_type == 'Insertion':
            continue
        else:
            final_accuracy_scores.append(word.accuracy_score)
    accuracy_score = sum(final_accuracy_scores) / len(final_accuracy_scores)

    # Re-calculate the prosody score by averaging
    if len(prosody_scores) == 0:
        prosody_score = float("nan")
    else:
        prosody_score = sum(prosody_scores) / len(durations)

    # Re-calculate fluency score
    fluency_score = sum([x * y for (x, y) in zip(fluency_scores, durations)]) / sum(durations)
    # Calculate whole completeness score
    completeness_score = len([w for w in recognized_words if w.error_type == "None"]) / len(reference_words) * 100
    completeness_score = completeness_score if completeness_score <= 100 else 100
    words = [w for w in final_words]

    if math.isnan(prosody_score):
        scores = [accuracy_score, fluency_score, completeness_score]
        scores.sort()
        pronunciation_score = 0.6 * scores[0] + 0.2 * scores[1] + 0.2 * scores[2]
    else:
        scores = [accuracy_score, prosody_score, fluency_score, completeness_score]
        scores.sort()
        pronunciation_score = 0.4 * scores[0] + 0.2 * scores[1] + 0.2 * scores[2] + 0.2 * scores[3]

    print(f"Accuracy Score: {accuracy_score:.1f}")
    if not math.isnan(prosody_score):
        print(f"Prosody Score: {prosody_score:.1f}")
    print(f"Fluency Score: {fluency_score:.1f}")
    print(f"Completeness Score: {completeness_score:.1f}")
    print(f"Pronunciation Score: {pronunciation_score:.1f}")
    print("\n    Index:\tWord\t\tWordAccScore\tPhonemeAccScore")
    for idx in range(len(words)):
        word = words[idx]
        phoneme_accuracy_score = [(x.phoneme, x.accuracy_score) for x in word.phonemes]
        print(f"       {idx + 1:02d}:\t{word.word:16s}{word.accuracy_score:.1f}\t\t{phoneme_accuracy_score}")


if __name__ == "__main__":
    while True:
        funs = [get_assessment_results_with_scenario_id, get_content_results, get_prosody_results,
                get_prosody_continuous_results]
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
