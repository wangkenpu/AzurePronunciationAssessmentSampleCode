import json
import sys

try:
    import azure.cognitiveservices.speech as speechsdk
except ImportError:
    print("""
    Importing the Speech SDK for Python failed.
    Refer to
    https://docs.microsoft.com/azure/cognitive-services/speech-service/quickstart-python for
    installation instructions.
    """)
    import sys
    sys.exit(1)


# Set up the subscription info for the Speech Service:
# Replace with your own subscription key and service region (e.g., "westus").
speech_key, service_region = "YourSubscriptionKey", "YourServiceRegion"


def get_assessment_results_with_scenario_id_json():
    """Performs pronunciation assessment asynchronously with input from an audio file.
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
    # create pronunciation assessment config, set grading system, granularity and if enable miscue based on your requirement.
    pronunciation_config = speechsdk.PronunciationAssessmentConfig(json_string=json.dumps(json_string))
    pronunciation_config.reference_text = reference_text

    # Creates a speech recognizer using a file as audio input.
    language = 'en-US'
    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, language=language, audio_config=audio_config)
    # apply pronunciation assessment config to speech recognizer
    pronunciation_config.apply_to(speech_recognizer)

    result = speech_recognizer.recognize_once_async().get()

    # Check the result
    if result.reason == speechsdk.ResultReason.RecognizedSpeech:
        pronunciation_result_json = json.loads(result.properties.get(speechsdk.PropertyId.SpeechServiceResponse_JsonResult))
        print(pronunciation_result_json)
    elif result.reason == speechsdk.ResultReason.NoMatch:
        print("No speech could be recognized")
    elif result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = result.cancellation_details
        print("Speech Recognition canceled: {}".format(cancellation_details.reason))
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            print("Error details: {}".format(cancellation_details.error_details))


def get_content_results_json():
    """Performs pronunciation assessment asynchronously with input from an audio file.
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
        pronunciation_result_json = json.loads(result.properties.get(speechsdk.PropertyId.SpeechServiceResponse_JsonResult))
        print(pronunciation_result_json["NBest"][0]["ContentAssessment"])
    else:
        message = f">>> [ERROR] WaveName: {wave_filename}, Reason: {result.reason}"
        raise Exception(message)

    # close the connection
    connection.close()


def get_prosody_results_json():
    """Performs pronunciation assessment asynchronously with input from an audio file.
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
    json_string = {
        "GradingSystem": "HundredMark",
        "Granularity": "Phoneme",
        "EnableMiscue": "True",
        "EnableProsodyAssessment": "True",
    }
    # create pronunciation assessment config, set grading system, granularity and if enable miscue based on your requirement.
    pronunciation_config = speechsdk.PronunciationAssessmentConfig(json_string=json.dumps(json_string))
    pronunciation_config.reference_text = reference_text

    # Creates a speech recognizer using a file as audio input.
    language = 'en-US'
    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, language=language, audio_config=audio_config)
    # apply pronunciation assessment config to speech recognizer
    pronunciation_config.apply_to(speech_recognizer)

    result = speech_recognizer.recognize_once_async().get()

    # Check the result
    if result.reason == speechsdk.ResultReason.RecognizedSpeech:
        pronunciation_result_json = json.loads(result.properties.get(speechsdk.PropertyId.SpeechServiceResponse_JsonResult))
        print(pronunciation_result_json)
    elif result.reason == speechsdk.ResultReason.NoMatch:
        print("No speech could be recognized")
    elif result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = result.cancellation_details
        print("Speech Recognition canceled: {}".format(cancellation_details.reason))
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            print("Error details: {}".format(cancellation_details.error_details))


if __name__ == "__main__":
    while True:
        funs = [get_assessment_results_with_scenario_id_json, get_content_results_json, get_prosody_results_json]
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
