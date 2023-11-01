import difflib
import json
import math
import string
import sys
import time
import requests
import wave
import threading

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


def get_assessment_results_with_json_config():
    """Performs pronunciation assessment asynchronously with input from an audio file and configured with Json.
        See more information at https://aka.ms/csspeech/pa"""

    # Specify the path to an audio file containing speech (mono WAV / PCM with a sampling rate of 16 kHz).
    wave_filename = "../resources/weather_audio.wav"
    script_filename = "../resources/weather_script.txt"

    enable_miscue = True
    enable_prosody_assessment = True
    scenario_id = ""  # scenario ID will be assigned by product team, by default it is empty string.

    # Creates an instance of a speech config with specified subscription key and service region.
    # Replace with your own subscription key and service region (e.g., "westus").
    # Note: The sample is for en-US language.
    speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)
    audio_config = speechsdk.audio.AudioConfig(filename=wave_filename)

    with open(script_filename, "r", encoding="utf-8") as f:
        reference_text = f.read()

    # Create pronunciation assessment config, set grading system, granularity and if enable miscue
    # based on your requirement.
    json_string = {
        "GradingSystem": "HundredMark",
        "Granularity": "Phoneme",
        "EnableMiscue": enable_miscue,
        "ScenarioId": f"{scenario_id}",
        "EnableProsodyAssessment": enable_prosody_assessment,
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
        print("Pronunciation results:")
        print(json.dumps(pronunciation_result_json, indent=4))
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

    # Open the connection
    connection.open(for_continuous_recognition=True)

    done = False
    recognized_text = ""

    def stop_cb(evt):
        """callback that signals to stop continuous recognition upon receiving an event `evt`"""
        print("CLOSING on {}".format(evt))
        nonlocal done
        done = True

    def recognized(evt):
        nonlocal recognized_text
        if (evt.result.reason == speechsdk.ResultReason.RecognizedSpeech or
                evt.result.reason == speechsdk.ResultReason.NoMatch):
            json_result = json.loads(evt.result.properties.get(speechsdk.PropertyId.SpeechServiceResponse_JsonResult))
            if len(json_result["DisplayText"].strip()) > 1:
                print(f"Pronunciation Assessment for: {evt.result.text}")
                print(json.dumps(json_result, indent=4))
                recognized_text += " " + evt.result.text
            else:
                print(f"Content Assessment for: {recognized_text}")
                print(json.dumps(json_result, indent=4))

    # Connect callbacks to the events fired by the speech recognizer
    speech_recognizer.recognized.connect(recognized)
    speech_recognizer.session_started.connect(lambda evt: print("SESSION STARTED: {}".format(evt)))
    speech_recognizer.session_stopped.connect(lambda evt: print("SESSION STOPPED {}".format(evt)))
    speech_recognizer.canceled.connect(lambda evt: print("CANCELED {}".format(evt)))
    # Stop continuous recognition on either session stopped or canceled events
    speech_recognizer.session_stopped.connect(stop_cb)
    speech_recognizer.canceled.connect(stop_cb)

    # Start continuous pronunciation assessment
    speech_recognizer.start_continuous_recognition()
    while not done:
        time.sleep(.5)
    speech_recognizer.stop_continuous_recognition()

    # close the connection
    connection.close()


def get_continuous_results():
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
        prosody_score = sum(prosody_scores) / len(prosody_scores)

    # Re-calculate fluency score
    fluency_score = sum([x * y for (x, y) in zip(fluency_scores, durations)]) / sum(durations)
    # Calculate whole completeness score
    completeness_score = len([w for w in recognized_words if w.error_type == "None"]) / len(reference_words) * 100
    completeness_score = completeness_score if completeness_score <= 100 else 100
    words = [w for w in final_words]

    print(f"Accuracy Score: {accuracy_score:.1f}")
    if not math.isnan(prosody_score):
        print(f"Prosody Score: {prosody_score:.1f}")
    print(f"Fluency Score: {fluency_score:.1f}")
    print(f"Completeness Score: {completeness_score:.1f}")
    print("\n    Index:\tWord\t\tWordAccScore\tPhonemeAccScore")
    for idx in range(len(words)):
        word = words[idx]
        phoneme_accuracy_score = [(x.phoneme, x.accuracy_score) for x in word.phonemes]
        print(f"       {idx + 1:02d}:\t{word.word:16s}{word.accuracy_score:.1f}\t\t{phoneme_accuracy_score}")


def read_wave_header(file_path):
    with wave.open(file_path, 'rb') as audio_file:
        framerate = audio_file.getframerate()
        bits_per_sample = audio_file.getsampwidth() * 8
        num_channels = audio_file.getnchannels()
        return framerate, bits_per_sample, num_channels


def push_stream_writer(stream, filenames):
    # The number of bytes to push per buffer
    n_bytes = 3200
    try:
        for filename in filenames:
            wav_fh = wave.open(filename)
            # Start pushing data until all data has been read from the file
            try:
                while True:
                    frames = wav_fh.readframes(n_bytes // 2)
                    # print('read {} bytes'.format(len(frames)))
                    if not frames:
                        break
                    stream.write(frames)
                    time.sleep(.1)
            finally:
                wav_fh.close()
    finally:
        stream.close()


def chatting_from_file():
    """Performs pronunciation assessment asynchronously from an audio file and enable prosody/content assessment
        with continuous mode.
        See more information at https://aka.ms/csspeech/pa"""

    topic = "YourOwnTopic"
    input_files = ["../resources/chat_input_1.wav", "../resources/chat_input_2.wav"]

    def stt(filename):
        result_text = []

        speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)
        audio_config = speechsdk.audio.AudioConfig(filename=filename)

        speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)

        done = False

        def stop_cb(evt: speechsdk.SessionEventArgs):
            """callback that signals to stop continuous recognition upon receiving an event `evt`"""
            nonlocal done
            done = True

        # Connect callbacks to the events fired by the speech recognizer
        speech_recognizer.recognized.connect(lambda evt: result_text.append(evt.result.text))
        # Stop continuous recognition on either session stopped or canceled events
        speech_recognizer.session_stopped.connect(stop_cb)
        speech_recognizer.canceled.connect(stop_cb)

        # Start continuous speech recognition
        speech_recognizer.start_continuous_recognition()
        while not done:
            time.sleep(.5)

        speech_recognizer.stop_continuous_recognition()
        text = "".join(result_text)
        print("YOU: ", text)
        return text


    def call_gpt(send_text):
        your_resource_name = "YourResourceName"
        your_deployment_id = "YourDeploymentId"
        api_version = "YourApiVersion"
        your_api_key = "YourApiKey"

        url = f"https://{your_resource_name}.openai.azure.com/openai/deployments/{your_deployment_id}/chat/completions?api-version={api_version}"
        headers = {"Content-Type": "application/json", "api-key": your_api_key}
        data = {"messages":[
            {"role": "system", "content": "You are a voice assistant, and when you answer questions, your response should not exceed 25 words."},
            {"role": "user", "content": send_text}
        ]}

        text = json.loads(requests.post(url=url, headers=headers, data=json.dumps(data)).content)["choices"][0]["message"]["content"]
        print("GPT: ", text)
        return f'<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="en-US">\
                    <voice name="en-US-JennyNeural">\
                        {text}\
                    </voice>\
                </speak>'


    def tts(text, output_filename):
        file_config = speechsdk.audio.AudioOutputConfig(filename=output_filename)
        speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)
        speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=file_config)

        result = speech_synthesizer.speak_ssml_async(text).get()
        # Check result
        if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            pass
        elif result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = result.cancellation_details
            print("Speech synthesis canceled: {}".format(cancellation_details.reason))
            if cancellation_details.reason == speechsdk.CancellationReason.Error:
                print("Error details: {}".format(cancellation_details.error_details))


    def pronunciation_assessment():
        # Setup the audio stream
        framerate, bits_per_sample, num_channels = read_wave_header(input_files[0])
        format = speechsdk.audio.AudioStreamFormat(samples_per_second=framerate, bits_per_sample=bits_per_sample, channels=num_channels)
        stream = speechsdk.audio.PushAudioInputStream(format)
        audio_config = speechsdk.audio.AudioConfig(stream=stream)
        
        speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)

        # Create pronunciation assessment config, set grading system, granularity and if enable miscue based on your requirement.
        pronunciation_config = speechsdk.PronunciationAssessmentConfig(
            grading_system=speechsdk.PronunciationAssessmentGradingSystem.HundredMark,
            granularity=speechsdk.PronunciationAssessmentGranularity.Phoneme,
            enable_miscue=False)
        pronunciation_config.enable_prosody_assessment()
        pronunciation_config.enable_content_assessment_with_topic(topic)

        # Creates a speech recognizer using a file as audio input.
        language = 'en-US'
        speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, language=language, audio_config=audio_config)
        # Apply pronunciation assessment config to speech recognizer
        pronunciation_config.apply_to(speech_recognizer)

        done = False
        recognized_words = []
        prosody_scores = []
        fluency_scores = []
        durations = []
        results = []
        json_words = []
        mis_pronunciation_words = []
        display_text = ""

        def stop_cb(evt):
            """callback that signals to stop continuous recognition upon receiving an event `evt`"""
            nonlocal done
            done = True

        def recognized(evt):
            pronunciation_result = speechsdk.PronunciationAssessmentResult(evt.result)
            nonlocal recognized_words, prosody_scores, fluency_scores, durations, results, json_words, display_text, mis_pronunciation_words
            results.append(pronunciation_result)
            recognized_words += pronunciation_result.words
            fluency_scores.append(pronunciation_result.fluency_score)
            json_result = evt.result.properties.get(speechsdk.PropertyId.SpeechServiceResponse_JsonResult)
            jo = json.loads(json_result)
            nb = jo["NBest"][0]
            display_text += nb["Display"]
            json_words += nb["Words"]
            if "ProsodyScore" in nb["PronunciationAssessment"]:
                prosody_score = nb["PronunciationAssessment"]["ProsodyScore"]
                prosody_scores.append(prosody_score)
            
            for word in pronunciation_result.words:
                if word.error_type == "Mispronunciation":
                    mis_pronunciation_words.append(word)

            durations.append(sum([int(w["Duration"]) for w in nb["Words"]]))

        # Connect callbacks to the events fired by the speech recognizer
        speech_recognizer.recognized.connect(recognized)
        # stop continuous recognition on either session stopped or canceled events
        speech_recognizer.session_stopped.connect(stop_cb)
        speech_recognizer.canceled.connect(stop_cb)

        # Start push stream writer thread
        push_stream_writer_thread = threading.Thread(target=push_stream_writer, args=[stream, input_files])
        push_stream_writer_thread.start()
        # Start continuous pronunciation assessment
        speech_recognizer.start_continuous_recognition()
        while not done:
            time.sleep(.5)

        speech_recognizer.stop_continuous_recognition()
        push_stream_writer_thread.join()

        # We can calculate whole accuracy by averaging
        final_accuracy_scores = []
        for word in recognized_words:
            if word.error_type == 'Insertion':
                continue
            else:
                final_accuracy_scores.append(word.accuracy_score)
        accuracy_score = sum(final_accuracy_scores) / len(final_accuracy_scores)

        # Re-calculate the prosody score by averaging
        if len(prosody_scores) == 0:
            prosody_score = float("nan")
        else:
            prosody_score = sum(prosody_scores) / len(prosody_scores)

        # Re-calculate fluency score
        fluency_score = sum([x * y for (x, y) in zip(fluency_scores, durations)]) / sum(durations)

        pron_score = accuracy_score * 0.6 + fluency_score * 0.2 + prosody_score * 0.2
        print(f"Pronunciation score: {pron_score:.1f}")
        print(f"Accuracy Score: {accuracy_score:.1f}")
        if not math.isnan(prosody_score):
            print(f"Prosody Score: {prosody_score:.1f}")
        print(f"Fluency Score: {fluency_score:.1f}")
        # Content assessment result is in the last pronunciation assessment block
        assert results[-1].content_assessment_result is not None
        content_result = results[-1].content_assessment_result
        print(f"Vocabulary score: {content_result.vocabulary_score:.1f} \nGrammar score: {content_result.grammar_score:.1f} \nTopic score: {content_result.topic_score:.1f}")

        comment_result(
            {
                "accuracy score": accuracy_score,
                "fluency score": fluency_score,
                "prosody score": prosody_score,
                "vocabulary score": content_result.vocabulary_score,
                "grammar score": content_result.grammar_score,
                "topic score": content_result.topic_score
            },
            set_punctuation(json_words, display_text),
            mis_pronunciation_words
        )


    def set_punctuation(json_words, display_text):
        for idx, word in enumerate(display_text.split(" ")):
            if not word[-1].isalpha() and not word[-1].isdigit():
                json_words[idx]["is_punctuation"] = True
        return json_words


    def comment_result(scores_dict, json_words, mis_pronunciation_words):
        message_dict = {
            "Excellent": [],
            "Good": [],
            "Fair": [],
            "Poor": [],
            "Bad": [],
        }
        error_dict = {
            "Missing break": [],
            "Unexpected break": [],
            "Monotone": [],
        }

        def set_message_dict(score, score_name):
            if score >= 80:
                return message_dict["Excellent"].append(score_name)
            elif score < 80 and score >= 60:
                return message_dict["Good"].append(score_name)
            elif score < 60 and score >= 40:
                return message_dict["Fair"].append(score_name)
            elif score < 40 and score >= 20:
                return message_dict["Poor"].append(score_name)
            else:
                return message_dict["Bad"].append(score_name)


        def get_prosody_error(error_type, word, last_word):
            threshold = 0.1
            if error_type == "MissingBreak" or error_type == "UnexpectedBreak":
                break_error_info = word["PronunciationAssessment"]["Feedback"]["Prosody"]["Break"].get(error_type, "null")
                if break_error_info == "null":
                    return False
                if error_type == "MissingBreak":
                    if break_error_info["Confidence"] >= threshold and last_word.get("is_punctuation", False):
                        return True
                if error_type == "UnexpectedBreak":
                    if break_error_info["Confidence"] >= threshold and not last_word.get("is_punctuation", False):
                        return True
                return False
            elif error_type == "Monotone" and error_type in word["PronunciationAssessment"]["Feedback"]["Prosody"]["Intonation"]["ErrorTypes"]:
                return True
            else:
                return False


        def set_error_dict(json_words):
            for idx, word in enumerate(json_words):
                if get_prosody_error("MissingBreak", word, json_words[idx-1]):
                    error_dict["Missing break"].append(word)
                elif get_prosody_error("UnexpectedBreak", word, json_words[idx-1]):
                    error_dict["Unexpected break"].append(word)
                elif get_prosody_error("Monotone", word, json_words[idx-1]):
                    error_dict["Monotone"].append(word)


        def get_error_message(error_types):
            message = ""
            for error_type in error_types:
                if len(error_dict[error_type]) != 0:
                    message += f"{error_type} count is {len(error_dict[error_type])}. near the word "
                    message += f"{' '.join([word['Word'].strip() for word in error_dict[error_type]])}. "
            
            return message


        def get_report(json_words, mis_pronunciation_words):

            set_error_dict(json_words)

            origin_content = ""
            if len(mis_pronunciation_words) != 0:
                origin_content = "Accuracy report:"
                for mis_word in mis_pronunciation_words:
                    phone = "".join([syllable.syllable for syllable in mis_word.syllables])
                    origin_content += f" word {mis_word.word}"
                    origin_content += f" correct pronunciation is {mis_word.word},"
                    origin_content += f' your pronunciation is <phoneme alphabet="ipa" ph="{phone}">{mis_word.word}</phoneme>. '

            if scores_dict["fluency score"] < 60 or scores_dict["prosody score"] < 60:
                if scores_dict["fluency score"] < 60:
                    origin_content += "Fluency "
                if scores_dict["prosody score"] < 60:
                    origin_content += "Prosody "
                origin_content += "report: "
                origin_content += get_error_message(["Missing break", "Unexpected break", "Monotone"])

            tts(f'<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="en-US">\
                    <voice name="en-US-JennyNeural">\
                        {origin_content}\
                    </voice>\
                </speak>', "chat_report_output.wav")


        def get_score_comment(scores_dict):
            for score_key in scores_dict:
                set_message_dict(scores_dict[score_key], score_key)

            messages = ""
            for message_key in message_dict:
                if message_dict[message_key] != []:
                    is_or_are = "is" if len(message_dict[message_key]) == 1 else "are"
                    messages += f"{' and '.join(message_dict[message_key])} {is_or_are} {message_key}. "

            tts(f'<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="en-US">\
                    <voice name="en-US-JennyNeural">\
                        {messages}\
                    </voice>\
                </speak>', "chat_score_comment_output.wav")


        get_score_comment(scores_dict)
        get_report(json_words, mis_pronunciation_words)

    for idx, file in enumerate(input_files):
        tts(call_gpt(stt(file)), f"gpt_output_{idx+1}.wav")
    pronunciation_assessment()


if __name__ == "__main__":
    while True:
        funs = [get_assessment_results_with_json_config, get_content_results, get_continuous_results, chatting_from_file]
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
